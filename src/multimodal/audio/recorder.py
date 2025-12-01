"""
Audio Recorder - Audio Recording
"""

from typing import Optional
import threading

try:
    import sounddevice as sd
    import soundfile as sf
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False

from src.utils.logger import get_logger

logger = get_logger(__name__)


class AudioRecorder:
    """Audio Recorder"""
    
    def __init__(self, sample_rate: int = 44100):
        """
        Initialize Audio Recorder.
        
        Args:
            sample_rate: Sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.recording = False
        self.output_path: Optional[str] = None
        self.audio_data = []
        self.thread = None
        
        if not SOUNDDEVICE_AVAILABLE:
            logger.warning("sounddevice not available. Install with: pip install sounddevice soundfile")
    
    def start(self, output_path: str):
        """Start audio recording"""
        if not SOUNDDEVICE_AVAILABLE:
            logger.error("sounddevice not available")
            return
        
        if self.recording:
            logger.warning("Recording already in progress")
            return
        
        self.output_path = output_path
        self.recording = True
        self.audio_data = []
        
        # Start recording thread
        self.thread = threading.Thread(target=self._record_loop)
        self.thread.start()
        
        logger.info(f"Audio recording started: {output_path}")
    
    def stop(self) -> Optional[str]:
        """Stop audio recording"""
        if not self.recording:
            return None
        
        self.recording = False
        
        if self.thread:
            self.thread.join()
        
        # Save audio data
        if self.audio_data and self.output_path:
            try:
                sf.write(self.output_path, self.audio_data, self.sample_rate)
                logger.info("Audio recording stopped")
                return self.output_path
            except Exception as e:
                logger.error(f"Error saving audio: {e}")
        
        return None
    
    def _record_loop(self):
        """Recording loop"""
        if not SOUNDDEVICE_AVAILABLE:
            return
        
        try:
            def callback(indata, frames, time, status):
                if status:
                    logger.warning(f"Audio recording status: {status}")
                if self.recording:
                    self.audio_data.extend(indata.copy())
            
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                callback=callback
            ):
                while self.recording:
                    import time
                    time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error in audio recording loop: {e}")

