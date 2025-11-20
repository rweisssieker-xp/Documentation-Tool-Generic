"""
Exploration Strategy: Verschiedene Strategien für App-Erkundung
"""

from enum import Enum
from typing import List, Dict, Optional
from src.automation.element_discovery import ElementDiscovery
from src.automation.ai_navigator import AINavigator
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ExplorationStrategyType(Enum):
    """Typen von Erkundungsstrategien"""
    BREADTH_FIRST = "breadth_first"
    DEPTH_FIRST = "depth_first"
    AI_GUIDED = "ai_guided"
    HYBRID = "hybrid"


class ExplorationStrategy:
    """Verschiedene Strategien für App-Erkundung"""
    
    def __init__(self, strategy_type: ExplorationStrategyType = ExplorationStrategyType.HYBRID):
        """
        Initialisiert Exploration Strategy
        
        Args:
            strategy_type: Typ der Strategie
        """
        self.strategy_type = strategy_type
        self.ai_navigator = AINavigator() if strategy_type in [ExplorationStrategyType.AI_GUIDED, ExplorationStrategyType.HYBRID] else None
    
    def get_next_element(
        self,
        element_discovery: ElementDiscovery,
        navigation_state,
        screenshot_path: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Gibt nächste Aktion basierend auf Strategie zurück
        
        Args:
            element_discovery: Element Discovery Instanz
            navigation_state: Navigation State Instanz
            screenshot_path: Pfad zum Screenshot (für AI-Guided)
            
        Returns:
            Element-Informationen oder None
        """
        if self.strategy_type == ExplorationStrategyType.BREADTH_FIRST:
            return self._breadth_first_strategy(element_discovery, navigation_state)
        
        elif self.strategy_type == ExplorationStrategyType.DEPTH_FIRST:
            return self._depth_first_strategy(element_discovery, navigation_state)
        
        elif self.strategy_type == ExplorationStrategyType.AI_GUIDED:
            if screenshot_path and self.ai_navigator:
                return self._ai_guided_strategy(screenshot_path, navigation_state)
            else:
                # Fallback auf Breadth-First
                return self._breadth_first_strategy(element_discovery, navigation_state)
        
        elif self.strategy_type == ExplorationStrategyType.HYBRID:
            # Versuche zuerst AI-Guided, dann Fallback
            if screenshot_path and self.ai_navigator:
                ai_action = self._ai_guided_strategy(screenshot_path, navigation_state)
                if ai_action:
                    return ai_action
            
            # Fallback auf Breadth-First
            return self._breadth_first_strategy(element_discovery, navigation_state)
        
        return None
    
    def _breadth_first_strategy(self, element_discovery: ElementDiscovery, navigation_state) -> Optional[Dict]:
        """Breadth-First: Alle Top-Level-Menüs zuerst"""
        elements = element_discovery.discover_all_elements()
        
        if not elements:
            return None
        
        # Filtere bereits geklickte Elemente
        clicked_coords = {(e['x'], e['y']) for e in navigation_state.clicked_elements}
        
        # Priorisiere Menü-Items und Buttons
        prioritized = []
        others = []
        
        for element in elements:
            if not element.get('visible', True) or not element.get('enabled', True):
                continue
            
            coords = (element['x'], element['y'])
            if coords in clicked_coords:
                continue
            
            if element['type'] in ['menu_item', 'button']:
                prioritized.append(element)
            else:
                others.append(element)
        
        # Gib zuerst priorisierte Elemente zurück
        if prioritized:
            return prioritized[0]
        
        if others:
            return others[0]
        
        return None
    
    def _depth_first_strategy(self, element_discovery: ElementDiscovery, navigation_state) -> Optional[Dict]:
        """Depth-First: Ein Menü komplett durchgehen"""
        # Ähnlich wie Breadth-First, aber priorisiert verschachtelte Elemente
        elements = element_discovery.discover_all_elements()
        
        if not elements:
            return None
        
        # Filtere bereits geklickte Elemente
        clicked_coords = {(e['x'], e['y']) for e in navigation_state.clicked_elements}
        
        # Priorisiere nach Tiefe (zuerst tiefere Elemente)
        available = []
        
        for element in elements:
            if not element.get('visible', True) or not element.get('enabled', True):
                continue
            
            coords = (element['x'], element['y'])
            if coords in clicked_coords:
                continue
            
            available.append(element)
        
        # Sortiere nach Typ (Menü-Items zuerst)
        available.sort(key=lambda e: (e['type'] == 'menu_item', e['type'] == 'button'))
        
        return available[0] if available else None
    
    def _ai_guided_strategy(self, screenshot_path: str, navigation_state) -> Optional[Dict]:
        """AI-Guided: KI entscheidet basierend auf Screenshot"""
        if not self.ai_navigator:
            return None
        
        from pathlib import Path
        
        visited_areas = navigation_state.get_visited_areas()
        current_context = navigation_state.get_current_context()
        
        action = self.ai_navigator.decide_next_action(
            screenshot_path=Path(screenshot_path),
            visited_areas=visited_areas,
            current_context=current_context
        )
        
        return action

