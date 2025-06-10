from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database.config import get_db
from ..services.data_acquisition import DataAcquisitionService
from ..models.user import User
from ..services.auth import get_current_active_user

router = APIRouter(prefix="/data", tags=["Data Acquisition"])

@router.post("/fetch/brand/{brand_id}")
async def fetch_brand_data(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Fetch all data for a specific brand."""
    try:
        data_service = DataAcquisitionService({
            "similarweb_api_key": "your-api-key-here",
            "similarweb_api_host": "similarweb-insights.p.rapidapi.com",
            "instagram_api_key": "your-api-key-here",
            "instagram_api_host": "instagram-premium-api-2023.p.rapidapi.com",
            "facebook_api_key": "your-api-key-here",
            "facebook_api_host": "facebook-scraper3.p.rapidapi.com",
            "nlp_api_key": "your-api-key-here",
            "nlp_api_host": "japerk-text-processing.p.rapidapi.com"
        })
        
        data = data_service.fetch_brand_data(brand_id, db)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/fetch/traffic/{domain}")
async def fetch_traffic(
    domain: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Fetch traffic data for a domain."""
    try:
        data_service = DataAcquisitionService({
            "similarweb_api_key": "your-api-key-here",
            "similarweb_api_host": "similarweb-insights.p.rapidapi.com"
        })
        
        brand = db.query(Brand).filter(Brand.website == domain).first()
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Brand not found"
            )
            
        data = data_service._fetch_traffic(brand)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/fetch/social-posts/{brand_id}")
async def fetch_social_posts(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Fetch social posts for a brand."""
    try:
        data_service = DataAcquisitionService({
            "instagram_api_key": "your-api-key-here",
            "instagram_api_host": "instagram-premium-api-2023.p.rapidapi.com",
            "facebook_api_key": "your-api-key-here",
            "facebook_api_host": "facebook-scraper3.p.rapidapi.com"
        })
        
        posts = data_service._fetch_social_posts(brand_id, db)
        return posts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/fetch/reviews/{brand_id}")
async def fetch_reviews(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Fetch reviews for a brand."""
    try:
        data_service = DataAcquisitionService({
            "instagram_api_key": "your-api-key-here",
            "instagram_api_host": "instagram-premium-api-2023.p.rapidapi.com",
            "facebook_api_key": "your-api-key-here",
            "facebook_api_host": "facebook-scraper3.p.rapidapi.com"
        })
        
        reviews = data_service._fetch_reviews(brand_id, db)
        return reviews
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
