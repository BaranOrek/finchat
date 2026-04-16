from pydantic import BaseModel
from typing import List, Optional, Literal


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


class ChartPoint(BaseModel):
    time: str
    price: float


class ChartData(BaseModel):
    label: str
    points: List[ChartPoint]


class ChatResponse(BaseModel):
    reply: str
    chart: Optional[ChartData] = None


class PlannerOutput(BaseModel):
    intent: Literal["finance_query", "casual", "unsupported"]
    asset: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    needs_current_price: bool
    needs_chart: bool