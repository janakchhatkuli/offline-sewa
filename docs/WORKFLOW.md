# Block-by-Block Workflow

Full workflow lives in the team document. This file mirrors the high-level plan.
Update each block's checklist as work progresses.

## Stack adaptation

The original workflow referenced Flask + SQLite. This project uses:

- **FastAPI** in place of Flask (async, auto OpenAPI docs)
- **PostgreSQL + SQLAlchemy 2.x (async) + Alembic** in place of raw SQLite
- **Flutter** in place of vanilla HTML/JS for all three frontends

Endpoint names and responsibilities stay the same; only the implementation tech differs.

## Blocks

### Block 1 — Backend foundation
- FastAPI app boots, `/health` returns `backend_online`
- Config via `pydantic-settings`, logging configured
- Dockerfile + docker-compose work

### Block 2 — Database & models
- Postgres up via docker-compose
- SQLAlchemy models: `Customer`, `Merchant`, `OfflineTransaction`, `NonceLog`
- Alembic initial migration generated & applied

### Block 3A — Core API endpoints
- `POST /api/v1/transactions/create-offline-qr`
- `POST /api/v1/transactions/verify-offline-qr`
- `GET  /api/v1/customers/{id}`
- `GET  /api/v1/merchants/{id}`

### Block 3B — SMS integration
- [x] `POST /api/v1/sms/confirm-payment` (webhook) — parses inbound SMS, identifies merchant by sender phone, verifies QR via `qr_service`, sends confirmation SMS back (Sparrow stub).
- [x] Nonce double-spend prevention reused from Block 3A (same `verify_offline_qr` path).
- [x] `POST /api/v1/merchants/{id}/settle` — moves `pending_settlement` → `settled_balance` and flips all matching `offline_transactions` rows to `settled` atomically.
- [x] Tests: `backend/tests/test_sms.py` (11 cases — parsing, webhook happy/error paths, replay, settlement).

### Block 4 — Customer Flutter app
- Login / pick customer
- Show balances
- Generate offline QR
- Transaction history

### Block 5 — Shopkeeper Flutter app
- Scan QR (camera) + manual entry
- Show SMS payload + copy/share
- Pending vs settled view

### Block 6 — Admin dashboard (Flutter Web)
- Stats cards
- Transactions table with live refresh
- Customer / merchant management

### Block 7 — Integration testing
- Full flow: create → verify → SMS → settle
- Double-spend, insufficient balance, invalid QR

### Block 8 — Deployment
- See `docs/DEPLOYMENT.md`

### Block 9 — Hardware (Phase 2)
- ESP32 + camera + SIM module integration
