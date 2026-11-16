from sqlalchemy import Integer, String, CheckConstraint, select
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Service(Base):
    """CREATE TABLE services (id SERIAL PRIMARY KEY, name VARCHAR(120) UNIQUE NOT NULL,
    description VARCHAR(500) NOT NULL, budget_min INTEGER NOT NULL,
    budget_max INTEGER NOT NULL, CHECK(budget_min >= 0 AND budget_max >= budget_min));"""
    __tablename__ = "services"
    __table_args__ = (CheckConstraint("budget_min >= 0 AND budget_max >= budget_min"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    description: Mapped[str] = mapped_column(String(500), default="")
    budget_min: Mapped[int] = mapped_column(Integer)
    budget_max: Mapped[int] = mapped_column(Integer)

class ServiceCRUD:
    @staticmethod
    def all(db):
        return db.scalars(select(Service).order_by(Service.id)).all()

    @staticmethod
    def create(db, data):
        item = Service(**data); db.add(item); db.commit(); return item

    @staticmethod
    def update(db, item, data):
        for key, value in data.items():
            setattr(item, key, value)
        db.commit(); return item

    @staticmethod
    def delete(db, item):
        db.delete(item); db.commit()
