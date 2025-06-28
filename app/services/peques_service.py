import json
from app.repositories.peques_repository import fetch_peques_from_google_sheet
from app.utils.score_utils import calculate_score_normalized
from app.utils.google_sheets import (
    leer_hoja_results,
    generar_url_scraping,
    agregar_a_hoja_scrape,
)
import time
import requests

# URL de n8n webhook
N8N_WEBHOOK_URL = "https://maxpasten.app.n8n.cloud/webhook-test/f182d304-1d67-4798-bd58-24dc84caec48"


def get_peques_from_sheet():
    peques = fetch_peques_from_google_sheet()
    for p in peques:
        p.score_normalized = calculate_score_normalized(p)
    return peques


def calcular_distancia_km(lat1, lng1, lat2, lng2):
    # Aproximación usando distancia euclidiana en grados, luego escala a km (1° ≈ 111 km)
    return ((lat1 - lat2) ** 2 + (lng1 - lng2) ** 2) ** 0.5 * 111


def get_nearby_peques(lat, lng, max_km=1.5):
    rows = leer_hoja_results()
    cercanos = []

    for row in rows:
        try:
            coords_str = row.get("gps_coordinates", "{}")
            coords = json.loads(coords_str)
            lat2 = coords.get("latitude")
            lng2 = coords.get("longitude")
            if lat2 is not None and lng2 is not None:
                dist = calcular_distancia_km(lat, lng, lat2, lng2)
                if dist <= max_km:
                    row["score_normalized"] = calculate_score_normalized(row)
                    cercanos.append(row)
        except Exception:
            continue

    return cercanos

def lanzar_n8n():
    try:
        response = requests.get(N8N_WEBHOOK_URL, timeout=10)
        print(f"✅ Webhook lanzado: {response.status_code}")
    except Exception as e:
        print("❌ Error al lanzar webhook n8n:", e)

def registrar_peque(data):
    try:
        lat_str, lng_str = data.ubicacion.split(",")
        lat, lng = float(lat_str.strip()), float(lng_str.strip())
    except Exception as e:
        raise ValueError("Ubicación mal formateada. Usa el formato: '-17.68,-63.15'") from e

    url = generar_url_scraping(data.tipo_negocio, lat, lng)
    agregar_a_hoja_scrape(url)

    lanzar_n8n()  # <-- Lanzamos el flujo
    time.sleep(4)  # <-- Esperamos 4 segundos para que n8n complete

    return get_nearby_peques(lat, lng)