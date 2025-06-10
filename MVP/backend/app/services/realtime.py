from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.canonical import Brand, TrafficSnapshot, SocialPost, Review
from ..services.cache import cache_service
import asyncio
from fastapi_sse import sse
import json

class RealtimeAnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.connections = {}
        self.update_interval = 5  # seconds

    async def subscribe_brand_health(
        self,
        brand_id: int,
        client_id: str
    ):
        """Subscribe to real-time brand health updates."""
        if client_id not in self.connections:
            self.connections[client_id] = {
                "brand_id": brand_id,
                "last_update": datetime.utcnow(),
                "queue": asyncio.Queue()
            }

        while True:
            try:
                # Check for new data
                await self._check_for_updates(brand_id)
                
                # Get data from queue
                update = await self.connections[client_id]["queue"].get()
                yield json.dumps(update)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in subscription: {e}")
                break

    async def _check_for_updates(self, brand_id: int):
        """Check for updates and notify subscribers."""
        # Get latest data
        latest_traffic = self.db.query(TrafficSnapshot).filter(
            TrafficSnapshot.brand_id == brand_id
        ).order_by(TrafficSnapshot.date.desc()).first()

        latest_posts = self.db.query(SocialPost).filter(
            SocialPost.brand_id == brand_id
        ).order_by(SocialPost.timestamp.desc()).limit(5).all()

        latest_reviews = self.db.query(Review).filter(
            Review.brand_id == brand_id
        ).order_by(Review.timestamp.desc()).limit(5).all()

        # Create update message
        update = {
            "timestamp": datetime.utcnow().isoformat(),
            "traffic": {
                "visits": latest_traffic.visits if latest_traffic else 0,
                "bounce_rate": latest_traffic.bounce_rate if latest_traffic else 0.0
            },
            "new_posts": [p.__dict__ for p in latest_posts],
            "new_reviews": [r.__dict__ for r in latest_reviews]
        }

        # Notify all subscribers
        for conn in self.connections.values():
            if conn["brand_id"] == brand_id:
                await conn["queue"].put(update)

    async def notify_update(
        self,
        brand_id: int,
        update_type: str,
        data: Dict[str, Any]
    ):
        """Notify all subscribers about a specific update."""
        update = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": update_type,
            "data": data
        }

        # Notify all subscribers
        for conn in self.connections.values():
            if conn["brand_id"] == brand_id:
                await conn["queue"].put(update)

    async def unsubscribe(self, client_id: str):
        """Unsubscribe a client."""
        if client_id in self.connections:
            del self.connections[client_id]

    def get_active_subscriptions(self) -> List[Dict[str, Any]]:
        """Get list of active subscriptions."""
        return [
            {
                "client_id": client_id,
                "brand_id": conn["brand_id"],
                "last_update": conn["last_update"].isoformat()
            }
            for client_id, conn in self.connections.items()
        ]
