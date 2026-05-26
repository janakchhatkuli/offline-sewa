"""v1 API aggregator."""
from fastapi import APIRouter

from app.api.v1 import admin, customers, merchants, sms, transactions

api_router = APIRouter()
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(merchants.router, prefix="/merchants", tags=["merchants"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(sms.router, prefix="/sms", tags=["sms"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
