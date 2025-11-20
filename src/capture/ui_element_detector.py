"""
UI-Element-Erkennung: Erkennt automatisch UI-Elemente in Screenshots
"""

from pathlib import Path
from typing import List, Dict, Optional
from PIL import Image
import numpy as np

from src.utils.logger import get_logger

logger = get_logger(__name__)


class UIElementDetector:
    """Erkennt UI-Elemente in Screenshots"""
    
    def __init__(self, min_button_size: int = 30, min_field_size: int = 50, use_template_matching: bool = True):
        """
        Initialisiert den UI Element Detector
        
        Args:
            min_button_size: Minimale Button-Größe in Pixeln
            min_field_size: Minimale Feld-Größe in Pixeln
            use_template_matching: Ob Template Matching verwendet werden soll
        """
        self.min_button_size = min_button_size
        self.min_field_size = min_field_size
        self.use_template_matching = use_template_matching
        self.templates = self._load_templates() if use_template_matching else {}
    
    def _load_templates(self) -> Dict:
        """Lädt Template-Bilder für Template Matching"""
        templates = {}
        
        # Template-Verzeichnis (falls vorhanden)
        template_dir = Path("templates") / "ui_elements"
        
        if template_dir.exists():
            try:
                # Lade Button-Templates
                button_templates = list(template_dir.glob("button_*.png"))
                if button_templates:
                    templates['buttons'] = []
                    for template_path in button_templates:
                        try:
                            import cv2
                            template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
                            if template is not None:
                                templates['buttons'].append(template)
                        except Exception as e:
                            logger.debug(f"Konnte Template {template_path} nicht laden: {e}")
                
                # Lade Input-Field-Templates
                input_templates = list(template_dir.glob("input_*.png"))
                if input_templates:
                    templates['input_fields'] = []
                    for template_path in input_templates:
                        try:
                            import cv2
                            template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
                            if template is not None:
                                templates['input_fields'].append(template)
                        except Exception as e:
                            logger.debug(f"Konnte Template {template_path} nicht laden: {e}")
            
            except Exception as e:
                logger.debug(f"Fehler beim Laden von Templates: {e}")
        
        return templates
    
    def _template_match(self, image: np.ndarray, templates: List[np.ndarray], threshold: float = 0.7) -> List[Dict]:
        """
        Führt Template Matching durch
        
        Args:
            image: Graustufenbild
            templates: Liste von Template-Bildern
            threshold: Schwellenwert für Matching (0.0-1.0)
            
        Returns:
            Liste von erkannten Elementen mit Koordinaten
        """
        matches = []
        
        try:
            import cv2
            
            for template in templates:
                # Template Matching
                result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
                locations = np.where(result >= threshold)
                
                # Finde alle Matches
                for pt in zip(*locations[::-1]):
                    matches.append({
                        'x': int(pt[0]),
                        'y': int(pt[1]),
                        'width': template.shape[1],
                        'height': template.shape[0],
                        'confidence': float(result[pt[1], pt[0]])
                    })
            
            # Non-Maximum Suppression um Duplikate zu entfernen
            matches = self._non_max_suppression(matches, overlap_threshold=0.5)
            
        except ImportError:
            logger.warning("OpenCV nicht verfügbar für Template Matching")
        except Exception as e:
            logger.debug(f"Fehler bei Template Matching: {e}")
        
        return matches
    
    def _non_max_suppression(self, matches: List[Dict], overlap_threshold: float = 0.5) -> List[Dict]:
        """
        Entfernt überlappende Matches (Non-Maximum Suppression)
        
        Args:
            matches: Liste von Matches
            overlap_threshold: Schwellenwert für Überlappung
            
        Returns:
            Gefilterte Liste von Matches
        """
        if not matches:
            return []
        
        # Sortiere nach Confidence (höchste zuerst)
        matches = sorted(matches, key=lambda x: x.get('confidence', 0.0), reverse=True)
        
        filtered = []
        used = set()
        
        for i, match in enumerate(matches):
            if i in used:
                continue
            
            x1 = match['x']
            y1 = match['y']
            x2 = x1 + match['width']
            y2 = y1 + match['height']
            
            filtered.append(match)
            used.add(i)
            
            # Markiere überlappende Matches
            for j, other_match in enumerate(matches[i+1:], start=i+1):
                if j in used:
                    continue
                
                ox1 = other_match['x']
                oy1 = other_match['y']
                ox2 = ox1 + other_match['width']
                oy2 = oy1 + other_match['height']
                
                # Berechne Überlappung
                overlap_area = max(0, min(x2, ox2) - max(x1, ox1)) * max(0, min(y2, oy2) - max(y1, oy1))
                match_area = match['width'] * match['height']
                other_area = other_match['width'] * other_match['height']
                overlap_ratio = overlap_area / min(match_area, other_area)
                
                if overlap_ratio > overlap_threshold:
                    used.add(j)
        
        return filtered
    
    def detect_elements(self, image_path: Path) -> List[Dict]:
        """
        Erkennt UI-Elemente in einem Screenshot
        
        Args:
            image_path: Pfad zum Screenshot
            
        Returns:
            Liste von erkannten Elementen
        """
        try:
            img = Image.open(image_path)
            img_array = np.array(img)
            
            elements = []
            
            # Erkenne Buttons
            buttons = self._detect_buttons(img_array)
            elements.extend(buttons)
            
            # Erkenne Eingabefelder
            input_fields = self._detect_input_fields(img_array)
            elements.extend(input_fields)
            
            # Erkenne Dropdown-Menüs
            dropdowns = self._detect_dropdowns(img_array)
            elements.extend(dropdowns)
            
            # Erkenne Checkboxen/Radio-Buttons
            checkboxes = self._detect_checkboxes(img_array)
            elements.extend(checkboxes)
            
            logger.info(f"{len(elements)} UI-Elemente erkannt in {image_path.name}")
            return elements
        
        except Exception as e:
            logger.error(f"Fehler bei UI-Element-Erkennung: {e}", exc_info=True)
            return []
    
    def _detect_buttons(self, img_array: np.ndarray) -> List[Dict]:
        """Erkennt Buttons mit OpenCV Edge-Detection und Template Matching"""
        elements = []
        
        try:
            import cv2
            
            # Konvertiere zu Graustufen falls nötig
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Verwende Template Matching falls Templates verfügbar sind
            if self.use_template_matching and self.templates.get('buttons'):
                template_matches = self._template_match(gray, self.templates['buttons'], threshold=0.6)
                for match in template_matches:
                    elements.append({
                        'type': 'button',
                        'bbox': {
                            'x': match['x'],
                            'y': match['y'],
                            'width': match['width'],
                            'height': match['height']
                        },
                        'confidence': match['confidence']
                    })
            
            # Edge-Detection als zusätzliche Methode
            edges = cv2.Canny(gray, 50, 150)
            
            # Finde Konturen
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            height, width = gray.shape
            
            for contour in contours:
                # Berechne Bounding Box
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filtere nach Größe (Button-ähnliche Größe)
                if (self.min_button_size <= w <= width * 0.3 and 
                    self.min_button_size <= h <= height * 0.15 and
                    w / h >= 1.5):  # Buttons sind typischerweise breiter als hoch
                    
                    # Prüfe ob Bereich Text enthält (OCR)
                    roi = gray[y:y+h, x:x+w]
                    has_text = self._check_for_text(roi)
                    
                    # Prüfe ob bereits durch Template Matching erkannt
                    already_detected = False
                    for existing in elements:
                        ex_bbox = existing['bbox']
                        # Prüfe auf Überlappung
                        if (abs(ex_bbox['x'] - x) < 10 and abs(ex_bbox['y'] - y) < 10):
                            already_detected = True
                            break
                    
                    if not already_detected:
                        elements.append({
                            'type': 'button',
                            'bbox': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)},
                            'confidence': 0.7 if has_text else 0.5
                        })
        
        except ImportError:
            logger.warning("OpenCV nicht verfügbar, verwende vereinfachte Button-Erkennung")
            # Fallback: Vereinfachte Erkennung basierend auf Kontrast
            height, width = img_array.shape[:2]
            if len(img_array.shape) == 3:
                gray = np.mean(img_array, axis=2).astype(np.uint8)
            else:
                gray = img_array
            
            # Suche nach rechteckigen Bereichen mit hohem Kontrast
            # (Vereinfachte Implementierung)
        
        return elements
    
    def _detect_input_fields(self, img_array: np.ndarray) -> List[Dict]:
        """Erkennt Eingabefelder mit Edge-Detection und Template Matching"""
        elements = []
        
        try:
            import cv2
            
            # Konvertiere zu Graustufen
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Verwende Template Matching falls Templates verfügbar sind
            if self.use_template_matching and self.templates.get('input_fields'):
                template_matches = self._template_match(gray, self.templates['input_fields'], threshold=0.6)
                for match in template_matches:
                    elements.append({
                        'type': 'input_field',
                        'bbox': {
                            'x': match['x'],
                            'y': match['y'],
                            'width': match['width'],
                            'height': match['height']
                        },
                        'confidence': match['confidence']
                    })
            
            # Edge-Detection als zusätzliche Methode
            edges = cv2.Canny(gray, 50, 150)
            
            # Finde Konturen
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            height, width = gray.shape
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Eingabefelder sind typischerweise rechteckig und breiter als hoch
                if (self.min_field_size <= w <= width * 0.4 and 
                    self.min_field_size <= h <= height * 0.1 and
                    w / h >= 3.0):  # Eingabefelder sind viel breiter als hoch
                    
                    # Prüfe ob bereits durch Template Matching erkannt
                    already_detected = False
                    for existing in elements:
                        ex_bbox = existing['bbox']
                        if (abs(ex_bbox['x'] - x) < 10 and abs(ex_bbox['y'] - y) < 10):
                            already_detected = True
                            break
                    
                    if not already_detected:
                        elements.append({
                            'type': 'input_field',
                            'bbox': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)},
                            'confidence': 0.6
                        })
        
        except ImportError:
            logger.warning("OpenCV nicht verfügbar für Input-Field-Erkennung")
        
        return elements
    
    def _detect_dropdowns(self, img_array: np.ndarray) -> List[Dict]:
        """Erkennt Dropdown-Menüs"""
        elements = []
        
        try:
            import cv2
            
            # Dropdowns sind ähnlich wie Eingabefelder, aber mit Pfeil-Symbol
            # Verwende ähnliche Erkennung wie Input-Fields
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            height, width = gray.shape
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Dropdowns sind ähnlich wie Input-Fields
                if (self.min_field_size <= w <= width * 0.4 and 
                    self.min_field_size <= h <= height * 0.1 and
                    2.0 <= w / h <= 6.0):
                    
                    elements.append({
                        'type': 'dropdown',
                        'bbox': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)},
                        'confidence': 0.5
                    })
        
        except ImportError:
            pass
        
        return elements
    
    def _detect_checkboxes(self, img_array: np.ndarray) -> List[Dict]:
        """Erkennt Checkboxen und Radio-Buttons"""
        elements = []
        
        try:
            import cv2
            
            # Checkboxen sind kleine quadratische Bereiche
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Checkboxen sind typischerweise quadratisch und klein
                if (10 <= w <= 30 and 10 <= h <= 30 and 
                    0.7 <= w / h <= 1.3):  # Ungefähr quadratisch
                    
                    elements.append({
                        'type': 'checkbox',
                        'bbox': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)},
                        'confidence': 0.6
                    })
        
        except ImportError:
            pass
        
        return elements
    
    def _check_for_text(self, roi: np.ndarray) -> bool:
        """Prüft ob ROI Text enthält (vereinfacht)"""
        try:
            # Verwende OCR falls verfügbar
            from src.capture.ocr_engine import OCREngine
            ocr = OCREngine()
            if ocr.is_available():
                # Speichere temporäres Bild für OCR
                temp_img = Image.fromarray(roi)
                temp_path = Path("temp_ocr_check.png")
                temp_img.save(temp_path)
                
                text = ocr.extract_text(temp_path)
                if temp_path.exists():
                    temp_path.unlink()
                
                return len(text.strip()) > 0
        except Exception:
            pass
        
        # Fallback: Prüfe auf hohe Varianz (Text hat typischerweise hohe Varianz)
        variance = np.var(roi)
        return variance > 500
    
    def annotate_elements(
        self,
        image_path: Path,
        elements: List[Dict],
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Fügt Annotationen für erkannte Elemente hinzu
        
        Args:
            image_path: Pfad zum Screenshot
            elements: Liste von erkannten Elementen
            output_path: Ausgabepfad (None = überschreibt Original)
            
        Returns:
            Pfad zum annotierten Bild
        """
        try:
            from PIL import ImageDraw, ImageFont
            
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
            
            for i, element in enumerate(elements, start=1):
                element_type = element.get('type', 'unknown')
                bbox = element.get('bbox', {})
                
                x = bbox.get('x', 0)
                y = bbox.get('y', 0)
                width = bbox.get('width', 0)
                height = bbox.get('height', 0)
                
                # Zeichne Box
                color = self._get_color_for_type(element_type)
                draw.rectangle([x, y, x + width, y + height], outline=color, width=2)
                
                # Zeichne Label
                label = f"{i}. {element_type}"
                draw.text((x, y - 15), label, fill=color, font=font)
            
            if output_path is None:
                output_path = image_path
            
            img.save(output_path, format='PNG')
            return output_path
        
        except Exception as e:
            logger.error(f"Fehler beim Annotieren: {e}", exc_info=True)
            return image_path
    
    def _get_color_for_type(self, element_type: str) -> tuple:
        """Gibt Farbe für Element-Typ zurück"""
        colors = {
            'button': (0, 255, 0),      # Grün
            'input_field': (255, 0, 0),  # Rot
            'dropdown': (0, 0, 255),    # Blau
            'checkbox': (255, 165, 0),  # Orange
            'radio': (255, 0, 255)      # Magenta
        }
        return colors.get(element_type, (128, 128, 128))  # Grau als Standard

