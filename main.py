from fastapi import FastAPI
import requests
import csv
import json
from io import StringIO

app = FastAPI()

GOOGLE_SHEET_RESULTS_URL = (
    "https://docs.google.com/spreadsheets/d/18S8UejJZ1mOLtsbrryQsa7d99k4wsLCCaKQuwR9eEAA/export?format=csv&gid=25714632"
)

@app.get("/peques/from-sheet")
def get_peques():
    response = requests.get(GOOGLE_SHEET_RESULTS_URL)
    response.raise_for_status()

    content = response.content.decode("utf-8")
    reader = csv.DictReader(StringIO(content))
    results = []

    for row in reader:
        cleaned = {}
        for k, v in row.items():
            if v.startswith('{"') and v.endswith('}'):
                try:
                    parsed = json.loads(v)
                    cleaned[k] = parsed.get("URL", "")
                except:
                    cleaned[k] = ""
            else:
                cleaned[k] = v.strip() if v else ""
        results.append(cleaned)

    return results
