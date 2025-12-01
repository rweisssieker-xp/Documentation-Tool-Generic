"""
AR Overlay Engine - Zentrale AR Engine
"""

from typing import Optional, Dict, Any, List
from enum import Enum

from .platforms.vision_pro import VisionProPlatform
from .platforms.quest import QuestPlatform
from .spatial.anchoring import SpatialAnchoring
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ARPlatform(Enum):
    """AR Platform types"""
    VISION_PRO = "vision_pro"
    QUEST = "quest"
    HOLOLENS = "hololens"


class AROverlayEngine:
    """AR Overlay Engine"""
    
    def __init__(self, platform: ARPlatform = ARPlatform.VISION_PRO):
        """
        Initialize AR Overlay Engine.
        
        Args:
            platform: AR platform to use
        """
        self.platform = platform
        self.platform_handler = None
        self.anchoring = SpatialAnchoring()
        
        self._initialize_platform()
    
    def _initialize_platform(self):
        """Initialize platform handler"""
        try:
            if self.platform == ARPlatform.VISION_PRO:
                self.platform_handler = VisionProPlatform()
            elif self.platform == ARPlatform.QUEST:
                self.platform_handler = QuestPlatform()
            else:
                logger.warning(f"Platform {self.platform} not fully implemented")
        except Exception as e:
            logger.error(f"Error initializing AR platform: {e}")
    
    def show_overlay(self, content: str, position: tuple, anchor_id: Optional[str] = None):
        """Show AR overlay"""
        if not self.platform_handler:
            raise RuntimeError("AR platform not initialized")
        
        try:
            # Anchor content to position
            if anchor_id:
                anchor = self.anchoring.create_anchor(position, anchor_id)
            else:
                anchor = self.anchoring.create_anchor(position)
            
            # Render overlay
            self.platform_handler.render_overlay(content, anchor)
        except Exception as e:
            logger.error(f"Error showing overlay: {e}")
            raise
    
    def hide_overlay(self, anchor_id: str):
        """Hide AR overlay"""
        if not self.platform_handler:
            raise RuntimeError("AR platform not initialized")
        
        try:
            anchor = self.anchoring.get_anchor(anchor_id)
            if anchor:
                self.platform_handler.remove_overlay(anchor)
        except Exception as e:
            logger.error(f"Error hiding overlay: {e}")
            raise
    
    def update_overlay(self, anchor_id: str, content: str):
        """Update AR overlay"""
        if not self.platform_handler:
            raise RuntimeError("AR platform not initialized")
        
        try:
            anchor = self.anchoring.get_anchor(anchor_id)
            if anchor:
                self.platform_handler.update_overlay(anchor, content)
        except Exception as e:
            logger.error(f"Error updating overlay: {e}")
            raise

