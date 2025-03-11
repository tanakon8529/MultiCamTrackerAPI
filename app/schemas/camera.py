from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class CameraConfig(BaseModel):
    crossing_line: Optional[Dict[str, float]] = None
    detection_threshold: float = 0.5
    tracking_enabled: bool = True
    counting_enabled: bool = True

class CameraBase(BaseModel):
    name: str
    location: str
    conveyor_id: str
    ip_address: Optional[str] = None
    rtsp_url: Optional[str] = None
    active: bool = True
    config: Optional[CameraConfig] = None

class CameraCreate(CameraBase):
    pass

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    conveyor_id: Optional[str] = None
    ip_address: Optional[str] = None
    rtsp_url: Optional[str] = None
    active: Optional[bool] = None
    config: Optional[CameraConfig] = None

class CameraResponse(CameraBase):
    camera_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ConveyorConfig(BaseModel):
    direction: Optional[str] = "left-to-right"  # 'left-to-right', 'right-to-left'
    speed_estimate: Optional[float] = None  # in units/second

class ConveyorBase(BaseModel):
    name: str
    location: str
    active: bool = True
    config: Optional[ConveyorConfig] = None

class ConveyorCreate(ConveyorBase):
    pass

class ConveyorUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    active: Optional[bool] = None
    config: Optional[ConveyorConfig] = None

class ConveyorResponse(ConveyorBase):
    conveyor_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
