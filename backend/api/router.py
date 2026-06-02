from fastapi import APIRouter

from backend.api import market, portfolio, prediction, signal

api_router = APIRouter(prefix="/api/v1")

# Register sub-routers under the V1 API prefix
api_router.include_router(market.router)
api_router.include_router(prediction.router)
api_router.include_router(signal.router)
api_router.include_router(portfolio.router)
