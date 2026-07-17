from fastapi import FastAPI

from . import models
from .database import Base, engine
from .routers import auth, bookings, services

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HMK Agency API",
    description="Backend API for the HMK Agency mobile app — manages users, services, and bookings.",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(services.router)
app.include_router(bookings.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "HMK Agency API"}
