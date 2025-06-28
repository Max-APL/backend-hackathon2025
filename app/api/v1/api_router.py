from fastapi import APIRouter
from app.api.v1.endpoints import storage

api_router = APIRouter()

# Incluir el router de storage
api_router.include_router(storage.router, prefix="/storage", tags=["Storage"])
