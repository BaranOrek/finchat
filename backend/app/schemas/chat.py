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


class ChartSeries(BaseModel):
    asset_id: str
    label: str
    points: list[ChartPoint]


class ChartData(BaseModel):
    label: str
    points: list[ChartPoint] = []
    series: list[ChartSeries] = []
    is_normalized: bool = False


class ChatResponse(BaseModel):
    reply: str
    chart: Optional[ChartData] = None


class PlannerOutput(BaseModel):
    intent: str
    asset: str | None = None
    related_assets: list[str] = []
    start_date: str | None = None
    end_date: str | None = None
    needs_current_price: bool = False
    needs_chart: bool = False