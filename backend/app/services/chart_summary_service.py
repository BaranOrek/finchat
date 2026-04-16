from typing import Optional


def build_chart_summary(chart_points: list[dict]) -> Optional[dict]:
    if not chart_points:
        return None

    prices = [point["price"] for point in chart_points if "price" in point]

    if not prices:
        return None

    start_price = prices[0]
    end_price = prices[-1]
    absolute_change = round(end_price - start_price, 2)

    percentage_change = 0.0
    if start_price != 0:
        percentage_change = round((absolute_change / start_price) * 100, 2)

    return {
        "start_price": round(start_price, 2),
        "end_price": round(end_price, 2),
        "absolute_change": absolute_change,
        "percentage_change": percentage_change,
        "min_price": round(min(prices), 2),
        "max_price": round(max(prices), 2),
    }