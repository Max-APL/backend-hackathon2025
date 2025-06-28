# app/api/v1/endpoints/peques.py

from fastapi import APIRouter, Query
from typing import List
from app.schemas.peques import PequeEmpresaResponse
from app.services.peques_service import get_peques_from_sheet

router = APIRouter()

@router.get("/peques/from-sheet", response_model=List[PequeEmpresaResponse])
def obtener_peques_desde_sheet(
    sheet_csv_url: str = Query(..., description="URL CSV pública de Google Sheets")
):
    return get_peques_from_sheet(sheet_csv_url)
