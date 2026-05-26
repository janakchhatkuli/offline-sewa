# Offline Sewa

Offline payment system inspired by eSewa — works without internet using QR + SMS confirmation.

## Stack

- **Backend:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL 15+
- **Frontend (Customer & Shopkeeper apps):** Flutter
- **Admin Dashboard:** Flutter Web (shares codebase)
- **SMS Provider:** Sparrow SMS (pluggable)
- **Containerization:** Docker + docker-compose

## Repository Layout

```
offline-sewa/
├── backend/                  FastAPI service
├── frontend/
│   ├── customer_app/         Flutter app (customer)
│   ├── shopkeeper_app/       Flutter app (shopkeeper)
│   └── admin_dashboard/      Flutter web (admin)
├── database/                 SQL migrations & seed data
├── docs/                     Workflow & API docs
├── scripts/                  Dev helper scripts
├── tests/                    Cross-service e2e tests
├── docker-compose.yml
└── README.md
```

## Block-wise Workflow

See [docs/WORKFLOW.md](docs/WORKFLOW.md) for the full block-by-block plan.

| Block | Scope | Status |
|------|------|--------|
| 1 | Backend foundation (FastAPI skeleton) | ☐ |
| 2 | Database & SQLAlchemy models | ☐ |
| 3A | Core API endpoints (QR create/verify) | ☐ |
| 3B | SMS integration & settlement | ☐ |
| 4 | Customer Flutter app | ☐ |
| 5 | Shopkeeper Flutter app | ☐ |
| 6 | Admin dashboard | ☐ |
| 7 | Integration testing | ☐ |
| 8 | Deployment | ☐ |
| 9 | Hardware (ESP32) — phase 2 | ☐ |

## Quick Start

```bash
# 1. Spin up Postgres + backend
docker-compose up -d

# 2. Backend (manual / dev mode)
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# 3. Flutter apps
cd frontend/customer_app
flutter pub get
flutter run
```

API docs: <http://localhost:8000/docs>