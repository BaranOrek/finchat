"""
Utilities for normalized chart comparisons.

A normalized chart indexes each asset to 100 at the first data point.
This makes assets with very different price levels comparable on the same chart.
"""


def normalize_chart_series(chart_points: list[dict]) -> list[dict]:
    """
    Normalize price points so the first point starts at 100.

    Args:
        chart_points: List of chart points with "time" and "price" keys.

    Returns:
        Normalized chart points with the same time values.
    """
    if not chart_points:
        return []

    base_price = chart_points[0]["price"]

    if base_price == 0:
        return chart_points

    normalized = []

    for point in chart_points:
        normalized_price = (point["price"] / base_price) * 100

        normalized.append(
            {
                "time": point["time"],
                "price": round(normalized_price, 2),
            }
        )

    return normalized