"""
Video Renderer - Renders video from frames and audio.
Part of Feature: Video Tutorial Synthesizer (v2.0)
"""

import subprocess
from pathlib import Path
from typing import List, Optional
import numpy as np

from src.utils.logger import get_logger

logger = get_logger(__name__)


class VideoRenderer:
    """
    Renders video from frames and audio using FFmpeg.
    Creates MP4/WebM videos for tutorials.
    """
    
    def __init__(self, ffmpeg_path: Optional[str] = None):
        """
        Initialize video renderer.
        
        Args:
            ffmpeg_path: Optional path to FFmpeg executable
        """
        self.ffmpeg_path = ffmpeg_path or "ffmpeg"
    
    def render_video(
        self,
        frames: List[np.ndarray],
        audio_path: Optional[Path] = None,
        output_path: Path = Path("output.mp4"),
        frame_rate: int = 30,
        codec: str = "libx264"
    ) -> bool:
        """
        Render video from frames.
        
        Args:
            frames: List of frame arrays
            audio_path: Optional audio file path
            output_path: Output video path
            frame_rate: Frames per second
            codec: Video codec
            
        Returns:
            True if successful
        """
        if not frames:
            logger.error("No frames to render")
            return False
        
        try:
            # Save frames as temporary images
            temp_dir = Path("data/temp_frames")
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            frame_files = []
            for i, frame in enumerate(frames):
                frame_file = temp_dir / f"frame_{i:06d}.png"
                from PIL import Image
                Image.fromarray(frame).save(frame_file)
                frame_files.append(frame_file)
            
            # Build FFmpeg command
            cmd = [
                self.ffmpeg_path,
                "-y",  # Overwrite output
                "-framerate", str(frame_rate),
                "-i", str(temp_dir / "frame_%06d.png"),
            ]
            
            if audio_path and audio_path.exists():
                cmd.extend(["-i", str(audio_path)])
                cmd.extend(["-c:v", codec])
                cmd.extend(["-c:a", "aac"])
                cmd.extend(["-shortest"])  # Match video to audio length
            else:
                cmd.extend(["-c:v", codec])
                cmd.extend(["-pix_fmt", "yuv420p"])
            
            cmd.append(str(output_path))
            
            # Run FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Video rendered: {output_path}")
                # Cleanup temp frames
                for frame_file in frame_files:
                    try:
                        frame_file.unlink()
                    except:
                        pass
                return True
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error rendering video: {e}")
            return False

