"""
API-First Gateway - REST/GraphQL API für alle Features
"""

from .gateway import APIGateway
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

__all__ = [
    'APIGateway',
    'SessionAPI',
    'DocumentAPI',
    'KnowledgeAPI',
    'VoiceAPI',
    'CollaborationAPI',
    'AnalyticsAPI',
    'GraphQLSchema',
    'WebSocketHandler',
    'JWTAuth',
    'OAuth2Auth',
]

