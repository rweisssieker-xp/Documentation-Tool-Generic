"""
Screenshot-Erstellung für Windows-Fenster
"""

import win32gui
import win32ui
import win32con
from PIL import Image
from pathlib import Path
from typing import Optional
import time
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ScreenshotCapture:
    """Erstellt Screenshots von Windows-Fenster"""
    
    def __init__(self, output_dir: Path, privacy_mask=None):
        """
        Initialisiert den Screenshot Capture
        
        Args:
            output_dir: Ausgabeverzeichnis für Screenshots
            privacy_mask: Optional PrivacyMask-Instanz
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.privacy_mask = privacy_mask
    
    def capture_window(self, hwnd: Optional[int] = None, step_number: Optional[int] = None, max_retries: int = 2) -> Optional[Path]:
        """
        Erstellt einen Screenshot eines Fensters mit Retry-Logik
        
        Args:
            hwnd: Window Handle (None für aktives Fenster)
            step_number: Schrittnummer für Dateinamen
            max_retries: Maximale Anzahl Wiederholungsversuche
            
        Returns:
            Pfad zum erstellten Screenshot oder None bei Fehler
        """
        for attempt in range(max_retries + 1):
            try:
                if hwnd is None:
                    hwnd = win32gui.GetForegroundWindow()
                
                if not hwnd:
                    return None
                
                # Hole Fenster-Rechteck
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                width = right - left
                height = bottom - top
                
                # Erstelle Device Context
                hwnd_dc = win32gui.GetWindowDC(hwnd)
                mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
                save_dc = mfc_dc.CreateCompatibleDC()
                
                # Erstelle Bitmap
                bitmap = win32ui.CreateBitmap()
                bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
                save_dc.SelectObject(bitmap)
                
                # Kopiere Fenster-Inhalt
                save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)
                
                # Konvertiere zu PIL Image
                bmpinfo = bitmap.GetInfo()
                bmpstr = bitmap.GetBitmapBits(True)
                
                img = Image.frombuffer(
                    'RGB',
                    (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                    bmpstr, 'raw', 'BGRX', 0, 1
                )
                
                # Speichere Screenshot
                if step_number is None:
                    filename = f"screenshot_{int(time.time())}.png"
                else:
                    filename = f"step_{step_number:04d}.png"
                
                screenshot_path = self.output_dir / filename
                img.save(screenshot_path, 'PNG')
                
                # Wende Privacy-Mask an falls aktiviert (ohne OCR-Text hier, wird später angewendet)
                # Die automatische Erkennung wird später im SessionManager mit OCR-Text aufgerufen
                
                # Cleanup
                win32gui.DeleteObject(bitmap.GetHandle())
                save_dc.DeleteDC()
                mfc_dc.DeleteDC()
                win32gui.ReleaseDC(hwnd, hwnd_dc)
                
                return screenshot_path
            
            except Exception as e:
                if attempt < max_retries:
                    logger.warning(f"Fehler beim Erstellen des Screenshots (Versuch {attempt + 1}/{max_retries + 1}): {e}. Wiederhole...")
                    time.sleep(0.5)
                else:
                    logger.error(f"Fehler beim Erstellen des Screenshots nach {max_retries + 1} Versuchen: {e}", exc_info=True)
                    return None
        
        return None
    
    def capture_screen(self, step_number: Optional[int] = None) -> Optional[Path]:
        """
        Erstellt einen Screenshot des gesamten Bildschirms
        
        Args:
            step_number: Schrittnummer für Dateinamen
            
        Returns:
            Pfad zum erstellten Screenshot oder None bei Fehler
        """
        try:
            from mss import mss
            
            with mss() as sct:
                # Screenshot des Primär-Bildschirms
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                
                # Konvertiere zu PIL Image
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                
                # Speichere Screenshot
                if step_number is None:
                    filename = f"screenshot_{int(time.time())}.png"
                else:
                    filename = f"step_{step_number:04d}.png"
                
                screenshot_path = self.output_dir / filename
                img.save(screenshot_path, 'PNG')
                
                # Wende Privacy-Mask an falls aktiviert (ohne OCR-Text hier)
                # Die automatische Erkennung wird später im SessionManager mit OCR-Text aufgerufen
                
                return screenshot_path
        
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Bildschirm-Screenshots: {e}", exc_info=True)
            return None

