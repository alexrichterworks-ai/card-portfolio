import requests
from config import Config


def _headers():
    return {"X-Api-Key": Config.TCG_API_KEY}


def search_card(name: str, game: str = "pokemon") -> list:
    try:
        res = requests.get(
            f"{Config.TCG_BASE_URL}/search",
            headers=_headers(),
            params={"q": name, "game": game},
            timeout=10,
        )
        res.raise_for_status()
        return res.json().get("data", [])
    except Exception:
        return []


def get_card_price(card_id: str):
    try:
        res = requests.get(
            f"{Config.TCG_BASE_URL}/cards/{card_id}",
            headers=_headers(),
            timeout=10,
        )
        res.raise_for_status()
        data = res.json().get("data", {})
        raw = data.get("market_price") or data.get("low_price") or data.get("lowest_price_with_shipping")
        return float(raw) if raw else None
    except Exception:
        return None
