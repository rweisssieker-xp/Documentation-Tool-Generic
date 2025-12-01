"""
Mouse Tracker - Tracks mouse movements
"""

from typing import List, Dict, Any
import threading
import time

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

from src.utils.logger import get_logger

logger = get_logger(__name__)


class MouseTracker:
    """Mouse Tracker"""
    
    def __init__(self):
        """Initialize Mouse Tracker"""
        self.tracking = False
        self.mouse_data: List[Dict[str, Any]] = []
        self.thread = None
    
    def start(self):
        """Start mouse tracking"""
        if self.tracking:
            logger.warning("Mouse tracking already in progress")
            return
        
        self.tracking = True
        self.mouse_data = []
        
        # Start tracking thread
        self.thread = threading.Thread(target=self._track_loop)
        self.thread.start()
        
        logger.info("Mouse tracking started")
    
    def stop(self) -> List[Dict[str, Any]]:
        """Stop mouse tracking"""
        if not self.tracking:
            return []
        
        self.tracking = False
        
        if self.thread:
            self.thread.join()
        
        logger.info("Mouse tracking stopped")
        return self.mouse_data
    
    def _track_loop(self):
        """Tracking loop"""
        if not PYAUTOGUI_AVAILABLE:
            return
        
        try:
            while self.tracking:
                x, y = pyautogui.position()
                self.mouse_data.append({
                    'timestamp': time.time(),
                    'x': x,
                    'y': y,
                })
                time.sleep(0.1)  # 10 Hz sampling
        except Exception as e:
            logger.error(f"Error in mouse tracking loop: {e}")

