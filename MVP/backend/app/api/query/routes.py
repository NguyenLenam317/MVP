from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..database.config import get_db
from ..services.query import QueryService
from ..models.user import User
from ..services.auth import get_current_active_user
from pydantic import BaseModel

router = APIRouter(prefix="/query", tags=["Data Query"])

class DateRange(BaseModel):
    start_date: datetime
    end_date: datetime

class Pagination(BaseModel):
    page: int = 1
    page_size: int = 100

class SentimentFilter(BaseModel):
    sentiment: Optional[str] = None

class RatingFilter(BaseModel):
    rating: Optional[float] = None

class SourceFilter(BaseModel):
    source: Optional[str] = None

@router.get("/brand/{brand_id}")
async def get_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get brand details."""
    query_service = QueryService(db)
    brand = query_service.get_brand(brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found"
        )
    return brand

@router.get("/brand/website/{website}")
async def get_brand_by_website(
    website: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get brand by website."""
    query_service = QueryService(db)
    brand = query_service.get_brand_by_website(website)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found"
        )
    return brand

@router.post("/traffic/{brand_id}")
async def get_traffic_history(
    brand_id: int,
    date_range: DateRange,
    pagination: Pagination = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get traffic history with date range and pagination."""
    query_service = QueryService(db)
    return query_service.get_traffic_history(
        brand_id,
        date_range.start_date,
        date_range.end_date,
        pagination.page,
        pagination.page_size
    )

@router.post("/social-posts/{brand_id}")
async def get_social_posts(
    brand_id: int,
    date_range: DateRange = None,
    source_filter: SourceFilter = None,
    sentiment_filter: SentimentFilter = None,
    pagination: Pagination = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get social posts with filtering and pagination."""
    query_service = QueryService(db)
    return query_service.get_social_posts(
        brand_id,
        source_filter.source if source_filter else None,
        date_range.start_date if date_range else None,
        date_range.end_date if date_range else None,
        sentiment_filter.sentiment if sentiment_filter else None,
        pagination.page,
        pagination.page_size
    )

@router.post("/reviews/{brand_id}")
async def get_reviews(
    brand_id: int,
    source_filter: SourceFilter = None,
    rating_filter: RatingFilter = None,
    sentiment_filter: SentimentFilter = None,
    pagination: Pagination = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get reviews with filtering and pagination."""
    query_service = QueryService(db)
    return query_service.get_reviews(
        brand_id,
        source_filter.source if source_filter else None,
        rating_filter.rating if rating_filter else None,
        sentiment_filter.sentiment if sentiment_filter else None,
        pagination.page,
        pagination.page_size
    )

@router.post("/seo/{brand_id}")
async def get_seo_history(
    brand_id: int,
    date_range: DateRange,
    pagination: Pagination = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get SEO history with date range and pagination."""
    query_service = QueryService(db)
    return query_service.get_seo_history(
        brand_id,
        date_range.start_date,
        date_range.end_date,
        pagination.page,
        pagination.page_size
    )

@router.post("/sentiment/{brand_id}")
async def get_sentiment_stats(
    brand_id: int,
    date_range: DateRange = None,
    source_filter: SourceFilter = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get sentiment statistics."""
    query_service = QueryService(db)
    return query_service.get_sentiment_stats(
        brand_id,
        source_filter.source if source_filter else None,
        date_range.start_date if date_range else None,
        date_range.end_date if date_range else None
    )
