import csv
import requests
from io import StringIO
from app.core.config import settings
from app.models.peques_model import PequeModel

def fetch_peques_from_google_sheet():
    response = requests.get(settings.google_sheet_url)
    response.raise_for_status()
    decoded_content = response.content.decode("utf-8")
    reader = csv.DictReader(StringIO(decoded_content))

    results = []
    for row in reader:
        cleaned = {k.strip(): v.strip() for k, v in row.items()}
        results.append(PequeModel(**cleaned))
    return results
