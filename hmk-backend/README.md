# HMK Agency API

A REST API backend for the HMK Agency Flutter app, built with **FastAPI**, **SQLAlchemy**, and **JWT authentication**. Handles user accounts, the services the agency offers, and client bookings — the pieces that make sense to run on a real backend rather than Firebase alone (relational data with relationships between clients, services, and bookings, plus admin-only actions).

## Features

- User registration and login with JWT-based authentication
- Password hashing with bcrypt
- Admin vs. regular user roles
- CRUD for agency services (admin-managed)
- Clients can create bookings and view their own booking history
- Admins can view all bookings and update booking status (pending → confirmed → completed/cancelled)
- Auto-generated interactive API docs (Swagger UI) via FastAPI

## Project Structure

```
hmk-backend/
├── app/
│   ├── main.py          # FastAPI app + router registration
│   ├── database.py      # SQLAlchemy engine/session setup
│   ├── models.py        # ORM models: User, Service, Booking
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── auth.py           # Password hashing, JWT creation/validation
│   └── routers/
│       ├── auth.py       # /auth/register, /auth/login
│       ├── services.py   # /services (list, create, deactivate)
│       └── bookings.py   # /bookings (create, list, update status)
└── requirements.txt
```

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will run at `http://127.0.0.1:8000`. Interactive docs (test every endpoint from the browser) are at `http://127.0.0.1:8000/docs`.

This uses SQLite out of the box (`hmk_agency.db`, created automatically) so there's nothing else to install to try it locally. For production, swap the connection string in `app/database.py` for Postgres.

## Quick test flow (via `/docs` or curl)

1. `POST /auth/register` — create a user
2. `POST /auth/login` — get back a JWT (`access_token`)
3. Click **Authorize** in `/docs` and paste the token (or send `Authorization: Bearer <token>` header)
4. `POST /services` — as an admin, add a service (you'll need to manually set `is_admin=True` on a user row in the DB for your first admin, since there's no UI for that yet)
5. `POST /bookings` — as a regular user, book that service
6. `GET /bookings/me` — see your own bookings

## Connecting this to your Flutter app

In Flutter, call these endpoints with `http` or `dio`:

```dart
final response = await http.post(
  Uri.parse('http://<your-server>/auth/login'),
  body: {'username': email, 'password': password},
);
```

Store the returned `access_token` (e.g., in `flutter_secure_storage`) and send it as a Bearer token on subsequent requests. This can run alongside your existing Firebase setup — for example, keep Firebase for chat/real-time features and use this API for services and bookings, which fit a relational model better.

## Deploying it for real (so it's not just local)

To make this a genuinely live project you can link from your resume/GitHub, deploy it on a free tier:

- **Render** or **Railway** — easiest for FastAPI, free tier available, auto-deploys from GitHub
- Set `HMK_SECRET_KEY` as an environment variable on the host (don't use the default dev key in production)

Once deployed, you'd have a real, working, publicly-testable API — not just a resume line.
