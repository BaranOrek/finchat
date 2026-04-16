from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChartData,
    ChartPoint,
    PlannerOutput,
)
from app.services.finance_service import (
    SUPPORTED_ASSETS,
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

router = APIRouter(prefix="/chat", tags=["chat"])


def fallback_reply() -> str:
    return (
        "I can help with crypto questions like current price, recent movement, "
        "monthly or custom timeframe trends for supported assets such as BTC, ETH, and SOL."
    )


@router.post("/")
def chat_endpoint(payload: ChatRequest):
    try:
        conversation_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in payload.messages
        ]

        latest_user_message = payload.messages[-1].content if payload.messages else ""

        if not latest_user_message.strip():
            return ChatResponse(reply=fallback_reply(), chart=None)

        try:
            planner_raw = plan_user_query(conversation_messages)
            planner = PlannerOutput(**planner_raw)
        except (ValidationError, ValueError, KeyError):
            return ChatResponse(reply=fallback_reply(), chart=None)

        if planner.intent == "casual":
            reply = generate_casual_reply(conversation_messages)
            return ChatResponse(reply=reply, chart=None)

        if planner.intent == "unsupported":
            return ChatResponse(reply=fallback_reply(), chart=None)

        if planner.intent != "finance_query":
            return ChatResponse(reply=fallback_reply(), chart=None)

        if not planner.asset or planner.asset not in SUPPORTED_ASSETS:
            return ChatResponse(reply=fallback_reply(), chart=None)

        current_price = None
        chart = None
        market_context_parts = [
            f"Asset: {planner.asset}",
        ]

        normalized_start_date, normalized_end_date, timeframe_status = normalize_timeframe(
            planner.start_date,
            planner.end_date,
        )

        if planner.needs_current_price:
            current_price = fetch_current_price(planner.asset)
            market_context_parts.append(f"Current price: ${current_price} USD")

        if planner.needs_chart:
            if not normalized_start_date or not normalized_end_date:
                return ChatResponse(reply=fallback_reply(), chart=None)

            days = calculate_days_for_range(normalized_start_date, normalized_end_date)

            chart_points_raw = fetch_chart(planner.asset, days)

            chart_summary = build_chart_summary(chart_points_raw)

            market_context_parts.append(
                f"Analyzed range: {normalized_start_date.isoformat()} to {normalized_end_date.isoformat()}"
            )
            market_context_parts.append(
                f"Approximate chart range in days used for market data fetch: {days}"
            )

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

            if timeframe_status == "clamped_to_today":
                market_context_parts.append(
                    "The requested end date was in the future, so it was adjusted to today."
                )

            if timeframe_status == "clamped_to_365_days":
                market_context_parts.append(
                    "The requested range exceeded the last 365 days, so the analysis was limited to the most recent 365 days."
                )

            chart = ChartData(
                label=f"{planner.asset.upper()} {normalized_start_date.isoformat()} to {normalized_end_date.isoformat()}",
                points=[
                    ChartPoint(time=point["time"], price=point["price"])
                    for point in chart_points_raw
                ],
            )

        if not planner.needs_current_price and not planner.needs_chart:
            current_price = fetch_current_price(planner.asset)
            market_context_parts.append(f"Current price: ${current_price} USD")

        market_context = "\n".join(market_context_parts)

        reply = generate_financial_reply(
            conversation_messages=conversation_messages,
            market_context=market_context,
        )

        return ChatResponse(
            reply=reply,
            chart=chart,
        )

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/planner-test")
def planner_test(payload: ChatRequest):
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