from fastapi import APIRouter
from app.api.v1.endpoints import track, upload, stats, cameras

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(upload.router, prefix="/upload", tags=["Upload"])
api_router.include_router(track.router, prefix="/track", tags=["Track"])
api_router.include_router(stats.router, prefix="/stats", tags=["Statistics"])
api_router.include_router(cameras.router, prefix="/cameras", tags=["Cameras"])
