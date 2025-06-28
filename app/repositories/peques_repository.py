# app/repositories/peques_repository.py

import csv
import requests
from io import StringIO
from typing import List, Dict

def fetch_peques_from_google_sheet(sheet_csv_url: str) -> List[Dict[str, str]]:
    response = requests.get(sheet_csv_url)
    response.raise_for_status()
    csv_text = response.text
    csv_reader = csv.DictReader(StringIO(csv_text))
    return list(csv_reader)
