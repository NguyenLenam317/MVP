from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.canonical import Brand, TrafficSnapshot, SEOInfo, SocialPost, Review, SentimentResult
from ..services.cache import cache_service
import pandas as pd

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    @cache_service.cache_response("brand_health", ttl_seconds=3600)
    async def get_brand_health(
        self,
        brand_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get comprehensive brand health metrics over time."""
        # Get traffic data
        traffic = self.db.query(TrafficSnapshot).filter(
            TrafficSnapshot.brand_id == brand_id,
            TrafficSnapshot.date >= start_date,
            TrafficSnapshot.date <= end_date
        ).all()

        # Get social posts
        posts = self.db.query(SocialPost).filter(
            SocialPost.brand_id == brand_id,
            SocialPost.timestamp >= start_date,
            SocialPost.timestamp <= end_date
        ).all()

        # Get reviews
        reviews = self.db.query(Review).filter(
            Review.brand_id == brand_id,
            Review.timestamp >= start_date,
            Review.timestamp <= end_date
        ).all()

        # Create DataFrames
        traffic_df = pd.DataFrame([t.__dict__ for t in traffic])
        posts_df = pd.DataFrame([p.__dict__ for p in posts])
        reviews_df = pd.DataFrame([r.__dict__ for r in reviews])

        # Calculate metrics
        metrics = {
            "traffic": {
                "total_visits": traffic_df["visits"].sum(),
                "total_page_views": traffic_df["page_views"].sum(),
                "avg_bounce_rate": traffic_df["bounce_rate"].mean(),
                "avg_visit_duration": traffic_df["avg_visit_duration"].mean()
            },
            "social": {
                "total_posts": len(posts),
                "avg_engagement": posts_df["engagement"].apply(
                    lambda x: sum(x.values()) if isinstance(x, dict) else 0
                ).mean(),
                "avg_sentiment": posts_df["sentiment_score"].mean()
            },
            "reviews": {
                "total_reviews": len(reviews),
                "avg_rating": reviews_df["rating"].mean(),
                "avg_sentiment": reviews_df["sentiment_score"].mean()
            }
        }

        return {
            "brand_id": brand_id,
            "metrics": metrics,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }

    @cache_service.cache_response("brand_comparison", ttl_seconds=3600)
    async def compare_brands(
        self,
        brand_ids: List[int],
        metrics: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Compare metrics between multiple brands."""
        results = {}
        
        for brand_id in brand_ids:
            brand_metrics = await self.get_brand_health(
                brand_id,
                start_date,
                end_date
            )
            results[brand_id] = brand_metrics["metrics"]

        return {
            "brands": results,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }

    @cache_service.cache_response("custom_analytics", ttl_seconds=3600)
    async def custom_query(
        self,
        query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute custom analytics queries."""
        # TODO: Implement custom query execution
        # This would involve parsing the query and executing the appropriate SQL
        # For now, return a placeholder response
        return {
            "query": query,
            "status": "pending",
            "result": None
        }

    async def get_aggregated_data(
        self,
        brand_id: int,
        period: str,
        date: datetime
    ) -> Dict[str, Any]:
        """Get pre-aggregated data for a brand."""
        cache_key = f"aggregated_data:{brand_id}:{period}:{date.date().isoformat()}"
        cached = cache_service.redis.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
        # If not in cache, calculate and cache
        await _calculate_brand_aggregations(brand_id, period)
        return await self.get_aggregated_data(brand_id, period, date)
