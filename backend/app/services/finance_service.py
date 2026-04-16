import httpx
from app.core.config import COINGECKO_BASE_URL, COINGECKO_DEMO_API_KEY

SUPPORTED_ASSETS = {
    "bitcoin",
    "ethereum",
    "solana",
}


def _coingecko_headers() -> dict:
    headers = {}
    if COINGECKO_DEMO_API_KEY:
        headers["x-cg-demo-api-key"] = COINGECKO_DEMO_API_KEY
    return headers


def fetch_current_price(asset_id: str) -> float:
    url = f"{COINGECKO_BASE_URL}/simple/price"
    params = {
        "ids": asset_id,
        "vs_currencies": "usd",
    }

    response = httpx.get(
        url,
        params=params,
        headers=_coingecko_headers(),
        timeout=20.0,
    )
    response.raise_for_status()

    data = response.json()
    return data[asset_id]["usd"]


def fetch_chart(asset_id: str, days: int) -> list[dict]:
    url = f"{COINGECKO_BASE_URL}/coins/{asset_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
    }

    response = httpx.get(
        url,
        params=params,
        headers=_coingecko_headers(),
        timeout=20.0,
    )
    response.raise_for_status()

    data = response.json()
    prices = data.get("prices", [])

    chart_points = []
    for timestamp, price in prices:
        chart_points.append(
            {
                "time": str(int(timestamp)),
                "price": round(price, 2),
            }
        )

    return chart_points