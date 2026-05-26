# Architecture

```
┌────────────────┐   QR (offline)   ┌────────────────┐
│ Customer App   │ ───────────────▶ │ Shopkeeper App │
│ (Flutter)      │                  │ (Flutter)      │
└────────────────┘                  └───────┬────────┘
                                            │ SMS (cellular fallback)
                                            ▼
                                   ┌────────────────────┐
                                   │ SMS Provider       │
                                   │ (Sparrow webhook)  │
                                   └────────┬───────────┘
                                            │ HTTPS
                                            ▼
                                   ┌────────────────────┐
                                   │ FastAPI Backend    │
                                   │  - QR service      │
                                   │  - Payment service │
                                   │  - Settlement      │
                                   └────────┬───────────┘
                                            │ async SQLAlchemy
                                            ▼
                                   ┌────────────────────┐
                                   │ PostgreSQL         │
                                   └────────────────────┘
                                            ▲
                                            │
                                   ┌────────┴───────────┐
                                   │ Admin Dashboard    │
                                   │ (Flutter Web)      │
                                   └────────────────────┘
```
