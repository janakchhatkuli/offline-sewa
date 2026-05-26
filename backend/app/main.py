"""FastAPI application entrypoint.

Wire routers, middleware, and startup/shutdown events here.
Implementation lands in Block 1 of the workflow.
"""
from fastapi import FastAPI

from app.core.config import settings
from app.api.v1 import api_router

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "backend_online"}


@app.get("/", tags=["health"])
async def root():
    return {"message": "Offline Sewa Backend", "env": settings.APP_ENV}


app.include_router(api_router, prefix="/api/v1")
