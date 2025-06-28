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
import httpx
import asyncio

# URL de n8n webhook
N8N_WEBHOOK_URL = "https://maxpasten.app.n8n.cloud/webhook/f182d304-1d67-4798-bd58-24dc84caec48"




def iniciar_scrapeo(tipo: str, lat: float, lng: float) -> str:
    url_scrape = generar_url_scraping(tipo, lat, lng)
    agregar_a_hoja_scrape(url_scrape)
    print(f"📌 URL generada y enviada al sheet: {url_scrape}")

    # Activar N8N
    webhook_url = N8N_WEBHOOK_URL
    try:
        requests.get(webhook_url)
        print("🚀 N8N llamado exitosamente.")
    except Exception as e:
        print(f"⚠️ Error llamando a N8N: {e}")

    return url_scrape


API_KEY = "91b84c1ed4e5a321b7635f9411914876fab1e93e9883263f8261e5249cec417a"

def obtener_peques_cercanos(lat: float, lng: float, max_km: float = 1.0):
    resultados = leer_hoja_results()
    cercanos = []

    for row in resultados:
        try:
            coords_str = row.get("gps_coordinates", "{}")
            coords = eval(coords_str) if isinstance(coords_str, str) else coords_str
            lat2 = coords.get("latitude")
            lng2 = coords.get("longitude")

            if lat2 is not None and lng2 is not None:
                distancia = calcular_distancia_km(lat, lng, lat2, lng2)
                if distancia <= max_km:
                    popular_times = None
                    url_place = row.get("place_id_search")

                    if url_place:
                        # Agrega la api_key a la URL
                        if "?" in url_place:
                            url_place += f"&api_key={API_KEY}"
                        else:
                            url_place += f"?api_key={API_KEY}"

                        try:
                            resp = requests.get(url_place)
                            if resp.status_code == 200:
                                data = resp.json()
                                popular_times = (
                                    data.get("place_results", {}).get("popular_times")
                                )
                        except Exception as e:
                            print(f"⚠️ Error al obtener popular_times: {e}")

                    row["popular_times"] = popular_times
                    cercanos.append(row)

        except Exception as e:
            print(f"⚠️ Error leyendo coordenadas: {e}")
            continue

    return cercanos


def get_peques_from_sheet():
    peques = fetch_peques_from_google_sheet()
    for p in peques:
        p.score_normalized = calculate_score_normalized(p)
    return peques

def calcular_distancia_km(lat1, lng1, lat2, lng2):
    return ((lat1 - lat2) ** 2 + (lng1 - lng2) ** 2) ** 0.5 * 111


async def scrapear_y_retornar_cercanos_async(lat: float, lng: float, tipo: str = "restaurante"):
    url_scrape = generar_url_scraping(tipo, lat, lng)
    print(f"📌 URL generada: {url_scrape}")

    # Paso 1: Guardar la URL en el Google Sheet
    agregar_a_hoja_scrape(url_scrape)
    print("✅ URL agregada a hoja de scraping")

    # Paso 2: Llamar al Webhook de N8N
    webhook_url = N8N_WEBHOOK_URL
    print("🚀 Webhook de N8N activado")
    try:
        requests.get(webhook_url)
    except Exception as e:
        print(f"⚠️ Error al llamar al webhook de N8N: {e}")

    # Paso 3: Esperar que el N8N scrapee y registre en Results
    print("⏳ Esperando que N8N termine y cargue en Results...")
    max_retries = 60
    for i in range(max_retries):
        rows = leer_hoja_results()
        for row in rows:
            url_result = row.get("URL", "").strip()
            status = row.get("Status", "").lower()
            if url_scrape in url_result and "ok" in status:
                print("✅ Scrapeo confirmado en Results")
                # Filtro adicional: solo los cercanos al punto dado
                try:
                    coords = eval(row.get("gps_coordinates", "{}"))
                    lat2 = coords.get("latitude")
                    lng2 = coords.get("longitude")
                    if lat2 is not None and lng2 is not None:
                        dist = calcular_distancia_km(lat, lng, lat2, lng2)
                        if dist <= 1.0:  # dentro de 1 km
                            print(f"📍 Distancia válida: {dist:.2f} km")
                            return [row]
                except Exception as e:
                    print(f"⚠️ Error leyendo coordenadas de row: {e}")
        time.sleep(2)

    print("❌ No se encontró scrapeo válido en Results después del tiempo de espera")
    return {"error": "No se encontró un resultado cercano registrado por el N8N"}

def get_nearby_peques(lat, lng, max_km=1.0):
    rows = leer_hoja_results()
    cercanos = []
    for row in rows:
        try:
            coords = eval(row.get("gps_coordinates", "{}"))
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


def scrapear_y_retornar_cercanos(lat: float, lng: float, tipo: str = "restaurante"):
    url = generar_url_scraping(tipo, lat, lng)
    agregar_a_hoja_scrape(url)
    requests.get(N8N_WEBHOOK_URL)
    time.sleep(4)  # Espera a que el n8n actualice la hoja
    return get_nearby_peques(lat, lng)

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