from fastapi import APIRouter
from app.api.v1.endpoints import peques

api_router = APIRouter()
api_router.include_router(peques.router, tags=["Peques"])

# Incluir el router de storage
api_router.include_router(storage.router, prefix="/storage", tags=["Storage"])
