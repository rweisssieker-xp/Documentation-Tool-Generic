"""
Config Manager für YAML-Konfigurationen
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
from src.config.config_validator import ConfigValidator
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """Verwaltet Konfigurationsdateien und Prompt-Profile"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialisiert den Config Manager
        
        Args:
            config_dir: Pfad zum Konfigurationsverzeichnis
        """
        if config_dir is None:
            config_dir = Path(__file__).parent.parent.parent / "config"
        self.config_dir = Path(config_dir)
        self.prompt_profiles_dir = self.config_dir / "prompt_profiles"
    
    def load_prompt_profile(self, profile_name: str) -> Dict[str, Any]:
        """
        Lädt ein Prompt-Profil aus einer YAML-Datei
        
        Args:
            profile_name: Name des Profils (ohne .yml Extension)
            
        Returns:
            Dictionary mit Profil-Konfiguration
        """
        profile_path = self.prompt_profiles_dir / f"{profile_name}.yml"
        
        if not profile_path.exists():
            raise FileNotFoundError(f"Prompt-Profil '{profile_name}' nicht gefunden: {profile_path}")
        
        # Validiere Konfiguration
        is_valid, config, errors = ConfigValidator.validate_yaml_file(profile_path, 'prompt_profile')
        if not is_valid:
            error_msg = f"Ungültiges Prompt-Profil '{profile_name}':\n" + "\n".join(f"  - {e}" for e in errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        return config
    
    def list_prompt_profiles(self) -> list[str]:
        """
        Listet alle verfügbaren Prompt-Profile auf
        
        Returns:
            Liste von Profil-Namen
        """
        if not self.prompt_profiles_dir.exists():
            return []
        
        profiles = []
        for file in self.prompt_profiles_dir.glob("*.yml"):
            profiles.append(file.stem)
        
        return sorted(profiles)
    
    def save_prompt_profile(self, profile_name: str, config: Dict[str, Any]) -> None:
        """
        Speichert ein Prompt-Profil
        
        Args:
            profile_name: Name des Profils
            config: Konfigurations-Dictionary
        """
        self.prompt_profiles_dir.mkdir(parents=True, exist_ok=True)
        profile_path = self.prompt_profiles_dir / f"{profile_name}.yml"
        
        with open(profile_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


