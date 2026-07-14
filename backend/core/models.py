"""
core/models.py
Pydantic request/response models shared across the application.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
from enum import Enum


# ─── Enums ────────────────────────────────────────────────────────────────────

class Exchange(str, Enum):
    USA = "USA"
    JAPAN = "Japan"
    UK = "UK"
    GERMANY = "Germany"
    INDIA = "India"
    CSE = "CSE"
    AUTO = "AUTO"


class Verdict(str, Enum):
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"


class Confidence(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    MEDIUM_HIGH = "Medium-High"
    HIGH = "High"


class Sentiment(str, Enum):
    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"


# ─── Request ──────────────────────────────────────────────────────────────────

class ResearchRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=20, description="Stock ticker symbol")
    exchange: Exchange = Field(default=Exchange.AUTO, description="Stock exchange (AUTO detects from ticker suffix)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "ticker": "AAPL",
                "exchange": "AUTO"
            }
        }
    }


# ─── News Agent Output ────────────────────────────────────────────────────────

class NewsItem(BaseModel):
    title: str
    url: str
    published_at: str
    sentiment: Sentiment
    source: str


class NewsAgentOutput(BaseModel):
    ticker: str
    headlines: List[NewsItem]
    overall_sentiment: Sentiment
    key_events: List[str]


# ─── Financials Agent Output ──────────────────────────────────────────────────

class FinancialsAgentOutput(BaseModel):
    ticker: str
    company_name: str
    exchange: str
    pe_ratio: Optional[float] = None
    eps: Optional[float] = None
    revenue: Optional[float] = None
    market_cap: Optional[float] = None
    debt_to_equity: Optional[float] = None
    dividend_yield: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    current_price: Optional[float] = None
    valuation_commentary: str = ""
    data_source: str = "yfinance"  # "yfinance" or "cse_csv"


# ─── Synthesis Agent Output ───────────────────────────────────────────────────

class SynthesisAgentOutput(BaseModel):
    verdict: Verdict
    confidence: Confidence
    reasoning: str
    risks: List[str]
    disclaimer: str = (
        "This report is AI-generated for informational purposes only and does not "
        "constitute financial advice. Always consult a qualified financial advisor "
        "before making investment decisions."
    )


# ─── Full Research Report ─────────────────────────────────────────────────────

class ResearchReport(BaseModel):
    id: Optional[str] = None
    ticker: str
    exchange: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    news: Optional[NewsAgentOutput] = None
    financials: Optional[FinancialsAgentOutput] = None
    synthesis: Optional[SynthesisAgentOutput] = None
    processing_time_seconds: Optional[float] = None
    error: Optional[str] = None


# ─── API Responses ────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


class HistoryResponse(BaseModel):
    reports: List[ResearchReport]
    total: int
    page: int
    page_size: int
