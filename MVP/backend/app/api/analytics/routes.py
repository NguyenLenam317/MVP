from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from ..database.config import get_db
from ..services.analytics import AnalyticsService
from ..services.export import ExportService
from ..models.user import User
from ..services.auth import get_current_active_user
from pydantic import BaseModel

router = APIRouter(prefix="/analytics", tags=["Analytics"])

class DateRange(BaseModel):
    start_date: datetime
    end_date: datetime

class BrandHealthQuery(BaseModel):
    brand_id: int
    date_range: DateRange

class BrandComparisonQuery(BaseModel):
    brand_ids: List[int]
    metrics: List[str]
    date_range: DateRange

class CustomQuery(BaseModel):
    query: Dict[str, Any]

@router.post("/brand-health")
async def get_brand_health(
    query: BrandHealthQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive brand health metrics."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_brand_health(
        query.brand_id,
        query.date_range.start_date,
        query.date_range.end_date
    )

@router.post("/brand-comparison")
async def compare_brands(
    query: BrandComparisonQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Compare metrics between multiple brands."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.compare_brands(
        query.brand_ids,
        query.metrics,
        query.date_range.start_date,
        query.date_range.end_date
    )

@router.post("/custom-query")
async def custom_query(
    query: CustomQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Execute custom analytics queries."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.custom_query(query.query)

@router.post("/export/brand-data/{brand_id}")
async def export_brand_data(
    brand_id: int,
    date_range: DateRange,
    format: str = "xlsx",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export all data for a brand."""
    export_service = ExportService(db)
    return await export_service.export_brand_data(
        brand_id,
        date_range.start_date,
        date_range.end_date,
        format
    )

@router.post("/export/brand-comparison")
async def export_brand_comparison(
    query: BrandComparisonQuery,
    format: str = "xlsx",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export comparison data between brands."""
    export_service = ExportService(db)
    return await export_service.export_brand_comparison(
        query.brand_ids,
        query.metrics,
        query.date_range.start_date,
        query.date_range.end_date,
        format
    )
