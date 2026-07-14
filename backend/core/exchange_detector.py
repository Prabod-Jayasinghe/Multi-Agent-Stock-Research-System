"""
core/exchange_detector.py
Auto-detects the stock exchange from the ticker symbol suffix and returns
a normalised exchange name + the correct yfinance-compatible ticker string.

Supported:
  USA    (NYSE / NASDAQ)      — no suffix   e.g. AAPL, TSLA
  Japan  (TSE)                — .T suffix   e.g. 7203.T
  UK     (LSE)                — .L suffix   e.g. VOD.L
  Germany (XETRA)             — .DE suffix  e.g. SAP.DE
  India  (NSE)                — .NS suffix  e.g. RELIANCE.NS
  India  (BSE)                — .BO suffix  e.g. TATASTEEL.BO
  CSE    (Colombo SE)         — .N / .X / .CSE suffix  e.g. JKH.N
"""

from dataclasses import dataclass


@dataclass
class ExchangeInfo:
    name: str           # Human-readable exchange name
    country: str        # ISO 3166-1 alpha-2 country code
    currency: str       # ISO 4217 currency code
    yf_ticker: str      # Ticker as yfinance expects it
    is_cse: bool = False  # True → use CSV fallback instead of yfinance


# Suffix → exchange mapping
_SUFFIX_MAP: dict[str, dict] = {
    ".t":   {"name": "Tokyo Stock Exchange",   "country": "JP", "currency": "JPY"},
    ".l":   {"name": "London Stock Exchange",  "country": "GB", "currency": "GBP"},
    ".de":  {"name": "XETRA (Frankfurt)",      "country": "DE", "currency": "EUR"},
    ".as":  {"name": "Euronext Amsterdam",     "country": "NL", "currency": "EUR"},
    ".pa":  {"name": "Euronext Paris",         "country": "FR", "currency": "EUR"},
    ".sw":  {"name": "SIX Swiss Exchange",     "country": "CH", "currency": "CHF"},
    ".ax":  {"name": "Australian Securities Exchange", "country": "AU", "currency": "AUD"},
    ".to":  {"name": "Toronto Stock Exchange", "country": "CA", "currency": "CAD"},
    ".hk":  {"name": "Hong Kong Stock Exchange","country":"HK", "currency": "HKD"},
    # India — National Stock Exchange (NSE) and Bombay Stock Exchange (BSE)
    ".ns":  {"name": "National Stock Exchange (India)",  "country": "IN", "currency": "INR"},
    ".bo":  {"name": "Bombay Stock Exchange (India)",     "country": "IN", "currency": "INR"},
    # CSE suffixes — these trigger CSV fallback
    ".n":   {"name": "Colombo Stock Exchange (N board)", "country": "LK", "currency": "LKR", "is_cse": True},
    ".x":   {"name": "Colombo Stock Exchange (X board)", "country": "LK", "currency": "LKR", "is_cse": True},
    ".cse": {"name": "Colombo Stock Exchange",           "country": "LK", "currency": "LKR", "is_cse": True},
}

_USA_EXCHANGE = {"name": "NYSE / NASDAQ", "country": "US", "currency": "USD"}


def detect_exchange(ticker: str) -> ExchangeInfo:
    """
    Detect exchange from ticker suffix.

    Args:
        ticker: Raw ticker string, e.g. 'AAPL', '7203.T', 'JKH.N'

    Returns:
        ExchangeInfo with name, country, currency, yf_ticker, is_cse
    """
    ticker_clean = ticker.strip().upper()

    # Find suffix
    dot_pos = ticker_clean.rfind(".")
    if dot_pos == -1:
        # No suffix → US exchange
        return ExchangeInfo(
            name=_USA_EXCHANGE["name"],
            country=_USA_EXCHANGE["country"],
            currency=_USA_EXCHANGE["currency"],
            yf_ticker=ticker_clean,
            is_cse=False,
        )

    suffix = ticker_clean[dot_pos:].lower()
    meta = _SUFFIX_MAP.get(suffix)

    if meta is None:
        # Unknown suffix — assume US and pass through
        return ExchangeInfo(
            name=_USA_EXCHANGE["name"],
            country=_USA_EXCHANGE["country"],
            currency=_USA_EXCHANGE["currency"],
            yf_ticker=ticker_clean,
            is_cse=False,
        )

    is_cse = meta.get("is_cse", False)

    return ExchangeInfo(
        name=meta["name"],
        country=meta["country"],
        currency=meta["currency"],
        # yfinance uses uppercase suffixes (e.g. 7203.T, VOD.L)
        yf_ticker=ticker_clean,
        is_cse=is_cse,
    )


def normalise_ticker(ticker: str) -> str:
    """Return a clean, uppercase ticker string."""
    return ticker.strip().upper()
