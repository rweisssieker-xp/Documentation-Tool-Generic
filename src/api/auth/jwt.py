"""
JWT Authentication
"""

try:
    import jwt
    from datetime import datetime, timedelta
    from typing import Optional, Dict, Any
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

from src.utils.logger import get_logger

logger = get_logger(__name__)


class JWTAuth:
    """JWT Authentication"""
    
    def __init__(self, secret_key: str = "your-secret-key", algorithm: str = "HS256"):
        """
        Initialize JWT Auth.
        
        Args:
            secret_key: Secret key for JWT signing
            algorithm: JWT algorithm
        """
        if not JWT_AVAILABLE:
            logger.warning("PyJWT not available. Install with: pip install PyJWT")
        
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def create_token(self, user_id: str, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT token"""
        if not JWT_AVAILABLE:
            raise ImportError("PyJWT not available")
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=24)
        
        payload = {
            "user_id": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        if not JWT_AVAILABLE:
            raise ImportError("PyJWT not available")
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None

