from fastapi import APIRouter
from app.controllers.pyme_controller import router as pyme_router

router = APIRouter()

# Incluir el router de análisis de Pyme
router.include_router(pyme_router)
