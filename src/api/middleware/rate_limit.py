"""
Rate Limiting Middleware
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple

from src.utils.logger import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        """
        Initialize rate limit middleware.
        
        Args:
            app: FastAPI app
            requests_per_minute: Max requests per minute per IP
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts: Dict[str, Tuple[int, datetime]] = defaultdict(lambda: (0, datetime.now()))
    
    async def dispatch(self, request: Request, call_next):
        """Check rate limit"""
        client_ip = request.client.host if request.client else "unknown"
        
        count, last_reset = self.request_counts[client_ip]
        now = datetime.now()
        
        # Reset counter if minute passed
        if (now - last_reset) > timedelta(minutes=1):
            count = 0
            last_reset = now
        
        # Check limit
        if count >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Increment counter
        count += 1
        self.request_counts[client_ip] = (count, last_reset)
        
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(self.requests_per_minute - count)
        
        return response

