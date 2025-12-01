"""
Request Logging Middleware
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

from src.utils.logger import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Request logging middleware"""
    
    async def dispatch(self, request: Request, call_next):
        """Log request"""
        start_time = time.time()
        
        # Log request
        logger.info(f"{request.method} {request.url.path} - {request.client.host if request.client else 'unknown'}")
        
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Duration: {duration:.3f}s"
        )
        
        response.headers["X-Process-Time"] = str(duration)
        
        return response

