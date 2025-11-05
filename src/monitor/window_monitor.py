"""
Windows-Fenster-Monitoring mit pywin32
"""

import win32gui
import win32process
import psutil
import time
from typing import Dict, Optional, Callable
import threading

from src.config.trigger_config import TriggerConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)


class WindowMonitor:
    """Überwacht Windows-Fenster-Wechsel und extrahiert Metadaten"""
    
    def __init__(self, callback: Optional[Callable] = None, trigger_config: Optional[TriggerConfig] = None):
        """
        Initialisiert den Window Monitor
        
        Args:
            callback: Callback-Funktion die bei Fensterwechsel aufgerufen wird
            trigger_config: Trigger-Konfiguration
        """
        self.callback = callback
        self.current_window = None
        self.monitoring = False
        self.monitor_thread = None
        
        # Lade Trigger-Konfiguration
        if trigger_config is None:
            trigger_config = TriggerConfig()
        self.trigger_config = trigger_config
        self.poll_interval = trigger_config.poll_interval
    
    def start_monitoring(self):
        """Startet die Überwachung"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Beendet die Überwachung"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
    
    def _monitor_loop(self):
        """Hauptschleife für die Überwachung"""
        while self.monitoring:
            try:
                # Hole aktives Fenster
                hwnd = win32gui.GetForegroundWindow()
                
                if hwnd:
                    window_info = self._get_window_info(hwnd)
                    
                    # Prüfe ob sich das Fenster geändert hat
                    if self._is_window_changed(window_info):
                        self.current_window = window_info
                        
                        if self.callback:
                            self.callback(window_info)
                
                time.sleep(self.poll_interval)
            
            except Exception as e:
                logger.error(f"Fehler im Monitor-Loop: {e}", exc_info=True)
                time.sleep(self.poll_interval)
    
    def _is_window_changed(self, window_info: Dict) -> bool:
        """
        Prüft ob sich das Fenster geändert hat
        
        Args:
            window_info: Fenster-Informationen
            
        Returns:
            True wenn sich das Fenster geändert hat
        """
        if not self.current_window:
            return True
        
        # Vergleiche Fenstertitel und Klasse
        return (
            window_info.get('title') != self.current_window.get('title') or
            window_info.get('class_name') != self.current_window.get('class_name')
        )
    
    def _get_window_info(self, hwnd: int) -> Dict:
        """
        Extrahiert Informationen über ein Fenster
        
        Args:
            hwnd: Window Handle
            
        Returns:
            Dictionary mit Fenster-Informationen
        """
        try:
            # Fenstertitel
            title = win32gui.GetWindowText(hwnd)
            
            # Fensterklasse
            class_name = win32gui.GetClassName(hwnd)
            
            # Fensterposition und Größe
            rect = win32gui.GetWindowRect(hwnd)
            left, top, right, bottom = rect
            width = right - left
            height = bottom - top
            
            # Prozess-Informationen
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process_name = None
            executable_path = None
            
            try:
                process = psutil.Process(pid)
                process_name = process.name()
                executable_path = process.exe()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            
            return {
                'hwnd': hwnd,
                'title': title,
                'class_name': class_name,
                'pid': pid,
                'process_name': process_name,
                'executable_path': executable_path,
                'position': {
                    'left': left,
                    'top': top,
                    'right': right,
                    'bottom': bottom,
                    'width': width,
                    'height': height
                },
                'timestamp': time.time()
            }
        
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Fenster-Informationen: {e}", exc_info=True)
            return {
                'hwnd': hwnd,
                'title': 'Unbekannt',
                'class_name': 'Unbekannt',
                'timestamp': time.time()
            }
    
    def get_current_window(self) -> Optional[Dict]:
        """
        Gibt das aktuelle aktive Fenster zurück
        
        Returns:
            Fenster-Informationen oder None
        """
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                return self._get_window_info(hwnd)
        except Exception:
            pass
        
        return None


