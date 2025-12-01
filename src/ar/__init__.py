"""
AR Documentation Overlay - Mixed Reality Overlays
"""

from .overlay_engine import AROverlayEngine
from .platforms.vision_pro import VisionProPlatform
from .platforms.quest import QuestPlatform
from .spatial.anchoring import SpatialAnchoring
from .rendering.text_overlay import TextOverlayRenderer

__all__ = [
    'AROverlayEngine',
    'VisionProPlatform',
    'QuestPlatform',
    'SpatialAnchoring',
    'TextOverlayRenderer',
]

