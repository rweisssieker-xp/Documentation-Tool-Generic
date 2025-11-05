"""
Privacy-Masking: Automatische Schwärzung von Bereichen
"""

import yaml
import re
from PIL import Image, ImageDraw
from pathlib import Path
from typing import List, Dict, Optional
import os
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PrivacyMask:
    """Verwaltet Privacy-Masking für Screenshots"""
    
    def __init__(self, config_path: Optional[Path] = None, auto_detect_enabled: bool = True):
        """
        Initialisiert den Privacy Mask
        
        Args:
            config_path: Pfad zur YAML-Konfigurationsdatei
            auto_detect_enabled: Ob automatische Erkennung aktiviert sein soll
        """
        self.enabled = os.getenv('PRIVACY_MASK_ENABLED', 'false').lower() == 'true'
        self.mask_regions = []
        self.auto_detect_enabled = auto_detect_enabled
        
        # Pattern für personenbezogene Daten
        self.patterns = {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'\b\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b'),
            'credit_card': re.compile(r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b'),
            'date_of_birth': re.compile(r'\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b'),
            'ip_address': re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
        }
        
        if config_path and config_path.exists():
            self.load_config(config_path)
        else:
            # Lade Standard-Config falls vorhanden
            default_config = Path("config") / "privacy_mask.yml"
            if default_config.exists():
                self.load_config(default_config)
    
    def load_config(self, config_path: Path):
        """
        Lädt Mask-Konfiguration aus YAML
        
        Args:
            config_path: Pfad zur YAML-Datei
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            self.enabled = config.get('enabled', False)
            self.mask_regions = config.get('regions', [])
        
        except Exception as e:
            logger.warning(f"Fehler beim Laden der Privacy-Mask-Konfiguration: {e}", exc_info=True)
            self.mask_regions = []
    
    def apply_mask(self, image_path: Path, output_path: Optional[Path] = None, ocr_text: Optional[str] = None) -> Path:
        """
        Wendet Masking auf ein Bild an
        
        Args:
            image_path: Pfad zum Eingabebild
            output_path: Pfad zum Ausgabebild (None = überschreibt Original)
            ocr_text: Optional OCR-Text für automatische Erkennung
            
        Returns:
            Pfad zum gemaskten Bild
        """
        if not self.enabled:
            return image_path
        
        try:
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)
            
            # Wende manuelle Mask-Regionen an
            for region in self.mask_regions:
                region_type = region.get('type', 'rectangle')
                
                if region_type == 'rectangle':
                    self._apply_rectangle_mask(draw, img.size, region)
                elif region_type == 'circle':
                    self._apply_circle_mask(draw, img.size, region)
                elif region_type == 'polygon':
                    self._apply_polygon_mask(draw, img.size, region)
            
            # Automatische Erkennung falls aktiviert
            if self.auto_detect_enabled and ocr_text:
                self._auto_detect_and_mask(draw, img.size, ocr_text)
            
            # Speichere gemasktes Bild
            if output_path is None:
                output_path = image_path
            
            img.save(output_path, 'PNG')
            return output_path
        
        except Exception as e:
            logger.error(f"Fehler beim Anwenden des Privacy-Masks: {e}", exc_info=True)
            return image_path
    
    def _auto_detect_and_mask(self, draw: ImageDraw.Draw, image_size: tuple, ocr_text: str):
        """
        Erkennt automatisch personenbezogene Daten im OCR-Text und maskiert sie
        
        Args:
            draw: ImageDraw-Objekt
            image_size: Bildgröße (width, height)
            ocr_text: OCR-Text zum Analysieren
        """
        # Diese Methode würde normalerweise OCR-Positionen verwenden
        # Für eine einfachere Implementierung verwenden wir Pattern-Matching
        # und maskieren potenzielle Bereiche
        
        detected_regions = []
        
        # Suche nach Pattern im Text
        for pattern_name, pattern in self.patterns.items():
            matches = pattern.findall(ocr_text)
            if matches:
                # Für jedes Match: Erstelle eine Mask-Region
                # Hinweis: Ohne OCR-Positionen können wir nur approximieren
                # Eine vollständige Implementierung würde OCR-Daten mit Koordinaten benötigen
                for match in matches[:5]:  # Maximal 5 Matches pro Pattern
                    # Approximiere Position basierend auf Textlänge
                    # In einer echten Implementierung würden wir OCR-Koordinaten verwenden
                    detected_regions.append({
                        'type': 'rectangle',
                        'x': 0.1,
                        'y': 0.1 + len(detected_regions) * 0.05,
                        'width': 0.3,
                        'height': 0.03,
                        'pattern': pattern_name,
                        'matched': match
                    })
        
        # Wende erkannte Regionen an
        for region in detected_regions:
            self._apply_rectangle_mask(draw, image_size, region)
    
    def _apply_rectangle_mask(self, draw: ImageDraw.Draw, image_size: tuple, region: Dict):
        """
        Wendet rechteckige Maske an
        
        Args:
            draw: ImageDraw-Objekt
            image_size: Bildgröße (width, height)
            region: Region-Konfiguration
        """
        x = region.get('x', 0)
        y = region.get('y', 0)
        width = region.get('width', 0)
        height = region.get('height', 0)
        
        # Normalisiere Koordinaten (0-1) zu Pixel-Koordinaten
        if x <= 1.0:
            x = int(x * image_size[0])
        if y <= 1.0:
            y = int(y * image_size[1])
        if width <= 1.0:
            width = int(width * image_size[0])
        if height <= 1.0:
            height = int(height * image_size[1])
        
        # Zeichne schwarzes Rechteck
        draw.rectangle([x, y, x + width, y + height], fill='black')
    
    def _apply_circle_mask(self, draw: ImageDraw.Draw, image_size: tuple, region: Dict):
        """
        Wendet kreisförmige Maske an
        
        Args:
            draw: ImageDraw-Objekt
            image_size: Bildgröße (width, height)
            region: Region-Konfiguration
        """
        center_x = region.get('center_x', 0.5)
        center_y = region.get('center_y', 0.5)
        radius = region.get('radius', 0.1)
        
        # Normalisiere Koordinaten
        if center_x <= 1.0:
            center_x = int(center_x * image_size[0])
        if center_y <= 1.0:
            center_y = int(center_y * image_size[1])
        if radius <= 1.0:
            radius = int(radius * min(image_size))
        
        # Zeichne schwarzen Kreis
        bbox = [
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius
        ]
        draw.ellipse(bbox, fill='black')
    
    def _apply_polygon_mask(self, draw: ImageDraw.Draw, image_size: tuple, region: Dict):
        """
        Wendet polygonförmige Maske an
        
        Args:
            draw: ImageDraw-Objekt
            image_size: Bildgröße (width, height)
            region: Region-Konfiguration
        """
        points = region.get('points', [])
        
        if len(points) < 3:
            return
        
        # Normalisiere Koordinaten
        normalized_points = []
        for point in points:
            x, y = point
            if x <= 1.0:
                x = int(x * image_size[0])
            if y <= 1.0:
                y = int(y * image_size[1])
            normalized_points.append((x, y))
        
        # Zeichne schwarzes Polygon
        draw.polygon(normalized_points, fill='black')
    
    def add_region(self, region_type: str, **kwargs):
        """
        Fügt eine Mask-Region hinzu
        
        Args:
            region_type: Typ der Region ('rectangle', 'circle', 'polygon')
            **kwargs: Region-Parameter
        """
        region = {'type': region_type, **kwargs}
        self.mask_regions.append(region)
    
    def save_config(self, config_path: Path):
        """
        Speichert Mask-Konfiguration
        
        Args:
            config_path: Pfad zur YAML-Datei
        """
        config = {
            'enabled': self.enabled,
            'regions': self.mask_regions
        }
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)


