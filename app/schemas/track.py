from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime

class Point(BaseModel):
    x: float
    y: float

class Line(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

class DetectionConfig(BaseModel):
    confidence_threshold: float = 0.5
    nms_threshold: float = 0.4
    target_classes: Optional[List[int]] = None

class TrackingConfig(BaseModel):
    max_time_diff: float = 1.0
    min_detection_confidence: float = 0.3
    max_distance: float = 100.0

class CountingConfig(BaseModel):
    crossing_line: Line = Field(..., description="Line used to count objects crossing")
    direction: str = "any"  # 'any', 'positive', 'negative'

class TrackingRequest(BaseModel):
    upload_id: str
    detection_config: Optional[DetectionConfig] = None
    tracking_config: Optional[TrackingConfig] = None
    counting_config: Optional[CountingConfig] = None

class TrackingResponse(BaseModel):
    tracking_id: str
    upload_id: str
    camera_id: str
    conveyor_id: str
    timestamp: datetime
    status: str
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ObjectPosition(BaseModel):
    id: str
    x: float
    y: float
    width: float
    height: float
    confidence: float
    class_id: Optional[int] = None
    class_name: Optional[str] = None
    timestamp: datetime

class CountByTimestamp(BaseModel):
    timestamp: datetime
    count: int
    direction: Optional[str] = None
    object_ids: List[str]

class TrackingResults(BaseModel):
    object_count: int
    counts_by_timestamp: List[CountByTimestamp]

class TrackingResult(BaseModel):
    tracking_id: str
    upload_id: str
    camera_id: str
    conveyor_id: str
    timestamp: datetime
    status: str
    detection_config: Dict[str, Any] = {}
    tracking_config: Dict[str, Any] = {}
    counting_config: Dict[str, Any] = {}
    completed_at: Optional[datetime] = None
    detection_count: Optional[int] = None
    tracked_objects_count: Optional[int] = None
    object_count: Optional[int] = None
    processing_time: Optional[float] = None
    results: Optional[Union[TrackingResults, Dict[str, Any]]] = None
    error: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
