"""
Voice Capture Module - Records audio during documentation sessions.
Part of Feature 7: Voice-First Documentation
"""
from __future__ import annotations

import threading
import queue
import wave
import tempfile
import os
from datetime import datetime
from typing import Optional, Callable, List
from pathlib import Path

try:
    import sounddevice as sd
    import numpy as np
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False

from src.utils.logger import get_logger

logger = get_logger(__name__)


class VoiceCapture:
    """
    Captures voice audio during documentation sessions.
    Supports continuous recording with automatic chunking for real-time transcription.
    """
    
    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_duration: float = 5.0,
        output_dir: Optional[str] = None
    ):
        """
        Initialize voice capture.
        
        Args:
            sample_rate: Audio sample rate (16000 Hz optimal for Whisper)
            channels: Number of audio channels (1 = mono)
            chunk_duration: Duration of each audio chunk in seconds
            output_dir: Directory to save audio files
        """
        if not SOUNDDEVICE_AVAILABLE:
            raise ImportError("sounddevice is required for voice capture. Install with: pip install sounddevice")
        
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_duration = chunk_duration
        self.output_dir = Path(output_dir) if output_dir else Path(tempfile.gettempdir()) / "ahg_voice"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self._is_recording = False
        self._is_paused = False
        self._audio_queue: queue.Queue = queue.Queue()
        self._recording_thread: Optional[threading.Thread] = None
        self._chunks: List[np.ndarray] = []
        self._current_session_id: Optional[str] = None
        self._chunk_callback: Optional[Callable[[bytes, str], None]] = None
        
        logger.info(f"VoiceCapture initialized: {sample_rate}Hz, {channels}ch, {chunk_duration}s chunks")
    
    def start_recording(
        self,
        session_id: str,
        on_chunk: Optional[Callable[[bytes, str], None]] = None
    ) -> bool:
        """
        Start recording audio.
        
        Args:
            session_id: Current documentation session ID
            on_chunk: Callback function called with (audio_bytes, chunk_path) for each chunk
            
        Returns:
            True if recording started successfully
        """
        if self._is_recording:
            logger.warning("Recording already in progress")
            return False
        
        self._current_session_id = session_id
        self._chunk_callback = on_chunk
        self._chunks = []
        self._is_recording = True
        self._is_paused = False
        
        # Start recording thread
        self._recording_thread = threading.Thread(target=self._record_audio, daemon=True)
        self._recording_thread.start()
        
        logger.info(f"Voice recording started for session: {session_id}")
        return True
    
    def stop_recording(self) -> Optional[str]:
        """
        Stop recording and save the complete audio file.
        
        Returns:
            Path to the complete audio file, or None if no audio was recorded
        """
        if not self._is_recording:
            logger.warning("No recording in progress")
            return None
        
        self._is_recording = False
        
        # Wait for recording thread to finish
        if self._recording_thread:
            self._recording_thread.join(timeout=2.0)
        
        # Save complete audio
        if self._chunks:
            complete_audio = np.concatenate(self._chunks)
            output_path = self._save_audio(complete_audio, "complete")
            logger.info(f"Voice recording saved: {output_path}")
            return str(output_path)
        
        logger.warning("No audio data recorded")
        return None
    
    def pause_recording(self) -> None:
        """Pause audio recording."""
        if self._is_recording and not self._is_paused:
            self._is_paused = True
            logger.info("Voice recording paused")
    
    def resume_recording(self) -> None:
        """Resume audio recording."""
        if self._is_recording and self._is_paused:
            self._is_paused = False
            logger.info("Voice recording resumed")
    
    def is_recording(self) -> bool:
        """Check if recording is active."""
        return self._is_recording and not self._is_paused
    
    def _record_audio(self) -> None:
        """Internal method to record audio in a separate thread."""
        chunk_samples = int(self.sample_rate * self.chunk_duration)
        chunk_buffer = []
        
        def audio_callback(indata, frames, time_info, status):
            if status:
                logger.warning(f"Audio status: {status}")
            if not self._is_paused:
                self._audio_queue.put(indata.copy())
        
        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=audio_callback,
                blocksize=int(self.sample_rate * 0.1)  # 100ms blocks
            ):
                while self._is_recording:
                    try:
                        data = self._audio_queue.get(timeout=0.5)
                        chunk_buffer.append(data)
                        
                        # Calculate total samples in buffer
                        total_samples = sum(len(d) for d in chunk_buffer)
                        
                        if total_samples >= chunk_samples:
                            # Combine buffer into chunk
                            chunk_data = np.concatenate(chunk_buffer)
                            self._chunks.append(chunk_data[:chunk_samples])
                            
                            # Save chunk and trigger callback
                            chunk_path = self._save_audio(
                                chunk_data[:chunk_samples],
                                f"chunk_{len(self._chunks):04d}"
                            )
                            
                            if self._chunk_callback:
                                audio_bytes = self._audio_to_bytes(chunk_data[:chunk_samples])
                                self._chunk_callback(audio_bytes, str(chunk_path))
                            
                            # Keep remainder for next chunk
                            if len(chunk_data) > chunk_samples:
                                chunk_buffer = [chunk_data[chunk_samples:]]
                            else:
                                chunk_buffer = []
                    
                    except queue.Empty:
                        continue
                
                # Save any remaining audio
                if chunk_buffer:
                    remaining = np.concatenate(chunk_buffer)
                    self._chunks.append(remaining)
        
        except Exception as e:
            logger.error(f"Voice recording error: {e}")
            self._is_recording = False
    
    def _save_audio(self, audio_data: np.ndarray, suffix: str) -> Path:
        """Save audio data to a WAV file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self._current_session_id}_{timestamp}_{suffix}.wav"
        filepath = self.output_dir / filename
        
        # Convert to 16-bit PCM
        audio_int16 = (audio_data * 32767).astype(np.int16)
        
        with wave.open(str(filepath), 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_int16.tobytes())
        
        return filepath
    
    def _audio_to_bytes(self, audio_data: np.ndarray) -> bytes:
        """Convert audio data to bytes for API transmission."""
        audio_int16 = (audio_data * 32767).astype(np.int16)
        return audio_int16.tobytes()
    
    @staticmethod
    def get_available_devices() -> List[dict]:
        """Get list of available audio input devices."""
        if not SOUNDDEVICE_AVAILABLE:
            return []
        
        devices = []
        for i, device in enumerate(sd.query_devices()):
            if device['max_input_channels'] > 0:
                devices.append({
                    'id': i,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'sample_rate': device['default_samplerate']
                })
        return devices

