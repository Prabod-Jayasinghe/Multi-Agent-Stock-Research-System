"""
tests/test_news_agent.py
Unit & integration tests for agents/news_agent.py

All network calls (GNews, Groq) are mocked — no real API keys needed.
"""

import pytest
import sys, os
from unittest.mock import patch, MagicMock, AsyncMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.news_agent import (
    run_news_agent,
    clear_news_cache,
    _analyse_headline,
    _aggregate_sentiments,
    _majority_sentiment,
    _build_gnews_query,
)
from core.models import NewsAgentOutput, NewsItem, Sentiment


# ─── Fixtures ─────────────────────────────────────────────────────────────────

MOCK_ARTICLES = [
    {
        "title": "Apple reports record Q4 earnings, beats estimates",
        "url": "https://example.com/1",
        "publishedAt": "2026-07-01T10:00:00Z",
        "source": {"name": "Reuters"},
    },
    {
        "title": "Apple faces antitrust probe in EU over App Store practices",
        "url": "https://example.com/2",
        "publishedAt": "2026-07-01T09:00:00Z",
        "source": {"name": "Bloomberg"},
    },
    {
        "title": "Apple stock relatively flat amid broader market volatility",
        "url": "https://example.com/3",
        "publishedAt": "2026-07-01T08:00:00Z",
        "source": {"name": "MarketWatch"},
    },
]

MOCK_SENTIMENT_POSITIVE = {"sentiment": "Positive", "key_event": "Record earnings beat"}
MOCK_SENTIMENT_NEGATIVE = {"sentiment": "Negative", "key_event": "Antitrust regulatory risk"}
MOCK_SENTIMENT_NEUTRAL  = {"sentiment": "Neutral",  "key_event": "Flat stock performance"}

MOCK_AGGREGATE = {
    "overall_sentiment": "Neutral",
    "key_events": ["Record earnings", "Antitrust probe", "Market volatility"],
}


# Helper to clear cache before each test
@pytest.fixture(autouse=True)
def clear_cache():
    clear_news_cache()
    yield
    clear_news_cache()


# ─── _build_gnews_query ───────────────────────────────────────────────────────

def test_query_no_suffix():
    assert _build_gnews_query("AAPL") == "AAPL stock"

def test_query_strips_exchange_suffix():
    assert _build_gnews_query("7203.T") == "7203 stock"

def test_query_cse_suffix():
    assert _build_gnews_query("JKH.N") == "JKH stock"


# ─── _majority_sentiment ──────────────────────────────────────────────────────

def test_majority_positive():
    s = [Sentiment.POSITIVE, Sentiment.POSITIVE, Sentiment.NEGATIVE]
    assert _majority_sentiment(s) == Sentiment.POSITIVE

def test_majority_empty():
    assert _majority_sentiment([]) == Sentiment.NEUTRAL

def test_majority_all_same():
    s = [Sentiment.NEGATIVE] * 4
    assert _majority_sentiment(s) == Sentiment.NEGATIVE


# ─── _analyse_headline ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_analyse_headline_positive():
    with patch("agents.news_agent.chat_completion_json", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = MOCK_SENTIMENT_POSITIVE
        sentiment, key_event = await _analyse_headline("Apple beats earnings estimates")

    assert sentiment == Sentiment.POSITIVE
    assert key_event == "Record earnings beat"

@pytest.mark.asyncio
async def test_analyse_headline_negative():
    with patch("agents.news_agent.chat_completion_json", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = MOCK_SENTIMENT_NEGATIVE
        sentiment, _ = await _analyse_headline("Apple faces antitrust probe")

    assert sentiment == Sentiment.NEGATIVE

@pytest.mark.asyncio
async def test_analyse_headline_invalid_sentiment_becomes_neutral():
    """If LLM returns an invalid sentiment string, fallback to Neutral."""
    with patch("agents.news_agent.chat_completion_json", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = {"sentiment": "BULLISH", "key_event": "something"}
        sentiment, _ = await _analyse_headline("Some headline")

    assert sentiment == Sentiment.NEUTRAL

@pytest.mark.asyncio
async def test_analyse_headline_llm_exception_returns_neutral():
    """LLM failure must return Neutral gracefully without raising."""
    with patch("agents.news_agent.chat_completion_json", new_callable=AsyncMock) as mock_llm:
        mock_llm.side_effect = RuntimeError("Groq down")
        sentiment, key_event = await _analyse_headline("Some headline")

    assert sentiment == Sentiment.NEUTRAL
    assert key_event == ""


# ─── _aggregate_sentiments ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_aggregate_returns_correct_fields():
    headlines = ["Apple beats earnings", "Apple antitrust probe", "Stock flat"]
    sentiments = [Sentiment.POSITIVE, Sentiment.NEGATIVE, Sentiment.NEUTRAL]

    with patch("agents.news_agent.chat_completion_json", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = MOCK_AGGREGATE
        overall, events = await _aggregate_sentiments(headlines, sentiments)

    assert overall == Sentiment.NEUTRAL
    assert len(events) == 3

@pytest.mark.asyncio
async def test_aggregate_empty_list():
    overall, events = await _aggregate_sentiments([], [])
    assert overall == Sentiment.NEUTRAL
    assert events == []

@pytest.mark.asyncio
async def test_aggregate_llm_failure_falls_back_to_majority():
    headlines = ["H1", "H2", "H3"]
    sentiments = [Sentiment.POSITIVE, Sentiment.POSITIVE, Sentiment.NEGATIVE]

    with patch("agents.news_agent.chat_completion_json", new_callable=AsyncMock) as mock_llm:
        mock_llm.side_effect = RuntimeError("LLM unavailable")
        overall, events = await _aggregate_sentiments(headlines, sentiments)

    assert overall == Sentiment.POSITIVE  # majority
    assert events == []


# ─── run_news_agent — full flow ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_full_flow_happy_path():
    """Full pipeline with mocked GNews + Groq."""
    sentiment_responses = [
        MOCK_SENTIMENT_POSITIVE,
        MOCK_SENTIMENT_NEGATIVE,
        MOCK_SENTIMENT_NEUTRAL,
    ]

    call_count = 0
    async def mock_llm_json(system, user, **kwargs):
        nonlocal call_count
        # First 3 calls = headline sentiments, last call = aggregation
        if call_count < len(MOCK_ARTICLES):
            resp = sentiment_responses[call_count]
        else:
            resp = MOCK_AGGREGATE
        call_count += 1
        return resp

    with patch("agents.news_agent._fetch_gnews", return_value=MOCK_ARTICLES), \
         patch("agents.news_agent.chat_completion_json", side_effect=mock_llm_json):
        result = await run_news_agent("AAPL")

    assert isinstance(result, NewsAgentOutput)
    assert result.ticker == "AAPL"
    assert len(result.headlines) == 3
    assert all(isinstance(h, NewsItem) for h in result.headlines)
    assert result.overall_sentiment == Sentiment.NEUTRAL
    assert len(result.key_events) > 0

@pytest.mark.asyncio
async def test_no_articles_returns_neutral_with_message():
    """When GNews returns nothing, agent returns Neutral with informative key_event."""
    with patch("agents.news_agent._fetch_gnews", return_value=[]):
        result = await run_news_agent("AAPL")

    assert result.ticker == "AAPL"
    assert result.headlines == []
    assert result.overall_sentiment == Sentiment.NEUTRAL
    assert any("No recent news" in e for e in result.key_events)

@pytest.mark.asyncio
async def test_gnews_api_key_missing_returns_empty():
    """No API key → empty articles → graceful empty output."""
    with patch("agents.news_agent.settings") as mock_settings:
        mock_settings.gnews_api_key = ""
        result = await run_news_agent("AAPL")

    assert result.headlines == []
    assert result.overall_sentiment == Sentiment.NEUTRAL


# ─── Caching ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_cache_hit_avoids_second_fetch():
    """Second call for same ticker must NOT call _fetch_gnews again."""
    sentiment_responses = [MOCK_SENTIMENT_POSITIVE, MOCK_SENTIMENT_POSITIVE, MOCK_AGGREGATE]
    idx = 0
    async def mock_llm(*a, **kw):
        nonlocal idx
        r = sentiment_responses[min(idx, len(sentiment_responses)-1)]
        idx += 1
        return r

    with patch("agents.news_agent._fetch_gnews", return_value=MOCK_ARTICLES[:1]) as mock_fetch, \
         patch("agents.news_agent.chat_completion_json", side_effect=mock_llm):
        r1 = await run_news_agent("MSFT")
        r2 = await run_news_agent("MSFT")

    assert mock_fetch.call_count == 1   # only called once despite 2 invocations
    assert r1.ticker == r2.ticker

@pytest.mark.asyncio
async def test_different_tickers_independent_cache():
    """Separate tickers must have independent cache entries."""
    with patch("agents.news_agent._fetch_gnews", return_value=[]) as mock_fetch:
        await run_news_agent("AAPL")
        await run_news_agent("TSLA")

    assert mock_fetch.call_count == 2

@pytest.mark.asyncio
async def test_clear_cache_forces_refetch():
    """After cache cleared, next call must re-fetch from GNews."""
    with patch("agents.news_agent._fetch_gnews", return_value=[]) as mock_fetch:
        await run_news_agent("AAPL")
        clear_news_cache("AAPL")
        await run_news_agent("AAPL")

    assert mock_fetch.call_count == 2


# ─── Output schema validation ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_output_field_types():
    """All fields in the output must match the expected Python types."""
    async def mock_llm(*a, **kw):
        return MOCK_SENTIMENT_POSITIVE

    with patch("agents.news_agent._fetch_gnews", return_value=MOCK_ARTICLES[:1]), \
         patch("agents.news_agent.chat_completion_json", new_callable=AsyncMock) as m:
        m.side_effect = [MOCK_SENTIMENT_POSITIVE, MOCK_AGGREGATE]
        result = await run_news_agent("AAPL")

    assert isinstance(result.ticker, str)
    assert isinstance(result.headlines, list)
    assert isinstance(result.overall_sentiment, Sentiment)
    assert isinstance(result.key_events, list)

    for item in result.headlines:
        assert isinstance(item.title, str)
        assert isinstance(item.url, str)
        assert isinstance(item.sentiment, Sentiment)
        assert isinstance(item.source, str)
