"""
Multi-Modal Capture Engine - Zentrale Capture Engine
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
import threading

from .video.recorder import VideoRecorder
from .audio.recorder import AudioRecorder
from .sensors.mouse_tracker import MouseTracker
from .sensors.keyboard_tracker import KeyboardTracker
from .sync.synchronizer import StreamSynchronizer
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MultiModalCaptureEngine:
    """Multi-Modal Capture Engine"""
    
    def __init__(self):
        """Initialize Multi-Modal Capture Engine"""
        self.video_recorder = VideoRecorder()
        self.audio_recorder = AudioRecorder()
        self.mouse_tracker = MouseTracker()
        self.keyboard_tracker = KeyboardTracker()
        self.synchronizer = StreamSynchronizer()
        
        self.recording = False
        self.streams: Dict[str, Any] = {}
    
    def start_recording(self, output_dir: str):
        """Start multi-modal recording"""
        if self.recording:
            logger.warning("Recording already in progress")
            return
        
        self.recording = True
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Start all recorders
        self.video_recorder.start(str(output_path / "video.mp4"))
        self.audio_recorder.start(str(output_path / "audio.wav"))
        self.mouse_tracker.start()
        self.keyboard_tracker.start()
        
        logger.info("Multi-modal recording started")
    
    def stop_recording(self) -> Dict[str, str]:
        """Stop multi-modal recording"""
        if not self.recording:
            logger.warning("No recording in progress")
            return {}
        
        self.recording = False
        
        # Stop all recorders
        video_path = self.video_recorder.stop()
        audio_path = self.audio_recorder.stop()
        mouse_data = self.mouse_tracker.stop()
        keyboard_data = self.keyboard_tracker.stop()
        
        # Synchronize streams
        synchronized = self.synchronizer.synchronize({
            'video': video_path,
            'audio': audio_path,
            'mouse': mouse_data,
            'keyboard': keyboard_data,
        })
        
        logger.info("Multi-modal recording stopped")
        
        return synchronized
    
    def is_recording(self) -> bool:
        """Check if recording"""
        return self.recording

