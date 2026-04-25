"""
Finance service for resolving crypto assets and fetching market data.

This module wraps CoinGecko API calls and converts external API failures
into controlled application errors.
"""

import httpx

from app.core.config import COINGECKO_BASE_URL, COINGECKO_DEMO_API_KEY
from app.core.exceptions import AppException
from app.core.logger import get_logger


logger = get_logger(__name__)

REQUEST_TIMEOUT_SECONDS = 10.0


ASSET_ALIASES = {
    "btc": "bitcoin",
    "bitcoin": "bitcoin",
    "eth": "ethereum",
    "ethereum": "ethereum",
    "sol": "solana",
    "solana": "solana",
    "doge": "dogecoin",
    "dogecoin": "dogecoin",
    "bnb": "binancecoin",
    "binance coin": "binancecoin",
    "binancecoin": "binancecoin",
    "avax": "avalanche-2",
    "avalanche": "avalanche-2",
    "xrp": "ripple",
    "ripple": "ripple",
    "ada": "cardano",
    "cardano": "cardano",
}


def _coingecko_headers() -> dict:
    """Return CoinGecko request headers."""
    headers = {}

    if COINGECKO_DEMO_API_KEY:
        headers["x-cg-demo-api-key"] = COINGECKO_DEMO_API_KEY

    return headers


def _get_json(url: str, params: dict) -> dict:
    """
    Send a GET request to CoinGecko and return parsed JSON.

    Args:
        url (str): CoinGecko endpoint URL.
        params (dict): Query parameters.

    Returns:
        dict: Parsed JSON response.

    Raises:
        AppException: If CoinGecko request fails or returns invalid JSON.
    """
    try:
        logger.info("Calling CoinGecko endpoint: %s params=%s", url, params)

        response = httpx.get(
            url,
            params=params,
            headers=_coingecko_headers(),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()

        return response.json()

    except httpx.TimeoutException as exc:
        logger.warning("CoinGecko request timed out: %s", str(exc))
        raise AppException(
            message="Market data provider timed out. Please try again.",
            status_code=504,
            error_code="MARKET_DATA_TIMEOUT",
        ) from exc

    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code
        logger.warning("CoinGecko HTTP error: status=%s", status_code)

        if status_code == 429:
            raise AppException(
                message="Market data provider rate limit reached. Please try again shortly.",
                status_code=429,
                error_code="MARKET_DATA_RATE_LIMIT",
            ) from exc

        raise AppException(
            message="Market data provider returned an error.",
            status_code=502,
            error_code="MARKET_DATA_PROVIDER_ERROR",
        ) from exc

    except httpx.HTTPError as exc:
        logger.warning("CoinGecko network error: %s", str(exc))
        raise AppException(
            message="Unable to reach market data provider.",
            status_code=502,
            error_code="MARKET_DATA_NETWORK_ERROR",
        ) from exc

    except ValueError as exc:
        logger.warning("Invalid JSON from CoinGecko: %s", str(exc))
        raise AppException(
            message="Market data provider returned invalid data.",
            status_code=502,
            error_code="MARKET_DATA_INVALID_RESPONSE",
        ) from exc


def resolve_asset_id(asset_query: str | None) -> str | None:
    """
    Resolve a user-provided crypto asset query into a CoinGecko asset ID.

    Args:
        asset_query (str | None): User-provided asset name or symbol.

    Returns:
        str | None: CoinGecko asset ID, or None if no confident match exists.
    """
    if not asset_query:
        return None

    normalized = asset_query.strip().lower()

    if not normalized:
        return None

    if normalized in ASSET_ALIASES:
        logger.info("Resolved asset using alias: %s -> %s", normalized, ASSET_ALIASES[normalized])
        return ASSET_ALIASES[normalized]

    url = f"{COINGECKO_BASE_URL}/search"
    params = {"query": normalized}

    data = _get_json(url, params)
    coins = data.get("coins", [])

    if not coins:
        logger.info("No CoinGecko asset found for query: %s", normalized)
        return None

    top_match = coins[0]
    resolved_id = top_match.get("id")

    logger.info("Resolved asset using CoinGecko search: %s -> %s", normalized, resolved_id)

    return resolved_id


def fetch_current_price(asset_id: str) -> float:
    """
    Fetch the current USD price for a crypto asset.

    Args:
        asset_id (str): CoinGecko asset ID.

    Returns:
        float: Current USD price.

    Raises:
        AppException: If price data is missing or invalid.
    """
    url = f"{COINGECKO_BASE_URL}/simple/price"
    params = {
        "ids": asset_id,
        "vs_currencies": "usd",
    }

    data = _get_json(url, params)

    try:
        price = data[asset_id]["usd"]
    except KeyError as exc:
        logger.warning("Price missing from CoinGecko response for asset_id=%s", asset_id)
        raise AppException(
            message="Current price is not available for this asset.",
            status_code=404,
            error_code="PRICE_NOT_AVAILABLE",
        ) from exc

    logger.info("Fetched current price: asset_id=%s price=%s", asset_id, price)

    return float(price)


def fetch_chart(asset_id: str, days: int) -> list[dict]:
    """
    Fetch historical chart data for a crypto asset.

    Args:
        asset_id (str): CoinGecko asset ID.
        days (int): Number of days to fetch.

    Returns:
        list[dict]: Chart points with timestamp and rounded price.

    Raises:
        AppException: If chart data is missing or invalid.
    """
    url = f"{COINGECKO_BASE_URL}/coins/{asset_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
    }

    data = _get_json(url, params)
    prices = data.get("prices", [])

    if not prices:
        logger.warning("No chart data returned for asset_id=%s days=%s", asset_id, days)
        raise AppException(
            message="Chart data is not available for this asset or timeframe.",
            status_code=404,
            error_code="CHART_DATA_NOT_AVAILABLE",
        )

    chart_points = [
        {
            "time": str(int(timestamp)),
            "price": round(price, 2),
        }
        for timestamp, price in prices
    ]

    logger.info(
        "Fetched chart data: asset_id=%s days=%s points=%s",
        asset_id,
        days,
        len(chart_points),
    )

    return chart_points