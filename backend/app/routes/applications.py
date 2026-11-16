from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_admin
from app.models.application import Application, ApplicationCRUD
from app.models.service import Service
from app.models.metrics import MetricsCRUD
from app.schemas import ApplicationInput
from app.core.scoring import rank_application

router = APIRouter(prefix="/api", tags=["Заявки"])

@router.post("/applications", status_code=201)
def submit(data: ApplicationInput, db: Session = Depends(get_db)):
    service = db.get(Service, data.service_id)
    if not service: raise HTTPException(422, "Выберите существующую услугу")
    if not service.budget_min <= data.budget <= service.budget_max:
        raise HTTPException(422, "Бюджет вне диапазона выбранной услуги")
    item = ApplicationCRUD.create(db, data.model_dump(exclude={"metrics", "consent"}), data.metrics.model_dump())
    return {"id": item.id, "message": "Заявка отправлена!"}

@router.get("/admin/applications", dependencies=[Depends(require_admin)])
def applications(db: Session = Depends(get_db)):
    items = []
    for item in ApplicationCRUD.all(db):
        service = db.get(Service, item.service_id)
        fields = {c.name:getattr(item,c.name) for c in Application.__table__.columns}
        items.append({**fields, "service_name":service.name, "priority":rank_application(item,service)})
    return sorted(items, key=lambda item:(-item["priority"]["score"], -item["id"]))

@router.get("/admin/applications/{application_id}/metrics", dependencies=[Depends(require_admin)])
def metrics(application_id: int, db: Session = Depends(get_db)):
    item = MetricsCRUD.get(db, application_id)
    if not item: raise HTTPException(404, "Заявка не найдена")
    return item

@router.delete("/admin/applications/{application_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_application(application_id: int, db: Session = Depends(get_db)):
    item = db.get(Application, application_id)
    if not item: raise HTTPException(404, "Заявка не найдена")
    ApplicationCRUD.delete(db, item)
    return Response(status_code=204)
