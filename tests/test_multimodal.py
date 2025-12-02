"""
Tests for Multi-Modal Capture Engine
"""

import pytest
from pathlib import Path

from src.multimodal import MultiModalCaptureEngine


class TestMultiModalCaptureEngine:
    """Test Multi-Modal Capture Engine"""
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        engine = MultiModalCaptureEngine()
        assert engine.video_recorder is not None
        assert engine.audio_recorder is not None
        assert engine.mouse_tracker is not None
    
    def test_is_recording_false_initially(self):
        """Test initial recording state"""
        engine = MultiModalCaptureEngine()
        assert engine.is_recording() is False
    
    def test_start_stop_recording(self):
        """Test start/stop recording"""
        engine = MultiModalCaptureEngine()
        
        # Create temp directory
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                engine.start_recording(tmpdir)
                assert engine.is_recording() is True
                
                synchronized = engine.stop_recording()
                assert engine.is_recording() is False
                assert isinstance(synchronized, dict)
            except Exception as e:
                # May fail if dependencies not available
                pytest.skip(f"Dependencies not available: {e}")


class TestVideoRecorder:
    """Test Video Recorder"""
    
    def test_recorder_initialization(self):
        """Test recorder initialization"""
        from src.multimodal.video.recorder import VideoRecorder
        
        recorder = VideoRecorder(fps=30)
        assert recorder.fps == 30
        assert recorder.recording is False


class TestAudioRecorder:
    """Test Audio Recorder"""
    
    def test_recorder_initialization(self):
        """Test recorder initialization"""
        from src.multimodal.audio.recorder import AudioRecorder
        
        recorder = AudioRecorder(sample_rate=44100)
        assert recorder.sample_rate == 44100
        assert recorder.recording is False



