from typing import Any, Optional

import httpx

from backend.config import Settings
from backend.ingestion.exceptions import SmartAPIError
from backend.ingestion.schemas import NormalizedTick, RawSmartAPIResponse
from backend.ingestion.validator import normalize_ltp_payload
from backend.utils.logger import logger


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

    async def __aenter__(self) -> "SmartAPIClient":
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=self.settings.angel_one_base_url)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._client:
            await self._client.aclose()

    async def get_ltp(
        self, exchange: str, symbol: str, symbol_token: str
    ) -> NormalizedTick:
        """
        Fetch Last Traded Price (LTP) and return a NormalizedTick.
        """
        if not self._client:
            raise SmartAPIError(
                "Client session not initialized. Use 'async with' context manager."
            )

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
            response.raise_for_status()

            # Use model_validate for strictly typed dict unpacking in pydantic v2
            raw_response = RawSmartAPIResponse.model_validate(response.json())

            if not raw_response.status or not raw_response.data:
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
