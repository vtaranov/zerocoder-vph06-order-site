from datetime import datetime
from sqlalchemy import String, DateTime, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Admin(Base):
    """CREATE TABLE admins (id INTEGER PRIMARY KEY CHECK(id=1),
    username VARCHAR(80) UNIQUE NOT NULL, password_hash VARCHAR(300) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now());"""
    __tablename__ = "admins"
    __table_args__ = (CheckConstraint("id = 1", name="single_bootstrap_admin"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True)
    password_hash: Mapped[str] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
