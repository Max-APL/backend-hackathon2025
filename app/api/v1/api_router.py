from fastapi import APIRouter
from app.controllers.pyme_controller import router as pyme_router
from app.api.v1.endpoints import peques, storage

api_router = APIRouter()

api_router.include_router(pyme_router)

# Incluir el router de peques
api_router.include_router(peques.router, tags=["Peques"])

# Incluir el router de storage
api_router.include_router(storage.router, prefix="/storage", tags=["Storage"])

