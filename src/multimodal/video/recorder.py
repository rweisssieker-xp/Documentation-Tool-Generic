"""
Video Recorder - Screen Recording
"""

from typing import Optional
import threading

try:
    import cv2
    import numpy as np
    from mss import mss
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

from src.utils.logger import get_logger

logger = get_logger(__name__)


class VideoRecorder:
    """Video Recorder"""
    
    def __init__(self, fps: int = 30):
        """
        Initialize Video Recorder.
        
        Args:
            fps: Frames per second
        """
        self.fps = fps
        self.recording = False
        self.output_path: Optional[str] = None
        self.writer = None
        self.thread = None
        
        if not CV2_AVAILABLE:
            logger.warning("OpenCV not available. Install with: pip install opencv-python")
    
    def start(self, output_path: str):
        """Start video recording"""
        if not CV2_AVAILABLE:
            logger.error("OpenCV not available")
            return
        
        if self.recording:
            logger.warning("Recording already in progress")
            return
        
        self.output_path = output_path
        self.recording = True
        
        # Start recording thread
        self.thread = threading.Thread(target=self._record_loop)
        self.thread.start()
        
        logger.info(f"Video recording started: {output_path}")
    
    def stop(self) -> Optional[str]:
        """Stop video recording"""
        if not self.recording:
            return None
        
        self.recording = False
        
        if self.thread:
            self.thread.join()
        
        if self.writer:
            self.writer.release()
            self.writer = None
        
        logger.info("Video recording stopped")
        return self.output_path
    
    def _record_loop(self):
        """Recording loop"""
        if not CV2_AVAILABLE:
            return
        
        try:
            sct = mss()
            monitor = sct.monitors[1]  # Primary monitor
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.writer = cv2.VideoWriter(
                self.output_path,
                fourcc,
                self.fps,
                (monitor['width'], monitor['height'])
            )
            
            while self.recording:
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                self.writer.write(frame)
                
                import time
                time.sleep(1.0 / self.fps)
        except Exception as e:
            logger.error(f"Error in video recording loop: {e}")

