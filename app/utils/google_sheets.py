import requests
import csv
from io import StringIO
from app.core.config import settings
from google.oauth2.service_account import Credentials
import gspread

SERVICE_ACCOUNT_FILE = "./hackaton-a44c8-f3d9ad76a54d.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
client = gspread.authorize(credentials)

spreadsheet = client.open_by_key(settings.GOOGLE_SHEET_ID)

def leer_hoja_results():
    response = requests.get(settings.google_sheet_url)
    data = list(csv.DictReader(StringIO(response.text)))
    return data

def generar_url_scraping(tipo: str, lat: float, lng: float) -> str:
    """Genera la URL para scraping con tipo y coordenadas"""
    return f"https://www.google.com/maps/search/{tipo}/@{lat},{lng},14z/data=!4m2!2m1!6e6?entry=ttu"


def agregar_a_hoja_scrape(url: str):
    """Agrega una fila a la hoja 'Add your search url here' (scrape sheet)"""
    hoja = spreadsheet.worksheet("Add your search url here")
    hoja.append_row([url, ""])  # deja 'status' vacío




