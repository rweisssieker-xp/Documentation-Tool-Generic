"""REST API Modules"""

from .sessions import SessionAPI
from .documents import DocumentAPI
from .knowledge import KnowledgeAPI
from .voice import VoiceAPI
from .collaboration import CollaborationAPI
from .analytics import AnalyticsAPI
from .edge_ai import EdgeAIAPI
from .ar import ARAPI
from .blockchain import BlockchainAPI
from .predictive import PredictiveAPI
from .multimodal import MultiModalAPI
from .plugins import PluginAPI

__all__ = [
    'SessionAPI',
    'DocumentAPI',
    'KnowledgeAPI',
    'VoiceAPI',
    'CollaborationAPI',
    'AnalyticsAPI',
    'EdgeAIAPI',
    'ARAPI',
    'BlockchainAPI',
    'PredictiveAPI',
    'MultiModalAPI',
    'PluginAPI',
]
