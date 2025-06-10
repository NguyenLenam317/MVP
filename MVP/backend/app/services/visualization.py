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
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from python_pptx import Presentation
from PIL import Image

class VisualizationService:
    def __init__(self, db: Session):
        self.db = db
        self.cache_service = cache_service

    def get_time_series_data(
        self,
        brand_id: int,
        metric: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get time series data for a metric."""
        cache_key = f"timeseries:{brand_id}:{metric}:{start_date}:{end_date}"
        cached = self.cache_service.redis.get(cache_key)
        
        if cached:
            return json.loads(cached)

        # Get data based on metric type
        if metric == "visits":
            data = self.db.query(TrafficSnapshot).filter(
                TrafficSnapshot.brand_id == brand_id,
                TrafficSnapshot.date >= start_date,
                TrafficSnapshot.date <= end_date
            ).all()
            
            df = pd.DataFrame([d.__dict__ for d in data])
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date")["visits"]
            
        elif metric == "sentiment":
            data = self.db.query(SocialPost).filter(
                SocialPost.brand_id == brand_id,
                SocialPost.timestamp >= start_date,
                SocialPost.timestamp <= end_date
            ).all()
            
            df = pd.DataFrame([d.__dict__ for d in data])
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.set_index("timestamp")["sentiment_score"]
            
        # Calculate rolling mean and standard deviation
        df["rolling_mean"] = df.rolling(window=7).mean()
        df["rolling_std"] = df.rolling(window=7).std()
        
        # Prepare response
        response = {
            "data": df.to_dict(),
            "summary": {
                "mean": df.mean(),
                "median": df.median(),
                "std": df.std(),
                "min": df.min(),
                "max": df.max()
            }
        }
        
        # Cache result
        self.cache_service.redis.setex(
            cache_key,
            timedelta(hours=1),
            json.dumps(response)
        )
        
        return response

    def get_top_n(
        self,
        metric: str,
        n: int = 10,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Get top N items by metric."""
        query = self.db.query(Brand)
        
        if filters:
            for field, value in filters.items():
                query = query.filter(getattr(Brand, field) == value)
        
        # Get latest metrics
        latest_metrics = self.db.query(TrafficSnapshot).filter(
            TrafficSnapshot.date >= datetime.utcnow() - timedelta(days=7)
        ).all()
        
        # Calculate metric scores
        brand_scores = {}
        for metric_data in latest_metrics:
            brand_id = metric_data.brand_id
            if brand_id not in brand_scores:
                brand_scores[brand_id] = 0
            
            if metric == "traffic":
                brand_scores[brand_id] += metric_data.visits
            elif metric == "engagement":
                brand_scores[brand_id] += metric_data.engagement
        
        # Get top N brands
        top_brands = sorted(
            brand_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n]
        
        return {
            "top_brands": [
                {
                    "brand_id": brand_id,
                    "score": score,
                    "brand": self.db.query(Brand).filter(Brand.id == brand_id).first().__dict__
                }
                for brand_id, score in top_brands
            ]
        }

    def get_distribution_data(
        self,
        metric: str,
        bins: int = 10,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Get distribution data for a metric."""
        data = []
        
        if metric == "sentiment":
            posts = self.db.query(SocialPost).all()
            data = [p.sentiment_score for p in posts if p.sentiment_score is not None]
            
        elif metric == "rating":
            reviews = self.db.query(Review).all()
            data = [r.rating for r in reviews if r.rating is not None]
        
        if not data:
            return {"error": "No data available"}
        
        # Calculate distribution stats
        hist, bin_edges = np.histogram(data, bins=bins)
        
        return {
            "histogram": {
                "counts": hist.tolist(),
                "bins": bin_edges.tolist()
            },
            "stats": {
                "mean": np.mean(data),
                "median": np.median(data),
                "std": np.std(data),
                "min": min(data),
                "max": max(data),
                "percentiles": {
                    "25": np.percentile(data, 25),
                    "50": np.percentile(data, 50),
                    "75": np.percentile(data, 75)
                }
            }
        }

    def generate_chart_image(
        self,
        chart_type: str,
        data: Dict[str, Any],
        title: str,
        format: str = "png"
    ) -> BytesIO:
        """Generate chart image."""
        plt.figure(figsize=(10, 6))
        
        if chart_type == "line":
            dates = pd.to_datetime(data["dates"])
            values = data["values"]
            plt.plot(dates, values)
            
        elif chart_type == "bar":
            labels = data["labels"]
            values = data["values"]
            plt.bar(labels, values)
            
        elif chart_type == "histogram":
            values = data["values"]
            plt.hist(values, bins=data.get("bins", 10))
        
        plt.title(title)
        plt.xlabel(data.get("xlabel", ""))
        plt.ylabel(data.get("ylabel", ""))
        
        buffer = BytesIO()
        plt.savefig(buffer, format=format)
        plt.close()
        buffer.seek(0)
        
        return buffer

    def generate_dashboard_pptx(
        self,
        brand_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> BytesIO:
        """Generate PowerPoint presentation."""
        prs = Presentation()
        
        # Add title slide
        title_slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(title_slide_layout)
        title = slide.shapes.title
        subtitle = slide.placeholders[1]
        
        title.text = "Brand Analytics Dashboard"
        subtitle.text = f"{start_date.date()} to {end_date.date()}"
        
        # Add traffic chart
        traffic_data = self.get_time_series_data(
            brand_id,
            "visits",
            start_date,
            end_date
        )
        
        chart_slide = prs.slides.add_slide(prs.slide_layouts[5])
        chart_slide.shapes.title.text = "Traffic Trends"
        
        # Add chart image
        buffer = self.generate_chart_image(
            "line",
            {
                "dates": list(traffic_data["data"].keys()),
                "values": list(traffic_data["data"].values()),
                "xlabel": "Date",
                "ylabel": "Visits"
            },
            "Traffic Trends"
        )
        
        img = Image.open(buffer)
        chart_slide.shapes.add_picture(
            buffer,
            left=100,
            top=200,
            width=img.width,
            height=img.height
        )
        
        buffer = BytesIO()
        prs.save(buffer)
        buffer.seek(0)
        
        return buffer
