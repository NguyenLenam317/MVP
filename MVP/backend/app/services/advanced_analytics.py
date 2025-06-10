from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.canonical import Brand, TrafficSnapshot, SEOInfo, SocialPost, Review, SentimentResult
from ..services.cache import cache_service
import pandas as pd
import numpy as np
from scipy import stats
import json
from io import BytesIO

class AdvancedAnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.cache_service = cache_service

    def execute_custom_query(
        self,
        query: Dict[str, Any],
        user_id: int
    ) -> Dict[str, Any]:
        """Execute a custom analytics query."""
        cache_key = f"custom_query:{user_id}:{json.dumps(query)}"
        cached = self.cache_service.redis.get(cache_key)
        
        if cached:
            return json.loads(cached)

        # Parse query parameters
        metrics = query.get("metrics", [])
        dimensions = query.get("dimensions", [])
        filters = query.get("filters", {})
        group_by = query.get("group_by", [])
        date_range = query.get("date_range", {})

        # Build base query
        query = self.db.query(Brand)
        
        # Apply filters
        for field, value in filters.items():
            query = query.filter(getattr(Brand, field) == value)
        
        # Get data
        brands = query.all()
        
        # Build DataFrame
        data = []
        for brand in brands:
            brand_data = brand.__dict__
            
            # Get metrics
            metrics_data = {}
            if "traffic" in metrics:
                traffic = self.db.query(TrafficSnapshot).filter(
                    TrafficSnapshot.brand_id == brand.id,
                    TrafficSnapshot.date >= date_range.get("start", datetime.utcnow() - timedelta(days=30)),
                    TrafficSnapshot.date <= date_range.get("end", datetime.utcnow())
                ).all()
                metrics_data["traffic"] = sum(t.visits for t in traffic)
            
            if "engagement" in metrics:
                posts = self.db.query(SocialPost).filter(
                    SocialPost.brand_id == brand.id,
                    SocialPost.timestamp >= date_range.get("start", datetime.utcnow() - timedelta(days=30)),
                    SocialPost.timestamp <= date_range.get("end", datetime.utcnow())
                ).all()
                metrics_data["engagement"] = sum(
                    sum(p.engagement.values()) if isinstance(p.engagement, dict) else 0
                    for p in posts
                )
            
            data.append({
                **brand_data,
                **metrics_data
            })
        
        df = pd.DataFrame(data)
        
        # Group by specified dimensions
        if group_by:
            df = df.groupby(group_by).agg({
                m: "sum" for m in metrics
            }).reset_index()
        
        # Calculate additional metrics
        if "growth_rate" in metrics:
            df["growth_rate"] = df[metrics[0]].pct_change()
        
        if "moving_average" in metrics:
            df["moving_average"] = df[metrics[0]].rolling(window=7).mean()
        
        # Prepare response
        response = {
            "data": df.to_dict(),
            "summary": {
                "total": len(df),
                "metrics": {
                    m: {
                        "mean": df[m].mean(),
                        "median": df[m].median(),
                        "std": df[m].std()
                    }
                    for m in metrics
                }
            }
        }
        
        # Cache result
        self.cache_service.redis.setex(
            cache_key,
            timedelta(hours=1),
            json.dumps(response)
        )
        
        return response

    def get_cohort_analysis(
        self,
        brand_id: int,
        metric: str,
        cohort_size: int = 100,
        periods: int = 12
    ) -> Dict[str, Any]:
        """Perform cohort analysis."""
        # Get data
        posts = self.db.query(SocialPost).filter(
            SocialPost.brand_id == brand_id
        ).all()
        
        # Create DataFrame
        df = pd.DataFrame([p.__dict__ for p in posts])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        # Create cohorts
        df["cohort"] = pd.cut(
            df["timestamp"],
            periods,
            labels=False
        )
        
        # Calculate metrics
        cohort_metrics = {}
        for cohort in df["cohort"].unique():
            cohort_data = df[df["cohort"] == cohort]
            cohort_metrics[cohort] = {
                "size": len(cohort_data),
                "metric_values": cohort_data[metric].tolist()
            }
        
        return {
            "cohorts": cohort_metrics,
            "summary": {
                "total_cohorts": len(cohort_metrics),
                "avg_cohort_size": len(df) / len(cohort_metrics)
            }
        }

    def get_retention_analysis(
        self,
        brand_id: int,
        period: str = "month",
        lookback: int = 12
    ) -> Dict[str, Any]:
        """Perform retention analysis."""
        # Get data
        posts = self.db.query(SocialPost).filter(
            SocialPost.brand_id == brand_id
        ).all()
        
        # Create DataFrame
        df = pd.DataFrame([p.__dict__ for p in posts])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        # Group by period
        if period == "month":
            df["period"] = df["timestamp"].dt.to_period("M")
        elif period == "week":
            df["period"] = df["timestamp"].dt.to_period("W")
        
        # Calculate retention
        retention = {}
        for period in df["period"].unique():
            cohort = df[df["period"] == period]
            retention[str(period)] = {
                "cohort_size": len(cohort),
                "retained": len(df[df["period"] == period + 1])
            }
        
        return {
            "retention": retention,
            "summary": {
                "avg_retention_rate": sum(
                    r["retained"] / r["cohort_size"]
                    for r in retention.values()
                ) / len(retention)
            }
        }

    def get_cross_brand_comparison(
        self,
        brand_ids: List[int],
        metrics: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Compare metrics across brands."""
        data = []
        
        for brand_id in brand_ids:
            brand_data = {}
            
            # Get metrics
            for metric in metrics:
                if metric == "traffic":
                    traffic = self.db.query(TrafficSnapshot).filter(
                        TrafficSnapshot.brand_id == brand_id,
                        TrafficSnapshot.date >= start_date,
                        TrafficSnapshot.date <= end_date
                    ).all()
                    brand_data[metric] = sum(t.visits for t in traffic)
                
                elif metric == "engagement":
                    posts = self.db.query(SocialPost).filter(
                        SocialPost.brand_id == brand_id,
                        SocialPost.timestamp >= start_date,
                        SocialPost.timestamp <= end_date
                    ).all()
                    brand_data[metric] = sum(
                        sum(p.engagement.values()) if isinstance(p.engagement, dict) else 0
                        for p in posts
                    )
            
            # Add brand info
            brand = self.db.query(Brand).filter(Brand.id == brand_id).first()
            brand_data["brand"] = brand.__dict__
            
            data.append(brand_data)
        
        return {
            "brands": data,
            "summary": {
                "total_brands": len(brand_ids),
                "metrics": {
                    m: {
                        "mean": np.mean([d[m] for d in data if m in d]),
                        "std": np.std([d[m] for d in data if m in d])
                    }
                    for m in metrics
                }
            }
        }
