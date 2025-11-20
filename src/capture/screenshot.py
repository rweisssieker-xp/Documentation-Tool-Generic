"""
Cross-platform screenshot capture
"""

import platform
from PIL import Image
from pathlib import Path
from typing import Optional, Tuple, Dict
import time
import uuid
from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ScreenshotCapture:
    """Cross-platform screenshot capture"""
    
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
        self.platform = platform.system().lower()
        
        # Initialize platform-specific modules
        if self.platform == "windows":
            import win32gui
            import win32ui
            import win32con
            self.win32gui = win32gui
            self.win32ui = win32ui
            self.win32con = win32con
        else:
            # For cross-platform window detection, we'll use pywinctl
            try:
                import pywinctl
                self.pywinctl = pywinctl
            except ImportError:
                logger.warning("pywinctl not available. Window capture may be limited on non-Windows platforms.")
                self.pywinctl = None
            try:
                import mss
                self.mss = mss
            except ImportError:
                logger.error("mss library not available for non-Windows platforms")
                raise ImportError("mss library is required for cross-platform screenshot capture")
    
    def capture_window(self, hwnd: Optional[int] = None, step_number: Optional[int] = None, max_retries: int = 2, session_id: Optional[str] = None) -> Optional[Tuple[Path, Dict]]:
        """
        Erstellt einen Screenshot eines Fensters mit Retry-Logik (plattformübergreifend)
        
        Args:
            hwnd: Window Handle (None für aktives Fenster - nur Windows)
            step_number: Schrittnummer für Dateinamen
            max_retries: Maximale Anzahl Wiederholungsversuche
            session_id: Session-ID für Dateinamen (optional)
            
        Returns:
            Tuple (Pfad zum Screenshot, Metadaten-Dict) oder None bei Fehler
            Metadaten enthalten: screenshot_id (UUID), timestamp (ISO 8601), window_title
        """
        if self.platform == "windows":
            return self._capture_window_windows(hwnd, step_number, max_retries, session_id)
        else:
            return self._capture_window_cross_platform(step_number, max_retries, session_id)
    
    def _capture_window_windows(self, hwnd: Optional[int] = None, step_number: Optional[int] = None, max_retries: int = 2, session_id: Optional[str] = None) -> Optional[Tuple[Path, Dict]]:
        """
        Windows-specific window capture
        """
        for attempt in range(max_retries + 1):
            try:
                if hwnd is None:
                    hwnd = self.win32gui.GetForegroundWindow()
                
                if not hwnd:
                    return None
                
                # Hole Fenster-Rechteck
                left, top, right, bottom = self.win32gui.GetWindowRect(hwnd)
                width = right - left
                height = bottom - top
                
                # Erstelle Device Context
                hwnd_dc = self.win32gui.GetWindowDC(hwnd)
                mfc_dc = self.win32ui.CreateDCFromHandle(hwnd_dc)
                save_dc = mfc_dc.CreateCompatibleDC()
                
                # Erstelle Bitmap
                bitmap = self.win32ui.CreateBitmap()
                bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
                save_dc.SelectObject(bitmap)
                
                # Kopiere Fenster-Inhalt
                save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), self.win32con.SRCCOPY)
                
                # Konvertiere zu PIL Image
                bmpinfo = bitmap.GetInfo()
                bmpstr = bitmap.GetBitmapBits(True)
                
                img = Image.frombuffer(
                    'RGB',
                    (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                    bmpstr, 'raw', 'BGRX', 0, 1
                )
                
                # Generiere UUID für Screenshot-ID
                screenshot_id = str(uuid.uuid4())
                timestamp = datetime.now().isoformat().replace(':', '-').split('.')[0]
                
                # Hole Fenstertitel für Metadaten
                window_title = self.win32gui.GetWindowText(hwnd) if hwnd else "Unknown"
                
                # Generiere Dateinamen nach Schema: {session_id}_{step_number}_{timestamp}.png
                if session_id and step_number is not None:
                    filename = f"{session_id}_{step_number:04d}_{timestamp}.png"
                elif step_number is not None:
                    filename = f"{step_number:04d}_{timestamp}.png"
                else:
                    filename = f"{screenshot_id}_{timestamp}.png"
                
                screenshot_path = self.output_dir / filename
                img.save(screenshot_path, 'PNG')
                
                # Erstelle Metadaten-Dict
                metadata = {
                    'screenshot_id': screenshot_id,
                    'timestamp': datetime.now().isoformat(),
                    'window_title': window_title,
                    'file_path': str(screenshot_path),
                    'step_number': step_number,
                    'session_id': session_id
                }
                
                # Wende Privacy-Mask an falls aktiviert (ohne OCR-Text hier, wird später angewendet)
                # Die automatische Erkennung wird später im SessionManager mit OCR-Text aufgerufen
                
                # Cleanup
                self.win32gui.DeleteObject(bitmap.GetHandle())
                save_dc.DeleteDC()
                mfc_dc.DeleteDC()
                self.win32gui.ReleaseDC(hwnd, hwnd_dc)
                
                return (screenshot_path, metadata)
            
            except Exception as e:
                if attempt < max_retries:
                    logger.warning(f"Fehler beim Erstellen des Screenshots (Versuch {attempt + 1}/{max_retries + 1}): {e}. Wiederhole...")
                    time.sleep(0.5)
                else:
                    logger.error(f"Fehler beim Erstellen des Screenshots nach {max_retries + 1} Versuchen: {e}", exc_info=True)
                    return None
        
        return None
    
    def _capture_window_cross_platform(self, step_number: Optional[int] = None, max_retries: int = 2, session_id: Optional[str] = None) -> Optional[Tuple[Path, Dict]]:
        """
        Cross-platform window capture using pywinctl and mss
        """
        for attempt in range(max_retries + 1):
            try:
                from mss import mss
                
                # Get the active window using pywinctl if available
                if self.pywinctl:
                    try:
                        active_window = self.pywinctl.getActiveWindow()
                        if active_window:
                            # Get window position and size
                            left, top, right, bottom = active_window.left, active_window.top, active_window.right, active_window.bottom
                            width = right - left
                            height = bottom - top
                            
                            # Capture specific region
                            with mss() as sct:
                                # Get monitor that contains the window
                                monitor = None
                                for m in sct.monitors[1:]:  # Skip the "all monitors" monitor at index 0
                                    if (left >= m['left'] and left < m['left'] + m['width'] and
                                        top >= m['top'] and top < m['top'] + m['height']):
                                        monitor = m
                                        break
                                
                                if monitor:
                                    # Capture the specific window region
                                    window_region = {
                                        "top": top,
                                        "left": left,
                                        "width": width,
                                        "height": height
                                    }
                                    screenshot = sct.grab(window_region)
                                    img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                                else:
                                    # Fallback to primary monitor
                                    monitor = sct.monitors[1]
                                    screenshot = sct.grab(monitor)
                                    img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                        else:
                            # No active window found, capture primary monitor
                            with mss() as sct:
                                monitor = sct.monitors[1]
                                screenshot = sct.grab(monitor)
                                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                    except Exception as e:
                        logger.warning(f"Fehler beim Abrufen des aktiven Fensters mit pywinctl: {e}. Fallback zu primärem Monitor.")
                        # Fallback to primary monitor capture
                        with mss() as sct:
                            monitor = sct.monitors[1]
                            screenshot = sct.grab(monitor)
                            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                else:
                    # Fallback to primary monitor if pywinctl is not available
                    with mss() as sct:
                        monitor = sct.monitors[1]
                        screenshot = sct.grab(monitor)
                        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                
                # Generiere UUID für Screenshot-ID
                screenshot_id = str(uuid.uuid4())
                timestamp = datetime.now().isoformat().replace(':', '-').split('.')[0]
                
                # Hole Fenstertitel für Metadaten (falls pywinctl verfügbar)
                window_title = "Unknown"
                if self.pywinctl:
                    try:
                        active_window = self.pywinctl.getActiveWindow()
                        if active_window:
                            window_title = active_window.title or "Unknown"
                    except Exception:
                        pass
                
                # Generiere Dateinamen nach Schema: {session_id}_{step_number}_{timestamp}.png
                if session_id and step_number is not None:
                    filename = f"{session_id}_{step_number:04d}_{timestamp}.png"
                elif step_number is not None:
                    filename = f"{step_number:04d}_{timestamp}.png"
                else:
                    filename = f"{screenshot_id}_{timestamp}.png"
                
                screenshot_path = self.output_dir / filename
                img.save(screenshot_path, 'PNG')
                
                # Erstelle Metadaten-Dict
                metadata = {
                    'screenshot_id': screenshot_id,
                    'timestamp': datetime.now().isoformat(),
                    'window_title': window_title,
                    'file_path': str(screenshot_path),
                    'step_number': step_number,
                    'session_id': session_id
                }
                
                return (screenshot_path, metadata)
            
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
                
                # Generiere UUID für Screenshot-ID
                screenshot_id = str(uuid.uuid4())
                timestamp = datetime.now().isoformat().replace(':', '-').split('.')[0]
                
                # Generiere Dateinamen nach Schema: {session_id}_{step_number}_{timestamp}.png
                if session_id and step_number is not None:
                    filename = f"{session_id}_{step_number:04d}_{timestamp}.png"
                elif step_number is not None:
                    filename = f"{step_number:04d}_{timestamp}.png"
                else:
                    filename = f"{screenshot_id}_{timestamp}.png"
                
                screenshot_path = self.output_dir / filename
                img.save(screenshot_path, 'PNG')
                
                # Erstelle Metadaten-Dict
                metadata = {
                    'screenshot_id': screenshot_id,
                    'timestamp': datetime.now().isoformat(),
                    'window_title': 'Screen Capture',
                    'file_path': str(screenshot_path),
                    'step_number': step_number,
                    'session_id': session_id
                }
                
                # Wende Privacy-Mask an falls aktiviert (ohne OCR-Text hier)
                # Die automatische Erkennung wird später im SessionManager mit OCR-Text aufgerufen
                
                return (screenshot_path, metadata)
        
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Bildschirm-Screenshots: {e}", exc_info=True)
            return None

