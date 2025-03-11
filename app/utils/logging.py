import logging
import sys
from typing import Dict, Any
import json
from fastapi import Request
from datetime import datetime

# Configure root logger
def setup_logging(log_level: str = "INFO"):
    """
    Setup application logging with the specified log level.
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    # Set OpenCV log level higher to avoid excessive output
    logging.getLogger("opencv").setLevel(logging.WARNING)
    
    # Set MongoDB driver log level higher to avoid excessive output
    logging.getLogger("motor").setLevel(logging.WARNING)
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    return logger

class RequestLogMiddleware:
    """
    Middleware for logging HTTP requests.
    """
    
    async def __call__(self, request: Request, call_next):
        """
        Log request and response information.
        
        Args:
            request (Request): FastAPI request object
            call_next (Callable): Function to call to process the request
        """
        logger = logging.getLogger("api")
        
        # Request information
        request_time = datetime.now()
        request_id = request.headers.get("X-Request-ID", "")
        client_ip = request.client.host if request.client else ""
        
        request_info = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": client_ip,
            "timestamp": request_time.isoformat()
        }
        
        logger.info(f"Request: {json.dumps(request_info)}")
        
        # Process request
        response = await call_next(request)
        
        # Response information
        response_time = datetime.now()
        processing_time = (response_time - request_time).total_seconds() * 1000
        
        response_info = {
            "request_id": request_id,
            "status_code": response.status_code,
            "processing_time_ms": processing_time,
            "timestamp": response_time.isoformat()
        }
        
        logger.info(f"Response: {json.dumps(response_info)}")
        
        return response

def log_error(logger: logging.Logger, error: Exception, request: Request = None, context: Dict[str, Any] = None):
    """
    Log an error with request information.
    
    Args:
        logger (logging.Logger): Logger instance
        error (Exception): The exception to log
        request (Request, optional): FastAPI request object
        context (Dict[str, Any], optional): Additional context information
    """
    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": datetime.now().isoformat()
    }
    
    if request:
        error_info["method"] = request.method
        error_info["path"] = request.url.path
        error_info["client_ip"] = request.client.host if request.client else ""
    
    if context:
        error_info["context"] = context
    
    logger.error(f"Error: {json.dumps(error_info)}", exc_info=True)
