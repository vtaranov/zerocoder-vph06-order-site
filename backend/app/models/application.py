from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, DateTime, func, select
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Application(Base):
    """CREATE TABLE applications (id SERIAL PRIMARY KEY, service_id INTEGER NOT NULL REFERENCES services(id),
    name VARCHAR(120) NOT NULL, contact VARCHAR(200) NOT NULL, business VARCHAR(300) NOT NULL,
    company_size VARCHAR(80) NOT NULL, role VARCHAR(80) NOT NULL, task_scope VARCHAR(500) NOT NULL,
    deadline VARCHAR(100) NOT NULL, budget INTEGER NOT NULL, contact_method VARCHAR(80) NOT NULL,
    contact_time VARCHAR(100) NOT NULL, comment TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now());"""
    __tablename__ = "applications"
    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="RESTRICT"))
    name: Mapped[str] = mapped_column(String(120))
    contact: Mapped[str] = mapped_column(String(200))
    business: Mapped[str] = mapped_column(String(300), default="")
    company_size: Mapped[str] = mapped_column(String(80), default="")
    role: Mapped[str] = mapped_column(String(80), default="")
    task_scope: Mapped[str] = mapped_column(String(500), default="")
    deadline: Mapped[str] = mapped_column(String(100), default="")
    budget: Mapped[int]
    contact_method: Mapped[str] = mapped_column(String(80))
    contact_time: Mapped[str] = mapped_column(String(100), default="")
    comment: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class ApplicationCRUD:
    @staticmethod
    def all(db):
        return db.scalars(select(Application).order_by(Application.id.desc())).all()

    @staticmethod
    def create(db, data, metrics):
        from app.models.metrics import BehaviorMetrics
        item = Application(**data)
        db.add(item); db.flush()
        db.add(BehaviorMetrics(application_id=item.id, **metrics))
        db.commit(); return item

    @staticmethod
    def delete(db, item):
        db.delete(item); db.commit()
