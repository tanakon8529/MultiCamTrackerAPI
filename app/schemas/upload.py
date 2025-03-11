from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
import os

class VideoMetadata(BaseModel):
    fps: float
    frame_count: int
    duration: float
    width: int
    height: int
    extracted_frames: Optional[int] = None

class UploadResponse(BaseModel):
    upload_id: str
    camera_id: str
    conveyor_id: str
    file_count: int
    timestamp: datetime
    status: str
    video_metadata: Optional[VideoMetadata] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
