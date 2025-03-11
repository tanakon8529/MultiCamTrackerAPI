from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Path, Query
from typing import List, Optional
import os
import glob
import logging
from uuid import uuid4
from datetime import datetime

from app.db.database import get_database
from app.schemas.track import TrackingRequest, TrackingResponse, TrackingResult
from app.services.detector import Detector
from app.services.tracker import Tracker
from app.services.counter import Counter
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("", response_model=TrackingResponse)
async def track_objects(
    request: TrackingRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_database)
):
    """
    Process uploaded files for object detection, tracking, and counting.
    This endpoint initiates tracking in the background.
    """
    # Check if upload exists
    upload = await db.uploads.find_one({"upload_id": request.upload_id})
    
    if not upload:
        raise HTTPException(status_code=404, detail=f"Upload with ID {request.upload_id} not found")
    
    # Create a tracking job
    tracking_id = str(uuid4())
    now = datetime.now()
    
    tracking_job = {
        "tracking_id": tracking_id,
        "upload_id": request.upload_id,
        "camera_id": upload["camera_id"],
        "conveyor_id": upload["conveyor_id"],
        "timestamp": now,
        "status": "queued",
        "detection_config": request.detection_config.dict() if request.detection_config else {},
        "tracking_config": request.tracking_config.dict() if request.tracking_config else {},
        "counting_config": request.counting_config.dict() if request.counting_config else {}
    }
    
    await db.tracking_jobs.insert_one(tracking_job)
    
    # Schedule tracking task in background
    background_tasks.add_task(
        process_tracking_job, 
        tracking_id=tracking_id,
        upload_id=request.upload_id, 
        db=db
    )
    
    return TrackingResponse(
        tracking_id=tracking_id,
        upload_id=request.upload_id,
        camera_id=upload["camera_id"],
        conveyor_id=upload["conveyor_id"],
        timestamp=now,
        status="queued"
    )

@router.get("/{tracking_id}", response_model=TrackingResult)
async def get_tracking_result(
    tracking_id: str = Path(..., description="The ID of the tracking job"),
    db = Depends(get_database)
):
    """
    Get the results of a tracking job.
    """
    tracking_job = await db.tracking_jobs.find_one({"tracking_id": tracking_id})
    
    if not tracking_job:
        raise HTTPException(status_code=404, detail=f"Tracking job with ID {tracking_id} not found")
    
    return TrackingResult(**tracking_job)

async def process_tracking_job(tracking_id: str, upload_id: str, db):
    """
    Process a tracking job in the background.
    
    Steps:
    1. Update job status to "processing"
    2. Get upload files
    3. Process files with Detector
    4. Process detections with Tracker
    5. Process tracked objects with Counter
    6. Save results to database
    7. Update job status to "completed"
    """
    logger.info(f"Starting processing of tracking job {tracking_id}")
    
    # Update job status
    await db.tracking_jobs.update_one(
        {"tracking_id": tracking_id},
        {"$set": {"status": "processing"}}
    )
    
    try:
        # Get upload
        upload = await db.uploads.find_one({"upload_id": upload_id})
        
        if not upload:
            raise Exception(f"Upload with ID {upload_id} not found")
        
        # Get files to process
        files = []
        if upload["type"] == "image":
            files = upload["files"]
        elif upload["type"] == "video" and upload.get("extracted_frames"):
            # Use extracted frames if available
            files = [f for f in upload["files"] if f.endswith(('.jpg', '.jpeg', '.png'))]
        
        # Sort files to ensure proper sequence
        files.sort()
        
        # Get tracking job configuration
        tracking_job = await db.tracking_jobs.find_one({"tracking_id": tracking_id})
        detection_config = tracking_job.get("detection_config", {})
        tracking_config = tracking_job.get("tracking_config", {})
        counting_config = tracking_job.get("counting_config", {})
        
        # Process files in optimal batch size for detector
        batch_size = settings.BATCH_SIZE
        detections = []
        
        # Initialize services
        detector = Detector()
        tracker = Tracker()
        counter = Counter(crossing_line=counting_config.get("crossing_line", {"x1": 0, "y1": 0, "x2": 100, "y2": 0}))
        
        # Process files in batches
        for i in range(0, len(files), batch_size):
            batch_files = files[i:i+batch_size]
            batch_detections = detector.detect(batch_files)
            detections.extend(batch_detections)
        
        # Track objects
        tracked_objects = []
        for i in range(1, len(detections)):
            # Ensure time difference is within limit
            tracker.update(detections[i-1], detections[i])
            tracked_objects.append(tracker.get_tracked_objects())
        
        # Count objects
        counts = []
        for objects in tracked_objects:
            counter.update(objects)
            counts.append(counter.get_counts())
        
        # Calculate final count
        final_count = counter.get_total_count()
        
        # Save results to database
        result = {
            "status": "completed",
            "completed_at": datetime.now(),
            "detection_count": len(detections),
            "tracked_objects_count": sum(len(objects) for objects in tracked_objects),
            "object_count": final_count,
            "processing_time": (datetime.now() - tracking_job["timestamp"]).total_seconds(),
            "results": {
                "object_count": final_count,
                "counts_by_timestamp": counts
            }
        }
        
        # Update tracking job
        await db.tracking_jobs.update_one(
            {"tracking_id": tracking_id},
            {"$set": result}
        )
        
        logger.info(f"Completed processing of tracking job {tracking_id}")
    
    except Exception as e:
        logger.error(f"Error processing tracking job {tracking_id}: {str(e)}")
        
        # Update job status to failed
        await db.tracking_jobs.update_one(
            {"tracking_id": tracking_id},
            {"$set": {
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.now()
            }}
        )
