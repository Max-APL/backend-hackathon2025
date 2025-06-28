from fastapi import APIRouter
from app.services.peques_service import get_peques_from_sheet

router = APIRouter()

@router.get("/peques/from-sheet")
def obtener_peques_desde_sheet():
    return get_peques_from_sheet()
