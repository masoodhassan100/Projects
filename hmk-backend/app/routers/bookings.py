from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user, require_admin
from ..database import get_db

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/", response_model=schemas.BookingOut, status_code=201)
def create_booking(
    booking_in: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    service = db.query(models.Service).filter(models.Service.id == booking_in.service_id).first()
    if not service or not service.is_active:
        raise HTTPException(status_code=404, detail="Service not found")

    booking = models.Booking(
        client_id=current_user.id,
        service_id=booking_in.service_id,
        scheduled_date=booking_in.scheduled_date,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/me", response_model=List[schemas.BookingOut])
def my_bookings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Booking).filter(models.Booking.client_id == current_user.id).all()


@router.get("/", response_model=List[schemas.BookingOut])
def all_bookings(
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    return db.query(models.Booking).all()


@router.patch("/{booking_id}/status", response_model=schemas.BookingOut)
def update_booking_status(
    booking_id: int,
    update: schemas.BookingStatusUpdate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    valid_statuses = {"pending", "confirmed", "completed", "cancelled"}
    if update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of {valid_statuses}")

    booking.status = update.status
    db.commit()
    db.refresh(booking)
    return booking
