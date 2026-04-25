"""
AI service for FinChat.

This module wraps AI provider calls for:
- Query planning
- Financial response generation
- Casual response generation

External AI errors are converted into controlled application errors.
"""

import json
from datetime import date

import httpx

from app.core.config import AI_BASE_URL, AI_API_KEY, AI_MODEL
from app.core.exceptions import AppException
from app.core.logger import get_logger


logger = get_logger(__name__)

REQUEST_TIMEOUT_SECONDS = 30.0


def _post_chat_completion(messages: list[dict], temperature: float = 0.3) -> str:
    """
    Send a chat completion request to the configured AI provider.

    Args:
        messages (list[dict]): Chat messages in OpenAI-compatible format.
        temperature (float): Sampling temperature.

    Returns:
        str: Assistant message content.

    Raises:
        AppException: If provider configuration, request, or response is invalid.
    """
    if not AI_API_KEY:
        logger.error("AI_API_KEY is missing")
        raise AppException(
            message="AI service is not configured.",
            status_code=500,
            error_code="AI_SERVICE_NOT_CONFIGURED",
        )

    endpoint = AI_BASE_URL.rstrip("/") + "/chat/completions"

    try:
        logger.info(
            "Calling AI provider: model=%s messages=%s", AI_MODEL, len(messages)
        )

        response = httpx.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {AI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": AI_MODEL,
                "messages": messages,
                "temperature": temperature,
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        if not content or not content.strip():
            raise KeyError("Empty AI response content")

        return content

    except httpx.TimeoutException as exc:
        logger.warning("AI provider request timed out: %s", str(exc))
        raise AppException(
            message="AI provider timed out. Please try again.",
            status_code=504,
            error_code="AI_PROVIDER_TIMEOUT",
        ) from exc

    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code
        logger.warning("AI provider HTTP error: status=%s", status_code)

        if status_code == 401:
            raise AppException(
                message="AI provider authentication failed.",
                status_code=502,
                error_code="AI_PROVIDER_AUTH_FAILED",
            ) from exc

        if status_code == 429:
            raise AppException(
                message="AI provider rate limit reached. Please try again shortly.",
                status_code=429,
                error_code="AI_PROVIDER_RATE_LIMIT",
            ) from exc

        raise AppException(
            message="AI provider returned an error.",
            status_code=502,
            error_code="AI_PROVIDER_ERROR",
        ) from exc

    except httpx.HTTPError as exc:
        logger.warning("AI provider network error: %s", str(exc))
        raise AppException(
            message="Unable to reach AI provider.",
            status_code=502,
            error_code="AI_PROVIDER_NETWORK_ERROR",
        ) from exc

    except (ValueError, KeyError, IndexError, TypeError) as exc:
        logger.warning("Invalid AI provider response: %s", str(exc))
        raise AppException(
            message="AI provider returned an invalid response.",
            status_code=502,
            error_code="AI_PROVIDER_INVALID_RESPONSE",
        ) from exc


def plan_user_query(conversation_messages: list[dict]) -> dict:
    """
    Parse the latest user request into a structured planner output.

    Args:
        conversation_messages (list[dict]): Recent conversation history.

    Returns:
        dict: Planner JSON output.
    """
    today_str = date.today().isoformat()

    planner_prompt = f"""
    You are a finance query parser for a chat application.

    Today's date is {today_str}.

    You will be given the recent conversation history.
    Your task is to analyze the conversation, paying special attention to the latest user message.

    Return only valid JSON.

    Output format:
    {{
    "intent": "finance_query" | "casual" | "unsupported",
    "asset": "string | null",
    "related_assets": ["string"],
    "start_date": "YYYY-MM-DD" | null,
    "end_date": "YYYY-MM-DD" | null,
    "needs_current_price": boolean,
    "needs_chart": boolean
    }}

    Rules:
    - Use the latest user message as the main request.
    - If the latest user message omits the asset but clearly refers to the asset discussed earlier in the conversation, infer the asset from recent context.
    - If the user is greeting, making small talk, or asking a non-finance conversational question, use "casual".
    - If the user asks about crypto assets and wants current price, trend, movement, or chart-related information, use "finance_query".
    - If the request is outside supported capabilities, use "unsupported".
    - Extract the crypto asset the user refers to as a lowercase string when possible.
    - Map common shorthand like BTC -> bitcoin, ETH -> ethereum, SOL -> solana, DOGE -> dogecoin when possible.
    - If the user refers to a crypto asset but the exact provider-specific ID is unclear, still return the most likely lowercase asset name.
    - Resolve natural language date references into explicit dates in YYYY-MM-DD format.
    - If the user asks for a month like February, resolve it into start_date and end_date for that month.
    - If the user asks for a relative range like last 200 days, compute explicit start_date and end_date.
    - If no timeframe is provided and a trend/chart is requested, default to the last 7 days.
    - If only current price is requested, start_date and end_date may be null.
    - Return JSON only. No markdown. No explanation.
    - If the user mentions multiple crypto assets, put the first/main asset in "asset" and all additional assets in "related_assets".
    - Do not include the main asset again inside "related_assets".
    - If there are no additional assets, return "related_assets": [].
    - If the user asks to compare multiple assets or performance, set needs_chart=true.
    - If the user asks to compare multiple crypto assets, compare performance, asks "which performed better", or asks for relative movement between assets, set needs_chart=true.
    - For multi-asset comparison requests, include all mentioned additional assets in "related_assets".
    - If you extract a start_date or end_date, you must set needs_chart=true because the request involves historical or timeframe-based data.
    - When needs_chart=true, set needs_current_price=false unless the user explicitly asks for both current price and historical information.
    """.strip()

    messages = [{"role": "system", "content": planner_prompt}]
    messages.extend(conversation_messages[-6:])

    content = _post_chat_completion(messages=messages, temperature=0)

    try:
        planner_output = json.loads(content)
        logger.info("Planner JSON parsed successfully")
        return planner_output

    except json.JSONDecodeError as exc:
        logger.warning("Planner returned invalid JSON: %s", content)
        raise AppException(
            message="Could not understand the request. Please try rephrasing it.",
            status_code=400,
            error_code="PLANNER_INVALID_JSON",
        ) from exc


def generate_financial_reply(
    conversation_messages: list[dict],
    market_context: str = "",
) -> str:
    """
    Generate a financial reply using conversation history and market context.

    Args:
        conversation_messages (list[dict]): Recent conversation history.
        market_context (str): Trusted market data context.

    Returns:
        str: AI-generated financial reply.
    """
    # system_prompt = (
    #     "You are FinChat, a helpful AI financial assistant. "
    #     "Answer clearly, briefly, and confidently using the provided market data. "
    #     "If start price, end price, absolute change, or percentage change are provided, explicitly use them in your answer. "
    #     "When chart-related data is available, summarize the trend direction in simple terms such as increased, decreased, or remained relatively stable. "
    #     "If chart values are normalized to 100, explain that the chart compares relative performance rather than raw price levels. "
    #     "If the analyzed timeframe was adjusted due to system limits, mention that briefly. "
    #     "Do not say that data is unavailable if market data context is provided. "
    #     "Do not make up price data."
    #     "If an asset limit note is provided, clearly explain that only the first supported assets were analyzed instead of saying data is unavailable. "
    # )
    system_prompt = (
        "You are FinChat, a helpful AI financial assistant. "
        "Answer clearly, briefly, and confidently using the provided market data. "
        "Never mention your own knowledge cutoff or training data limits. "
        "If start price, end price, absolute change, or percentage change are provided, explicitly use them in your answer. "
        "When chart-related data is available, summarize the trend direction in simple terms such as increased, decreased, or remained relatively stable. "
        "If chart values are normalized to 100, explain that the chart compares relative performance rather than raw price levels. "
        "If an asset limit note is provided, clearly explain that only the first supported assets were analyzed instead of saying data is unavailable. "
        "If the analyzed timeframe was adjusted due to system limits, clearly say that this app currently analyzes up to the most recent 365 days. "
        "If the requested timeframe was adjusted, only explain the actual system limit provided in the market context. "
        "Do not say that data is unavailable if market data context is provided. "
        "Do not make up price data."
    )

    api_messages = [{"role": "system", "content": system_prompt}]

    if market_context:
        api_messages.append(
            {
                "role": "system",
                "content": f"Market data context:\n{market_context}",
            }
        )

    api_messages.extend(conversation_messages)

    return _post_chat_completion(messages=api_messages, temperature=0.3)


def generate_casual_reply(conversation_messages: list[dict]) -> str:
    """
    Generate a short casual reply for non-financial conversational messages.

    Args:
        conversation_messages (list[dict]): Recent conversation history.

    Returns:
        str: AI-generated casual reply.
    """
    system_prompt = (
        "You are FinChat, a friendly assistant in a finance chat application. "
        "You can respond naturally to greetings and casual small talk. "
        "Keep the response short and friendly."
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_messages)

    return _post_chat_completion(messages=messages, temperature=0.4)
