import json
import httpx
from datetime import date
from app.core.config import AI_BASE_URL, AI_API_KEY, AI_MODEL


def _post_chat_completion(messages: list[dict], temperature: float = 0.3) -> str:
    endpoint = AI_BASE_URL.rstrip("/") + "/chat/completions"

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
        timeout=40.0,
    )
    response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"]

def plan_user_query(conversation_messages: list[dict]) -> dict:
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
  "asset": "bitcoin" | "ethereum" | "solana" | null,
  "start_date": "YYYY-MM-DD" | null,
  "end_date": "YYYY-MM-DD" | null,
  "needs_current_price": boolean,
  "needs_chart": boolean
}}

Rules:
- Use the latest user message as the main request.
- If the latest user message omits the asset but clearly refers to the asset discussed earlier in the conversation, infer the asset from recent context.
- If the user is greeting, making small talk, or asking a non-finance conversational question, use "casual".
- If the user asks about supported crypto assets and wants current price, trend, movement, or chart-related information, use "finance_query".
- If the request is outside supported capabilities, use "unsupported".
- Supported assets are bitcoin, ethereum, and solana.
- Map BTC to bitcoin, ETH to ethereum, SOL to solana.
- Resolve natural language date references into explicit dates in YYYY-MM-DD format.
- If the user asks for a month like February, resolve it into start_date and end_date for that month.
- If the user asks for a relative range like last 200 days, compute explicit start_date and end_date.
- If no timeframe is provided and a trend/chart is requested, default to the last 7 days.
- If only current price is requested, start_date and end_date may be null.
- Return JSON only. No markdown. No explanation.
""".strip()

    messages = [{"role": "system", "content": planner_prompt}]
    messages.extend(conversation_messages[-6:])

    content = _post_chat_completion(messages=messages, temperature=0)
    return json.loads(content)


def generate_financial_reply(
    conversation_messages: list[dict],
    market_context: str = "",
) -> str:
    system_prompt = (
        "You are FinChat, a helpful AI financial assistant. "
        "Answer clearly, briefly, and confidently using the provided market data. "
        "If start price, end price, absolute change, or percentage change are provided, explicitly use them in your answer. "
        "When chart-related data is available, summarize the trend direction in simple terms such as increased, decreased, or remained relatively stable. "
        "If the analyzed timeframe was adjusted due to system limits, mention that briefly. "
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
    system_prompt = (
        "You are FinChat, a friendly assistant in a finance chat application. "
        "You can respond naturally to greetings and casual small talk. "
        "Keep the response short and friendly."
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_messages)

    return _post_chat_completion(messages=messages, temperature=0.4)