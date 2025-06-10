from celery import shared_task
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..database.config import get_db
from ..models.canonical import Brand, TrafficSnapshot, SEOInfo, SocialPost, Review, SentimentResult
from ..services.cache import cache_service
import pandas as pd

@shared_task
async def daily_aggregations():
    """Calculate daily aggregations for all brands."""
    db = next(get_db())
    
    # Get all active brands
    brands = db.query(Brand).all()
    
    for brand in brands:
        await _calculate_brand_aggregations(brand.id, "daily")

@shared_task
async def weekly_aggregations():
    """Calculate weekly aggregations for all brands."""
    db = next(get_db())
    
    # Get all active brands
    brands = db.query(Brand).all()
    
    for brand in brands:
        await _calculate_brand_aggregations(brand.id, "weekly")

@shared_task
async def monthly_aggregations():
    """Calculate monthly aggregations for all brands."""
    db = next(get_db())
    
    # Get all active brands
    brands = db.query(Brand).all()
    
    for brand in brands:
        await _calculate_brand_aggregations(brand.id, "monthly")

async def _calculate_brand_aggregations(brand_id: int, period: str):
    """Calculate aggregations for a specific brand."""
    db = next(get_db())
    
    # Calculate date range based on period
    now = datetime.utcnow()
    if period == "daily":
        start_date = now - timedelta(days=1)
    elif period == "weekly":
        start_date = now - timedelta(weeks=1)
    else:  # monthly
        start_date = now - timedelta(days=30)

    # Calculate traffic metrics
    traffic = db.query(TrafficSnapshot).filter(
        TrafficSnapshot.brand_id == brand_id,
        TrafficSnapshot.date >= start_date
    ).all()
    
    if traffic:
        traffic_df = pd.DataFrame([t.__dict__ for t in traffic])
        traffic_summary = {
            "total_visits": traffic_df["visits"].sum(),
            "total_page_views": traffic_df["page_views"].sum(),
            "avg_bounce_rate": traffic_df["bounce_rate"].mean(),
            "avg_visit_duration": traffic_df["avg_visit_duration"].mean()
        }
    else:
        traffic_summary = {
            "total_visits": 0,
            "total_page_views": 0,
            "avg_bounce_rate": 0.0,
            "avg_visit_duration": 0.0
        }

    # Calculate social metrics
    posts = db.query(SocialPost).filter(
        SocialPost.brand_id == brand_id,
        SocialPost.timestamp >= start_date
    ).all()
    
    if posts:
        posts_df = pd.DataFrame([p.__dict__ for p in posts])
        social_summary = {
            "total_posts": len(posts),
            "avg_engagement": posts_df["engagement"].apply(
                lambda x: sum(x.values()) if isinstance(x, dict) else 0
            ).mean(),
            "avg_sentiment": posts_df["sentiment_score"].mean()
        }
    else:
        social_summary = {
            "total_posts": 0,
            "avg_engagement": 0.0,
            "avg_sentiment": 0.0
        }

    # Calculate review metrics
    reviews = db.query(Review).filter(
        Review.brand_id == brand_id,
        Review.timestamp >= start_date
    ).all()
    
    if reviews:
        reviews_df = pd.DataFrame([r.__dict__ for r in reviews])
        review_summary = {
            "total_reviews": len(reviews),
            "avg_rating": reviews_df["rating"].mean(),
            "avg_sentiment": reviews_df["sentiment_score"].mean()
        }
    else:
        review_summary = {
            "total_reviews": 0,
            "avg_rating": 0.0,
            "avg_sentiment": 0.0
        }

    # Store aggregated data
    aggregated_data = {
        "brand_id": brand_id,
        "period": period,
        "date": now.isoformat(),
        "traffic": traffic_summary,
        "social": social_summary,
        "reviews": review_summary
    }

    # Cache the results
    cache_key = f"aggregated_data:{brand_id}:{period}:{now.date().isoformat()}"
    cache_service.redis.setex(
        cache_key,
        timedelta(days=1),  # Cache for 1 day
        json.dumps(aggregated_data)
    )
