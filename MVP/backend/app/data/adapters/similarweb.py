from typing import Dict, Any, Optional
from .base import BaseAdapter
from ..models.core import Brand, SocialPost, Review, PriceSnapshot

class SimilarWebAdapter(BaseAdapter):
    BASE_URL = "https://similarweb-insights.p.rapidapi.com/"
    
    def __init__(self, api_key: str, api_host: str):
        super().__init__(api_key, api_host)
        self.session.headers.update({"Accept": "application/json"})

    def fetch_all_insights(self, domain: str) -> Dict[str, Any]:
        return self._request("GET", self.BASE_URL + "all-insights", params={"domain": domain})

    def fetch_traffic(self, domain: str) -> Dict[str, Any]:
        return self._request("GET", self.BASE_URL + "traffic", params={"domain": domain})

    def fetch_rank(self, domain: str) -> Dict[str, Any]:
        return self._request("GET", self.BASE_URL + "rank", params={"domain": domain})

    def fetch_similar_sites(self, domain: str) -> Dict[str, Any]:
        return self._request("GET", self.BASE_URL + "similar-sites", params={"domain": domain})

    def fetch_seo(self, domain: str) -> Dict[str, Any]:
        return self._request("GET", self.BASE_URL + "seo", params={"domain": domain})

    def fetch_website_details(self, domain: str) -> Dict[str, Any]:
        return self._request("GET", self.BASE_URL + "website-details", params={"domain": domain})

    def normalize_traffic(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize traffic data to canonical model."""
        if not raw_data.get("success"):
            return {}
            
        return {
            "domain": raw_data.get("domain"),
            "visits": raw_data.get("visits", 0),
            "page_views": raw_data.get("pageViewsPerVisit", 0),
            "bounce_rate": raw_data.get("bounceRate", 0),
            "avg_visit_duration": raw_data.get("avgVisitDuration", 0),
            "traffic_sources": raw_data.get("trafficSources", {}),
            "date": raw_data.get("date"),
            "timestamp": int(time.time())
        }

    def normalize_seo(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize SEO data to canonical model."""
        if not raw_data.get("success"):
            return {}
            
        return {
            "domain": raw_data.get("domain"),
            "organic_keywords": raw_data.get("organicKeywords", 0),
            "paid_keywords": raw_data.get("paidKeywords", 0),
            "organic_traffic": raw_data.get("organicTraffic", 0),
            "paid_traffic": raw_data.get("paidTraffic", 0),
            "seo_score": raw_data.get("seoScore", 0),
            "date": raw_data.get("date"),
            "timestamp": int(time.time())
        }
