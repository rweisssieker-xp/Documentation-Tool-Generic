"""
Prompt-Template-System
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from src.config.config_manager import ConfigManager


class PromptTemplateSystem:
    """Verwaltet Prompt-Templates aus YAML-Profilen"""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialisiert das Prompt-Template-System
        
        Args:
            config_manager: ConfigManager-Instanz
        """
        if config_manager is None:
            config_manager = ConfigManager()
        self.config_manager = config_manager
        self.current_profile = None
    
    def load_profile(self, profile_name: str) -> Dict[str, Any]:
        """
        Lädt ein Prompt-Profil
        
        Args:
            profile_name: Name des Profils
            
        Returns:
            Profil-Konfiguration
        """
        profile = self.config_manager.load_prompt_profile(profile_name)
        self.current_profile = profile
        return profile
    
    def get_system_prompt(self) -> str:
        """
        Gibt den System-Prompt zurück
        
        Returns:
            System-Prompt
        """
        if not self.current_profile:
            raise ValueError("Kein Profil geladen!")
        
        return self.current_profile.get('system_prompt', '')
    
    def format_step_prompt(
        self,
        step_number: int,
        window_title: str,
        ocr_text: str,
        previous_steps: Optional[list] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Formatiert einen Schritt-Prompt
        
        Args:
            step_number: Schrittnummer
            window_title: Fenstertitel
            ocr_text: OCR-Text aus Screenshot
            previous_steps: Vorherige Schritte für Kontext
            metadata: Zusätzliche Metadaten
            
        Returns:
            Formatierter User-Prompt
        """
        if not self.current_profile:
            raise ValueError("Kein Profil geladen!")
        
        template = self.current_profile.get('step_template', '')
        
        # Kontext aus vorherigen Schritten
        context = ""
        if previous_steps:
            context_lines = []
            for prev_step in previous_steps[-3:]:  # Nur letzte 3 Schritte
                prev_title = prev_step.get('window_title', 'Unbekannt')
                prev_desc = prev_step.get('description', '')
                context_lines.append(f"- {prev_title}: {prev_desc}")
            context = "\n".join(context_lines)
        
        # Ersetze Template-Variablen
        prompt = template.format(
            step_number=step_number,
            window_title=window_title,
            ocr_text=ocr_text[:2000] if ocr_text else "",  # Begrenze OCR-Text
            context=context,
            metadata=metadata or {}
        )
        
        return prompt
    
    def format_introduction_prompt(self, total_steps: int, window_titles: list) -> str:
        """
        Formatiert einen Einleitungs-Prompt
        
        Args:
            total_steps: Gesamtanzahl der Schritte
            window_titles: Liste der Fenstertitel
            
        Returns:
            Formatierter Prompt
        """
        if not self.current_profile:
            raise ValueError("Kein Profil geladen!")
        
        template = self.current_profile.get('introduction_template', '')
        
        return template.format(
            total_steps=total_steps,
            window_titles=", ".join(window_titles[:10])  # Erste 10 Fenstertitel
        )
    
    def format_conclusion_prompt(self, steps: list) -> str:
        """
        Formatiert einen Fazit-Prompt
        
        Args:
            steps: Liste aller Schritte
            
        Returns:
            Formatierter Prompt
        """
        if not self.current_profile:
            raise ValueError("Kein Profil geladen!")
        
        template = self.current_profile.get('conclusion_template', '')
        
        summary = "\n".join([
            f"Schritt {s.get('step_number', '?')}: {s.get('description', '')[:100]}"
            for s in steps
        ])
        
        return template.format(summary=summary)
    
    def format_security_notes_prompt(self, steps: List[Dict]) -> str:
        """
        Formatiert einen Sicherheitshinweise-Prompt
        
        Args:
            steps: Liste aller Schritte
            
        Returns:
            Formatierter Prompt
        """
        if not self.current_profile:
            raise ValueError("Kein Profil geladen!")
        
        template = self.current_profile.get('security_notes_template', '')
        
        summary = "\n".join([
            f"Schritt {s.get('step_number', '?')}: {s.get('description', '')[:100]}"
            for s in steps
        ])
        
        return template.format(summary=summary) if template else ""
    
    def format_troubleshooting_prompt(self, steps: List[Dict]) -> str:
        """
        Formatiert einen Troubleshooting-Prompt
        
        Args:
            steps: Liste aller Schritte
            
        Returns:
            Formatierter Prompt
        """
        if not self.current_profile:
            raise ValueError("Kein Profil geladen!")
        
        template = self.current_profile.get('troubleshooting_template', '')
        
        summary = "\n".join([
            f"Schritt {s.get('step_number', '?')}: {s.get('description', '')[:100]}"
            for s in steps
        ])
        
        return template.format(summary=summary) if template else ""
    
    def get_language(self) -> str:
        """
        Gibt die Sprache des Profils zurück
        
        Returns:
            Sprache (z.B. 'de', 'en')
        """
        if not self.current_profile:
            return 'de'
        
        return self.current_profile.get('language', 'de')
    
    def get_style(self) -> str:
        """
        Gibt den Stil des Profils zurück
        
        Returns:
            Stil (z.B. 'sop', 'training', 'technical')
        """
        if not self.current_profile:
            return 'technical'
        
        return self.current_profile.get('style', 'technical')

