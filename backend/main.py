"""
main.py
FastAPI application — Phase 5: Database Integration

Endpoints:
  GET  /             — service info
  GET  /health       — health check (+ DB connectivity status)
  POST /api/research — run full 3-agent research pipeline + save to DB
  GET  /api/history  — retrieve past reports from Supabase (paginated)
  GET  /api/report/{id} — single report lookup
  GET  /api/cse      — list CSE stocks
  GET  /api/cse/{ticker} — get single CSE stock
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import get_settings
from core.models import (
    ErrorResponse,
    HealthResponse,
    HistoryResponse,
    ResearchReport,
    ResearchRequest,
)
from data.cse_loader import get_cse_stock, list_cse_stocks, get_cse_sectors
from db.database import (
    init_db,
    save_report,
    get_reports,
    get_report_by_id,
    get_db_stats,
)
from orchestrator import run_research_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()


# ─── Lifespan ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Multi-Agent Stock Research System — starting up")
    logger.info("   Groq model  : %s", settings.groq_model)
    logger.info("   CORS origins: %s", settings.cors_origins_list)
    logger.info("   GNews key   : %s", "configured" if settings.gnews_api_key else "NOT SET")
    logger.info("   Database    : %s", "configured" if settings.database_url else "NOT SET (in-memory fallback)")

    # Attempt DB init (creates tables if they don't exist — safe to call repeatedly)
    if settings.database_url:
        await init_db()

    yield
    logger.info("🛑 Shutting down")


# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Multi-Agent Stock Research System",
    description=(
        "AI-powered financial research platform. "
        "Submit a ticker to receive a structured BUY/HOLD/SELL research report "
        "produced by three coordinated AI agents."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ─── Timing middleware ────────────────────────────────────────────────────────
@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    t0 = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{time.perf_counter() - t0:.3f}s"
    return response

# ─── In-memory fallback store (used when DATABASE_URL not set) ────────────────
_memory_store: list[dict] = []


# ─── Input validation helper ──────────────────────────────────────────────────
_ALLOWED_TICKER_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.")


def _validate_ticker(ticker: str) -> str:
    """Normalise and validate a ticker string. Raises HTTPException on failure."""
    clean = ticker.strip().upper()
    if not clean or len(clean) > 20:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid ticker '{ticker}': must be 1-20 characters.",
        )
    if not all(c in _ALLOWED_TICKER_CHARS for c in clean):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid ticker '{ticker}': only letters, digits, and dots allowed.",
        )
    return clean


# ─── System endpoints ─────────────────────────────────────────────────────────
@app.get("/", tags=["System"])
async def root():
    return {
        "service": "Multi-Agent Stock Research System",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["System"])
async def health():
    """
    Returns service health status including database connectivity.
    """
    db_stats = await get_db_stats()
    return {
        "status": "ok",
        "version": "1.0.0",
        "database": db_stats,
        "groq_configured": bool(settings.groq_api_key),
        "gnews_configured": bool(settings.gnews_api_key),
    }


# ─── Research endpoint ────────────────────────────────────────────────────────
@app.post(
    "/api/research",
    response_model=ResearchReport,
    tags=["Research"],
    summary="Run full stock research pipeline",
    responses={
        200: {"description": "Full research report with BUY/HOLD/SELL verdict"},
        400: {"model": ErrorResponse, "description": "Invalid ticker"},
        500: {"model": ErrorResponse, "description": "Pipeline error"},
    },
)
async def research(request: ResearchRequest):
    """
    Submit a stock ticker to run the full multi-agent research pipeline.

    - **ticker**: Stock symbol (e.g. `AAPL`, `7203.T`, `JKH.N`)
    - **exchange**: Optional exchange hint (`AUTO` detects from ticker suffix)

    The report is automatically saved to Supabase. Returns the full report
    within ~30-45 seconds.
    """
    ticker = _validate_ticker(request.ticker)
    logger.info("POST /api/research | ticker=%s | exchange=%s", ticker, request.exchange)

    # Normalise request ticker
    request = ResearchRequest(ticker=ticker, exchange=request.exchange)

    try:
        report = await run_research_pipeline(request)
    except Exception as exc:
        logger.exception("Pipeline error for ticker %s: %s", ticker, exc)
        raise HTTPException(
            status_code=500,
            detail=f"Research pipeline failed: {exc}",
        )

    # ── Persist to DB (fire-and-forget style, never blocks the response) ──────
    saved_id = await save_report(report)
    if saved_id:
        logger.info("Report persisted to DB: id=%s", saved_id)
    else:
        # DB save failed or DB not configured — fall back to in-memory store
        _memory_store.append(report.model_dump(mode="json"))
        logger.info("Report stored in-memory fallback (DB unavailable)")

    return report


# ─── History endpoint ─────────────────────────────────────────────────────────
@app.get(
    "/api/history",
    response_model=HistoryResponse,
    tags=["History"],
    summary="Retrieve past research reports",
)
async def history(
    ticker: Optional[str] = Query(None, description="Filter by ticker symbol"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Reports per page"),
):
    """
    Returns paginated list of previously generated research reports.

    Results are served from Supabase when configured, or the in-memory
    fallback store when DATABASE_URL is not set.
    """
    # Try DB first
    db_reports, total = await get_reports(
        ticker=ticker,
        page=page,
        page_size=page_size,
    )

    if db_reports or total > 0:
        return HistoryResponse(
            reports=db_reports,
            total=total,
            page=page,
            page_size=page_size,
        )

    # Fallback: in-memory store
    reports = list(reversed(_memory_store))
    if ticker:
        reports = [r for r in reports if r.get("ticker") == ticker.strip().upper()]

    total = len(reports)
    start = (page - 1) * page_size
    paginated = reports[start: start + page_size]

    return HistoryResponse(
        reports=paginated,
        total=total,
        page=page,
        page_size=page_size,
    )


# ─── Single report by ID ──────────────────────────────────────────────────────
@app.get(
    "/api/report/{report_id}",
    tags=["History"],
    summary="Get a single report by ID",
)
async def get_report(report_id: str):
    """
    Retrieve a single research report by its UUID.
    Returns 404 if not found.
    """
    # Validate UUID format
    try:
        import uuid as _uuid
        _uuid.UUID(report_id)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid report ID format: {report_id}")

    report = await get_report_by_id(report_id)
    if not report:
        # Check in-memory fallback
        for r in _memory_store:
            if r.get("id") == report_id:
                return r
        raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found.")

    return report


# ─── CSE endpoints ────────────────────────────────────────────────────────────
@app.get(
    "/api/cse",
    tags=["CSE"],
    summary="List all Colombo Stock Exchange stocks",
)
async def cse_list(
    sector: Optional[str] = Query(None, description="Filter by sector"),
):
    """
    Returns the full CSE stock dataset (50 stocks), optionally filtered by sector.
    """
    stocks = list_cse_stocks(sector=sector)
    sectors = get_cse_sectors()
    return {
        "stocks": stocks,
        "total": len(stocks),
        "sectors": sectors,
        "note": "CSE data is manually maintained and may not reflect real-time prices.",
    }


@app.get(
    "/api/cse/{ticker}",
    tags=["CSE"],
    summary="Get a single CSE stock by ticker",
)
async def cse_ticker(ticker: str):
    """
    Returns static fundamental data for a single CSE ticker (e.g. `JKH.N`).
    Returns 404 if the ticker is not in the dataset.
    """
    stock = get_cse_stock(ticker)
    if not stock:
        raise HTTPException(
            status_code=404,
            detail=f"Ticker '{ticker.upper()}' not found in CSE dataset.",
        )
    return stock


# ─── Dev runner ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
    )
