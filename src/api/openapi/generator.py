"""
OpenAPI Specification Generator
"""

from fastapi import FastAPI
from typing import Dict, Any

from src.utils.logger import get_logger

logger = get_logger(__name__)


class OpenAPIGenerator:
    """OpenAPI Specification Generator"""
    
    def __init__(self, app: FastAPI):
        """
        Initialize OpenAPI Generator.
        
        Args:
            app: FastAPI application
        """
        self.app = app
    
    def generate_spec(self) -> Dict[str, Any]:
        """Generate OpenAPI specification"""
        try:
            # Use FastAPI's built-in OpenAPI generator
            openapi_schema = self.app.openapi()
            
            # Enhance with AI-generated examples
            # This would use GPT-4o to generate example requests/responses
            # For now, return the standard schema
            
            return openapi_schema
        except Exception as e:
            logger.error(f"Error generating OpenAPI spec: {e}")
            return {
                "openapi": "3.0.0",
                "info": {
                    "title": self.app.title,
                    "version": self.app.version,
                },
                "paths": {},
            }

