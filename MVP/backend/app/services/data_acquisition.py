from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.core import Brand, SocialPost, Review
from ..data.adapters.base import BaseAdapter
from ..data.adapters.similarweb import SimilarWebAdapter
from ..data.adapters.instagram import InstagramAdapter
from ..data.adapters.facebook import FacebookAdapter
from ..data.adapters.nlp import JaperkNLPAdapter
from ..database.config import get_db
from ..models.audit import AuditLog

class DataAcquisitionService:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.adapters = {
            "similarweb": SimilarWebAdapter(
                config["similarweb_api_key"],
                config["similarweb_api_host"]
            ),
            "instagram": InstagramAdapter(
                config["instagram_api_key"],
                config["instagram_api_host"]
            ),
            "facebook": FacebookAdapter(
                config["facebook_api_key"],
                config["facebook_api_host"]
            ),
            "nlp": JaperkNLPAdapter(
                config["nlp_api_key"],
                config["nlp_api_host"]
            )
        }

    def fetch_brand_data(self, brand_id: int, db: Session) -> Dict[str, Any]:
        """Fetch all data for a brand from all sources."""
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            raise ValueError(f"Brand {brand_id} not found")

        data = {
            "traffic": self._fetch_traffic(brand),
            "social_posts": self._fetch_social_posts(brand),
            "reviews": self._fetch_reviews(brand)
        }

        return data

    def _fetch_traffic(self, brand: Brand) -> Dict[str, Any]:
        """Fetch traffic data using SimilarWeb."""
        try:
            adapter = self.adapters["similarweb"]
            raw_data = adapter.fetch_traffic(brand.website)
            normalized = adapter.normalize_traffic(raw_data)
            
            # Log the fetch
            self._log_fetch(
                "traffic_fetch",
                {"brand_id": brand.id, "website": brand.website}
            )
            
            return normalized
        except Exception as e:
            self._log_error(
                "traffic_fetch_error",
                {"brand_id": brand.id, "error": str(e)}
            )
            raise

    def _fetch_social_posts(self, brand: Brand) -> List[Dict[str, Any]]:
        """Fetch social posts from Instagram and Facebook."""
        posts = []
        
        # Instagram posts
        if brand.instagram_username:
            try:
                adapter = self.adapters["instagram"]
                user_data = adapter.fetch_user_by_username(brand.instagram_username)
                if user_data.get("success"):
                    posts.extend(
                        adapter.normalize_post(p)
                        for p in adapter.fetch_user_medias(user_data["id"]).get("data", [])
                    )
            except Exception as e:
                self._log_error(
                    "instagram_fetch_error",
                    {"brand_id": brand.id, "error": str(e)}
                )

        # Facebook posts
        if brand.facebook_page_id:
            try:
                adapter = self.adapters["facebook"]
                posts.extend(
                    adapter.normalize_post(p)
                    for p in adapter.fetch_page_posts(brand.facebook_page_id).get("data", [])
                )
            except Exception as e:
                self._log_error(
                    "facebook_fetch_error",
                    {"brand_id": brand.id, "error": str(e)}
                )

        return posts

    def _fetch_reviews(self, brand: Brand) -> List[Dict[str, Any]]:
        """Fetch reviews from social media."""
        reviews = []
        
        # Instagram comments
        if brand.instagram_username:
            try:
                adapter = self.adapters["instagram"]
                user_data = adapter.fetch_user_by_username(brand.instagram_username)
                if user_data.get("success"):
                    posts = adapter.fetch_user_medias(user_data["id"]).get("data", [])
                    for post in posts:
                        reviews.extend(
                            adapter.normalize_comment(c)
                            for c in adapter.fetch_media_comments(post["id"]).get("data", [])
                        )
            except Exception as e:
                self._log_error(
                    "instagram_reviews_error",
                    {"brand_id": brand.id, "error": str(e)}
                )

        # Facebook reviews
        if brand.facebook_page_id:
            try:
                adapter = self.adapters["facebook"]
                reviews.extend(
                    adapter.normalize_review(r)
                    for r in adapter.fetch_page_reviews(brand.facebook_page_id).get("data", [])
                )
            except Exception as e:
                self._log_error(
                    "facebook_reviews_error",
                    {"brand_id": brand.id, "error": str(e)}
                )

        return reviews

    def _log_fetch(self, action: str, details: Dict[str, Any]):
        """Log successful data fetch."""
        db = next(get_db())
        try:
            audit_log = AuditLog(
                action=action,
                details=details,
                ip_address="127.0.0.1",
                user_agent="Data Acquisition Service"
            )
            db.add(audit_log)
            db.commit()
        except Exception as e:
            print(f"Failed to log fetch: {e}")
            db.rollback()

    def _log_error(self, action: str, details: Dict[str, Any]):
        """Log data fetch error."""
        db = next(get_db())
        try:
            audit_log = AuditLog(
                action=action,
                details=details,
                ip_address="127.0.0.1",
                user_agent="Data Acquisition Service"
            )
            db.add(audit_log)
            db.commit()
        except Exception as e:
            print(f"Failed to log error: {e}")
            db.rollback()
