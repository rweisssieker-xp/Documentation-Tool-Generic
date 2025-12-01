"""
Subtitle Generator - Generates subtitles for video tutorials.
Part of Feature: Video Tutorial Synthesizer (v2.0)
"""

from typing import List, Dict, Any, Tuple
from pathlib import Path
from dataclasses import dataclass

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Subtitle:
    """A subtitle entry."""
    start_time: float  # seconds
    end_time: float  # seconds
    text: str
    language: str


class SubtitleGenerator:
    """
    Generates subtitles for video tutorials.
    Creates SRT/VTT format subtitles with timing.
    """
    
    def __init__(self):
        """Initialize subtitle generator."""
        pass
    
    def generate_subtitles(
        self,
        narrations: List[str],
        timings: List[float],
        language: str = "de"
    ) -> List[Subtitle]:
        """
        Generate subtitles from narrations and timings.
        
        Args:
            narrations: List of narration texts
            timings: List of start times for each narration
            language: Language code
            
        Returns:
            List of Subtitle objects
        """
        subtitles = []
        current_time = 0.0
        
        for i, (narration, start_time) in enumerate(zip(narrations, timings)):
            # Estimate duration based on text length (average reading speed: 150 words/min)
            words = len(narration.split())
            duration = (words / 150) * 60  # seconds
            duration = max(2.0, min(duration, 7.0))  # Clamp between 2-7 seconds
            
            subtitle = Subtitle(
                start_time=start_time,
                end_time=start_time + duration,
                text=narration,
                language=language
            )
            subtitles.append(subtitle)
            current_time = start_time + duration
        
        return subtitles
    
    def export_srt(self, subtitles: List[Subtitle], output_path: Path) -> bool:
        """
        Export subtitles as SRT format.
        
        Args:
            subtitles: List of subtitles
            output_path: Output file path
            
        Returns:
            True if successful
        """
        try:
            srt_content = []
            
            for i, subtitle in enumerate(subtitles, 1):
                start_time = self._format_srt_time(subtitle.start_time)
                end_time = self._format_srt_time(subtitle.end_time)
                
                srt_content.append(f"{i}")
                srt_content.append(f"{start_time} --> {end_time}")
                srt_content.append(subtitle.text)
                srt_content.append("")
            
            output_path.write_text("\n".join(srt_content), encoding='utf-8')
            return True
        except Exception as e:
            logger.error(f"Error exporting SRT: {e}")
            return False
    
    def export_vtt(self, subtitles: List[Subtitle], output_path: Path) -> bool:
        """
        Export subtitles as VTT format.
        
        Args:
            subtitles: List of subtitles
            output_path: Output file path
            
        Returns:
            True if successful
        """
        try:
            vtt_content = ["WEBVTT", ""]
            
            for subtitle in subtitles:
                start_time = self._format_vtt_time(subtitle.start_time)
                end_time = self._format_vtt_time(subtitle.end_time)
                
                vtt_content.append(f"{start_time} --> {end_time}")
                vtt_content.append(subtitle.text)
                vtt_content.append("")
            
            output_path.write_text("\n".join(vtt_content), encoding='utf-8')
            return True
        except Exception as e:
            logger.error(f"Error exporting VTT: {e}")
            return False
    
    def _format_srt_time(self, seconds: float) -> str:
        """Format time for SRT (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _format_vtt_time(self, seconds: float) -> str:
        """Format time for VTT (HH:MM:SS.mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

