"""
Navigation State Manager: Verwaltet den Erkundungszustand
"""

import hashlib
from typing import Set, List, Dict, Optional
from pathlib import Path
from PIL import Image
import numpy as np

from src.utils.logger import get_logger

logger = get_logger(__name__)


class NavigationState:
    """Verwaltet den Erkundungszustand"""
    
    def __init__(self, max_depth: int = 3, max_steps: int = 1000):
        """
        Initialisiert Navigation State
        
        Args:
            max_depth: Maximale Tiefe in Menü-Hierarchie
            max_steps: Maximale Anzahl Schritte
        """
        self.max_depth = max_depth
        self.max_steps = max_steps
        
        # Bereits besuchte Fenster/Menüs
        self.visited_screenshots: Set[str] = set()
        
        # Bereits geklickte Elemente
        self.clicked_elements: List[Dict] = []
        
        # Erkundungspfad (History)
        self.exploration_path: List[Dict] = []
        
        # Aktuelle Tiefe in Menü-Hierarchie
        self.current_depth = 0
        
        # Schritt-Zähler
        self.step_count = 0
    
    def add_screenshot(self, screenshot_path: Path) -> bool:
        """
        Fügt Screenshot hinzu und prüft ob bereits besucht
        
        Args:
            screenshot_path: Pfad zum Screenshot
            
        Returns:
            True wenn neu, False wenn bereits besucht
        """
        screenshot_hash = self._calculate_screenshot_hash(screenshot_path)
        
        if screenshot_hash in self.visited_screenshots:
            return False
        
        self.visited_screenshots.add(screenshot_hash)
        return True
    
    def _calculate_screenshot_hash(self, screenshot_path: Path) -> str:
        """
        Berechnet Hash eines Screenshots für Duplikat-Erkennung
        
        Args:
            screenshot_path: Pfad zum Screenshot
            
        Returns:
            Hash-String
        """
        try:
            # Lade Bild
            img = Image.open(screenshot_path)
            
            # Konvertiere zu Graustufen für Vergleich
            img_gray = img.convert('L')
            
            # Resize auf kleinere Größe für schnelleren Vergleich
            img_gray = img_gray.resize((100, 100), Image.Resampling.LANCZOS)
            
            # Konvertiere zu Array
            img_array = np.array(img_gray)
            
            # Berechne Hash
            img_bytes = img_array.tobytes()
            hash_obj = hashlib.md5(img_bytes)
            
            return hash_obj.hexdigest()
        
        except Exception as e:
            logger.error(f"Fehler beim Berechnen des Screenshot-Hashes: {e}", exc_info=True)
            # Fallback: Dateiname-Hash
            return hashlib.md5(str(screenshot_path).encode()).hexdigest()
    
    def add_clicked_element(self, element: Dict):
        """
        Fügt geklicktes Element hinzu
        
        Args:
            element: Element-Informationen
        """
        self.clicked_elements.append({
            **element,
            'step_number': self.step_count,
            'timestamp': self._get_timestamp()
        })
    
    def increment_step(self):
        """Erhöht Schritt-Zähler"""
        self.step_count += 1
    
    def increment_depth(self):
        """Erhöht aktuelle Tiefe"""
        self.current_depth += 1
    
    def decrement_depth(self):
        """Verringert aktuelle Tiefe"""
        self.current_depth = max(0, self.current_depth - 1)
    
    def add_to_path(self, action: Dict):
        """
        Fügt Aktion zum Erkundungspfad hinzu
        
        Args:
            action: Aktions-Informationen
        """
        self.exploration_path.append({
            **action,
            'step': self.step_count,
            'depth': self.current_depth,
            'timestamp': self._get_timestamp()
        })
    
    def can_continue(self) -> bool:
        """
        Prüft ob Erkundung fortgesetzt werden kann
        
        Returns:
            True wenn fortgesetzt werden kann
        """
        if self.step_count >= self.max_steps:
            logger.info(f"Maximale Schrittanzahl ({self.max_steps}) erreicht")
            return False
        
        if self.current_depth > self.max_depth:
            logger.info(f"Maximale Tiefe ({self.max_depth}) erreicht")
            return False
        
        return True
    
    def get_visited_areas(self) -> List[str]:
        """
        Gibt Liste bereits besuchter Bereiche zurück
        
        Returns:
            Liste von Hash-Strings
        """
        return list(self.visited_screenshots)
    
    def get_current_context(self) -> str:
        """
        Gibt aktuellen Kontext zurück
        
        Returns:
            Kontext-String
        """
        if not self.exploration_path:
            return "Start"
        
        # Letzte 3 Aktionen als Kontext
        recent_actions = self.exploration_path[-3:]
        context_parts = []
        
        for action in recent_actions:
            element_text = action.get('element_text', '')
            action_type = action.get('action', '')
            if element_text:
                context_parts.append(f"{action_type}: {element_text}")
        
        return " → ".join(context_parts) if context_parts else "Unbekannt"
    
    def get_statistics(self) -> Dict:
        """
        Gibt Erkundungs-Statistiken zurück
        
        Returns:
            Dictionary mit Statistiken
        """
        return {
            'steps': self.step_count,
            'visited_screenshots': len(self.visited_screenshots),
            'clicked_elements': len(self.clicked_elements),
            'current_depth': self.current_depth,
            'max_depth': self.max_depth,
            'path_length': len(self.exploration_path)
        }
    
    def _get_timestamp(self) -> float:
        """Gibt aktuellen Timestamp zurück"""
        import time
        return time.time()
    
    def reset(self):
        """Setzt State zurück"""
        self.visited_screenshots.clear()
        self.clicked_elements.clear()
        self.exploration_path.clear()
        self.current_depth = 0
        self.step_count = 0

