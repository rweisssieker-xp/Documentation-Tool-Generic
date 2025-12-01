"""
Spatial Anchoring - Anchors AR content to positions
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import uuid

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Anchor:
    """AR Anchor"""
    id: str
    position: tuple
    rotation: tuple = (0, 0, 0)
    scale: float = 1.0
    metadata: Optional[Dict[str, Any]] = None


class SpatialAnchoring:
    """Spatial Anchoring System"""
    
    def __init__(self):
        """Initialize spatial anchoring"""
        self.anchors: Dict[str, Anchor] = {}
    
    def create_anchor(self, position: tuple, anchor_id: Optional[str] = None) -> Anchor:
        """Create anchor"""
        if anchor_id is None:
            anchor_id = str(uuid.uuid4())
        
        anchor = Anchor(
            id=anchor_id,
            position=position,
        )
        
        self.anchors[anchor_id] = anchor
        logger.debug(f"Created anchor: {anchor_id}")
        
        return anchor
    
    def get_anchor(self, anchor_id: str) -> Optional[Anchor]:
        """Get anchor by ID"""
        return self.anchors.get(anchor_id)
    
    def remove_anchor(self, anchor_id: str):
        """Remove anchor"""
        if anchor_id in self.anchors:
            del self.anchors[anchor_id]
            logger.debug(f"Removed anchor: {anchor_id}")
    
    def update_anchor(self, anchor_id: str, position: Optional[tuple] = None, rotation: Optional[tuple] = None):
        """Update anchor"""
        anchor = self.anchors.get(anchor_id)
        if anchor:
            if position:
                anchor.position = position
            if rotation:
                anchor.rotation = rotation
            logger.debug(f"Updated anchor: {anchor_id}")

