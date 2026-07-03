"""
tests/test_database.py
Tests for db/database.py

Verifies connection string conversion, no-op behavior when DB is not configured,
and robust error isolation during DB read/write failures.
"""
import pytest
import sys
import os
import uuid
from unittest.mock import patch, AsyncMock, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from db.database import (
    _get_engine,
    save_report,
    get_reports,
    get_report_by_id,
    _report_to_dict,
)
from core.models import (
    ResearchReport,
    NewsAgentOutput,
    FinancialsAgentOutput,
    SynthesisAgentOutput,
    Sentiment,
    Verdict,
    Confidence,
)


# ─── Mock Report Builder ──────────────────────────────────────────────────────
def _make_test_report(ticker="AAPL") -> ResearchReport:
    return ResearchReport(
        id=str(uuid.uuid4()),
        ticker=ticker,
        exchange="NYSE / NASDAQ",
        news=NewsAgentOutput(
            ticker=ticker,
            headlines=[],
            overall_sentiment=Sentiment.POSITIVE,
            key_events=["Earnings beat"],
        ),
        financials=FinancialsAgentOutput(
            ticker=ticker,
            company_name="Apple Inc.",
            exchange="NYSE / NASDAQ",
            pe_ratio=30.0,
            data_source="yfinance",
        ),
        synthesis=SynthesisAgentOutput(
            verdict=Verdict.BUY,
            confidence=Confidence.HIGH,
            reasoning="Reasoning.",
            risks=["Risk 1", "Risk 2", "Risk 3"],
        ),
        processing_time_seconds=1.5,
    )


# ─── Connection Normalisation Tests ───────────────────────────────────────────
def test_connection_string_normalisation():
    """Verify that postgresql:// is properly converted to postgresql+asyncpg://"""
    with patch("db.database.settings") as mock_settings:
        # Test postgresql conversion
        mock_settings.database_url = "postgresql://user:pass@host:5432/db"
        with patch("db.database.create_async_engine") as mock_create:
            _get_engine()
            mock_create.assert_called_once()
            args, kwargs = mock_create.call_args
            assert args[0] == "postgresql+asyncpg://user:pass@host:5432/db"

    # Reset cache/singleton for subsequent tests
    import db.database
    db.database._engine = None


def test_connection_string_normalisation_postgres():
    """Verify that postgres:// is converted to postgresql+asyncpg://"""
    import db.database
    db.database._engine = None
    with patch("db.database.settings") as mock_settings:
        mock_settings.database_url = "postgres://user:pass@host/db"
        with patch("db.database.create_async_engine") as mock_create:
            _get_engine()
            mock_create.assert_called_once()
            args, _ = mock_create.call_args
            assert args[0] == "postgresql+asyncpg://user:pass@host/db"


# ─── No-Op/Fallback Tests ─────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_save_report_no_db_url_returns_none():
    """If DATABASE_URL is empty, save_report should skip saving and return None without error."""
    import db.database
    db.database._engine = None
    db.database._session_factory = None
    with patch("db.database.settings") as mock_settings:
        mock_settings.database_url = ""
        report = _make_test_report()
        result = await save_report(report)
        assert result is None


@pytest.mark.asyncio
async def test_get_reports_no_db_url_returns_empty():
    """If DATABASE_URL is empty, get_reports should return ([], 0) without raising."""
    import db.database
    db.database._engine = None
    db.database._session_factory = None
    with patch("db.database.settings") as mock_settings:
        mock_settings.database_url = ""
        reports, total = await get_reports()
        assert reports == []
        assert total == 0


# ─── Error Isolation/Graceful Fallback Tests ──────────────────────────────────
@pytest.mark.asyncio
async def test_save_report_exception_does_not_raise():
    """If committing to DB raises an exception, the function should log it and return None instead of crashing."""
    mock_factory = MagicMock()
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock(side_effect=Exception("Database connection timeout"))
    mock_session.__aenter__.return_value = mock_session
    mock_factory.return_value = mock_session

    with patch("db.database._get_session_factory", return_value=mock_factory):
        report = _make_test_report()
        result = await save_report(report)
        # Should gracefully return None instead of raising Exception
        assert result is None


@pytest.mark.asyncio
async def test_get_reports_exception_returns_empty():
    """If querying the DB raises an exception, get_reports should return ([], 0) gracefully."""
    mock_factory = MagicMock()
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(side_effect=Exception("Connection lost"))
    mock_session.__aenter__.return_value = mock_session
    mock_factory.return_value = mock_session

    with patch("db.database._get_session_factory", return_value=mock_factory):
        reports, total = await get_reports("AAPL")
        assert reports == []
        assert total == 0


@pytest.mark.asyncio
async def test_get_report_by_id_exception_returns_none():
    """If querying single report raises an exception, return None gracefully."""
    mock_factory = MagicMock()
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(side_effect=Exception("Connection lost"))
    mock_session.__aenter__.return_value = mock_session
    mock_factory.return_value = mock_session

    with patch("db.database._get_session_factory", return_value=mock_factory):
        report = await get_report_by_id(str(uuid.uuid4()))
        assert report is None
