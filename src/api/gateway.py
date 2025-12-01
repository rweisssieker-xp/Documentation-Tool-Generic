"""
API Gateway - Zentrale API-Schicht für alle Features
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any
import logging

from .rest.sessions import SessionAPI
from .rest.documents import DocumentAPI
from .rest.knowledge import KnowledgeAPI
from .rest.voice import VoiceAPI
from .rest.collaboration import CollaborationAPI
from .rest.analytics import AnalyticsAPI
from .graphql.schema import GraphQLSchema
from .websocket.realtime import WebSocketHandler
from .auth.jwt import JWTAuth
from .auth.oauth import OAuth2Auth
from .middleware.rate_limit import RateLimitMiddleware
from .middleware.logging import RequestLoggingMiddleware
from .openapi.generator import OpenAPIGenerator
from src.utils.logger import get_logger

logger = get_logger(__name__)


class APIGateway:
    """Zentrale API-Gateway-Klasse"""
    
    def __init__(
        self,
        title: str = "AHG API Gateway",
        version: str = "3.0.0",
        description: str = "REST/GraphQL API für Automatischer Handbuch-Generator",
        enable_cors: bool = True,
        enable_auth: bool = True,
        enable_rate_limit: bool = True,
        api_key: Optional[str] = None,
    ):
        """
        Initialize API Gateway.
        
        Args:
            title: API Title
            version: API Version
            description: API Description
            enable_cors: Enable CORS
            enable_auth: Enable Authentication
            enable_rate_limit: Enable Rate Limiting
            api_key: Optional API Key for simple auth
        """
        self.title = title
        self.version = version
        self.description = description
        self.enable_cors = enable_cors
        self.enable_auth = enable_auth
        self.enable_rate_limit = enable_rate_limit
        self.api_key = api_key
        
        self.app = FastAPI(
            title=title,
            version=version,
            description=description,
        )
        
        self._setup_middleware()
        self._setup_routes()
        self._setup_error_handlers()
        
        # Initialize OpenAPI Generator
        self.openapi_generator = OpenAPIGenerator(self.app)
    
    def _setup_middleware(self):
        """Setup middleware"""
        if self.enable_cors:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        
        if self.enable_rate_limit:
            self.app.add_middleware(RateLimitMiddleware)
        
        self.app.add_middleware(RequestLoggingMiddleware)
    
    def _setup_routes(self):
        """Setup API routes"""
        # REST API Routes
        session_api = SessionAPI()
        document_api = DocumentAPI()
        knowledge_api = KnowledgeAPI()
        voice_api = VoiceAPI()
        collaboration_api = CollaborationAPI()
        analytics_api = AnalyticsAPI()
        
        self.app.include_router(session_api.router, prefix="/api/v1/sessions", tags=["Sessions"])
        self.app.include_router(document_api.router, prefix="/api/v1/documents", tags=["Documents"])
        self.app.include_router(knowledge_api.router, prefix="/api/v1/knowledge", tags=["Knowledge"])
        self.app.include_router(voice_api.router, prefix="/api/v1/voice", tags=["Voice"])
        self.app.include_router(collaboration_api.router, prefix="/api/v1/collaboration", tags=["Collaboration"])
        self.app.include_router(analytics_api.router, prefix="/api/v1/analytics", tags=["Analytics"])
        
        # GraphQL Route
        graphql_schema = GraphQLSchema()
        self.app.add_route("/graphql", graphql_schema.graphql_app, methods=["GET", "POST"])
        
        # WebSocket Route
        ws_handler = WebSocketHandler()
        self.app.add_websocket_route("/ws", ws_handler.handle)
        
        # Health Check
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "version": self.version}
        
        # OpenAPI Spec
        @self.app.get("/openapi.json")
        async def openapi_spec():
            return self.openapi_generator.generate_spec()
    
    def _setup_error_handlers(self):
        """Setup error handlers"""
        @self.app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            logger.error(f"Unhandled exception: {exc}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": str(exc),
                    "path": str(request.url),
                }
            )
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, **kwargs):
        """Run API server"""
        try:
            import uvicorn
            uvicorn.run(self.app, host=host, port=port, **kwargs)
        except ImportError:
            logger.error("uvicorn not installed. Install with: pip install uvicorn")
            raise

