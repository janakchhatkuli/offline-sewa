# Database

PostgreSQL 15. Schema is owned by Alembic migrations in `backend/alembic/versions/`.
This folder holds raw SQL helpers and seed data.

```
database/
├── migrations/   Raw .sql files auto-loaded by docker-entrypoint on first boot
├── seeds/        Seed data for dev/test
└── README.md
```
