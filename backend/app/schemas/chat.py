# # from pydantic import BaseModel
# # from typing import List, Optional


# # class Message(BaseModel):
# #     role: str
# #     content: str


# # class ChatRequest(BaseModel):
# #     messages: List[Message]


# # class ChartPoint(BaseModel):
# #     time: str
# #     price: float


# # class ChartData(BaseModel):
# #     label: str
# #     points: List[ChartPoint]


# # class ChatResponse(BaseModel):
# #     reply: str
# #     chart: Optional[ChartData] = None

# from pydantic import BaseModel
# from typing import List, Optional, Literal


# class Message(BaseModel):
#     role: str
#     content: str


# class ChatRequest(BaseModel):
#     messages: List[Message]


# class ChartPoint(BaseModel):
#     time: str
#     price: float


# class ChartData(BaseModel):
#     label: str
#     points: List[ChartPoint]


# class ChatResponse(BaseModel):
#     reply: str
#     chart: Optional[ChartData] = None


# class PlannerOutput(BaseModel):
#     intent: Literal["finance_query", "casual", "unsupported"]
#     asset: Optional[Literal["bitcoin", "ethereum", "solana"]] = None
#     days: Literal[3, 7, 30, 365] = 7
#     needs_current_price: bool
#     needs_chart: bool

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
    asset: Optional[Literal["bitcoin", "ethereum", "solana"]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    needs_current_price: bool
    needs_chart: bool