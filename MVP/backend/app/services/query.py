from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from ..models.canonical import (
    Brand, TrafficSnapshot, SEOInfo, SocialPost, Review, SentimentResult
)
from ..models.user import User
from ..services.auth import get_current_active_user

class QueryService:
    def __init__(self, db: Session):
        self.db = db

    def get_brand(self, brand_id: int) -> Optional[Brand]:
        return self.db.query(Brand).filter(Brand.id == brand_id).first()

    def get_brand_by_website(self, website: str) -> Optional[Brand]:
        return self.db.query(Brand).filter(Brand.website == website).first()

    def get_traffic_history(
        self,
        brand_id: int,
        start_date: datetime,
        end_date: datetime,
        page: int = 1,
        page_size: int = 100
    ) -> Dict[str, Any]:
        query = self.db.query(TrafficSnapshot).filter(
            TrafficSnapshot.brand_id == brand_id,
            TrafficSnapshot.date >= start_date,
            TrafficSnapshot.date <= end_date
        ).order_by(desc(TrafficSnapshot.date))

        total = query.count()
        traffic = query.offset((page - 1) * page_size).limit(page_size).all()

        return {
            "data": traffic,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    def get_social_posts(
        self,
        brand_id: int,
        source: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        sentiment: Optional[str] = None,
        page: int = 1,
        page_size: int = 100
    ) -> Dict[str, Any]:
        query = self.db.query(SocialPost).filter(SocialPost.brand_id == brand_id)
        
        if source:
            query = query.filter(SocialPost.source == source)
        if start_date:
            query = query.filter(SocialPost.timestamp >= start_date)
        if end_date:
            query = query.filter(SocialPost.timestamp <= end_date)
        if sentiment:
            query = query.filter(SocialPost.sentiment_label == sentiment)

        total = query.count()
        posts = query.order_by(desc(SocialPost.timestamp))\
            .offset((page - 1) * page_size)\
            .limit(page_size)\
            .all()

        return {
            "data": posts,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    def get_reviews(
        self,
        brand_id: int,
        source: Optional[str] = None,
        rating: Optional[float] = None,
        sentiment: Optional[str] = None,
        page: int = 1,
        page_size: int = 100
    ) -> Dict[str, Any]:
        query = self.db.query(Review).filter(Review.brand_id == brand_id)
        
        if source:
            query = query.filter(Review.source == source)
        if rating:
            query = query.filter(Review.rating >= rating)
        if sentiment:
            query = query.filter(Review.sentiment_label == sentiment)

        total = query.count()
        reviews = query.order_by(desc(Review.timestamp))\
            .offset((page - 1) * page_size)\
            .limit(page_size)\
            .all()

        return {
            "data": reviews,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    def get_seo_history(
        self,
        brand_id: int,
        start_date: datetime,
        end_date: datetime,
        page: int = 1,
        page_size: int = 100
    ) -> Dict[str, Any]:
        query = self.db.query(SeoInfo).filter(
            SeoInfo.brand_id == brand_id,
            SeoInfo.date >= start_date,
            SeoInfo.date <= end_date
        ).order_by(desc(SeoInfo.date))

        total = query.count()
        seo_data = query.offset((page - 1) * page_size).limit(page_size).all()

        return {
            "data": seo_data,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    def get_sentiment_stats(
        self,
        brand_id: int,
        source: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        query = self.db.query(SentimentResult).join(SocialPost).filter(
            SocialPost.brand_id == brand_id
        )
        
        if source:
            query = query.filter(SocialPost.source == source)
        if start_date:
            query = query.filter(SocialPost.timestamp >= start_date)
        if end_date:
            query = query.filter(SocialPost.timestamp <= end_date)

        # Calculate sentiment distribution
        sentiment_dist = query.with_entities(
            SentimentResult.label,
            func.count(SentimentResult.id)
        ).group_by(SentimentResult.label).all()

        # Calculate average sentiment score
        avg_score = query.with_entities(
            func.avg(SentimentResult.score)
        ).scalar()

        return {
            "sentiment_distribution": dict(sentiment_dist),
            "average_sentiment": avg_score or 0.0,
            "total_posts": query.count()
        }
