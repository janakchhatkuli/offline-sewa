# Backend (FastAPI)

## Layout

```
backend/
├── app/
│   ├── api/              Route handlers (versioned)
│   │   └── v1/
│   │       ├── customers.py
│   │       ├── merchants.py
│   │       ├── transactions.py
│   │       ├── sms.py
│   │       └── admin.py
│   ├── core/             Config, security, logging
│   ├── db/               DB session, base, init
│   ├── models/           SQLAlchemy ORM models
│   ├── schemas/          Pydantic request/response models
│   ├── services/         Business logic (payments, settlement, sms)
│   ├── utils/            Helpers (nonce, qr, etc.)
│   └── main.py           FastAPI entrypoint
├── alembic/              DB migrations
├── tests/                Pytest tests
├── requirements.txt
├── Dockerfile
└── .env.example
```

## Development

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Docs: <http://localhost:8000/docs>
