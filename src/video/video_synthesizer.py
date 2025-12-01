"""
Video Synthesizer - Main orchestration for video generation.
Part of Feature: Video Tutorial Synthesizer (v2.0)
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from src.video.frame_generator import FrameGenerator
from src.video.narration import NarrationEngine, TTSClient
from src.video.subtitle_generator import SubtitleGenerator
from src.video.renderer import VideoRenderer
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class VideoConfig:
    """Video generation configuration."""
    frame_rate: int = 30
    frame_duration: float = 3.0  # seconds per screenshot
    transition_type: str = "ken_burns"
    voice: str = "alloy"
    language: str = "de"
    include_subtitles: bool = True
    include_narration: bool = True


class VideoSynthesizer:
    """
    Synthesizes video tutorials from documentation sessions.
    Combines screenshots, narration, and subtitles into professional videos.
    """
    
    def __init__(self, config: Optional[VideoConfig] = None):
        """
        Initialize video synthesizer.
        
        Args:
            config: Optional video configuration
        """
        self.config = config or VideoConfig()
        self.frame_generator = FrameGenerator(
            frame_rate=self.config.frame_rate,
            transition_duration=0.5
        )
        self.narration_engine = NarrationEngine()
        self.tts_client = TTSClient()
        self.subtitle_generator = SubtitleGenerator()
        self.renderer = VideoRenderer()
    
    def generate_video(
        self,
        session_data: Dict[str, Any],
        screenshot_paths: List[Path],
        output_path: Path,
        title: Optional[str] = None
    ) -> bool:
        """
        Generate video from session data and screenshots.
        
        Args:
            session_data: Session data with steps
            screenshot_paths: List of screenshot paths
            output_path: Output video path
            title: Optional video title
            
        Returns:
            True if successful
        """
        try:
            steps = session_data.get('steps', [])
            
            # Generate frames
            logger.info("Generating video frames...")
            frames = self.frame_generator.generate_frames(
                screenshot_paths,
                frame_duration=self.config.frame_duration,
                transition_type=self.config.transition_type
            )
            
            if not frames:
                logger.error("No frames generated")
                return False
            
            # Generate narration
            audio_path = None
            if self.config.include_narration:
                logger.info("Generating narration...")
                narrations = self.narration_engine.generate_narration_script(
                    steps,
                    language=self.config.language
                )
                
                # Synthesize speech
                narration_text = " ".join(narrations)
                audio_path = output_path.parent / f"{output_path.stem}_audio.mp3"
                audio_data = self.tts_client.synthesize_speech(
                    narration_text,
                    voice=self.config.voice,
                    language=self.config.language,
                    output_path=audio_path
                )
                
                if not audio_data:
                    logger.warning("Could not generate audio, continuing without")
                    audio_path = None
            
            # Generate subtitles
            subtitle_path = None
            if self.config.include_subtitles and narrations:
                logger.info("Generating subtitles...")
                # Calculate timings (simplified - would sync with audio in production)
                timings = [i * self.config.frame_duration for i in range(len(narrations))]
                subtitles = self.subtitle_generator.generate_subtitles(
                    narrations,
                    timings,
                    language=self.config.language
                )
                
                subtitle_path = output_path.with_suffix('.srt')
                self.subtitle_generator.export_srt(subtitles, subtitle_path)
            
            # Render video
            logger.info("Rendering video...")
            success = self.renderer.render_video(
                frames,
                audio_path=audio_path,
                output_path=output_path,
                frame_rate=self.config.frame_rate
            )
            
            if success:
                logger.info(f"Video generated: {output_path}")
                if subtitle_path:
                    logger.info(f"Subtitles: {subtitle_path}")
            
            return success
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            return False

