# from typing import Optional
# import httpx
# from app.core.config import COINGECKO_BASE_URL

# SUPPORTED_ASSETS = {
#     "bitcoin": "bitcoin",
#     "btc": "bitcoin",
#     "ethereum": "ethereum",
#     "eth": "ethereum",
#     "solana": "solana",
#     "sol": "solana",
# }


# def detect_asset(user_text: str) -> Optional[str]:
#     text = user_text.lower()

#     for keyword, asset_id in SUPPORTED_ASSETS.items():
#         if keyword in text:
#             return asset_id

#     return None


# def fetch_current_price(asset_id: str) -> float:
#     url = f"{COINGECKO_BASE_URL}/simple/price"
#     params = {
#         "ids": asset_id,
#         "vs_currencies": "usd",
#     }

#     response = httpx.get(url, params=params, timeout=20.0)
#     response.raise_for_status()

#     data = response.json()
#     return data[asset_id]["usd"]


# def fetch_7d_chart(asset_id: str) -> list[dict]:
#     url = f"{COINGECKO_BASE_URL}/coins/{asset_id}/market_chart"
#     params = {
#         "vs_currency": "usd",
#         "days": 7,
#     }

#     response = httpx.get(url, params=params, timeout=20.0)
#     response.raise_for_status()

#     data = response.json()
#     prices = data.get("prices", [])

#     chart_points = []
#     for timestamp, price in prices:
#         chart_points.append(
#             {
#                 "time": str(int(timestamp)),
#                 "price": round(price, 2),
#             }
#         )

#     return chart_points

import httpx
from app.core.config import COINGECKO_BASE_URL

SUPPORTED_ASSETS = {
    "bitcoin",
    "ethereum",
    "solana",
}


def fetch_current_price(asset_id: str) -> float:
    url = f"{COINGECKO_BASE_URL}/simple/price"
    params = {
        "ids": asset_id,
        "vs_currencies": "usd",
    }

    response = httpx.get(url, params=params, timeout=20.0)
    response.raise_for_status()

    data = response.json()
    return data[asset_id]["usd"]


def fetch_chart(asset_id: str, days: int) -> list[dict]:
    url = f"{COINGECKO_BASE_URL}/coins/{asset_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
    }

    response = httpx.get(url, params=params, timeout=20.0)
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