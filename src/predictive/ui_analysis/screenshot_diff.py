"""
Screenshot Diff - Vergleicht Screenshots
"""

from typing import List, Dict, Any
from pathlib import Path

try:
    from PIL import Image
    import numpy as np
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ScreenshotDiff:
    """Screenshot Diff"""
    
    def detect_drift(self, session_id: str) -> List[Dict[str, Any]]:
        """Detect UI drift by comparing screenshots"""
        issues = []
        
        if not PILLOW_AVAILABLE:
            logger.warning("PIL not available for screenshot comparison")
            return issues
        
        # Placeholder implementation
        logger.info(f"Detecting UI drift for session: {session_id}")
        
        return issues
    
    def compare_screenshots(self, screenshot1: str, screenshot2: str) -> float:
        """Compare two screenshots and return similarity score"""
        if not PILLOW_AVAILABLE:
            return 0.0
        
        try:
            img1 = Image.open(screenshot1)
            img2 = Image.open(screenshot2)
            
            # Resize if needed
            if img1.size != img2.size:
                img2 = img2.resize(img1.size)
            
            # Convert to numpy arrays
            arr1 = np.array(img1)
            arr2 = np.array(img2)
            
            # Calculate similarity
            diff = np.abs(arr1 - arr2)
            similarity = 1.0 - (np.mean(diff) / 255.0)
            
            return similarity
        except Exception as e:
            logger.error(f"Error comparing screenshots: {e}")
            return 0.0

