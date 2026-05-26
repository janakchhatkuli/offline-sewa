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

## Getting Started (for teammates)

### 1. Clone the repo
```powershell
git clone https://github.com/<your-username>/offline-sewa.git
cd offline-sewa
```

### 2. Set up your local environment file
```powershell
cd backend
Copy-Item .env.example .env
```
> `.env` is git-ignored — it never gets pushed. Fill in your own values.
> For local dev the defaults in `.env.example` work as-is.
> Only `SPARROW_API_KEY` needs a real value (Block 3B — SMS, not yet).

### 3. Start the backend + database
```powershell
cd ..   # back to repo root
docker compose up -d
```
Visit <http://localhost:8000/health> — you should see `{"status":"backend_online"}`.
Full API docs: <http://localhost:8000/docs>

### 4. Flutter apps
```powershell
cd frontend\customer_app          # or shopkeeper_app / admin_dashboard
flutter create . --project-name customer_app --platforms=android,ios
flutter pub get
flutter run
```

---

## Daily Git Workflow

> **Never push directly to `main`.** Always branch → code → PR.

```powershell
git pull                              # get latest from main
git checkout -b block-2-database      # one branch per block
# ...make your changes...
git add .
git commit -m "Block 2: add customer model"
git push -u origin block-2-database
# then open a Pull Request on GitHub for review
```

---

## Block-wise Plan

See [docs/WORKFLOW.md](docs/WORKFLOW.md) for the full block-by-block plan.

| Block | Scope | Status |
|------|------|--------|
| 1 | Backend foundation (FastAPI skeleton) | ✅ |
| 2 | Database & SQLAlchemy models | ☐ |
| 3A | Core API endpoints (QR create/verify) | ☐ |
| 3B | SMS integration & settlement | ☐ |
| 4 | Customer Flutter app | ☐ |
| 5 | Shopkeeper Flutter app | ☐ |
| 6 | Admin dashboard | ☐ |
| 7 | Integration testing | ☐ |
| 8 | Deployment | ☐ |
| 9 | Hardware (ESP32) — phase 2 | ☐ |