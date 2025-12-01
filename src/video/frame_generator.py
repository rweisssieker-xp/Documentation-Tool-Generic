"""
Frame Generator - Generates video frames from screenshots.
Part of Feature: Video Tutorial Synthesizer (v2.0)
"""

from pathlib import Path
from typing import List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from src.utils.logger import get_logger

logger = get_logger(__name__)


class FrameGenerator:
    """
    Generates video frames from screenshots with transitions.
    Supports Ken Burns effect and other transitions.
    """
    
    def __init__(self, frame_rate: int = 30, transition_duration: float = 0.5):
        """
        Initialize frame generator.
        
        Args:
            frame_rate: Frames per second
            transition_duration: Transition duration in seconds
        """
        self.frame_rate = frame_rate
        self.transition_duration = transition_duration
        self.transition_frames = int(frame_rate * transition_duration)
    
    def generate_frames(
        self,
        screenshot_paths: List[Path],
        frame_duration: float = 3.0,
        transition_type: str = "ken_burns"
    ) -> List[np.ndarray]:
        """
        Generate video frames from screenshots.
        
        Args:
            screenshot_paths: List of screenshot paths
            frame_duration: Duration per screenshot in seconds
            transition_type: Transition type ("ken_burns", "fade", "slide")
            
        Returns:
            List of frame arrays (numpy arrays)
        """
        frames = []
        
        for i, screenshot_path in enumerate(screenshot_paths):
            if not screenshot_path.exists():
                logger.warning(f"Screenshot not found: {screenshot_path}")
                continue
            
            try:
                img = Image.open(screenshot_path)
                img = img.convert('RGB')
                
                # Generate frames for this screenshot
                screenshot_frames = int(self.frame_rate * frame_duration)
                
                for frame_idx in range(screenshot_frames):
                    if transition_type == "ken_burns" and i > 0:
                        # Ken Burns effect: zoom and pan
                        frame = self._apply_ken_burns(img, frame_idx, screenshot_frames)
                    else:
                        frame = np.array(img)
                    
                    frames.append(frame)
                
                # Add transition frames between screenshots
                if i < len(screenshot_paths) - 1:
                    next_img_path = screenshot_paths[i + 1]
                    if next_img_path.exists():
                        next_img = Image.open(next_img_path).convert('RGB')
                        transition_frames = self._generate_transition(img, next_img, transition_type)
                        frames.extend(transition_frames)
                
            except Exception as e:
                logger.error(f"Error processing screenshot {screenshot_path}: {e}")
                continue
        
        return frames
    
    def _apply_ken_burns(self, img: Image.Image, frame_idx: int, total_frames: int) -> np.ndarray:
        """Apply Ken Burns effect (zoom and pan)."""
        width, height = img.size
        
        # Zoom factor (1.0 to 1.2)
        zoom_start = 1.0
        zoom_end = 1.2
        zoom = zoom_start + (zoom_end - zoom_start) * (frame_idx / total_frames)
        
        # Pan (center to top-left)
        pan_x = (frame_idx / total_frames) * 0.1 * width
        pan_y = (frame_idx / total_frames) * 0.1 * height
        
        # Calculate crop box
        new_width = int(width / zoom)
        new_height = int(height / zoom)
        
        left = int(pan_x)
        top = int(pan_y)
        right = left + new_width
        bottom = top + new_height
        
        # Crop and resize
        cropped = img.crop((left, top, min(right, width), min(bottom, height)))
        resized = cropped.resize((width, height), Image.Resampling.LANCZOS)
        
        return np.array(resized)
    
    def _generate_transition(
        self,
        img1: Image.Image,
        img2: Image.Image,
        transition_type: str
    ) -> List[np.ndarray]:
        """Generate transition frames between two images."""
        frames = []
        
        if transition_type == "fade":
            for i in range(self.transition_frames):
                alpha = i / self.transition_frames
                blended = Image.blend(img1, img2, alpha)
                frames.append(np.array(blended))
        elif transition_type == "slide":
            width, height = img1.size
            for i in range(self.transition_frames):
                offset = int((i / self.transition_frames) * width)
                # Create composite with sliding effect
                composite = Image.new('RGB', (width, height))
                composite.paste(img1, (0, 0))
                composite.paste(img2, (offset - width, 0))
                frames.append(np.array(composite))
        else:
            # Default: crossfade
            for i in range(self.transition_frames):
                alpha = i / self.transition_frames
                blended = Image.blend(img1, img2, alpha)
                frames.append(np.array(blended))
        
        return frames

