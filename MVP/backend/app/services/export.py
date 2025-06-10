from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.canonical import Brand, TrafficSnapshot, SEOInfo, SocialPost, Review, SentimentResult
from ..services.cache import cache_service
import pandas as pd
import io
import magic
from fastapi.responses import StreamingResponse

class ExportService:
    def __init__(self, db: Session):
        self.db = db

    async def export_brand_data(
        self,
        brand_id: int,
        start_date: datetime,
        end_date: datetime,
        format: str = "csv"
    ) -> StreamingResponse:
        """Export all data for a brand in specified format."""
        # Get all data
        traffic = self.db.query(TrafficSnapshot).filter(
            TrafficSnapshot.brand_id == brand_id,
            TrafficSnapshot.date >= start_date,
            TrafficSnapshot.date <= end_date
        ).all()

        posts = self.db.query(SocialPost).filter(
            SocialPost.brand_id == brand_id,
            SocialPost.timestamp >= start_date,
            SocialPost.timestamp <= end_date
        ).all()

        reviews = self.db.query(Review).filter(
            Review.brand_id == brand_id,
            Review.timestamp >= start_date,
            Review.timestamp <= end_date
        ).all()

        # Create DataFrames
        traffic_df = pd.DataFrame([t.__dict__ for t in traffic])
        posts_df = pd.DataFrame([p.__dict__ for p in posts])
        reviews_df = pd.DataFrame([r.__dict__ for r in reviews])

        # Create Excel writer
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            traffic_df.to_excel(writer, sheet_name='Traffic', index=False)
            posts_df.to_excel(writer, sheet_name='Social Posts', index=False)
            reviews_df.to_excel(writer, sheet_name='Reviews', index=False)

        output.seek(0)

        # Create response
        media_type = magic.from_buffer(output.getvalue(), mime=True)
        filename = f"brand_data_{brand_id}_{start_date.date()}_{end_date.date()}.xlsx"

        return StreamingResponse(
            output,
            media_type=media_type,
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )

    async def export_brand_comparison(
        self,
        brand_ids: List[int],
        metrics: List[str],
        start_date: datetime,
        end_date: datetime,
        format: str = "csv"
    ) -> StreamingResponse:
        """Export comparison data between brands."""
        # Get comparison data
        analytics_service = AnalyticsService(self.db)
        comparison_data = await analytics_service.compare_brands(
            brand_ids,
            metrics,
            start_date,
            end_date
        )

        # Create DataFrame
        df = pd.DataFrame(comparison_data["brands"]).T

        # Create Excel writer
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Brand Comparison', index=True)

        output.seek(0)

        # Create response
        media_type = magic.from_buffer(output.getvalue(), mime=True)
        filename = f"brand_comparison_{start_date.date()}_{end_date.date()}.xlsx"

        return StreamingResponse(
            output,
            media_type=media_type,
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )

    async def export_custom_query(
        self,
        query: Dict[str, Any],
        format: str = "csv"
    ) -> StreamingResponse:
        """Export results of a custom query."""
        # TODO: Implement custom query export
        # This would involve executing the query and exporting the results
        raise NotImplementedError("Custom query export not implemented yet")
