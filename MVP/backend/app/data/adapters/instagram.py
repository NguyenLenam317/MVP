from typing import Dict, Any, Optional
from .base import BaseAdapter
from ..models.core import SocialPost, Review

class InstagramAdapter(BaseAdapter):
    BASE_URL = "https://instagram-premium-api-2023.p.rapidapi.com/v2/"

    def __init__(self, api_key: str, api_host: str):
        super().__init__(api_key, api_host)
        self.session.headers.update({"Accept": "application/json"})

    def fetch_user_by_username(self, username: str) -> Dict[str, Any]:
        return self._request("GET", self.BASE_URL + "user/by/username", params={"username": username})

    def fetch_user_medias(self, user_id: str) -> Dict[str, Any]:
        return self._request("GET", self.BASE_URL + "user/medias", params={"user_id": user_id})

    def fetch_media_comments(self, page_id: str, can_support_threading: bool) -> Dict[str, Any]:
        return self._request(
            "GET", self.BASE_URL + "media/comments",
            params={"page_id": page_id, "can_support_threading": str(can_support_threading).lower()}
        )

    def fetch_user_followers(self, user_id: str) -> Dict[str, Any]:
        return self._request("GET", self.BASE_URL + "user/followers", params={"user_id": user_id})

    def fetch_search_hashtags(self, query: str) -> Dict[str, Any]:
        return self._request("GET", self.BASE_URL + "search/hashtags", params={"query": query})

    def normalize_post(self, raw_post: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Instagram post to canonical SocialPost model."""
        if not raw_post.get("success"):
            return {}
            
        return {
            "id": raw_post.get("id"),
            "content": raw_post.get("caption", ""),
            "source": "instagram",
            "engagement": {
                "likes": raw_post.get("likes_count", 0),
                "comments": raw_post.get("comments_count", 0),
                "shares": 0
            },
            "sentiment_score": None,  # Will be calculated by NLP adapter
            "timestamp": int(time.time()),
            "media_url": raw_post.get("display_url"),
            "author": {
                "id": raw_post.get("owner", {}).get("id"),
                "username": raw_post.get("owner", {}).get("username")
            }
        }

    def normalize_comment(self, raw_comment: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Instagram comment to canonical Review model."""
        if not raw_comment.get("success"):
            return {}
            
        return {
            "id": raw_comment.get("id"),
            "content": raw_comment.get("text", ""),
            "source": "instagram",
            "sentiment_score": None,  # Will be calculated by NLP adapter
            "timestamp": int(time.time()),
            "author": {
                "id": raw_comment.get("owner", {}).get("id"),
                "username": raw_comment.get("owner", {}).get("username")
            },
            "post_id": raw_comment.get("media_id")
        }
