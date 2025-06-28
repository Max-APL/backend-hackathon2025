from math import log10

def calculate_score_normalized(peque):
    try:
        rating = float(peque.rating) if peque.rating else 0
    except:
        rating = 0

    try:
        reviews = int(peque.reviews.replace(',', '')) if peque.reviews else 0
    except:
        reviews = 0

    rating_score = rating / 5.0
    reviews_score = min(log10(reviews + 1) / 3, 1.0)

    address_score = 1.0 if peque.address else 0.0
    thumbnail_score = 1.0 if peque.thumbnail else 0.0
    hours_score = 1.0 if peque.operating_hours and peque.operating_hours.startswith("{") else 0.0

    score = (
        0.4 * rating_score +
        0.3 * reviews_score +
        0.1 * address_score +
        0.1 * thumbnail_score +
        0.1 * hours_score
    )

    return round(score, 4)
