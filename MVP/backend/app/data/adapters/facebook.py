from typing import Dict, Any, Optional
from .base import BaseAdapter
from ..models.core import SocialPost, Review

class FacebookAdapter(BaseAdapter):
    BASE_URL = "https://facebook-scraper3.p.rapidapi.com/"

    def __init__(self, api_key: str, api_host: str):
        super().__init__(api_key, api_host)
        self.session.headers.update({"Accept": "application/json"})

    def fetch_page_posts(self, page_id: str) -> Dict[str, Any]:
        return self._request("GET", self.BASE_URL + "page/posts", params={"page_id": page_id})

    def fetch_post_comments(self, post_id: str) -> Dict[str, Any]:
        return self._request("GET", self.BASE_URL + "post/comments", params={"post_id": post_id})

    def fetch_page_reviews(self, page_id: str) -> Dict[str, Any]:
        return self._request("GET", self.BASE_URL + "page/reviews", params={"page_id": page_id})

    def fetch_page_details(self, url: str) -> Dict[str, Any]:
        return self._request("GET", self.BASE_URL + "page/details", params={"url": url})

    def normalize_post(self, raw_post: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Facebook post to canonical SocialPost model."""
        if not raw_post.get("success"):
            return {}
            
        return {
            "id": raw_post.get("id"),
            "content": raw_post.get("message", ""),
            "source": "facebook",
            "engagement": {
                "likes": raw_post.get("likes_count", 0),
                "comments": raw_post.get("comments_count", 0),
                "shares": raw_post.get("shares_count", 0)
            },
            "sentiment_score": None,  # Will be calculated by NLP adapter
            "timestamp": int(time.time()),
            "media_url": raw_post.get("image_url"),
            "author": {
                "id": raw_post.get("author_id"),
                "name": raw_post.get("author_name")
            }
        }

    def normalize_review(self, raw_review: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Facebook review to canonical Review model."""
        if not raw_review.get("success"):
            return {}
            
        return {
            "id": raw_review.get("id"),
            "content": raw_review.get("text", ""),
            "rating": raw_review.get("rating", 0),
            "source": "facebook",
            "sentiment_score": None,  # Will be calculated by NLP adapter
            "timestamp": int(time.time()),
            "author": {
                "id": raw_review.get("author_id"),
                "name": raw_review.get("author_name")
            }
        }
