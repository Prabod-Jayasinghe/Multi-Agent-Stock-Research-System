"""
db/models.py
SQLAlchemy ORM model for the reports table.
Uses the modern declarative style (SQLAlchemy 2.x).
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import String, Float, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Report(Base):
    """ORM mapping for the `reports` table."""

    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    ticker: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    exchange: Mapped[Optional[str]] = mapped_column(String(100))
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    news: Mapped[Optional[Any]] = mapped_column(JSONB)
    financials: Mapped[Optional[Any]] = mapped_column(JSONB)
    synthesis: Mapped[Optional[Any]] = mapped_column(JSONB)
    processing_time_seconds: Mapped[Optional[float]] = mapped_column(Float)
    error: Mapped[Optional[str]] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<Report id={self.id} ticker={self.ticker} generated_at={self.generated_at}>"
