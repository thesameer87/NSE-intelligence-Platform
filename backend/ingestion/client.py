from typing import Any, Optional

import httpx

from backend.config import Settings
from backend.ingestion.exceptions import SmartAPIError
from backend.ingestion.schemas import NormalizedTick, RawSmartAPIResponse
from backend.ingestion.validator import normalize_ltp_payload
from backend.utils.logger import logger
import pyotp


class SmartAPIClient:
    """
    Mock-safe boundary for SmartAPI interactions.
    Handles authentication, HTTP retries, and data normalization.
    No live polling loop or websocket streaming here.
    """

    def __init__(
        self, settings: Settings, client: Optional[httpx.AsyncClient] = None
    ) -> None:
        self.settings = settings
        self._client = client
        self._jwt_token: Optional[str] = None

    async def __aenter__(self) -> "SmartAPIClient":
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=self.settings.angel_one_base_url)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._client:
            await self._client.aclose()

    async def login(self) -> None:
        """
        Authenticate with Angel One using TOTP and store the JWT securely in memory.
        Does not log the credentials or token.
        """
        if not self._client:
            raise SmartAPIError("Client session not initialized.")
            
        try:
            totp = pyotp.TOTP(self.settings.angel_one_totp_secret).now()
        except Exception as e:
            logger.error("Failed to generate TOTP. Check ANGEL_ONE_TOTP_SECRET configuration.")
            raise SmartAPIError("TOTP generation failed")

        payload = {
            "clientcode": self.settings.angel_one_client_id,
            "password": self.settings.angel_one_password,
            "totp": totp,
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-UserType": "USER",
            "X-SourceID": "WEB",
            "X-ClientLocalIP": "192.168.1.1",
            "X-ClientPublicIP": "1.1.1.1",
            "X-MACAddress": "00:00:00:00:00:00",
            "X-PrivateKey": self.settings.angel_one_api_key,
        }

        try:
            response = await self._client.post(
                "/rest/auth/angelbroking/user/v1/loginByPassword",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get("status") or not data.get("data"):
                raise SmartAPIError(f"Login failed: {data.get('message')}")
                
            self._jwt_token = data["data"].get("jwtToken")
            if not self._jwt_token:
                raise SmartAPIError("Login succeeded but no JWT returned")
                
            logger.info("Successfully authenticated with SmartAPI.")
        except httpx.HTTPError as e:
            logger.error("HTTP error during SmartAPI authentication")
            raise SmartAPIError(f"Auth HTTP request failed: {e}")

    async def get_ltp(
        self, exchange: str, symbol: str, symbol_token: str, _retry: bool = True
    ) -> NormalizedTick:
        """
        Fetch Last Traded Price (LTP) and return a NormalizedTick.
        Automatically handles re-authentication once if token is expired.
        """
        if not self._client:
            raise SmartAPIError(
                "Client session not initialized. Use 'async with' context manager."
            )
            
        if not self._jwt_token:
            await self.login()

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-UserType": "USER",
            "X-SourceID": "WEB",
            "X-ClientLocalIP": "192.168.1.1",
            "X-ClientPublicIP": "1.1.1.1",
            "X-MACAddress": "00:00:00:00:00:00",
            "X-PrivateKey": self.settings.angel_one_api_key,
            "Authorization": f"Bearer {self._jwt_token}"
        }

        payload = {
            "exchange": exchange,
            "tradingsymbol": symbol,
            "symboltoken": symbol_token,
        }

        try:
            response = await self._client.post(
                "/rest/secure/angelbroking/order/v1/getLtpData",
                json=payload,
                headers=headers,
            )
            
            # Handle token expiry (401/403) or specific API error code
            if response.status_code in (401, 403) and _retry:
                logger.warning("SmartAPI token expired. Re-authenticating...")
                self._jwt_token = None
                await self.login()
                return await self.get_ltp(exchange, symbol, symbol_token, _retry=False)
                
            response.raise_for_status()

            # Use model_validate for strictly typed dict unpacking in pydantic v2
            raw_response = RawSmartAPIResponse.model_validate(response.json())

            if not raw_response.status or not raw_response.data:
                # API sometimes returns 200 with internal error code for invalid token
                if raw_response.errorcode in ("AG8001", "AB8050") and _retry:
                    logger.warning("SmartAPI token invalid (AG8001/AB8050). Re-authenticating...")
                    self._jwt_token = None
                    await self.login()
                    return await self.get_ltp(exchange, symbol, symbol_token, _retry=False)
                    
                raise SmartAPIError(
                    f"SmartAPI error: {raw_response.message} "
                    f"(Code: {raw_response.errorcode})"
                )

            if not isinstance(raw_response.data, dict):
                raise SmartAPIError(
                    "SmartAPI returned unexpected data format for LTP: "
                    f"{type(raw_response.data)}"
                )

            return normalize_ltp_payload(symbol, raw_response.data)

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching LTP for {symbol}: {e}")
            raise SmartAPIError(f"HTTP request failed: {e}")
