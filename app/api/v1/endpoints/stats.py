from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel

from app.db.database import get_database
from app.schemas.stats import (
    HourlyCount, 
    DailyCount, 
    ConveyorStats, 
    CameraStats, 
    StatsResponse, 
    StatsTimeRange
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/hourly", response_model=List[HourlyCount])
async def get_hourly_stats(
    conveyor_id: Optional[str] = Query(None, description="Filter by conveyor ID"),
    camera_id: Optional[str] = Query(None, description="Filter by camera ID"),
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    db = Depends(get_database)
):
    """
    Get hourly object counts for specified conveyor belt and/or camera.
    If date is not provided, returns data for the current day.
    """
    # Set default date to today if not provided
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Parse date string to datetime
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Create date range for the given day
    start_date = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Build query
    query = {
        "status": "completed",
        "completed_at": {"$gte": start_date, "$lte": end_date}
    }
    
    if conveyor_id:
        query["conveyor_id"] = conveyor_id
    
    if camera_id:
        query["camera_id"] = camera_id
    
    # Aggregate results by hour
    pipeline = [
        {"$match": query},
        {"$addFields": {
            "hour": {"$hour": "$completed_at"}
        }},
        {"$group": {
            "_id": {
                "hour": "$hour",
                "conveyor_id": "$conveyor_id",
                "camera_id": "$camera_id"
            },
            "count": {"$sum": "$results.object_count"},
            "jobs": {"$sum": 1}
        }},
        {"$sort": {"_id.hour": 1}}
    ]
    
    results = await db.tracking_jobs.aggregate(pipeline).to_list(length=24)
    
    # Format results
    hourly_counts = []
    for result in results:
        hourly_counts.append(HourlyCount(
            hour=result["_id"]["hour"],
            conveyor_id=result["_id"]["conveyor_id"],
            camera_id=result["_id"]["camera_id"],
            count=result["count"],
            jobs=result["jobs"]
        ))
    
    return hourly_counts

@router.get("/daily", response_model=List[DailyCount])
async def get_daily_stats(
    conveyor_id: Optional[str] = Query(None, description="Filter by conveyor ID"),
    camera_id: Optional[str] = Query(None, description="Filter by camera ID"),
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    db = Depends(get_database)
):
    """
    Get daily object counts for specified conveyor belt and/or camera.
    If date range is not provided, returns data for the last 7 days.
    """
    # Set default date range to last 7 days if not provided
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    if not start_date:
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    # Parse date strings to datetime
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Create date range
    start_datetime = start_date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
    end_datetime = end_date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Build query
    query = {
        "status": "completed",
        "completed_at": {"$gte": start_datetime, "$lte": end_datetime}
    }
    
    if conveyor_id:
        query["conveyor_id"] = conveyor_id
    
    if camera_id:
        query["camera_id"] = camera_id
    
    # Aggregate results by day
    pipeline = [
        {"$match": query},
        {"$addFields": {
            "date": {
                "$dateToString": {"format": "%Y-%m-%d", "date": "$completed_at"}
            }
        }},
        {"$group": {
            "_id": {
                "date": "$date",
                "conveyor_id": "$conveyor_id",
                "camera_id": "$camera_id"
            },
            "count": {"$sum": "$results.object_count"},
            "jobs": {"$sum": 1}
        }},
        {"$sort": {"_id.date": 1}}
    ]
    
    results = await db.tracking_jobs.aggregate(pipeline).to_list(length=None)
    
    # Format results
    daily_counts = []
    for result in results:
        daily_counts.append(DailyCount(
            date=result["_id"]["date"],
            conveyor_id=result["_id"]["conveyor_id"],
            camera_id=result["_id"]["camera_id"],
            count=result["count"],
            jobs=result["jobs"]
        ))
    
    return daily_counts

@router.get("/conveyor/{conveyor_id}", response_model=ConveyorStats)
async def get_conveyor_stats(
    conveyor_id: str,
    time_range: StatsTimeRange = StatsTimeRange.day,
    db = Depends(get_database)
):
    """
    Get statistics for a specific conveyor belt.
    """
    # Determine the time range
    end_date = datetime.now()
    
    if time_range == StatsTimeRange.day:
        start_date = end_date - timedelta(days=1)
    elif time_range == StatsTimeRange.week:
        start_date = end_date - timedelta(days=7)
    elif time_range == StatsTimeRange.month:
        start_date = end_date - timedelta(days=30)
    else:
        start_date = end_date - timedelta(days=1)
    
    # Build query
    query = {
        "conveyor_id": conveyor_id,
        "status": "completed",
        "completed_at": {"$gte": start_date, "$lte": end_date}
    }
    
    # Get cameras associated with this conveyor
    camera_pipeline = [
        {"$match": query},
        {"$group": {
            "_id": "$camera_id",
            "count": {"$sum": "$results.object_count"},
            "jobs": {"$sum": 1}
        }}
    ]
    
    camera_results = await db.tracking_jobs.aggregate(camera_pipeline).to_list(length=None)
    
    # Get total count
    total_pipeline = [
        {"$match": query},
        {"$group": {
            "_id": None,
            "total_count": {"$sum": "$results.object_count"},
            "total_jobs": {"$sum": 1},
            "avg_processing_time": {"$avg": "$processing_time"}
        }}
    ]
    
    total_result = await db.tracking_jobs.aggregate(total_pipeline).to_list(length=1)
    
    if not total_result:
        raise HTTPException(status_code=404, detail=f"No data found for conveyor {conveyor_id}")
    
    total_stats = total_result[0]
    
    # Get hourly distribution
    hourly_pipeline = [
        {"$match": query},
        {"$addFields": {
            "hour": {"$hour": "$completed_at"}
        }},
        {"$group": {
            "_id": "$hour",
            "count": {"$sum": "$results.object_count"}
        }},
        {"$sort": {"_id": 1}}
    ]
    
    hourly_results = await db.tracking_jobs.aggregate(hourly_pipeline).to_list(length=24)
    
    hourly_distribution = [0] * 24
    for result in hourly_results:
        hourly_distribution[result["_id"]] = result["count"]
    
    # Format camera stats
    camera_stats = []
    for result in camera_results:
        camera_stats.append(CameraStats(
            camera_id=result["_id"],
            count=result["count"],
            jobs=result["jobs"]
        ))
    
    return ConveyorStats(
        conveyor_id=conveyor_id,
        total_count=total_stats["total_count"],
        total_jobs=total_stats["total_jobs"],
        avg_processing_time=total_stats["avg_processing_time"],
        time_range=time_range,
        start_date=start_date,
        end_date=end_date,
        hourly_distribution=hourly_distribution,
        cameras=camera_stats
    )

@router.get("/camera/{camera_id}", response_model=CameraStats)
async def get_camera_stats(
    camera_id: str,
    time_range: StatsTimeRange = StatsTimeRange.day,
    db = Depends(get_database)
):
    """
    Get statistics for a specific camera.
    """
    # Determine the time range
    end_date = datetime.now()
    
    if time_range == StatsTimeRange.day:
        start_date = end_date - timedelta(days=1)
    elif time_range == StatsTimeRange.week:
        start_date = end_date - timedelta(days=7)
    elif time_range == StatsTimeRange.month:
        start_date = end_date - timedelta(days=30)
    else:
        start_date = end_date - timedelta(days=1)
    
    # Build query
    query = {
        "camera_id": camera_id,
        "status": "completed",
        "completed_at": {"$gte": start_date, "$lte": end_date}
    }
    
    # Get total count
    total_pipeline = [
        {"$match": query},
        {"$group": {
            "_id": None,
            "count": {"$sum": "$results.object_count"},
            "jobs": {"$sum": 1}
        }}
    ]
    
    total_result = await db.tracking_jobs.aggregate(total_pipeline).to_list(length=1)
    
    if not total_result:
        raise HTTPException(status_code=404, detail=f"No data found for camera {camera_id}")
    
    total_stats = total_result[0]
    
    return CameraStats(
        camera_id=camera_id,
        count=total_stats["count"],
        jobs=total_stats["jobs"]
    )
