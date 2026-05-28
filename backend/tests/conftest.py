"""Pytest fixtures: in-memory async SQLite DB + httpx client."""
from __future__ import annotations

from decimal import Decimal

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.customer import Customer
from app.models.merchant import Merchant


TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(TEST_DB_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def _override_get_db():
        async with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = _override_get_db
    try:
        async with SessionLocal() as s:
            yield s
    finally:
        app.dependency_overrides.pop(get_db, None)
        await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def seeded(db_session: AsyncSession):
    cust = Customer(
        customer_id="cust_test01",
        name="Test Customer",
        phone="+9779800000001",
        online_balance=Decimal("0.00"),
        offline_balance=Decimal("500.00"),
        is_active=True,
    )
    merch = Merchant(
        merchant_id="merch_test01",
        name="Test Merchant",
        phone="+9779800000002",
        pending_settlement=Decimal("0.00"),
        settled_balance=Decimal("0.00"),
        is_active=True,
    )
    db_session.add_all([cust, merch])
    await db_session.commit()
    return {"customer": cust, "merchant": merch}


def pytest_collection_modifyitems(config, items):
    # auto-mark async test functions
    for item in items:
        if "asyncio" not in item.keywords and item.get_closest_marker("asyncio") is None:
            if item.function.__code__.co_flags & 0x80:  # CO_COROUTINE
                item.add_marker(pytest.mark.asyncio)

