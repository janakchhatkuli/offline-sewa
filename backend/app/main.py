"""FastAPI application entrypoint.

Wire routers, middleware, and startup/shutdown events here.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1 import api_router
from app.db.base import Base
from app.db.session import engine
from app import models  # noqa: F401  ensure model metadata is registered

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.APP_ENV == "development" else [],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def _dev_create_tables() -> None:
    if settings.APP_ENV == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "backend_online"}


@app.get("/", tags=["health"])
async def root():
    return {"message": "Offline Sewa Backend", "env": settings.APP_ENV}


app.include_router(api_router, prefix="/api/v1")
