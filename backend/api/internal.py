from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import Settings
from backend.config_validator import validate_configuration
from backend.db.dependencies import get_db_session
from backend.engine.inference import InferenceManager, ModelReloadError
from backend.persistence.prediction import PredictionRepository
from backend.schemas.prediction import ModelReloadResponse
from backend.ingestion.client import SmartAPIClient
from backend.ingestion.exceptions import SmartAPIError
import pyotp

router = APIRouter(prefix="/internal", tags=["Internal"])

async def verify_internal_token(x_internal_token: str | None = Header(default=None, description="Internal API Token")) -> None:
    """Verify the X-Internal-Token header against settings."""
    settings = validate_configuration()
    if not x_internal_token or x_internal_token != settings.internal_api_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing internal token"
        )

@router.post("/reload-models", response_model=ModelReloadResponse, dependencies=[Depends(verify_internal_token)])
async def reload_models(session: AsyncSession = Depends(get_db_session)) -> ModelReloadResponse:
    """
    Trigger zero-downtime hot reload of ML models.
    Requires X-Internal-Token header.
    """
    manager = InferenceManager()
    
    try:
        repo = PredictionRepository(session)
        paths = await repo.get_active_model_paths()
        
        # This will raise ModelReloadError on failure (all-or-nothing)
        manager.load_models(paths)
        
        status_map = manager.model_status
        available = [k for k, v in status_map.items() if v]
        unavailable = [k for k, v in status_map.items() if not v]
        
        return ModelReloadResponse(
            success=True,
            reload_time_ms=manager.last_reload_duration_ms,
            available_models=available,
            unavailable_models=unavailable,
            last_reload_time=manager.last_reload_time,
            last_reload_status=manager.last_reload_status
        )
    except ModelReloadError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model reload transaction failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during reload: {str(e)}"
        )

@router.get("/diagnostics", dependencies=[Depends(verify_internal_token)])
async def get_diagnostics() -> dict:
    """
    Diagnostic endpoint to verify environment variables, pyotp decoding, and SmartAPI login pipeline.
    """
    settings = validate_configuration()
    
    secret = getattr(settings, "angel_one_totp_secret", "")
    secret_present = bool(secret and secret != "YOUR_COPIED_KEY" and secret != "dummy")
    
    diagnostics = {
        "environment": settings.environment,
        "ANGEL_ONE_TOTP_SECRET_present": secret_present,
        "ANGEL_ONE_TOTP_SECRET_length": len(secret) if secret else 0,
        "Base32_validation": "PENDING",
        "authentication_stage": "NOT_STARTED",
        "authentication_error": None
    }
    
    # 1. Base32 validation test
    diagnostics["authentication_stage"] = "TOTP_GENERATION"
    try:
        if not secret_present:
            raise ValueError("Secret is empty or placeholder")
        pyotp.TOTP(secret).now()
        diagnostics["Base32_validation"] = "SUCCESS"
    except Exception as e:
        diagnostics["Base32_validation"] = f"FAIL: {str(e)}"
        diagnostics["authentication_error"] = f"pyotp error: {str(e)}"
        return diagnostics
        
    # 2. SmartAPI Login Test
    diagnostics["authentication_stage"] = "SMARTAPI_LOGIN"
    async with SmartAPIClient(settings) as client:
        try:
            await client.login()
            diagnostics["authentication_stage"] = "SUCCESS"
        except SmartAPIError as e:
            diagnostics["authentication_error"] = f"SmartAPIError: {str(e)}"
        except Exception as e:
            diagnostics["authentication_error"] = f"Unexpected Error: {str(e)}"
            
    return diagnostics
