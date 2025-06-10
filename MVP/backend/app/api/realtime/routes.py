from fastapi import APIRouter, Depends, HTTPException, status, WebSocket
from sqlalchemy.orm import Session
from ..database.config import get_db
from ..services.realtime import RealtimeAnalyticsService
from ..models.user import User
from ..services.auth import get_current_active_user
from datetime import datetime
import json

router = APIRouter(prefix="/realtime", tags=["Real-time Analytics"])

@router.websocket("/brand/{brand_id}/health")
async def brand_health_websocket(
    websocket: WebSocket,
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """WebSocket endpoint for real-time brand health updates."""
    await websocket.accept()
    
    # Generate client ID
    client_id = f"client_{brand_id}_{datetime.utcnow().timestamp()}"
    
    try:
        # Initialize real-time service
        realtime_service = RealtimeAnalyticsService(db)
        
        # Subscribe to updates
        async for update in realtime_service.subscribe_brand_health(brand_id, client_id):
            await websocket.send_text(update)
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Unsubscribe on disconnect
        realtime_service.unsubscribe(client_id)

@router.get("/subscriptions")
async def get_active_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of active real-time subscriptions."""
    realtime_service = RealtimeAnalyticsService(db)
    return realtime_service.get_active_subscriptions()

@router.post("/notify/{brand_id}")
async def notify_update(
    brand_id: int,
    update_type: str,
    data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Notify all subscribers about an update."""
    realtime_service = RealtimeAnalyticsService(db)
    await realtime_service.notify_update(brand_id, update_type, data)
    return {"status": "success"}
