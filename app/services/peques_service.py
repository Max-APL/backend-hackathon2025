from app.repositories.peques_repository import fetch_peques_from_google_sheet
from app.utils.score_utils import calculate_score_normalized

def get_peques_from_sheet():
    peques = fetch_peques_from_google_sheet()
    for p in peques:
        p.score_normalized = calculate_score_normalized(p)
    return peques
