"""
tests/test_api_endpoints.py
Integration tests for the FastAPI endpoints in main.py

Uses FastAPI TestClient — no real network/LLM calls (all mocked).
"""
import pytest
import sys, os
from unittest.mock import patch, AsyncMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from main import app, _memory_store
from core.models import (
    Confidence, FinancialsAgentOutput, NewsAgentOutput,
    ResearchReport, Sentiment, SynthesisAgentOutput, Verdict,
)
from datetime import datetime, timezone

client = TestClient(app)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _make_full_report(ticker="AAPL") -> ResearchReport:
    return ResearchReport(
        id="test-id-123",
        ticker=ticker,
        exchange="NYSE / NASDAQ",
        generated_at=datetime.now(timezone.utc),
        news=NewsAgentOutput(
            ticker=ticker,
            headlines=[],
            overall_sentiment=Sentiment.POSITIVE,
            key_events=["Strong Q4"],
        ),
        financials=FinancialsAgentOutput(
            ticker=ticker,
            company_name="Apple Inc.",
            exchange="NYSE / NASDAQ",
            pe_ratio=32.1,
            data_source="yfinance",
        ),
        synthesis=SynthesisAgentOutput(
            verdict=Verdict.BUY,
            confidence=Confidence.HIGH,
            reasoning="Solid fundamentals and positive sentiment.",
            risks=["Risk A", "Risk B", "Risk C"],
        ),
        processing_time_seconds=4.21,
    )


@pytest.fixture(autouse=True)
def clear_report_store():
    """Reset in-memory report store before each test."""
    _memory_store.clear()
    yield
    _memory_store.clear()


# ─── GET / ────────────────────────────────────────────────────────────────────

def test_root_returns_service_info():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["service"] == "Multi-Agent Stock Research System"
    assert data["status"] == "running"


# ─── GET /health ──────────────────────────────────────────────────────────────

def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ─── POST /api/research ───────────────────────────────────────────────────────

def test_research_happy_path():
    mock_report = _make_full_report("AAPL")
    with patch("main.run_research_pipeline", new_callable=AsyncMock, return_value=mock_report):
        r = client.post("/api/research", json={"ticker": "AAPL", "exchange": "AUTO"})

    assert r.status_code == 200
    data = r.json()
    assert data["ticker"] == "AAPL"
    assert data["synthesis"]["verdict"] == "BUY"
    assert data["synthesis"]["confidence"] == "High"
    assert len(data["synthesis"]["risks"]) == 3

def test_research_stores_report_in_memory():
    mock_report = _make_full_report("TSLA")
    with patch("main.run_research_pipeline", new_callable=AsyncMock, return_value=mock_report):
        client.post("/api/research", json={"ticker": "TSLA"})

    assert len(_memory_store) == 1
    assert _memory_store[0]["ticker"] == "TSLA"

def test_research_lowercase_ticker_accepted():
    mock_report = _make_full_report("AAPL")
    with patch("main.run_research_pipeline", new_callable=AsyncMock, return_value=mock_report):
        r = client.post("/api/research", json={"ticker": "aapl"})
    assert r.status_code == 200

def test_research_invalid_ticker_returns_400():
    r = client.post("/api/research", json={"ticker": ""})
    assert r.status_code in (400, 422)

def test_research_special_chars_in_ticker_returns_400():
    r = client.post("/api/research", json={"ticker": "AAP L!@#"})
    assert r.status_code == 400

def test_research_too_long_ticker_returns_400():
    r = client.post("/api/research", json={"ticker": "A" * 25})
    assert r.status_code in (400, 422)

def test_research_pipeline_error_returns_500():
    with patch("main.run_research_pipeline", new_callable=AsyncMock,
               side_effect=RuntimeError("Pipeline crashed")):
        r = client.post("/api/research", json={"ticker": "AAPL"})
    assert r.status_code == 500

def test_research_default_exchange_is_auto():
    """Omitting exchange field should default to AUTO without error."""
    mock_report = _make_full_report()
    with patch("main.run_research_pipeline", new_callable=AsyncMock, return_value=mock_report):
        r = client.post("/api/research", json={"ticker": "AAPL"})
    assert r.status_code == 200


# ─── GET /api/history ────────────────────────────────────────────────────────

def test_history_empty():
    r = client.get("/api/history")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 0
    assert data["reports"] == []
    assert data["page"] == 1

def test_history_after_research():
    mock_report = _make_full_report("AAPL")
    with patch("main.run_research_pipeline", new_callable=AsyncMock, return_value=mock_report):
        client.post("/api/research", json={"ticker": "AAPL"})

    r = client.get("/api/history")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["reports"][0]["ticker"] == "AAPL"

def test_history_filter_by_ticker():
    for ticker in ("AAPL", "TSLA", "AAPL"):
        report = _make_full_report(ticker)
        with patch("main.run_research_pipeline", new_callable=AsyncMock, return_value=report):
            client.post("/api/research", json={"ticker": ticker})

    r = client.get("/api/history?ticker=AAPL")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2
    assert all(rep["ticker"] == "AAPL" for rep in data["reports"])

def test_history_pagination():
    for _ in range(5):
        report = _make_full_report("AAPL")
        with patch("main.run_research_pipeline", new_callable=AsyncMock, return_value=report):
            client.post("/api/research", json={"ticker": "AAPL"})

    r = client.get("/api/history?page=1&page_size=2")
    assert r.status_code == 200
    data = r.json()
    assert len(data["reports"]) == 2
    assert data["total"] == 5


# ─── GET /api/cse ─────────────────────────────────────────────────────────────

def test_cse_list_returns_stocks():
    r = client.get("/api/cse")
    assert r.status_code == 200
    data = r.json()
    assert "stocks" in data
    assert "total" in data
    assert data["total"] >= 30
    assert "sectors" in data

def test_cse_list_sector_filter():
    r = client.get("/api/cse?sector=Banking%20%26%20Finance")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] > 0
    for s in data["stocks"]:
        assert s["sector"] == "Banking & Finance"

def test_cse_ticker_found():
    r = client.get("/api/cse/JKH.N")
    assert r.status_code == 200
    data = r.json()
    assert data["ticker"] == "JKH.N"

def test_cse_ticker_lowercase_found():
    r = client.get("/api/cse/jkh.n")
    assert r.status_code == 200

def test_cse_ticker_not_found_returns_404():
    r = client.get("/api/cse/NOTEXIST.N")
    assert r.status_code == 404
