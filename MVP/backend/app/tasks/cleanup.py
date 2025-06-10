from celery import shared_task
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..database.config import get_db
from ..models.canonical import Brand, TrafficSnapshot, SEOInfo, SocialPost, Review, SentimentResult
from ..services.cache import cache_service

@shared_task
async def data_cleanup():
    """Perform regular data cleanup and maintenance."""
    db = next(get_db())
    
    # Calculate cleanup dates
    now = datetime.utcnow()
    old_data_threshold = now - timedelta(days=365)  # Keep data for 1 year
    
    # Delete old raw data (keep normalized data)
    # Note: This assumes you have separate tables for raw and normalized data
    # Here we only clean up old sentiment results as an example
    db.query(SentimentResult).filter(
        SentimentResult.timestamp < old_data_threshold
    ).delete()
    
    # Delete old cache entries
    cache_service.redis.delete(*cache_service.redis.keys("cache:*"))
    
    # Clean up any orphaned records
    orphaned_reviews = db.query(Review).filter(
        Review.brand_id.not_in(db.query(Brand.id))
    ).delete()
    
    orphaned_posts = db.query(SocialPost).filter(
        SocialPost.brand_id.not_in(db.query(Brand.id))
    ).delete()
    
    # Commit changes
    db.commit()
    
    return {
        "status": "success",
        "timestamp": now.isoformat(),
        "actions": {
            "deleted_sentiment_results": orphaned_reviews,
            "deleted_orphaned_reviews": orphaned_reviews,
            "deleted_orphaned_posts": orphaned_posts,
            "cleaned_cache": True
        }
    }
