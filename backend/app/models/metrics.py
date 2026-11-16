import uuid
from datetime import datetime, timezone
from sqlalchemy import ForeignKey, JSON, String, DateTime, select, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class BehaviorMetrics(Base):
    """CREATE TABLE behavior_metrics (id SERIAL PRIMARY KEY, session_id VARCHAR(64) UNIQUE NOT NULL,
    application_id INTEGER REFERENCES applications(id) ON DELETE CASCADE,
    time_on_page INTEGER NOT NULL, visits INTEGER NOT NULL, clicks JSON NOT NULL,
    pointer_samples JSON NOT NULL, technical JSON NOT NULL, layout VARCHAR(16) NOT NULL,
    sequence INTEGER NOT NULL DEFAULT 0, started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now());"""
    __tablename__ = "behavior_metrics"
    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(String(64), unique=True, default=lambda:str(uuid.uuid4()))
    application_id: Mapped[int | None] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), nullable=True)
    time_on_page: Mapped[int] = mapped_column(default=0)
    visits: Mapped[int] = mapped_column(default=1)
    clicks: Mapped[list] = mapped_column(JSON, default=list)
    pointer_samples: Mapped[list] = mapped_column(JSON, default=list)
    technical: Mapped[dict] = mapped_column(JSON, default=dict)
    layout: Mapped[str] = mapped_column(String(16), default="application")
    sequence: Mapped[int] = mapped_column(default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class MetricsCRUD:
    @staticmethod
    def get(db, application_id):
        return db.scalar(select(BehaviorMetrics).where(BehaviorMetrics.application_id == application_id))
