"""
Video-Export: Erstellt animierte Videos aus Screenshots
"""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import os

from src.utils.logger import get_logger

logger = get_logger(__name__)


class VideoExporter:
    """Exportiert Screenshots als animiertes Video"""
    
    def __init__(self, fps: int = 2, duration_per_step: float = 3.0):
        """
        Initialisiert den Video Exporter
        
        Args:
            fps: Frames per Second
            duration_per_step: Dauer pro Schritt in Sekunden
        """
        self.fps = fps
        self.duration_per_step = duration_per_step
    
    def export_video(
        self,
        steps: List[Dict],
        output_path: Path,
        title: str = "Handbuch-Video",
        include_transitions: bool = True,
        include_voice_over: bool = False
    ) -> Path:
        """
        Exportiert Video aus Screenshots
        
        Args:
            steps: Liste von Schritten
            output_path: Ausgabepfad
            title: Video-Titel
            include_transitions: Ob Übergänge zwischen Schritten eingefügt werden sollen
            include_voice_over: Ob Voice-Over (TTS) eingefügt werden soll
            
        Returns:
            Pfad zur erstellten Video-Datei
        """
        try:
            # Versuche OpenCV für Video-Erstellung
            import cv2
            import numpy as np
            
            return self._export_with_opencv(steps, output_path, title, include_transitions)
        
        except ImportError:
            try:
                # Fallback: Verwende imageio
                import imageio
                return self._export_with_imageio(steps, output_path, title, include_transitions)
            
            except ImportError:
                # Fallback: GIF mit PIL
                logger.warning("cv2 und imageio nicht verfügbar, verwende GIF-Export")
                return self._export_gif(steps, output_path, title)
    
    def _export_with_opencv(
        self,
        steps: List[Dict],
        output_path: Path,
        title: str,
        include_transitions: bool
    ) -> Path:
        """Exportiert Video mit OpenCV"""
        import cv2
        import numpy as np
        
        if not steps:
            raise ValueError("Keine Schritte zum Exportieren vorhanden")
        
        # Lade erstes Bild für Größe
        first_screenshot = Path(steps[0].get('screenshot_path', ''))
        if not first_screenshot.exists():
            raise ValueError(f"Screenshot nicht gefunden: {first_screenshot}")
        
        first_img = cv2.imread(str(first_screenshot))
        height, width = first_img.shape[:2]
        
        # Video Writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_path = output_path.with_suffix('.mp4')
        video_writer = cv2.VideoWriter(str(video_path), fourcc, self.fps, (width, height))
        
        frames_per_step = int(self.fps * self.duration_per_step)
        
        for i, step in enumerate(steps):
            screenshot_path = Path(step.get('screenshot_path', ''))
            
            if not screenshot_path.exists():
                logger.warning(f"Screenshot nicht gefunden: {screenshot_path}")
                continue
            
            img = cv2.imread(str(screenshot_path))
            
            # Resize falls nötig
            if img.shape[:2] != (height, width):
                img = cv2.resize(img, (width, height))
            
            # Füge Text-Overlay hinzu
            step_number = step.get('step_number', i + 1)
            window_title = step.get('window_title', '')
            
            # Zeichne Text
            cv2.putText(
                img,
                f"Schritt {step_number}: {window_title[:30]}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2
            )
            
            # Schreibe Frames
            for _ in range(frames_per_step):
                video_writer.write(img)
            
            # Übergang zum nächsten Schritt
            if include_transitions and i < len(steps) - 1:
                next_screenshot = Path(steps[i + 1].get('screenshot_path', ''))
                if next_screenshot.exists():
                    next_img = cv2.imread(str(next_screenshot))
                    if next_img.shape[:2] != (height, width):
                        next_img = cv2.resize(next_img, (width, height))
                    
                    # Fade-Übergang
                    transition_frames = int(self.fps * 0.5)  # 0.5 Sekunden Übergang
                    for j in range(transition_frames):
                        alpha = j / transition_frames
                        blended = cv2.addWeighted(img, 1 - alpha, next_img, alpha, 0)
                        video_writer.write(blended)
        
        video_writer.release()
        
        logger.info(f"Video exportiert: {video_path}")
        return video_path
    
    def _export_with_imageio(
        self,
        steps: List[Dict],
        output_path: Path,
        title: str,
        include_transitions: bool
    ) -> Path:
        """Exportiert Video mit imageio"""
        import imageio
        from PIL import Image
        
        frames = []
        frames_per_step = int(self.fps * self.duration_per_step)
        
        for step in steps:
            screenshot_path = Path(step.get('screenshot_path', ''))
            
            if not screenshot_path.exists():
                continue
            
            img = Image.open(screenshot_path)
            
            # Füge Text-Overlay hinzu
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            step_number = step.get('step_number', '?')
            window_title = step.get('window_title', '')
            text = f"Schritt {step_number}: {window_title[:30]}"
            
            draw.text((10, 10), text, fill=(255, 255, 255), font=font)
            
            # Füge Frames hinzu
            for _ in range(frames_per_step):
                frames.append(img.copy())
        
        # Exportiere als GIF
        gif_path = output_path.with_suffix('.gif')
        imageio.mimsave(str(gif_path), frames, fps=self.fps)
        
        logger.info(f"GIF exportiert: {gif_path}")
        return gif_path
    
    def _export_gif(self, steps: List[Dict], output_path: Path, title: str) -> Path:
        """Exportiert als GIF (Fallback)"""
        from PIL import Image, ImageDraw, ImageFont
        
        frames = []
        frames_per_step = int(self.fps * self.duration_per_step)
        
        for step in steps:
            screenshot_path = Path(step.get('screenshot_path', ''))
            
            if not screenshot_path.exists():
                continue
            
            img = Image.open(screenshot_path)
            
            # Füge Text hinzu
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            step_number = step.get('step_number', '?')
            window_title = step.get('window_title', '')
            text = f"Schritt {step_number}: {window_title[:30]}"
            
            draw.text((10, 10), text, fill=(255, 255, 255), font=font)
            
            # Füge Frames hinzu
            for _ in range(frames_per_step):
                frames.append(img.copy())
        
        # Speichere GIF
        gif_path = output_path.with_suffix('.gif')
        if frames:
            frames[0].save(
                str(gif_path),
                save_all=True,
                append_images=frames[1:],
                duration=int(1000 / self.fps),
                loop=0
            )
        
        logger.info(f"GIF exportiert: {gif_path}")
        return gif_path

