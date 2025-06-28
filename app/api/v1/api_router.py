from fastapi import APIRouter
from app.api.v1.endpoints import peques, storage

api_router = APIRouter()

# Incluir el router de peques
api_router.include_router(peques.router, tags=["Peques"])

# Incluir el router de storage
api_router.include_router(storage.router, prefix="/storage", tags=["Storage"])
