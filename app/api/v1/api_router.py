from fastapi import APIRouter
from app.api.v1.endpoints import storage, investment

api_router = APIRouter()

# Incluir el router de storage
api_router.include_router(storage.router, prefix="/storage", tags=["Storage"])

# Incluir el router de investment
api_router.include_router(investment.router, prefix="/investment", tags=["Investment"])
