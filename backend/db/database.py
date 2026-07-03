"""
db/database.py
Stub — will be fully implemented in Phase 6.
Handles SQLAlchemy async engine setup and Supabase connection.
"""


async def init_db():
    """Initialize database tables. Implemented in Phase 6."""
    pass


async def save_report(report: dict) -> str:
    """Persist a research report. Implemented in Phase 6."""
    raise NotImplementedError("DB integration will be implemented in Phase 6")


async def get_reports_by_ticker(ticker: str, page: int = 1, page_size: int = 10) -> list:
    """Retrieve paginated reports for a ticker. Implemented in Phase 6."""
    raise NotImplementedError("DB integration will be implemented in Phase 6")


async def get_all_reports(page: int = 1, page_size: int = 20) -> list:
    """Retrieve all reports (paginated). Implemented in Phase 6."""
    raise NotImplementedError("DB integration will be implemented in Phase 6")
