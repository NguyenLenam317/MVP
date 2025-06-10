from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.canonical import Brand, TrafficSnapshot, SEOInfo, SocialPost, Review, SentimentResult
from ..services.cache import cache_service
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import base64
import json
import os

class PDFExportService:
    def __init__(self, db: Session):
        self.db = db
        self.styles = getSampleStyleSheet()

    def _create_brand_header(self, brand: Brand, buffer):
        """Create PDF header with brand information."""
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Add company logo if available
        if brand.logo_url:
            try:
                logo_data = base64.b64decode(brand.logo_url.split(",")[-1])
                c.drawImage(
                    BytesIO(logo_data),
                    width - 100,
                    height - 50,
                    width=80,
                    height=40
                )
            except:
                pass

        # Add title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Brand Analytics Report")

        # Add brand info
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 70, f"Brand: {brand.name}")
        if brand.website:
            c.drawString(50, height - 90, f"Website: {brand.website}")

        # Add timestamp
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 110, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

        c.showPage()
        return c

    def _create_metrics_table(self, c, metrics, y_position):
        """Create a table for metrics."""
        data = [["Metric", "Value"]]
        for key, value in metrics.items():
            data.append([key.replace("_", " ").title(), str(value)])

        table = Table(data, colWidths=[200, 300])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 10),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 1, colors.black)
        ]))

        table.wrapOn(c, 400, 100)
        table.drawOn(c, 50, y_position)

    def _create_chart(self, c, data, title, y_position):
        """Create a simple chart."""
        # TODO: Implement actual chart generation
        # For now, just add placeholder
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, title)
        c.setFont("Helvetica", 10)
        c.drawString(50, y_position - 20, "(Chart will be generated here)")

    def generate_brand_report(
        self,
        brand_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> BytesIO:
        """Generate a comprehensive PDF report for a brand."""
        buffer = BytesIO()
        
        # Get brand data
        brand = self.db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            raise ValueError("Brand not found")

        # Get metrics
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

        # Create PDF
        c = self._create_brand_header(brand, buffer)
        
        # Add traffic metrics
        if traffic:
            traffic_metrics = {
                "Total Visits": sum(t.visits for t in traffic),
                "Average Bounce Rate": sum(t.bounce_rate for t in traffic) / len(traffic),
                "Total Page Views": sum(t.page_views for t in traffic)
            }
            self._create_metrics_table(c, traffic_metrics, 700)

        # Add social metrics
        if posts:
            social_metrics = {
                "Total Posts": len(posts),
                "Average Engagement": sum(
                    sum(p.engagement.values()) if isinstance(p.engagement, dict) else 0
                    for p in posts
                ) / len(posts)
            }
            self._create_metrics_table(c, social_metrics, 500)

        # Add review metrics
        if reviews:
            review_metrics = {
                "Total Reviews": len(reviews),
                "Average Rating": sum(r.rating for r in reviews) / len(reviews)
            }
            self._create_metrics_table(c, review_metrics, 300)

        # Add charts
        self._create_chart(c, {}, "Traffic Trend", 100)
        self._create_chart(c, {}, "Sentiment Analysis", 50)

        c.save()
        buffer.seek(0)
        return buffer

    def generate_comparison_report(
        self,
        brand_ids: List[int],
        metrics: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> BytesIO:
        """Generate a comparison report between brands."""
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Add title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Brand Comparison Report")

        # Add timestamp
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 70, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

        # Get brand data
        brands = self.db.query(Brand).filter(Brand.id.in_(brand_ids)).all()

        # Create comparison table
        data = [["Brand"] + metrics]
        for brand in brands:
            row = [brand.name]
            for metric in metrics:
                # TODO: Implement actual metric calculation
                row.append("N/A")
            data.append(row)

        table = Table(data, colWidths=[150] + [100] * len(metrics))
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 1, colors.black)
        ]))

        table.wrapOn(c, 400, 100)
        table.drawOn(c, 50, 500)

        # Add charts
        self._create_chart(c, {}, "Metric Comparison", 300)

        c.save()
        buffer.seek(0)
        return buffer
