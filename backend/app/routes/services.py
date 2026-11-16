from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.core.security import require_admin
from app.models.service import Service, ServiceCRUD
from app.schemas import ServiceInput, ServiceOutput

router = APIRouter(prefix="/api", tags=["Услуги"])

@router.get("/services", response_model=list[ServiceOutput])
def services(db: Session = Depends(get_db)):
    return ServiceCRUD.all(db)

@router.post("/admin/services", response_model=ServiceOutput, status_code=201, dependencies=[Depends(require_admin)])
def create_service(data: ServiceInput, db: Session = Depends(get_db)):
    try:
        return ServiceCRUD.create(db, data.model_dump())
    except IntegrityError:
        db.rollback(); raise HTTPException(409, "Услуга с таким названием уже существует")

@router.put("/admin/services/{service_id}", response_model=ServiceOutput, dependencies=[Depends(require_admin)])
def update_service(service_id: int, data: ServiceInput, db: Session = Depends(get_db)):
    item = db.get(Service, service_id)
    if not item: raise HTTPException(404, "Услуга не найдена")
    try: return ServiceCRUD.update(db, item, data.model_dump())
    except IntegrityError:
        db.rollback(); raise HTTPException(409, "Название занято")

@router.delete("/admin/services/{service_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_service(service_id: int, db: Session = Depends(get_db)):
    item = db.get(Service, service_id)
    if not item: raise HTTPException(404, "Услуга не найдена")
    try: ServiceCRUD.delete(db, item)
    except IntegrityError:
        db.rollback(); raise HTTPException(409, "Услуга используется в заявках")
    return Response(status_code=204)
