import secrets
from typing import List, Union, Dict, Any
try:
    # For Pydantic v2
    from pydantic_settings import BaseSettings
    from pydantic import validator, AnyHttpUrl
except ImportError:
    # Fallback for Pydantic v1
    from pydantic import BaseSettings, validator, AnyHttpUrl

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # 60 minutes * 24 hours = 1 day
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = ["*"]
    
    # MongoDB Settings
    MONGO_HOST: str = "mongodb"
    MONGO_PORT: int = 27017
    MONGO_USER: str = ""
    MONGO_PASSWORD: str = ""
    MONGO_DB: str = "multicam_tracker"
    
    # Auth Settings
    ALGORITHM: str = "HS256"
    
    # Project Settings
    PROJECT_NAME: str = "MultiCamTrackerAPI"
    
    # Detector Settings
    BATCH_SIZE: int = 128  # Optimal batch size for the detector
    
    # Tracker Settings
    MAX_TIME_DIFF: float = 1.0  # Maximum time difference in seconds
    
    # Debug mode
    DEBUG: bool = True

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
