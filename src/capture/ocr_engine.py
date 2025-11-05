"""
OCR-Engine mit Tesseract-Integration
"""

import pytesseract
from PIL import Image
from pathlib import Path
from typing import Optional, Dict
import os
from src.utils.logger import get_logger

logger = get_logger(__name__)


class OCREngine:
    """OCR-Engine für Textextraktion aus Screenshots"""
    
    def __init__(self, language: str = "deu+eng"):
        """
        Initialisiert die OCR-Engine
        
        Args:
            language: Tesseract-Sprache (z.B. "deu+eng" für Deutsch und Englisch)
        """
        self.language = language
        
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
    
    def extract_text(self, image_path: Path) -> str:
        """
        Extrahiert Text aus einem Bild
        
        Args:
            image_path: Pfad zum Bild
            
        Returns:
            Extrahierter Text
        """
        try:
            if not image_path.exists():
                return ""
            
            img = Image.open(image_path)
            
            # OCR mit konfigurierter Sprache
            text = pytesseract.image_to_string(img, lang=self.language)
            
            return text.strip()
        
        except Exception as e:
            logger.warning(f"Fehler bei OCR-Extraktion: {e}", exc_info=True)
            return ""
    
    def extract_text_with_confidence(self, image_path: Path) -> Dict[str, any]:
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
            
            img = Image.open(image_path)
            
            # OCR mit Details
            ocr_data = pytesseract.image_to_data(img, lang=self.language, output_type=pytesseract.Output.DICT)
            
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


