"""
Textgenerierung mit OpenAI und Kontext
"""

from typing import List, Dict, Optional
from pathlib import Path

from src.ai.openai_client import OpenAIClient
from src.ai.prompt_templates import PromptTemplateSystem
from src.capture.ocr_engine import OCREngine
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TextGenerator:
    """Generiert Texte für Handbuch-Schritte mit AI"""
    
    def __init__(self, prompt_profile: str, ocr_language: str = "deu+eng"):
        """
        Initialisiert den Text-Generator
        
        Args:
            prompt_profile: Name des Prompt-Profils
            ocr_language: Sprache für OCR
        """
        self.openai_client = OpenAIClient()
        self.prompt_system = PromptTemplateSystem()
        self.prompt_system.load_profile(prompt_profile)
        self.ocr_engine = OCREngine(language=ocr_language)
    
    def generate_step_description(
        self,
        step: Dict,
        previous_steps: Optional[List[Dict]] = None
    ) -> str:
        """
        Generiert Beschreibung für einen Schritt
        
        Args:
            step: Schritt-Dictionary
            previous_steps: Vorherige Schritte für Kontext
            
        Returns:
            Generierte Beschreibung
        """
        try:
            # Extrahiere OCR-Text aus Screenshot
            screenshot_path = Path(step.get('screenshot_path', ''))
            ocr_text = ""
            
            if screenshot_path.exists() and self.ocr_engine.is_available():
                ocr_text = self.ocr_engine.extract_text(screenshot_path)
            
            # Hole System-Prompt
            system_prompt = self.prompt_system.get_system_prompt()
            
            # Formatiere User-Prompt
            user_prompt = self.prompt_system.format_step_prompt(
                step_number=step.get('step_number', 0),
                window_title=step.get('window_title', 'Unbekannt'),
                ocr_text=ocr_text,
                previous_steps=previous_steps,
                metadata=step.get('metadata', {})
            )
            
            # Generiere Text
            description = self.openai_client.generate_text(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.7,
                max_tokens=500
            )
            
            return description
        
        except Exception as e:
            logger.error(f"Fehler bei Textgenerierung: {e}", exc_info=True)
            return f"Schritt {step.get('step_number', '?')}: {step.get('window_title', 'Unbekannt')}"
    
    def generate_all_step_descriptions(self, steps: List[Dict]) -> List[Dict]:
        """
        Generiert Beschreibungen für alle Schritte
        
        Args:
            steps: Liste von Schritten
            
        Returns:
            Liste von Schritten mit generierten Beschreibungen
        """
        updated_steps = []
        
        for i, step in enumerate(steps):
            previous_steps = updated_steps  # Verwende bereits generierte Schritte als Kontext
            
            logger.debug(f"Generiere Beschreibung für Schritt {step.get('step_number', i+1)}...")
            
            description = self.generate_step_description(step, previous_steps)
            step['description'] = description
            
            updated_steps.append(step)
        
        return updated_steps
    
    def generate_introduction(self, steps: List[Dict]) -> str:
        """
        Generiert Einleitung für das Handbuch
        
        Args:
            steps: Liste aller Schritte
            
        Returns:
            Generierte Einleitung
        """
        try:
            window_titles = [s.get('window_title', '') for s in steps]
            total_steps = len(steps)
            
            prompt = self.prompt_system.format_introduction_prompt(total_steps, window_titles)
            system_prompt = self.prompt_system.get_system_prompt()
            
            introduction = self.openai_client.generate_text(
                system_prompt=system_prompt,
                user_prompt=prompt,
                temperature=0.7,
                max_tokens=300
            )
            
            return introduction
        
        except Exception as e:
            logger.error(f"Fehler bei Einleitung-Generierung: {e}", exc_info=True)
            return f"Dieses Handbuch beschreibt einen Prozess mit {len(steps)} Schritten."
    
    def generate_conclusion(self, steps: List[Dict]) -> str:
        """
        Generiert Fazit für das Handbuch
        
        Args:
            steps: Liste aller Schritte
            
        Returns:
            Generiertes Fazit
        """
        try:
            prompt = self.prompt_system.format_conclusion_prompt(steps)
            system_prompt = self.prompt_system.get_system_prompt()
            
            conclusion = self.openai_client.generate_text(
                system_prompt=system_prompt,
                user_prompt=prompt,
                temperature=0.7,
                max_tokens=300
            )
            
            return conclusion
        
        except Exception as e:
            logger.error(f"Fehler bei Fazit-Generierung: {e}", exc_info=True)
            return f"Dieses Handbuch beschreibt einen Prozess mit {len(steps)} Schritten."
    
    def generate_security_notes(self, steps: List[Dict]) -> str:
        """
        Generiert Sicherheitshinweise für das Handbuch
        
        Args:
            steps: Liste aller Schritte
            
        Returns:
            Generierte Sicherheitshinweise
        """
        try:
            prompt = self.prompt_system.format_security_notes_prompt(steps)
            system_prompt = self.prompt_system.get_system_prompt()
            
            if not prompt:
                # Fallback wenn kein Template vorhanden
                return "Bitte beachten Sie die Sicherheitsrichtlinien Ihrer Organisation bei der Durchführung dieser Schritte."
            
            security_notes = self.openai_client.generate_text(
                system_prompt=system_prompt,
                user_prompt=prompt,
                temperature=0.7,
                max_tokens=400
            )
            
            return security_notes
        
        except Exception as e:
            logger.error(f"Fehler bei Sicherheitshinweise-Generierung: {e}", exc_info=True)
            return "Bitte beachten Sie die Sicherheitsrichtlinien Ihrer Organisation bei der Durchführung dieser Schritte."
    
    def generate_troubleshooting(self, steps: List[Dict]) -> List[Dict[str, str]]:
        """
        Generiert Troubleshooting-Einträge basierend auf erkannten Problemen
        
        Args:
            steps: Liste aller Schritte
            
        Returns:
            Liste von Troubleshooting-Einträgen (Problem/Lösung-Paare)
        """
        try:
            # Sammle alle Beschreibungen und OCR-Texte
            all_text = []
            for step in steps:
                description = step.get('description', '')
                if description:
                    all_text.append(description)
                
                # Extrahiere OCR-Text für Problem-Erkennung
                screenshot_path = Path(step.get('screenshot_path', ''))
                if screenshot_path.exists() and self.ocr_engine.is_available():
                    ocr_text = self.ocr_engine.extract_text(screenshot_path)
                    if ocr_text:
                        all_text.append(ocr_text[:500])  # Begrenze Textlänge
            
            combined_text = "\n\n".join(all_text[:10])  # Erste 10 Schritte
            
            # Generiere Troubleshooting mit AI
            system_prompt = """Du bist ein Experte für die Analyse von Software-Bedienungsanleitungen.
Analysiere die gegebenen Schritte und identifiziere potenzielle Probleme oder Fehlerquellen.
Für jedes identifizierte Problem erstelle einen Eintrag mit:
- Problem: Kurze Beschreibung des Problems
- Lösung: Konkrete Lösungsschritte

Antworte im Format:
PROBLEM: [Problem-Beschreibung]
LÖSUNG: [Lösung-Beschreibung]

Wenn keine Probleme erkannt werden, antworte mit "KEINE_PROBLEME"."""
            
            user_prompt = f"""Analysiere die folgenden Schritte einer Bedienungsanleitung und identifiziere potenzielle Probleme:

{combined_text}

Identifiziere 3-5 häufige Probleme und deren Lösungen."""
            
            response = self.openai_client.generate_text(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.7,
                max_tokens=600
            )
            
            # Parse Antwort
            troubleshooting_items = self._parse_troubleshooting_response(response)
            
            return troubleshooting_items
        
        except Exception as e:
            logger.error(f"Fehler bei Troubleshooting-Generierung: {e}", exc_info=True)
            return []
    
    def _parse_troubleshooting_response(self, response: str) -> List[Dict[str, str]]:
        """
        Parst die Troubleshooting-Antwort von OpenAI
        
        Args:
            response: Rohe Antwort von OpenAI
            
        Returns:
            Liste von Troubleshooting-Einträgen
        """
        items = []
        
        if "KEINE_PROBLEME" in response.upper():
            return items
        
        # Teile Antwort in Problem-Lösung-Paare
        lines = response.split('\n')
        current_problem = None
        current_solution = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.upper().startswith('PROBLEM:'):
                # Speichere vorheriges Paar
                if current_problem and current_solution:
                    items.append({
                        'problem': current_problem,
                        'solution': ' '.join(current_solution)
                    })
                
                # Starte neues Problem
                current_problem = line[8:].strip()  # Entferne "PROBLEM:"
                current_solution = []
            
            elif line.upper().startswith('LÖSUNG:') or line.upper().startswith('LÖSUNG:'):
                if current_solution:
                    current_solution.append(line[7:].strip())
            
            elif current_problem:
                # Fortsetzung der Lösung
                current_solution.append(line)
        
        # Füge letztes Paar hinzu
        if current_problem and current_solution:
            items.append({
                'problem': current_problem,
                'solution': ' '.join(current_solution)
            })
        
        return items

