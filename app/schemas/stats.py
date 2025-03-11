from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class StatsTimeRange(str, Enum):
    day = "day"
    week = "week"
    month = "month"

class HourlyCount(BaseModel):
    hour: int
    conveyor_id: str
    camera_id: str
    count: int
    jobs: int

class DailyCount(BaseModel):
    date: str
    conveyor_id: str
    camera_id: str
    count: int
    jobs: int

class CameraStats(BaseModel):
    camera_id: str
    count: int
    jobs: int

class ConveyorStats(BaseModel):
    conveyor_id: str
    total_count: int
    total_jobs: int
    avg_processing_time: float
    time_range: StatsTimeRange
    start_date: datetime
    end_date: datetime
    hourly_distribution: List[int]
    cameras: List[CameraStats]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class StatsResponse(BaseModel):
    time_period: str
    total_count: int
    average_per_hour: float
    peak_hour: int
    peak_hour_count: int
