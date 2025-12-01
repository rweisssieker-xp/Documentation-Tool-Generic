"""
AR Documentation Overlay - Mixed Reality Overlays
"""

from .overlay_engine import AROverlayEngine, ARPlatform
from .platforms.vision_pro import VisionProPlatform
from .platforms.quest import QuestPlatform
from .platforms.hololens import HoloLensPlatform
from .spatial.anchoring import SpatialAnchoring
from .rendering.text_overlay import TextOverlayRenderer
from .rendering.image_overlay import ImageOverlayRenderer
from .rendering.video_overlay import VideoOverlayRenderer
from .gestures.recognition import GestureRecognizer, GestureType
from .sync.realtime import MultiUserSync

__all__ = [
    'AROverlayEngine',
    'ARPlatform',
    'VisionProPlatform',
    'QuestPlatform',
    'HoloLensPlatform',
    'SpatialAnchoring',
    'TextOverlayRenderer',
    'ImageOverlayRenderer',
    'VideoOverlayRenderer',
    'GestureRecognizer',
    'GestureType',
    'MultiUserSync',
]

