"""
Automatische Screenshot-Annotationen: Fügt Pfeile, Boxes und Highlights hinzu
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import os

from src.utils.logger import get_logger

logger = get_logger(__name__)


class AnnotationEngine:
    """Erstellt automatische Annotationen für Screenshots"""
    
    def __init__(self, style: str = "modern"):
        """
        Initialisiert die Annotation-Engine
        
        Args:
            style: Annotation-Stil ("modern", "classic", "minimal")
        """
        self.style = style
    
    def annotate_screenshot(
        self,
        image_path: Path,
        output_path: Optional[Path] = None,
        annotations: Optional[List[Dict]] = None,
        auto_detect: bool = True
    ) -> Path:
        """
        Fügt Annotationen zu einem Screenshot hinzu
        
        Args:
            image_path: Pfad zum Eingabebild
            output_path: Pfad zum Ausgabebild (None = überschreibt Original)
            annotations: Manuelle Annotationen (optional)
            auto_detect: Ob automatische Erkennung aktiviert sein soll
            
        Returns:
            Pfad zum annotierten Bild
        """
        try:
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)
            
            # Lade Annotationen
            all_annotations = annotations or []
            
            if auto_detect:
                auto_annotations = self._auto_detect_elements(img)
                all_annotations.extend(auto_annotations)
            
            # Wende Annotationen an
            for annotation in all_annotations:
                self._apply_annotation(draw, img.size, annotation)
            
            # Speichere annotiertes Bild
            if output_path is None:
                output_path = image_path
            
            img.save(output_path, format='PNG')
            return output_path
        
        except Exception as e:
            logger.error(f"Fehler beim Annotieren des Screenshots: {e}", exc_info=True)
            return image_path
    
    def _apply_annotation(self, draw: ImageDraw.Draw, image_size: Tuple[int, int], annotation: Dict):
        """Wendet eine Annotation an"""
        annotation_type = annotation.get('type', 'box')
        
        if annotation_type == 'box':
            self._draw_box(draw, image_size, annotation)
        elif annotation_type == 'arrow':
            self._draw_arrow(draw, image_size, annotation)
        elif annotation_type == 'circle':
            self._draw_circle(draw, image_size, annotation)
        elif annotation_type == 'highlight':
            self._draw_highlight(draw, image_size, annotation)
        elif annotation_type == 'number':
            self._draw_number(draw, image_size, annotation)
    
    def _draw_box(self, draw: ImageDraw.Draw, image_size: Tuple[int, int], annotation: Dict):
        """Zeichnet eine Box"""
        x = annotation.get('x', 0)
        y = annotation.get('y', 0)
        width = annotation.get('width', 100)
        height = annotation.get('height', 100)
        
        # Konvertiere relative Koordinaten
        if annotation.get('relative', False):
            x = int(x * image_size[0])
            y = int(y * image_size[1])
            width = int(width * image_size[0])
            height = int(height * image_size[1])
        
        color = annotation.get('color', (255, 0, 0))  # Rot
        width_line = annotation.get('line_width', 3)
        
        # Zeichne Rechteck
        draw.rectangle(
            [x, y, x + width, y + height],
            outline=color,
            width=width_line
        )
    
    def _draw_arrow(self, draw: ImageDraw.Draw, image_size: Tuple[int, int], annotation: Dict):
        """Zeichnet einen Pfeil"""
        from_x = annotation.get('from_x', 0)
        from_y = annotation.get('from_y', 0)
        to_x = annotation.get('to_x', 100)
        to_y = annotation.get('to_y', 100)
        
        # Konvertiere relative Koordinaten
        if annotation.get('relative', False):
            from_x = int(from_x * image_size[0])
            from_y = int(from_y * image_size[1])
            to_x = int(to_x * image_size[0])
            to_y = int(to_y * image_size[1])
        
        color = annotation.get('color', (255, 0, 0))
        width_line = annotation.get('line_width', 3)
        
        # Zeichne Linie
        draw.line([from_x, from_y, to_x, to_y], fill=color, width=width_line)
        
        # Zeichne Pfeilspitze
        arrow_size = annotation.get('arrow_size', 10)
        self._draw_arrowhead(draw, from_x, from_y, to_x, to_y, arrow_size, color)
    
    def _draw_arrowhead(self, draw: ImageDraw.Draw, x1: int, y1: int, x2: int, y2: int, size: int, color: Tuple[int, int, int]):
        """Zeichnet Pfeilspitze"""
        import math
        
        # Berechne Winkel
        angle = math.atan2(y2 - y1, x2 - x1)
        
        # Berechne Pfeilspitzen-Punkte
        arrow_x1 = x2 - size * math.cos(angle - math.pi / 6)
        arrow_y1 = y2 - size * math.sin(angle - math.pi / 6)
        arrow_x2 = x2 - size * math.cos(angle + math.pi / 6)
        arrow_y2 = y2 - size * math.sin(angle + math.pi / 6)
        
        # Zeichne Pfeilspitze
        draw.polygon([x2, y2, arrow_x1, arrow_y1, arrow_x2, arrow_y2], fill=color)
    
    def _draw_circle(self, draw: ImageDraw.Draw, image_size: Tuple[int, int], annotation: Dict):
        """Zeichnet einen Kreis"""
        center_x = annotation.get('center_x', 100)
        center_y = annotation.get('center_y', 100)
        radius = annotation.get('radius', 50)
        
        # Konvertiere relative Koordinaten
        if annotation.get('relative', False):
            center_x = int(center_x * image_size[0])
            center_y = int(center_y * image_size[1])
            radius = int(radius * min(image_size[0], image_size[1]))
        
        color = annotation.get('color', (255, 0, 0))
        width_line = annotation.get('line_width', 3)
        
        # Zeichne Ellipse (Kreis)
        bbox = [
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius
        ]
        draw.ellipse(bbox, outline=color, width=width_line)
    
    def _draw_highlight(self, draw: ImageDraw.Draw, image_size: Tuple[int, int], annotation: Dict):
        """Zeichnet Highlight (halbdurchsichtige Box)"""
        x = annotation.get('x', 0)
        y = annotation.get('y', 0)
        width = annotation.get('width', 100)
        height = annotation.get('height', 100)
        
        # Konvertiere relative Koordinaten
        if annotation.get('relative', False):
            x = int(x * image_size[0])
            y = int(y * image_size[1])
            width = int(width * image_size[0])
            height = int(height * image_size[1])
        
        color = annotation.get('color', (255, 255, 0))  # Gelb
        alpha = annotation.get('alpha', 128)  # Halbdurchsichtig
        
        # Erstelle Overlay-Bild für Transparenz
        overlay = Image.new('RGBA', image_size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        overlay_draw.rectangle(
            [x, y, x + width, y + height],
            fill=(color[0], color[1], color[2], alpha)
        )
        
        # Kombiniere mit Original (wird später im annotate_screenshot kombiniert)
        # Für jetzt zeichnen wir einfach eine Box
        draw.rectangle(
            [x, y, x + width, y + height],
            outline=color,
            width=2
        )
    
    def _draw_number(self, draw: ImageDraw.Draw, image_size: Tuple[int, int], annotation: Dict):
        """Zeichnet Nummerierte Annotation"""
        x = annotation.get('x', 0)
        y = annotation.get('y', 0)
        number = annotation.get('number', 1)
        
        # Konvertiere relative Koordinaten
        if annotation.get('relative', False):
            x = int(x * image_size[0])
            y = int(y * image_size[1])
        
        color = annotation.get('color', (255, 255, 255))
        bg_color = annotation.get('bg_color', (255, 0, 0))
        size = annotation.get('size', 20)
        
        # Zeichne Hintergrund-Kreis
        bbox = [x - size, y - size, x + size, y + size]
        draw.ellipse(bbox, fill=bg_color)
        
        # Zeichne Nummer
        try:
            font = ImageFont.truetype("arial.ttf", size=int(size * 0.7))
        except:
            font = ImageFont.load_default()
        
        # Zentriere Text
        text = str(number)
        bbox_text = draw.textbbox((0, 0), text, font=font)
        text_width = bbox_text[2] - bbox_text[0]
        text_height = bbox_text[3] - bbox_text[1]
        
        text_x = x - text_width // 2
        text_y = y - text_height // 2
        
        draw.text((text_x, text_y), text, fill=color, font=font)
    
    def _auto_detect_elements(self, image: Image.Image) -> List[Dict]:
        """Automatische Erkennung von UI-Elementen (vereinfacht)"""
        annotations = []
        
        # Vereinfachte Erkennung: Erkenne helle Bereiche (Buttons, etc.)
        # In einer vollständigen Implementierung würde man hier ML/Computer Vision verwenden
        
        width, height = image.size
        
        # Beispiel: Erkenne Bereiche mit hohem Kontrast
        # Dies ist eine vereinfachte Implementierung
        # Für echte Erkennung würde man OpenCV oder ähnliche Libraries verwenden
        
        return annotations
    
    def create_step_sequence_annotations(
        self,
        steps: List[Dict],
        image_size: Tuple[int, int]
    ) -> List[List[Dict]]:
        """
        Erstellt nummerierte Annotationen für Schritt-Sequenzen
        
        Args:
            steps: Liste von Schritten
            image_size: Bildgröße
            
        Returns:
            Liste von Annotation-Listen (eine pro Schritt)
        """
        annotations_list = []
        
        for i, step in enumerate(steps, start=1):
            annotations = []
            
            # Erstelle Nummerierte Annotation für wichtigen Bereich
            # Beispiel: Zentrum des Bildes
            annotations.append({
                'type': 'number',
                'x': 0.5,  # Relativ
                'y': 0.1,  # Relativ
                'number': i,
                'relative': True,
                'color': (255, 255, 255),
                'bg_color': (0, 100, 200),
                'size': 30
            })
            
            annotations_list.append(annotations)
        
        return annotations_list

