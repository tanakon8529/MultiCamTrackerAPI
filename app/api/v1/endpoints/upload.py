from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Form, Query
from typing import List, Optional
from uuid import uuid4
import aiofiles
import os
import shutil
from datetime import datetime
import cv2
import numpy as np
from app.schemas.upload import UploadResponse, VideoMetadata
from app.db.database import get_database
from app.services.file_validator import validate_image, validate_video
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/image", response_model=UploadResponse)
async def upload_image(
    files: List[UploadFile] = File(...),
    camera_id: str = Form(...),
    conveyor_id: str = Form(...),
    db = Depends(get_database)
):
    """
    Upload single or multiple images for object detection and tracking.
    """
    upload_id = str(uuid4())
    now = datetime.now()
    
    # Create upload directory
    upload_path = os.path.join(UPLOAD_DIR, upload_id)
    os.makedirs(upload_path, exist_ok=True)
    
    saved_files = []
    
    for file in files:
        # Validate file is an image
        if not await validate_image(file):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not a valid image")
        
        # Save the file
        file_path = os.path.join(upload_path, file.filename)
        
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        saved_files.append(file_path)
    
    # Save record to MongoDB
    upload_record = {
        "upload_id": upload_id,
        "camera_id": camera_id,
        "conveyor_id": conveyor_id,
        "type": "image",
        "files": saved_files,
        "timestamp": now,
        "status": "uploaded",
    }
    
    await db.uploads.insert_one(upload_record)
    
    return UploadResponse(
        upload_id=upload_id,
        camera_id=camera_id,
        conveyor_id=conveyor_id,
        file_count=len(saved_files),
        timestamp=now,
        status="uploaded"
    )

@router.post("/video", response_model=UploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    camera_id: str = Form(...),
    conveyor_id: str = Form(...),
    extract_frames: bool = Form(False),
    frame_interval: int = Form(1),
    db = Depends(get_database)
):
    """
    Upload a video file for object detection and tracking.
    Optionally extract frames from the video at specified intervals.
    """
    upload_id = str(uuid4())
    now = datetime.now()
    
    # Create upload directory
    upload_path = os.path.join(UPLOAD_DIR, upload_id)
    os.makedirs(upload_path, exist_ok=True)
    
    # Validate file is a video
    if not await validate_video(file):
        raise HTTPException(status_code=400, detail=f"File {file.filename} is not a valid video")
    
    # Save the file
    video_path = os.path.join(upload_path, file.filename)
    
    async with aiofiles.open(video_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    saved_files = [video_path]
    extracted_frames = []
    
    # Extract frames if requested
    if extract_frames:
        frames_path = os.path.join(upload_path, "frames")
        os.makedirs(frames_path, exist_ok=True)
        
        # Open video and extract frames
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise HTTPException(status_code=400, detail="Could not open video file")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        
        # Extract frames at specified interval
        count = 0
        frame_index = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if count % frame_interval == 0:
                frame_filename = f"frame_{frame_index:06d}.jpg"
                frame_path = os.path.join(frames_path, frame_filename)
                cv2.imwrite(frame_path, frame)
                extracted_frames.append(frame_path)
                frame_index += 1
            
            count += 1
        
        cap.release()
        
        saved_files.extend(extracted_frames)
        
        # Video metadata
        video_metadata = VideoMetadata(
            fps=fps,
            frame_count=frame_count,
            duration=duration,
            width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            extracted_frames=len(extracted_frames)
        )
    else:
        video_metadata = None
    
    # Save record to MongoDB
    upload_record = {
        "upload_id": upload_id,
        "camera_id": camera_id,
        "conveyor_id": conveyor_id,
        "type": "video",
        "files": saved_files,
        "timestamp": now,
        "status": "uploaded",
        "video_metadata": video_metadata.dict() if video_metadata else None,
        "extracted_frames": extract_frames,
        "frame_interval": frame_interval if extract_frames else None
    }
    
    await db.uploads.insert_one(upload_record)
    
    return UploadResponse(
        upload_id=upload_id,
        camera_id=camera_id,
        conveyor_id=conveyor_id,
        file_count=len(saved_files),
        timestamp=now,
        status="uploaded",
        video_metadata=video_metadata
    )
