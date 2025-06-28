import time
from http.client import HTTPException
from typing import List

from fastapi import APIRouter, Query
import requests

from app.models.peques_model import PequeModel
from app.schemas.peques_schema import PequeRegistroResponse, PequeRegistroRequest
from app.services.peques_service import get_peques_from_sheet, registrar_peque, scrapear_y_retornar_cercanos, \
    scrapear_y_retornar_cercanos_async, iniciar_scrapeo, obtener_peques_cercanos

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




@router.get("/peques/scrapear")
async def scrapear_peques(
    lat: float = Query(..., description="Latitud"),
    lng: float = Query(..., description="Longitud"),
    tipo: str = Query("restaurante", description="Tipo de negocio")
):
    try:
        return await scrapear_y_retornar_cercanos_async(lat, lng, tipo)
    except Exception as e:
        # Capturamos el error real para debug
        return {"error": str(e)}

@router.post("/peques/scrapear-url")
def scrapear_url(tipo: str = "restaurante", lat: float = Query(...), lng: float = Query(...)):
    url = iniciar_scrapeo(tipo, lat, lng)
    return {"mensaje": "Scrapeo iniciado", "url": url}


@router.get("/peques/resultados-cercanos")
def get_peques_cercanos(lat: float = Query(...), lng: float = Query(...), max_km: float = 1.0):
    datos = obtener_peques_cercanos(lat, lng, max_km)
    return {"cercanos": datos, "cantidad": len(datos)}


@router.post("/peques/scrapear-y-buscar")
def scrapear_y_buscar(tipo: str = "restaurante", lat: float = Query(...), lng: float = Query(...)):
    # Iniciar el scraping
    url = iniciar_scrapeo(tipo, lat, lng)

    # Espera activa hasta que aparezcan resultados nuevos en esa zona
    tiempo_inicio = time.time()
    TIMEOUT = 30  # segundos máximos de espera
    INTERVALO = 2  # segundos entre chequeos

    while time.time() - tiempo_inicio < TIMEOUT:
        resultados = obtener_peques_cercanos(lat, lng)
        if resultados:
            return {
                "mensaje": "Scrapeo completado y resultados encontrados",
                "url_scrapeada": url,
                "cantidad": len(resultados),
                "cercanos": resultados,
            }
        time.sleep(INTERVALO)

    raise HTTPException(status_code=504, detail="No se encontraron resultados dentro del tiempo de espera.")

@router.get("/peques/scrapear-y-filtrar")
async def scrapear_y_filtrar(
    lat: float,
    lng: float,
    tipo: str = "restaurante"
):
    print("🚀 Iniciando scraping y filtrado de negocios...")
    await iniciar_scrapeo(lat, lng, tipo)
    print("🔍 Obteniendo negocios cercanos...")
    cercanos = obtener_peques_cercanos(lat, lng)
    return cercanos

