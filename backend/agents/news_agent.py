"""
agents/news_agent.py
Phase 3: News Agent

Fetches top 5 recent news headlines for a given ticker using the GNews API,
then runs each headline through Groq LLM for sentiment analysis and key-event
extraction. Results are cached per ticker for 1 hour to stay within the
GNews free-tier limit of 100 requests/day.

Public API:
    run_news_agent(ticker: str) -> NewsAgentOutput
"""

import asyncio
import logging
import time
from typing import Optional

import requests
from cachetools import TTLCache

from core.config import get_settings
from core.llm_client import chat_completion_json
from core.models import NewsAgentOutput, NewsItem, Sentiment

logger = logging.getLogger(__name__)
settings = get_settings()

# ─── In-memory cache: 500 slots, 1-hour TTL ──────────────────────────────────
_news_cache: TTLCache = TTLCache(maxsize=500, ttl=3600)

# ─── GNews API base URL ───────────────────────────────────────────────────────
_GNEWS_BASE = "https://gnews.io/api/v4/search"


# ─── Prompts ──────────────────────────────────────────────────────────────────

_SENTIMENT_SYSTEM = """
You are a financial news analyst. You will receive one news headline about a stock.
Respond ONLY with a valid JSON object in this exact format:
{
  "sentiment": "Positive" | "Neutral" | "Negative",
  "key_event": "One sentence summarising the main financial event or development in this headline"
}
No explanation, no markdown, no extra text — only the JSON object.
"""

_AGGREGATION_SYSTEM = """
You are a senior financial analyst. You will receive a list of news headlines and
their individual sentiments for a stock. Respond ONLY with a valid JSON object:
{
  "overall_sentiment": "Positive" | "Neutral" | "Negative",
  "key_events": ["event 1", "event 2", "event 3"]
}
Rules:
- overall_sentiment: choose whichever sentiment appears most, or Neutral if tied
- key_events: list the 3 most significant distinct financial events from the headlines
- Return exactly 3 key_events (or fewer if less than 3 articles)
No explanation, no markdown, no extra text — only the JSON object.
"""


# ─── GNews fetcher ────────────────────────────────────────────────────────────

def _build_gnews_query(ticker: str) -> str:
    """
    Build an effective GNews search query from a ticker.
    Strips exchange suffix to get a cleaner company-name search.
    E.g. '7203.T' → '7203' (yfinance resolves the company name),
         'AAPL'   → 'AAPL stock'
    """
    base = ticker.split(".")[0]
    return f"{base} stock"


def _fetch_gnews(ticker: str) -> list[dict]:
    """
    Fetch up to 5 news articles from GNews API.
    Returns a list of raw article dicts.
    Falls back to an empty list on any error (agent continues with limited data).
    """
    if not settings.gnews_api_key:
        logger.warning("GNEWS_API_KEY not set — skipping GNews fetch")
        return []

    query = _build_gnews_query(ticker)
    params = {
        "q": query,
        "lang": "en",
        "max": 5,
        "apikey": settings.gnews_api_key,
    }

    try:
        resp = requests.get(_GNEWS_BASE, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        articles = data.get("articles", [])
        logger.info("GNews returned %d articles for '%s'", len(articles), ticker)
        return articles
    except requests.exceptions.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 429:
            logger.warning("GNews rate-limit hit for ticker %s", ticker)
        else:
            logger.warning("GNews HTTP error for %s: %s", ticker, exc)
    except requests.exceptions.Timeout:
        logger.warning("GNews timeout for ticker %s", ticker)
    except Exception as exc:
        logger.warning("GNews unexpected error for %s: %s", ticker, exc)

    return []


# ─── Sentiment analysis per headline ─────────────────────────────────────────

async def _analyse_headline(title: str) -> tuple[Sentiment, str]:
    """
    Run a single headline through Groq LLM.
    Returns (Sentiment, key_event_string).
    Falls back to Neutral + empty string on any failure.
    """
    try:
        result = await chat_completion_json(
            _SENTIMENT_SYSTEM,
            f"Headline: {title}",
            temperature=0.1,
            max_tokens=128,
        )
        raw_sentiment = result.get("sentiment", "Neutral")
        key_event = result.get("key_event", "")

        # Validate sentiment value
        try:
            sentiment = Sentiment(raw_sentiment)
        except ValueError:
            sentiment = Sentiment.NEUTRAL

        return sentiment, key_event

    except Exception as exc:
        logger.warning("Sentiment analysis failed for headline '%s': %s", title[:50], exc)
        return Sentiment.NEUTRAL, ""


# ─── Overall sentiment + key event aggregation ────────────────────────────────

async def _aggregate_sentiments(
    headlines: list[str],
    sentiments: list[Sentiment],
) -> tuple[Sentiment, list[str]]:
    """
    Calls Groq to pick the overall sentiment and top 3 key events.
    Falls back to majority-vote sentiment + empty events on failure.
    """
    if not headlines:
        return Sentiment.NEUTRAL, []

    # Build input summary
    lines = [
        f"{i+1}. [{s.value}] {h}"
        for i, (h, s) in enumerate(zip(headlines, sentiments))
    ]
    user_msg = "Headlines and sentiments:\n" + "\n".join(lines)

    try:
        result = await chat_completion_json(
            _AGGREGATION_SYSTEM,
            user_msg,
            temperature=0.1,
            max_tokens=256,
        )
        raw_overall = result.get("overall_sentiment", "Neutral")
        key_events = result.get("key_events", [])

        try:
            overall = Sentiment(raw_overall)
        except ValueError:
            overall = _majority_sentiment(sentiments)

        return overall, key_events[:3]

    except Exception as exc:
        logger.warning("Sentiment aggregation failed: %s", exc)
        # Fallback: majority vote
        return _majority_sentiment(sentiments), []


def _majority_sentiment(sentiments: list[Sentiment]) -> Sentiment:
    """Return the most common sentiment, defaulting to Neutral on tie."""
    if not sentiments:
        return Sentiment.NEUTRAL
    counts = {s: sentiments.count(s) for s in Sentiment}
    return max(counts, key=lambda s: counts[s])


# ─── Public entry point ───────────────────────────────────────────────────────

async def run_news_agent(ticker: str) -> NewsAgentOutput:
    """
    Fetch and analyse news for a given ticker.

    Flow:
      1. Check in-memory cache (1h TTL) — return immediately if hit
      2. Fetch up to 5 headlines from GNews API
      3. Analyse each headline in parallel with Groq LLM
      4. Aggregate overall sentiment + extract top 3 key events
      5. Cache and return NewsAgentOutput

    Args:
        ticker: Stock ticker symbol (e.g. 'AAPL', '7203.T', 'JKH.N')

    Returns:
        NewsAgentOutput with headlines, individual sentiments, overall
        sentiment, and key events.
    """
    ticker = ticker.strip().upper()

    # ── Cache hit ─────────────────────────────────────────────────────────────
    if ticker in _news_cache:
        logger.info("News Agent cache HIT for %s", ticker)
        return _news_cache[ticker]

    logger.info("News Agent: fetching headlines for %s", ticker)

    # ── Fetch articles ────────────────────────────────────────────────────────
    articles = _fetch_gnews(ticker)

    if not articles:
        # No articles — return minimal output; synthesis will handle this
        logger.warning("No news articles found for %s", ticker)
        result = NewsAgentOutput(
            ticker=ticker,
            headlines=[],
            overall_sentiment=Sentiment.NEUTRAL,
            key_events=[f"No recent news found for {ticker}."],
        )
        _news_cache[ticker] = result
        return result

    # ── Analyse each headline in parallel ─────────────────────────────────────
    tasks = [_analyse_headline(article["title"]) for article in articles]
    analyses: list[tuple[Sentiment, str]] = await asyncio.gather(*tasks)

    # ── Build NewsItem list ───────────────────────────────────────────────────
    news_items: list[NewsItem] = []
    headline_texts: list[str] = []
    sentiment_list: list[Sentiment] = []

    for article, (sentiment, _key_event) in zip(articles, analyses):
        item = NewsItem(
            title=article.get("title", ""),
            url=article.get("url", ""),
            published_at=article.get("publishedAt", ""),
            sentiment=sentiment,
            source=article.get("source", {}).get("name", "Unknown"),
        )
        news_items.append(item)
        headline_texts.append(article.get("title", ""))
        sentiment_list.append(sentiment)

    # ── Aggregate ─────────────────────────────────────────────────────────────
    overall_sentiment, key_events = await _aggregate_sentiments(
        headline_texts, sentiment_list
    )

    result = NewsAgentOutput(
        ticker=ticker,
        headlines=news_items,
        overall_sentiment=overall_sentiment,
        key_events=key_events if key_events else [f"No key events extracted for {ticker}."],
    )

    # ── Cache and return ──────────────────────────────────────────────────────
    _news_cache[ticker] = result
    logger.info(
        "News Agent complete for %s: %d headlines, sentiment=%s",
        ticker, len(news_items), overall_sentiment.value
    )
    return result


def clear_news_cache(ticker: Optional[str] = None) -> None:
    """
    Clear the news cache. If ticker is provided, clear only that entry.
    Useful for testing and cache invalidation.
    """
    if ticker:
        _news_cache.pop(ticker.upper(), None)
    else:
        _news_cache.clear()
