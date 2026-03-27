"""
Data Endpoints - Business data queries

These endpoints are called by the LangGraph workflow (via RAG routing),
and can also be called directly by the frontend.
"""

from fastapi import APIRouter, Depends, Query
from app.services.auth import get_current_user
from app.services.data_service import DataService

router = APIRouter()


@router.get("/system/overview")
async def system_overview(user=Depends(get_current_user)):
    """System-wide overview: total users, active users, total funds, etc."""
    svc = DataService()
    return await svc.get_system_overview()


@router.get("/products/expiring")
async def expiring_products(
    date: str = Query(None, description="Date string, e.g. 'today', 'tomorrow', '2025-12-01'"),
    user=Depends(get_current_user),
):
    """Products expiring on or near the specified date."""
    svc = DataService()
    return await svc.get_expiring_products(date)


@router.get("/products/stats")
async def product_stats(
    start_date: str = Query(None),
    end_date: str = Query(None),
    user=Depends(get_current_user),
):
    """Product statistics for a date range."""
    svc = DataService()
    return await svc.get_product_stats(start_date, end_date)


@router.get("/finance/summary")
async def finance_summary(
    period: str = Query("daily", description="daily / weekly / monthly"),
    user=Depends(get_current_user),
):
    """Financial summary: income, expenses, profit."""
    svc = DataService()
    return await svc.get_finance_summary(period)


@router.get("/users/stats")
async def user_stats(user=Depends(get_current_user)):
    """User statistics: registrations, active, retention."""
    svc = DataService()
    return await svc.get_user_stats()
