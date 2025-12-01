"""
Tests for Video Synthesizer Module
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import numpy as np
from PIL import Image

from src.video.frame_generator import FrameGenerator
from src.video.narration import NarrationEngine, TTSClient
from src.video.subtitle_generator import SubtitleGenerator, Subtitle
from src.video.video_synthesizer import VideoSynthesizer, VideoConfig


class TestFrameGenerator:
    """Tests for FrameGenerator class."""
    
    @pytest.fixture
    def temp_screenshots(self):
        """Create temporary screenshot files."""
        temp_dir = tempfile.mkdtemp()
        screenshots = []
        
        for i in range(3):
            img = Image.new('RGB', (800, 600), color=(i*80, 100, 150))
            path = Path(temp_dir) / f"screenshot_{i}.png"
            img.save(path)
            screenshots.append(path)
        
        yield screenshots
        shutil.rmtree(temp_dir)
    
    def test_frame_generator_initialization(self):
        """Test FrameGenerator initialization."""
        generator = FrameGenerator(frame_rate=30)
        assert generator.frame_rate == 30
    
    def test_generate_frames(self, temp_screenshots):
        """Test generating frames."""
        generator = FrameGenerator(frame_rate=30)
        
        frames = generator.generate_frames(temp_screenshots, frame_duration=1.0)
        
        assert len(frames) > 0
        assert isinstance(frames[0], np.ndarray)


class TestNarrationEngine:
    """Tests for NarrationEngine class."""
    
    def test_narration_engine_initialization(self):
        """Test NarrationEngine initialization."""
        engine = NarrationEngine()
        assert engine.model == "gpt-4o"
    
    def test_generate_narration_script(self):
        """Test generating narration script."""
        engine = NarrationEngine()
        
        steps = [
            {"action": "Click", "description": "Click on button"},
            {"action": "Type", "description": "Enter text"}
        ]
        
        narrations = engine.generate_narration_script(steps, language="de")
        
        # Should return list of narrations (may be basic if no OpenAI)
        assert isinstance(narrations, list)
        assert len(narrations) == len(steps)


class TestSubtitleGenerator:
    """Tests for SubtitleGenerator class."""
    
    def test_subtitle_generator_initialization(self):
        """Test SubtitleGenerator initialization."""
        generator = SubtitleGenerator()
        assert generator is not None
    
    def test_generate_subtitles(self):
        """Test generating subtitles."""
        generator = SubtitleGenerator()
        
        narrations = ["First step", "Second step"]
        timings = [0.0, 5.0]
        
        subtitles = generator.generate_subtitles(narrations, timings, language="en")
        
        assert len(subtitles) == len(narrations)
        assert isinstance(subtitles[0], Subtitle)
        assert subtitles[0].start_time == 0.0
    
    def test_export_srt(self, tmp_path):
        """Test exporting SRT."""
        generator = SubtitleGenerator()
        
        subtitles = [
            Subtitle(start_time=0.0, end_time=2.0, text="Hello", language="en"),
            Subtitle(start_time=2.0, end_time=4.0, text="World", language="en")
        ]
        
        output_path = tmp_path / "test.srt"
        result = generator.export_srt(subtitles, output_path)
        
        assert result == True
        assert output_path.exists()
        assert "Hello" in output_path.read_text()


class TestVideoSynthesizer:
    """Tests for VideoSynthesizer class."""
    
    def test_video_synthesizer_initialization(self):
        """Test VideoSynthesizer initialization."""
        config = VideoConfig(frame_rate=30)
        synthesizer = VideoSynthesizer(config)
        
        assert synthesizer.config.frame_rate == 30

