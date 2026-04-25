"""
Chat API routes for FinChat.

This module handles user chat interactions, including:
- Query planning via AI
- Asset resolution
- Market data fetching
- Response generation

It includes structured logging and robust error handling to simulate
production-ready backend behavior.
"""

from fastapi import APIRouter
from pydantic import ValidationError

from app.core.logger import get_logger
from app.core.exceptions import AppException

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChartData,
    ChartPoint,
    ChartSeries,
    PlannerOutput,
)

from app.services.finance_service import (
    resolve_asset_id,
    fetch_current_price,
    fetch_chart,
)

from app.services.ai_service import (
    plan_user_query,
    generate_financial_reply,
    generate_casual_reply,
)

from app.services.timeframe_service import (
    normalize_timeframe,
    calculate_days_for_range,
)

from app.services.chart_summary_service import build_chart_summary

from app.services.normalized_chart_service import normalize_chart_series


logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

MAX_ASSET_COUNT = 5


def fallback_reply() -> str:
    """Return a generic fallback reply for unsupported or unclear queries."""
    return (
        "I can help with cryptocurrency questions like current prices, "
        "recent trends, and comparing how different assets perform based on recent market data (last 12 months). "
        "Try asking about a specific crypto such as Bitcoin or Ethereum."
    )


@router.post("/")
def chat_endpoint(payload: ChatRequest):
    """
    Main chat endpoint.

    Processes user messages, determines intent, fetches market data if needed,
    and generates an AI-powered response.

    Args:
        payload (ChatRequest): Incoming chat request containing messages.

    Returns:
        ChatResponse: AI-generated reply and optional chart data.

    Raises:
        AppException: For controlled application-level errors.
    """
    try:
        logger.info("Chat request received")

        conversation_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in payload.messages
        ]

        latest_user_message = payload.messages[-1].content if payload.messages else ""

        if not latest_user_message.strip():
            logger.warning("Empty user message received")
            return ChatResponse(reply=fallback_reply(), chart=None)

        # --- AI PLANNER ---
        try:
            planner_raw = plan_user_query(conversation_messages)
            planner = PlannerOutput(**planner_raw)
            logger.info(f"Planner output: {planner.dict()}")
        except (ValidationError, ValueError, KeyError) as err:
            logger.warning(f"Planner parsing failed: {str(err)}")
            return ChatResponse(reply=fallback_reply(), chart=None)

        # --- INTENT HANDLING ---
        if planner.intent == "casual":
            logger.info("Intent: casual")
            reply = generate_casual_reply(conversation_messages)
            return ChatResponse(reply=reply, chart=None)

        if planner.intent != "finance_query":
            logger.info(f"Unsupported intent: {planner.intent}")
            return ChatResponse(reply=fallback_reply(), chart=None)

        # --- ASSET RESOLUTION ---
        resolved_asset_id = resolve_asset_id(planner.asset)

        if not resolved_asset_id:
            logger.warning(f"Asset not resolved: {planner.asset}")
            return ChatResponse(
                reply="I couldn't identify the crypto asset. Try Bitcoin, Ethereum, etc.",
                chart=None,
            )

        logger.info(f"Resolved asset: {resolved_asset_id}")

        related_resolved_asset_ids = []

        for related_asset in planner.related_assets[: MAX_ASSET_COUNT - 1]:
            related_resolved_asset_id = resolve_asset_id(related_asset)

            if (
                related_resolved_asset_id
                and related_resolved_asset_id != resolved_asset_id
                and related_resolved_asset_id not in related_resolved_asset_ids
            ):
                related_resolved_asset_ids.append(related_resolved_asset_id)

        logger.info("Resolved related assets: %s", related_resolved_asset_ids)
        asset_limit_reached = len(planner.related_assets) > MAX_ASSET_COUNT - 1
        chart = None

        market_context_parts = [
            f"Resolved asset ID: {resolved_asset_id}",
        ]

        if asset_limit_reached:
            market_context_parts.append(
                f"The user requested more than {MAX_ASSET_COUNT} assets. "
                f"For reliability and performance, only the first {MAX_ASSET_COUNT} resolved assets were analyzed. "
                "Do not say prices are unavailable for the remaining assets; instead, briefly explain that they were skipped because of the asset limit."
            )

        # --- TIMEFRAME ---
        normalized_start_date, normalized_end_date, timeframe_status = normalize_timeframe(
            planner.start_date,
            planner.end_date,
        )

        # --- CURRENT PRICE ---
        if planner.needs_current_price:
            try:
                asset_ids_for_price = [resolved_asset_id, *related_resolved_asset_ids]

                for asset_id in asset_ids_for_price:
                    price = fetch_current_price(asset_id)
                    logger.info("Fetched current price: %s=%s", asset_id, price)
                    market_context_parts.append(
                        f"Current price for {asset_id}: ${price} USD"
                    )

            except Exception as err:
                logger.error("Price fetch failed: %s", str(err))
                raise AppException("Failed to fetch current price") from err

        if planner.needs_chart:
            if not normalized_start_date or not normalized_end_date:
                logger.warning("Invalid timeframe detected")
                return ChatResponse(reply=fallback_reply(), chart=None)

            days = calculate_days_for_range(normalized_start_date, normalized_end_date)
            asset_ids_for_chart = [resolved_asset_id, *related_resolved_asset_ids]

            try:
                if len(asset_ids_for_chart) > 1:
                    chart_series = []

                    for asset_id in asset_ids_for_chart:
                        raw_points = fetch_chart(asset_id, days)
                        normalized_points = normalize_chart_series(raw_points)

                        chart_series.append(
                            ChartSeries(
                                asset_id=asset_id,
                                label=asset_id.upper(),
                                points=[
                                    ChartPoint(time=point["time"], price=point["price"])
                                    for point in normalized_points
                                ],
                            )
                        )

                        summary = build_chart_summary(raw_points)

                        if summary:
                            market_context_parts.append(
                                f"{asset_id} performance over analyzed range: "
                                f"{summary['percentage_change']}%"
                            )

                    chart = ChartData(
                        label=(
                            f"Normalized comparison "
                            f"{normalized_start_date.isoformat()} to {normalized_end_date.isoformat()}"
                        ),
                        points=[],
                        series=chart_series,
                        is_normalized=True,
                    )

                    market_context_parts.append(
                        "Chart values are normalized to 100 at the start of the selected timeframe, "
                        "so the comparison shows relative performance instead of raw prices."
                    )

                else:
                    chart_points_raw = fetch_chart(resolved_asset_id, days)
                    logger.info("Fetched chart data: %s points", len(chart_points_raw))

                    chart_summary = build_chart_summary(chart_points_raw)

                    if chart_summary:
                        market_context_parts.append(
                            f"Start price over analyzed range: ${chart_summary['start_price']} USD"
                        )
                        market_context_parts.append(
                            f"End price over analyzed range: ${chart_summary['end_price']} USD"
                        )
                        market_context_parts.append(
                            f"Absolute change over analyzed range: ${chart_summary['absolute_change']} USD"
                        )
                        market_context_parts.append(
                            f"Percentage change over analyzed range: {chart_summary['percentage_change']}%"
                        )
                        market_context_parts.append(
                            f"Lowest observed price in returned series: ${chart_summary['min_price']} USD"
                        )
                        market_context_parts.append(
                            f"Highest observed price in returned series: ${chart_summary['max_price']} USD"
                        )

                    chart = ChartData(
                        label=(
                            f"{resolved_asset_id.upper()} "
                            f"{normalized_start_date.isoformat()} to {normalized_end_date.isoformat()}"
                        ),
                        points=[
                            ChartPoint(time=point["time"], price=point["price"])
                            for point in chart_points_raw
                        ],
                    )

            except Exception as err:
                logger.error("Chart fetch failed: %s", str(err))
                raise AppException("Failed to fetch chart data") from err

            market_context_parts.append(
                f"Analyzed range: {normalized_start_date.isoformat()} to {normalized_end_date.isoformat()}"
            )
            market_context_parts.append(
                f"Approximate chart range in days used for market data fetch: {days}"
            )

            if timeframe_status == "clamped_to_today":
                market_context_parts.append(
                    "The requested end date was in the future, so it was adjusted to today."
                )

            if timeframe_status == "clamped_to_365_days":
                market_context_parts.append(
                    "The requested range exceeded the last 365 days, so the analysis was limited to the most recent 365 days."
                )

        # --- FALLBACK PRICE ---
        if not planner.needs_current_price and not planner.needs_chart:
            try:
                asset_ids_for_price = [resolved_asset_id, *related_resolved_asset_ids]

                for asset_id in asset_ids_for_price:
                    price = fetch_current_price(asset_id)
                    market_context_parts.append(
                        f"Current price for {asset_id}: ${price} USD"
                    )

            except Exception as err:
                logger.error("Fallback price fetch failed: %s", str(err))

        market_context = "\n".join(market_context_parts)

        # --- FINAL RESPONSE ---
        try:
            reply = generate_financial_reply(
                conversation_messages=conversation_messages,
                market_context=market_context,
            )
        except Exception as err:
            logger.error(f"AI reply generation failed: {str(err)}")
            raise AppException("Failed to generate response")

        return ChatResponse(reply=reply, chart=chart)

    except AppException as exc:
        logger.warning(f"AppException: {exc.message}")
        raise exc

    except Exception as exc:
        logger.exception(f"Unexpected error: {str(exc)}")
        raise AppException("Unexpected server error occurred")


@router.post("/planner-test")
def planner_test(payload: ChatRequest):
    """
    Debug endpoint for testing planner output.

    Returns raw planner output for a given user message.
    """
    conversation_messages = [
        {"role": msg.role, "content": msg.content}
        for msg in payload.messages
    ]

    latest_user_message = payload.messages[-1].content if payload.messages else ""

    planner_raw = plan_user_query(conversation_messages)

    return {
        "latest_user_message": latest_user_message,
        "planner_output": planner_raw,
    }