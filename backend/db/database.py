"""
db/database.py
Phase 5: Database Integration

Async SQLAlchemy engine connecting to Supabase PostgreSQL.

Architecture decisions:
  - Uses asyncpg driver (postgresql+asyncpg://) for non-blocking I/O
  - All DB operations wrapped in try/except so a DB failure NEVER crashes
    the pipeline — reports are still returned to users even if save fails
  - Connection pool is created lazily on first use
  - DATABASE_URL not set → all DB functions are no-ops (dev without DB)

Public API:
    init_db()                              — create tables (dev only)
    save_report(report)  -> str | None     — persist a ResearchReport
    get_reports(ticker, page, page_size)   — paginated query
    get_report_by_id(report_id)            — single report lookup
"""

import json
import logging
import uuid
from typing import Optional

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.config import get_settings
from db.models import Base, Report

logger = logging.getLogger(__name__)
settings = get_settings()

# ─── Engine (module-level singleton) ─────────────────────────────────────────
_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker] = None


def _get_engine() -> Optional[AsyncEngine]:
    """Return the async engine, creating it on first call."""
    global _engine, _session_factory
    if _engine is not None:
        return _engine

    db_url = settings.database_url
    if not db_url:
        logger.warning(
            "DATABASE_URL not set — all DB operations will be skipped. "
            "Reports will still be returned; history will be empty."
        )
        return None

    # Convert postgresql:// → postgresql+asyncpg:// if needed
    if db_url.startswith("postgresql://") and "+asyncpg" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)

    try:
        _engine = create_async_engine(
            db_url,
            echo=False,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,          # detect stale connections
            pool_recycle=1800,           # recycle every 30 min
            connect_args={"ssl": "require"},  # Supabase requires SSL
        )
        _session_factory = async_sessionmaker(
            _engine, expire_on_commit=False, class_=AsyncSession
        )
        logger.info("Database engine created (asyncpg)")
        return _engine
    except Exception as exc:
        logger.error("Failed to create database engine: %s", exc)
        return None


def _get_session_factory() -> Optional[async_sessionmaker]:
    """Return the session factory, creating the engine if needed."""
    if _get_engine() is None:
        return None
    return _session_factory


# ─── Schema initialisation (used in dev / first-run) ─────────────────────────

async def init_db() -> bool:
    """
    Create all tables defined in db/models.py.
    Use this for local dev; in production use schema.sql via Supabase dashboard.

    Returns:
        True if successful, False if DB is unavailable.
    """
    engine = _get_engine()
    if engine is None:
        return False
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialised")
        return True
    except Exception as exc:
        logger.error("init_db failed: %s", exc)
        return False


# ─── Serialisation helpers ────────────────────────────────────────────────────

def _report_to_dict(report) -> dict:
    """
    Convert a ResearchReport Pydantic model to a plain dict suitable for
    JSONB storage. Handles datetime serialisation.
    """
    return json.loads(report.model_dump_json())


def _row_to_dict(row: Report) -> dict:
    """Convert an ORM Report row back to a plain dict for the API layer."""
    return {
        "id": str(row.id),
        "ticker": row.ticker,
        "exchange": row.exchange,
        "generated_at": row.generated_at.isoformat() if row.generated_at else None,
        "news": row.news,
        "financials": row.financials,
        "synthesis": row.synthesis,
        "processing_time_seconds": row.processing_time_seconds,
        "error": row.error,
    }


# ─── Write operations ─────────────────────────────────────────────────────────

async def save_report(report) -> Optional[str]:
    """
    Persist a ResearchReport to the database.

    Args:
        report: ResearchReport Pydantic model instance

    Returns:
        The stored report ID (str UUID) on success, or None if DB unavailable
        or an error occurred. The pipeline continues regardless.
    """
    factory = _get_session_factory()
    if factory is None:
        logger.debug("DB unavailable — skipping report save for %s", report.ticker)
        return None

    try:
        data = _report_to_dict(report)
        report_id = data.get("id") or str(uuid.uuid4())

        row = Report(
            id=uuid.UUID(report_id) if isinstance(report_id, str) else report_id,
            ticker=report.ticker,
            exchange=report.exchange,
            news=data.get("news"),
            financials=data.get("financials"),
            synthesis=data.get("synthesis"),
            processing_time_seconds=report.processing_time_seconds,
            error=report.error,
        )

        async with factory() as session:
            session.add(row)
            await session.commit()
            logger.info("Report saved to DB: id=%s ticker=%s", report_id, report.ticker)
            return report_id

    except Exception as exc:
        logger.error(
            "DB save failed for ticker=%s (report still returned to user): %s",
            report.ticker, exc
        )
        return None


# ─── Read operations ──────────────────────────────────────────────────────────

async def get_reports(
    ticker: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[dict], int]:
    """
    Fetch paginated reports, optionally filtered by ticker.

    Args:
        ticker:    Filter by ticker (None = all tickers)
        page:      1-indexed page number
        page_size: Number of results per page

    Returns:
        (list of report dicts, total count)
        Returns ([], 0) if DB unavailable.
    """
    factory = _get_session_factory()
    if factory is None:
        return [], 0

    try:
        async with factory() as session:
            base_q = select(Report)
            count_q = select(func.count()).select_from(Report)

            if ticker:
                ticker_up = ticker.strip().upper()
                base_q = base_q.where(Report.ticker == ticker_up)
                count_q = count_q.where(Report.ticker == ticker_up)

            # Total count
            total_result = await session.execute(count_q)
            total = total_result.scalar_one()

            # Paginated results — newest first
            offset = (page - 1) * page_size
            base_q = (
                base_q
                .order_by(desc(Report.generated_at))
                .offset(offset)
                .limit(page_size)
            )
            result = await session.execute(base_q)
            rows = result.scalars().all()

            return [_row_to_dict(r) for r in rows], total

    except Exception as exc:
        logger.error("DB get_reports failed: %s", exc)
        return [], 0


async def get_report_by_id(report_id: str) -> Optional[dict]:
    """
    Fetch a single report by its UUID.

    Returns:
        Report dict or None if not found / DB unavailable.
    """
    factory = _get_session_factory()
    if factory is None:
        return None

    try:
        async with factory() as session:
            result = await session.execute(
                select(Report).where(Report.id == uuid.UUID(report_id))
            )
            row = result.scalar_one_or_none()
            return _row_to_dict(row) if row else None
    except Exception as exc:
        logger.error("DB get_report_by_id failed for id=%s: %s", report_id, exc)
        return None


async def get_db_stats() -> dict:
    """
    Return basic DB statistics for the /health endpoint.

    Returns:
        dict with total_reports, db_connected flag.
    """
    factory = _get_session_factory()
    if factory is None:
        return {"db_connected": False, "total_reports": 0}

    try:
        async with factory() as session:
            result = await session.execute(select(func.count()).select_from(Report))
            total = result.scalar_one()
            return {"db_connected": True, "total_reports": total}
    except Exception as exc:
        logger.error("DB stats query failed: %s", exc)
        return {"db_connected": False, "total_reports": 0, "error": str(exc)}
