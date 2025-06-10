from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database.config import get_db
from ..services.visualization import VisualizationService
from ..models.user import User
from ..services.auth import get_current_active_user
from datetime import datetime
from typing import Dict, List, Optional, Any

router = APIRouter(prefix="/visualization", tags=["Visualization"])

@router.get("/time-series/{brand_id}/{metric}")
async def get_time_series(
    brand_id: int,
    metric: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get time series data for a specific metric."""
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    visualization_service = VisualizationService(db)
    return visualization_service.get_time_series_data(
        brand_id,
        metric,
        start_date,
        end_date
    )

@router.get("/top-n/{metric}")
async def get_top_n(
    metric: str,
    n: int = 10,
    filters: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get top N items by a specific metric."""
    visualization_service = VisualizationService(db)
    return visualization_service.get_top_n(metric, n, filters)

@router.get("/distribution/{metric}")
async def get_distribution(
    metric: str,
    bins: int = 10,
    filters: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get distribution data for a metric."""
    visualization_service = VisualizationService(db)
    return visualization_service.get_distribution_data(metric, bins, filters)

@router.get("/chart-image/{chart_type}")
async def get_chart_image(
    chart_type: str,
    data: Dict[str, Any],
    title: str,
    format: str = "png",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate and return a chart image."""
    visualization_service = VisualizationService(db)
    image = visualization_service.generate_chart_image(
        chart_type,
        data,
        title,
        format
    )
    
    return {
        "image": base64.b64encode(image.getvalue()).decode("utf-8"),
        "format": format
    }

@router.get("/dashboard-pptx/{brand_id}")
async def get_dashboard_pptx(
    brand_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate PowerPoint dashboard."""
    visualization_service = VisualizationService(db)
    pptx = visualization_service.generate_dashboard_pptx(
        brand_id,
        start_date,
        end_date
    )
    
    return {
        "pptx": base64.b64encode(pptx.getvalue()).decode("utf-8")
    }
