from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import require_admin
from ..database import get_db

router = APIRouter(prefix="/services", tags=["services"])


@router.get("/", response_model=List[schemas.ServiceOut])
def list_services(db: Session = Depends(get_db)):
    return db.query(models.Service).filter(models.Service.is_active == True).all()  # noqa: E712


@router.post("/", response_model=schemas.ServiceOut, status_code=201)
def create_service(
    service_in: schemas.ServiceCreate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    service = models.Service(**service_in.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.delete("/{service_id}", status_code=204)
def deactivate_service(
    service_id: int,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    service.is_active = False
    db.commit()
