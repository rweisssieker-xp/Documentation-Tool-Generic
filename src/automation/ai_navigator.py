"""
AI Navigator: Vision-Based Decision Engine für KI-gesteuerte Navigation
"""

import json
import re
from typing import Dict, List, Optional
from pathlib import Path

from src.ai.openai_client import OpenAIClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AINavigator:
    """Vision-Based Decision Engine für KI-gesteuerte Navigation"""
    
    def __init__(self, confidence_threshold: float = 0.7):
        """
        Initialisiert den AI Navigator
        
        Args:
            confidence_threshold: Minimum Confidence für AI-Entscheidungen
        """
        self.openai_client = OpenAIClient()
        self.confidence_threshold = confidence_threshold
        
        self.system_prompt = """Du bist ein UI-Tester und Automatisierungsexperte. 
Analysiere Screenshots von Windows-Anwendungen und identifiziere die nächste Aktion, die ausgeführt werden sollte, um die App vollständig zu erkunden.

WICHTIGE REGELN:
1. Vermeide bereits besuchte Bereiche
2. Priorisiere Hauptmenüs und wichtige Features
3. Klicke systematisch durch alle verfügbaren Optionen
4. Gehe nicht zu tief in verschachtelte Menüs (max. 3 Ebenen)
5. Wenn ein Dialog geöffnet wird, schließe ihn zuerst oder arbeite ihn ab

Antworte IMMER im folgenden JSON-Format:
{
    "action": "click" | "navigate_menu" | "wait" | "back" | "close_dialog",
    "x": <x-koordinate>,
    "y": <y-koordinate>,
    "element_text": "<text des elements>",
    "reason": "<kurze erklärung warum diese aktion>",
    "confidence": <0.0-1.0>,
    "menu_path": ["File", "Save"]  // nur bei navigate_menu
}"""
    
    def decide_next_action(
        self,
        screenshot_path: Path,
        visited_areas: List[str],
        current_context: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Entscheidet nächste Aktion basierend auf Screenshot-Analyse
        
        Args:
            screenshot_path: Pfad zum Screenshot
            visited_areas: Liste bereits besuchter Bereiche (Screenshot-Hashes oder Beschreibungen)
            current_context: Aktueller Kontext (z.B. "Im File-Menü")
            
        Returns:
            Dictionary mit Aktions-Informationen oder None bei Fehler
        """
        try:
            # Formatiere User-Prompt
            visited_text = "\n".join([f"- {area}" for area in visited_areas[-10:]])  # Nur letzte 10
            context_text = f"\nAktueller Kontext: {current_context}" if current_context else ""
            
            user_prompt = f"""Analysiere dieses Screenshot einer Windows-Anwendung und identifiziere die nächste Aktion zur vollständigen App-Erkundung.

Bereits besuchte Bereiche:
{visited_text}
{context_text}

Finde das nächste Element, das geklickt werden sollte, um neue Bereiche der App zu erkunden. Vermeide bereits besuchte Bereiche.

Antworte IMMER im JSON-Format wie oben beschrieben."""
            
            # Generiere Antwort mit Vision API
            response = self.openai_client.generate_text_with_vision(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                image_path=str(screenshot_path),
                temperature=0.3,  # Niedrigere Temperatur für konsistentere Entscheidungen
                max_tokens=500
            )
            
            # Parse JSON aus Antwort
            action_data = self._parse_response(response)
            
            # Prüfe Confidence
            if action_data and action_data.get('confidence', 0.0) >= self.confidence_threshold:
                logger.info(f"AI-Entscheidung: {action_data.get('action')} - {action_data.get('reason')}")
                return action_data
            else:
                logger.warning(f"AI-Entscheidung zu ungewiss (Confidence: {action_data.get('confidence', 0.0) if action_data else 0.0})")
                return None
        
        except Exception as e:
            logger.error(f"Fehler bei AI-Entscheidung: {e}", exc_info=True)
            return None
    
    def _parse_response(self, response: str) -> Optional[Dict]:
        """
        Parst JSON aus AI-Antwort
        
        Args:
            response: Rohe AI-Antwort
            
        Returns:
            Dictionary mit Aktions-Informationen oder None
        """
        try:
            # Versuche JSON zu extrahieren
            # Manchmal ist JSON in Code-Blöcken oder mit zusätzlichem Text
            json_match = re.search(r'\{[^{}]*"action"[^{}]*\}', response, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(0)
                action_data = json.loads(json_str)
                
                # Validiere erforderliche Felder
                if 'action' in action_data:
                    # Setze Standardwerte
                    if 'confidence' not in action_data:
                        action_data['confidence'] = 0.5
                    if 'x' not in action_data:
                        action_data['x'] = 0
                    if 'y' not in action_data:
                        action_data['y'] = 0
                    
                    return action_data
            
            # Fallback: Versuche gesamten Text als JSON zu parsen
            try:
                return json.loads(response)
            except:
                pass
            
            logger.warning(f"Konnte JSON nicht aus Antwort parsen: {response[:200]}")
            return None
        
        except Exception as e:
            logger.error(f"Fehler beim Parsen der AI-Antwort: {e}", exc_info=True)
            return None
    
    def set_confidence_threshold(self, threshold: float):
        """
        Setzt Confidence-Threshold
        
        Args:
            threshold: Neuer Threshold (0.0-1.0)
        """
        self.confidence_threshold = max(0.0, min(1.0, threshold))

