"""
Konfigurationsvalidierung für YAML-Config-Dateien
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ConfigValidator:
    """Validiert YAML-Konfigurationsdateien"""
    
    @staticmethod
    def validate_prompt_profile(config: Dict) -> Tuple[bool, List[str]]:
        """
        Validiert ein Prompt-Profil
        
        Args:
            config: Konfigurations-Dictionary
            
        Returns:
            Tuple (is_valid, list_of_errors)
        """
        errors = []
        
        # Erforderliche Felder
        required_fields = ['language', 'style', 'system_prompt']
        for field in required_fields:
            if field not in config:
                errors.append(f"Fehlendes erforderliches Feld: '{field}'")
        
        # Validiere Sprache
        if 'language' in config:
            valid_languages = ['de', 'en', 'deu', 'eng']
            if config['language'] not in valid_languages and not any(
                config['language'].startswith(lang) for lang in valid_languages
            ):
                errors.append(f"Ungültige Sprache: '{config['language']}'. Erlaubt: {valid_languages}")
        
        # Validiere Stil
        if 'style' in config:
            valid_styles = ['sop', 'training', 'technical', 'formal', 'informal']
            if config['style'] not in valid_styles:
                errors.append(f"Ungültiger Stil: '{config['style']}'. Erlaubt: {valid_styles}")
        
        # Validiere Templates
        template_fields = ['step_template', 'introduction_template', 'conclusion_template']
        for field in template_fields:
            if field in config and not isinstance(config[field], str):
                errors.append(f"Template-Feld '{field}' muss ein String sein")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_trigger_config(config: Dict) -> Tuple[bool, List[str]]:
        """
        Validiert Trigger-Konfiguration
        
        Args:
            config: Konfigurations-Dictionary
            
        Returns:
            Tuple (is_valid, list_of_errors)
        """
        errors = []
        
        numeric_fields = {
            'poll_interval': (0.1, 10.0),
            'change_threshold': (0.0, 10.0),
            'size_change_threshold': (0, 1000),
            'double_click_delay': (0.0, 5.0)
        }
        
        for field, (min_val, max_val) in numeric_fields.items():
            if field in config:
                try:
                    value = float(config[field])
                    if not (min_val <= value <= max_val):
                        errors.append(f"'{field}' muss zwischen {min_val} und {max_val} liegen. Aktuell: {value}")
                except (ValueError, TypeError):
                    errors.append(f"'{field}' muss eine Zahl sein. Aktuell: {type(config[field])}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_privacy_mask_config(config: Dict) -> Tuple[bool, List[str]]:
        """
        Validiert Privacy-Mask-Konfiguration
        
        Args:
            config: Konfigurations-Dictionary
            
        Returns:
            Tuple (is_valid, list_of_errors)
        """
        errors = []
        
        # 'enabled' sollte boolean sein
        if 'enabled' in config and not isinstance(config['enabled'], bool):
            errors.append("'enabled' muss ein Boolean sein")
        
        # 'regions' sollte eine Liste sein
        if 'regions' in config:
            if not isinstance(config['regions'], list):
                errors.append("'regions' muss eine Liste sein")
            else:
                # Validiere jede Region
                for i, region in enumerate(config['regions']):
                    if not isinstance(region, dict):
                        errors.append(f"Region {i} muss ein Dictionary sein")
                        continue
                    
                    region_type = region.get('type', '')
                    valid_types = ['rectangle', 'circle', 'polygon']
                    if region_type not in valid_types:
                        errors.append(f"Region {i}: Ungültiger Typ '{region_type}'. Erlaubt: {valid_types}")
                    
                    # Validiere Koordinaten je nach Typ
                    if region_type == 'rectangle':
                        required = ['x', 'y', 'width', 'height']
                        for req in required:
                            if req not in region:
                                errors.append(f"Region {i} (rectangle): Fehlendes Feld '{req}'")
                    
                    elif region_type == 'circle':
                        required = ['center_x', 'center_y', 'radius']
                        for req in required:
                            if req not in region:
                                errors.append(f"Region {i} (circle): Fehlendes Feld '{req}'")
                    
                    elif region_type == 'polygon':
                        if 'points' not in region:
                            errors.append(f"Region {i} (polygon): Fehlendes Feld 'points'")
                        elif not isinstance(region['points'], list) or len(region['points']) < 3:
                            errors.append(f"Region {i} (polygon): 'points' muss eine Liste mit mindestens 3 Punkten sein")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_document_template(config: Dict) -> Tuple[bool, List[str]]:
        """
        Validiert Dokumentvorlage
        
        Args:
            config: Konfigurations-Dictionary
            
        Returns:
            Tuple (is_valid, list_of_errors)
        """
        errors = []
        
        # Erforderliche Felder
        if 'name' not in config:
            errors.append("Fehlendes erforderliches Feld: 'name'")
        
        # Validiere Struktur
        if 'structure' in config:
            structure = config['structure']
            if not isinstance(structure, dict):
                errors.append("'structure' muss ein Dictionary sein")
            else:
                boolean_fields = [
                    'include_title_page', 'include_table_of_contents',
                    'include_introduction', 'include_steps',
                    'include_conclusion', 'include_security_notes',
                    'include_troubleshooting'
                ]
                for field in boolean_fields:
                    if field in structure and not isinstance(structure[field], bool):
                        errors.append(f"'{field}' muss ein Boolean sein")
        
        # Validiere Formatierung
        if 'formatting' in config:
            formatting = config['formatting']
            if not isinstance(formatting, dict):
                errors.append("'formatting' muss ein Dictionary sein")
            else:
                numeric_fields = ['title_font_size', 'heading_font_size', 'body_font_size']
                for field in numeric_fields:
                    if field in formatting:
                        try:
                            value = float(formatting[field])
                            if value <= 0:
                                errors.append(f"'{field}' muss größer als 0 sein")
                        except (ValueError, TypeError):
                            errors.append(f"'{field}' muss eine Zahl sein")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_yaml_file(file_path: Path, config_type: str) -> Tuple[bool, Optional[Dict], List[str]]:
        """
        Validiert eine YAML-Datei
        
        Args:
            file_path: Pfad zur YAML-Datei
            config_type: Typ der Konfiguration ('prompt_profile', 'trigger_config', 'privacy_mask', 'document_template')
            
        Returns:
            Tuple (is_valid, config_dict, list_of_errors)
        """
        errors = []
        
        # Prüfe ob Datei existiert
        if not file_path.exists():
            errors.append(f"Datei existiert nicht: {file_path}")
            return False, None, errors
        
        # Lade YAML
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            errors.append(f"YAML-Syntaxfehler: {e}")
            return False, None, errors
        except Exception as e:
            errors.append(f"Fehler beim Laden der Datei: {e}")
            return False, None, errors
        
        if config is None:
            errors.append("Konfigurationsdatei ist leer")
            return False, None, errors
        
        # Validiere basierend auf Typ
        if config_type == 'prompt_profile':
            is_valid, validation_errors = ConfigValidator.validate_prompt_profile(config)
        elif config_type == 'trigger_config':
            is_valid, validation_errors = ConfigValidator.validate_trigger_config(config)
        elif config_type == 'privacy_mask':
            is_valid, validation_errors = ConfigValidator.validate_privacy_mask_config(config)
        elif config_type == 'document_template':
            is_valid, validation_errors = ConfigValidator.validate_document_template(config)
        else:
            errors.append(f"Unbekannter Konfigurationstyp: {config_type}")
            return False, config, errors
        
        errors.extend(validation_errors)
        
        return len(errors) == 0, config, errors

