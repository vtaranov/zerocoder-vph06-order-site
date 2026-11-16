from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from uuid import UUID
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.core.security import require_admin
from app.models.metrics import BehaviorMetrics

router = APIRouter(prefix="/api", tags=["Метрики"])
class Tick(BaseModel):
    session_id: UUID
    sequence: int = Field(ge=1, le=1000000)
    time_on_page: int = Field(ge=0, le=604800)
    visits: int = Field(default=1, ge=1, le=1000000)
    clicks: list[str] = Field(default_factory=list, max_length=30)
    pointer_samples: list[tuple[int,int]] = Field(default_factory=list, max_length=2)
    layout: str = Field(pattern="^(desktop|mobile)$")
    @field_validator("clicks")
    @classmethod
    def bounded_clicks(cls, values):
        if any(len(v) > 80 for v in values): raise ValueError("Слишком длинная метка")
        return values
    @field_validator("pointer_samples")
    @classmethod
    def normalized_points(cls, points):
        if any(not (0 <= x <= 1000 and 0 <= y <= 1000) for x,y in points):
            raise ValueError("Координаты должны быть в пределах 0-1000")
        return points

@router.post("/behavior-metrics")
def tick(data: Tick, db: Session = Depends(get_db)):
    session_id = str(data.session_id)
    row = db.scalar(select(BehaviorMetrics).where(BehaviorMetrics.session_id == session_id).with_for_update())
    if row is None:
        row = BehaviorMetrics(session_id=session_id, layout=data.layout, time_on_page=0, visits=data.visits, clicks=[], pointer_samples=[], technical={}, sequence=0)
        db.add(row)
        try: db.flush()
        except IntegrityError:
            db.rollback()
            row = db.scalar(select(BehaviorMetrics).where(BehaviorMetrics.session_id == session_id).with_for_update())
    if data.sequence > row.sequence:
        row.time_on_page = max(row.time_on_page, data.time_on_page)
        row.visits = data.visits
        row.clicks = (row.clicks + data.clicks)[-1000:]
        row.pointer_samples = (row.pointer_samples + [list(p) for p in data.pointer_samples])[-3600:]
        row.sequence = data.sequence
        row.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"accepted":True, "sequence":row.sequence}

@router.get("/admin/statistics", dependencies=[Depends(require_admin)])
def statistics(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    today = now.astimezone(ZoneInfo("Europe/Moscow")).replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)
    periods = {"day":today, "week":now-timedelta(days=7), "month":now-timedelta(days=30)}
    results = {}
    for name,start in periods.items():
        count,avg,maximum = db.execute(select(func.count(),func.avg(BehaviorMetrics.time_on_page),func.max(BehaviorMetrics.time_on_page)).where(BehaviorMetrics.layout.in_(["desktop","mobile","legacy"]),BehaviorMetrics.started_at >= start)).one()
        results[name] = {"sessions":count, "average_seconds":round(float(avg or 0),1), "max_seconds":maximum or 0}
    rows = db.scalars(select(BehaviorMetrics).where(BehaviorMetrics.started_at >= periods["month"],BehaviorMetrics.layout.in_(["desktop","mobile"]))).all()
    heatmap = {"desktop":{},"mobile":{}}
    clicks = {}
    for row in rows:
        for point in row.pointer_samples:
            x,y=point
            cell=(min(19,x//50),min(29,y//34))
            heatmap[row.layout][cell] = heatmap[row.layout].get(cell,0)+1
        for key in row.clicks: clicks[key]=clicks.get(key,0)+1
    return {"periods":results,"timezone":"Europe/Moscow", "heatmap":{layout:[{"x":x*50+25,"y":y*34+17,"count":count} for (x,y),count in bins.items()] for layout,bins in heatmap.items()},"clicks":sorted([{"label":k,"count":v} for k,v in clicks.items()],key=lambda v:-v["count"])[:20],"samples":sum(len(r.pointer_samples) for r in rows)}
