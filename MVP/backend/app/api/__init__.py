from fastapi import APIRouter
from .auth.routes import router as auth_router
from .data.routes import router as data_router
from .query.routes import router as query_router
from .analytics.routes import router as analytics_router
from .realtime.routes import router as realtime_router
from .visualization.routes import router as visualization_router

router = APIRouter()

# Include auth routes
router.include_router(auth_router)

# Include data routes
router.include_router(data_router)

# Include query routes
router.include_router(query_router)

# Include analytics routes
router.include_router(analytics_router)

# Include real-time routes
router.include_router(realtime_router)

# Include visualization routes
router.include_router(visualization_router)
