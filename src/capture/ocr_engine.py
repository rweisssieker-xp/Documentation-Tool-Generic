"""
OCR-Engine mit Tesseract-Integration
"""

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from pathlib import Path
from typing import Optional, Dict
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from src.utils.logger import get_logger

logger = get_logger(__name__)


class OCREngine:
    """OCR-Engine für Textextraktion aus Screenshots"""
    
    def __init__(self, language: str = "deu+eng", enable_preprocessing: bool = True, max_workers: int = 2):
        """
        Initialisiert die OCR-Engine
        
        Args:
            language: Tesseract-Sprache (z.B. "deu+eng" für Deutsch und Englisch)
            enable_preprocessing: Ob Bildvorverarbeitung aktiviert sein soll
            max_workers: Maximale Anzahl paralleler OCR-Worker
        """
        self.language = language
        self.enable_preprocessing = enable_preprocessing
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Setze Tesseract-Pfad falls nötig
        self._configure_tesseract_path()
    
    def _configure_tesseract_path(self):
        """Konfiguriert den Tesseract-Pfad"""
        # Prüfe ob Tesseract-Pfad in Environment-Variable gesetzt ist
        tesseract_path = os.getenv('TESSERACT_CMD', '')
        if tesseract_path and Path(tesseract_path).exists():
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        else:
            # Standard-Pfade für Windows
            common_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            ]
            
            for path in common_paths:
                if Path(path).exists():
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
    
    def _preprocess_image(self, img: Image.Image) -> Image.Image:
        """
        Vorverarbeitet ein Bild für bessere OCR-Genauigkeit
        
        Args:
            img: PIL Image
            
        Returns:
            Vorverarbeitetes Bild
        """
        if not self.enable_preprocessing:
            return img
        
        try:
            # Konvertiere zu Graustufen falls nötig
            if img.mode != 'L':
                img = img.convert('L')
            
            # Kontrastverbesserung
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)  # 50% mehr Kontrast
            
            # Schärfung
            img = img.filter(ImageFilter.SHARPEN)
            
            # Skalierung für kleine Texte (min. 300 DPI für gute OCR)
            width, height = img.size
            min_size = 300
            if width < min_size or height < min_size:
                scale_factor = max(min_size / width, min_size / height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            return img
        
        except Exception as e:
            logger.warning(f"Fehler bei Bildvorverarbeitung: {e}", exc_info=True)
            return img
    
    def extract_text(self, image_path: Path, timeout: float = 2.0) -> str:
        """
        Extrahiert Text aus einem Bild (synchron)
        
        Args:
            image_path: Pfad zum Bild
            timeout: Timeout in Sekunden (Standard: 2.0)
            
        Returns:
            Extrahierter Text
        """
        try:
            if not image_path.exists():
                logger.warning(f"Screenshot nicht gefunden: {image_path}")
                return ""
            
            start_time = time.time()
            
            img = Image.open(image_path)
            
            # Vorverarbeitung
            img = self._preprocess_image(img)
            
            # OCR mit konfigurierter Sprache
            text = pytesseract.image_to_string(img, lang=self.language, timeout=int(timeout))
            
            duration = time.time() - start_time
            if duration > timeout:
                logger.warning(f"OCR-Verarbeitung dauerte {duration:.2f}s (Target: {timeout}s)")
            else:
                logger.debug(f"OCR-Verarbeitung abgeschlossen in {duration:.2f}s")
            
            return text.strip()
        
        except pytesseract.TesseractNotFoundError:
            logger.error("Tesseract OCR nicht gefunden. Bitte installieren Sie Tesseract OCR.")
            return ""
        except pytesseract.TesseractError as e:
            logger.error(f"Tesseract OCR Fehler: {e}")
            return ""
        except Exception as e:
            logger.warning(f"Fehler bei OCR-Extraktion: {e}", exc_info=True)
            return ""
    
    def extract_text_async(self, image_path: Path, callback: Optional[callable] = None, timeout: float = 2.0) -> None:
        """
        Extrahiert Text asynchron aus einem Bild
        
        Args:
            image_path: Pfad zum Bild
            callback: Callback-Funktion die mit (text, error) aufgerufen wird
            timeout: Timeout in Sekunden (Standard: 2.0)
        """
        def _process():
            try:
                text = self.extract_text(image_path, timeout=timeout)
                if callback:
                    callback(text, None)
            except Exception as e:
                logger.error(f"Fehler bei asynchroner OCR-Extraktion: {e}", exc_info=True)
                if callback:
                    callback("", str(e))
        
        self.executor.submit(_process)
    
    def extract_text_with_confidence(self, image_path: Path, timeout: float = 2.0) -> Dict[str, any]:
        """
        Extrahiert Text mit Konfidenz-Informationen
        
        Args:
            image_path: Pfad zum Bild
            
        Returns:
            Dictionary mit 'text' und 'confidence'
        """
        try:
            if not image_path.exists():
                return {'text': '', 'confidence': 0.0}
            
            start_time = time.time()
            
            img = Image.open(image_path)
            
            # Vorverarbeitung
            img = self._preprocess_image(img)
            
            # OCR mit Details
            ocr_data = pytesseract.image_to_data(img, lang=self.language, output_type=pytesseract.Output.DICT, timeout=int(timeout))
            
            # Extrahiere Text und berechne durchschnittliche Konfidenz
            texts = []
            confidences = []
            
            for i in range(len(ocr_data['text'])):
                text = ocr_data['text'][i].strip()
                if text:
                    texts.append(text)
                    conf = ocr_data['conf'][i]
                    if conf > 0:
                        confidences.append(conf)
            
            full_text = ' '.join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return {
                'text': full_text,
                'confidence': avg_confidence,
                'words': texts,
                'word_confidences': confidences
            }
        
        except Exception as e:
            logger.warning(f"Fehler bei OCR-Extraktion mit Konfidenz: {e}", exc_info=True)
            return {'text': '', 'confidence': 0.0}
    
    def is_available(self) -> bool:
        """
        Prüft ob Tesseract verfügbar ist
        
        Returns:
            True wenn Tesseract verfügbar ist
        """
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False


