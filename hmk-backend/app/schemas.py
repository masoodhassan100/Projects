from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


# ---------- Auth ----------

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    is_admin: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Services ----------

class ServiceCreate(BaseModel):
    name: str
    description: str | None = None
    price: float


class ServiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    price: float
    is_active: bool


# ---------- Bookings ----------

class BookingCreate(BaseModel):
    service_id: int
    scheduled_date: datetime


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    service_id: int
    scheduled_date: datetime
    status: str
    created_at: datetime


class BookingStatusUpdate(BaseModel):
    status: str  # confirmed, completed, cancelled
