"""
Maske-Änderungs-Detektor: Erkennt Änderungen in Fenstern
"""

import time
from typing import Dict, Optional
import win32gui

from src.config.trigger_config import TriggerConfig


class ActionDetector:
    """Erkennt Änderungen in Fenstern (Maske-Änderungen)"""
    
    def __init__(self, trigger_config: Optional[TriggerConfig] = None):
        """
        Initialisiert den Action Detector
        
        Args:
            trigger_config: Trigger-Konfiguration
        """
        self.last_window_state = {}
        
        # Lade Trigger-Konfiguration
        if trigger_config is None:
            trigger_config = TriggerConfig()
        self.trigger_config = trigger_config
        self.change_threshold = trigger_config.change_threshold
        self.size_change_threshold = trigger_config.size_change_threshold
    
    def detect_change(self, window_info: Dict) -> bool:
        """
        Prüft ob eine signifikante Änderung erkannt wurde
        
        Args:
            window_info: Aktuelle Fenster-Informationen
            
        Returns:
            True wenn eine Änderung erkannt wurde
        """
        if not window_info:
            return False
        
        window_key = self._get_window_key(window_info)
        current_time = time.time()
        
        # Prüfe ob sich Fenstertitel geändert hat
        if window_key in self.last_window_state:
            last_state = self.last_window_state[window_key]
            
            # Fenstertitel-Änderung
            if window_info.get('title') != last_state.get('title'):
                self.last_window_state[window_key] = window_info
                return True
            
            # Größenänderung (signifikant)
            if self._is_size_changed(window_info, last_state):
                self.last_window_state[window_key] = window_info
                return True
            
            # Zeit-basierte Änderung (falls Fenster lange aktiv war)
            time_diff = current_time - last_state.get('timestamp', 0)
            if time_diff > self.change_threshold:
                # Prüfe auf Content-Änderungen durch Fenster-Handle Vergleich
                if self._has_content_changed(window_info):
                    self.last_window_state[window_key] = window_info
                    return True
        
        else:
            # Neues Fenster
            self.last_window_state[window_key] = window_info
            return True
        
        return False
    
    def _get_window_key(self, window_info: Dict) -> str:
        """
        Erstellt einen eindeutigen Schlüssel für ein Fenster
        
        Args:
            window_info: Fenster-Informationen
            
        Returns:
            Eindeutiger Schlüssel
        """
        # Kombiniere Prozessname und Klasse für eindeutige Identifikation
        process_name = window_info.get('process_name', 'unknown')
        class_name = window_info.get('class_name', 'unknown')
        return f"{process_name}:{class_name}"
    
    def _is_size_changed(self, current: Dict, last: Dict) -> bool:
        """
        Prüft ob sich die Fenstergröße signifikant geändert hat
        
        Args:
            current: Aktuelle Fenster-Informationen
            last: Vorherige Fenster-Informationen
            
        Returns:
            True wenn Größe sich geändert hat
        """
        current_pos = current.get('position', {})
        last_pos = last.get('position', {})
        
        current_width = current_pos.get('width', 0)
        current_height = current_pos.get('height', 0)
        last_width = last_pos.get('width', 0)
        last_height = last_pos.get('height', 0)
        
        # Mindeständerung von konfigurierbaren Pixeln
        width_diff = abs(current_width - last_width)
        height_diff = abs(current_height - last_height)
        
        return width_diff > self.size_change_threshold or height_diff > self.size_change_threshold
    
    def _has_content_changed(self, window_info: Dict) -> bool:
        """
        Prüft ob sich der Inhalt eines Fensters geändert hat
        
        Args:
            window_info: Fenster-Informationen
            
        Returns:
            True wenn Content-Änderung vermutet wird
        """
        # Diese Methode kann erweitert werden mit:
        # - OCR-Vergleich des Fensterinhalts
        # - Pixel-Vergleich
        # - Fenster-Eigenschaften-Vergleich
        
        # Für jetzt: Prüfe ob Fenster noch aktiv ist
        hwnd = window_info.get('hwnd')
        if hwnd:
            try:
                current_hwnd = win32gui.GetForegroundWindow()
                return hwnd == current_hwnd
            except Exception:
                pass
        
        return False
    
    def reset(self):
        """Setzt den Detector zurück"""
        self.last_window_state = {}


