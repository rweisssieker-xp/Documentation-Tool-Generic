"""
Konfigurierbare Trigger-Schwellenwerte
"""

import yaml
from pathlib import Path
from typing import Dict, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TriggerConfig:
    """Verwaltet konfigurierbare Trigger-Schwellenwerte"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialisiert die Trigger-Konfiguration
        
        Args:
            config_path: Pfad zur YAML-Konfigurationsdatei
        """
        # Standard-Werte
        self.poll_interval = 0.5  # Sekunden zwischen Prüfungen
        self.change_threshold = 0.3  # Sekunden zwischen Änderungen
        self.size_change_threshold = 50  # Pixel für Größenänderung
        self.double_click_delay = 0.5  # Sekunden für Doppelklick
        
        if config_path and config_path.exists():
            self.load_config(config_path)
        else:
            # Lade Standard-Config falls vorhanden
            default_config = Path("config") / "trigger_config.yml"
            if default_config.exists():
                self.load_config(default_config)
    
    def load_config(self, config_path: Path):
        """
        Lädt Trigger-Konfiguration aus YAML
        
        Args:
            config_path: Pfad zur YAML-Datei
        """
        try:
            # Validiere Konfiguration
            from src.config.config_validator import ConfigValidator
            is_valid, config, errors = ConfigValidator.validate_yaml_file(config_path, 'trigger_config')
            
            if not is_valid:
                error_msg = f"Ungültige Trigger-Konfiguration:\n" + "\n".join(f"  - {e}" for e in errors)
                logger.warning(error_msg)
                # Verwende Standard-Werte wenn Validierung fehlschlägt
                return
            
            self.poll_interval = config.get('poll_interval', self.poll_interval)
            self.change_threshold = config.get('change_threshold', self.change_threshold)
            self.size_change_threshold = config.get('size_change_threshold', self.size_change_threshold)
            self.double_click_delay = config.get('double_click_delay', self.double_click_delay)
        
        except Exception as e:
            logger.warning(f"Fehler beim Laden der Trigger-Konfiguration: {e}", exc_info=True)
    
    def save_config(self, config_path: Path):
        """
        Speichert Trigger-Konfiguration
        
        Args:
            config_path: Pfad zur YAML-Datei
        """
        config = {
            'poll_interval': self.poll_interval,
            'change_threshold': self.change_threshold,
            'size_change_threshold': self.size_change_threshold,
            'double_click_delay': self.double_click_delay
        }
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    def to_dict(self) -> Dict:
        """
        Gibt Konfiguration als Dictionary zurück
        
        Returns:
            Dictionary mit Konfigurationswerten
        """
        return {
            'poll_interval': self.poll_interval,
            'change_threshold': self.change_threshold,
            'size_change_threshold': self.size_change_threshold,
            'double_click_delay': self.double_click_delay
        }

