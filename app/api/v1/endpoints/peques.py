from fastapi import APIRouter

from app.schemas.peques_schema import PequeRegistroResponse, PequeRegistroRequest
from app.services.peques_service import get_peques_from_sheet, registrar_peque

router = APIRouter()

@router.get("/peques/from-sheet")
def obtener_peques_desde_sheet():
    return get_peques_from_sheet()

@router.post("/peques/registrar", response_model=PequeRegistroResponse)
def registrar_peque_endpoint(data: PequeRegistroRequest):
    """
    Registra un nuevo negocio (peque) y devuelve negocios cercanos a la ubicación ingresada.
    """
    nearby_peques = registrar_peque(data)
    return {"nearby_peques": nearby_peques}


