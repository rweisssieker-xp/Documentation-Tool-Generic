"""
Unit-Tests für Config-Module
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import yaml
import tempfile
import shutil

# Füge src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.config.config_manager import ConfigManager
from src.config.config_validator import ConfigValidator
from src.config.trigger_config import TriggerConfig


class TestConfigManager:
    """Tests für ConfigManager"""
    
    def test_list_prompt_profiles(self, tmp_path):
        """Testet das Auflisten von Prompt-Profilen"""
        # Erstelle temporäres Config-Verzeichnis
        config_dir = tmp_path / "config" / "prompt_profiles"
        config_dir.mkdir(parents=True)
        
        # Erstelle Test-Profil
        test_profile = config_dir / "test.yml"
        test_profile.write_text(yaml.dump({
            'language': 'de',
            'style': 'technical'
        }))
        
        with patch('src.config.config_manager.Path') as mock_path:
            mock_path.return_value = config_dir
            manager = ConfigManager()
            profiles = manager.list_prompt_profiles()
            
            assert 'test' in profiles
    
    def test_load_prompt_profile(self, tmp_path):
        """Testet das Laden eines Prompt-Profils"""
        config_dir = tmp_path / "config" / "prompt_profiles"
        config_dir.mkdir(parents=True)
        
        test_profile = config_dir / "test.yml"
        test_data = {
            'language': 'de',
            'style': 'technical',
            'system_prompt': 'Test prompt'
        }
        test_profile.write_text(yaml.dump(test_data))
        
        with patch('src.config.config_manager.Path') as mock_path:
            mock_path.return_value = config_dir
            manager = ConfigManager()
            profile = manager.load_prompt_profile('test')
            
            assert profile['language'] == 'de'
            assert profile['style'] == 'technical'


class TestConfigValidator:
    """Tests für ConfigValidator"""
    
    def test_validate_prompt_profile_valid(self):
        """Testet Validierung eines gültigen Prompt-Profils"""
        valid_profile = {
            'language': 'de',
            'style': 'technical',
            'system_prompt': 'Test prompt',
            'step_template': 'Step: {step_number}',
            'introduction_template': 'Introduction',
            'conclusion_template': 'Conclusion'
        }
        
        is_valid, errors = ConfigValidator.validate_prompt_profile(valid_profile)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_prompt_profile_invalid(self):
        """Testet Validierung eines ungültigen Prompt-Profils"""
        invalid_profile = {
            'language': 'de'
            # Fehlende erforderliche Felder
        }
        
        is_valid, errors = ConfigValidator.validate_prompt_profile(invalid_profile)
        assert is_valid is False
        assert len(errors) > 0
    
    def test_validate_trigger_config_valid(self):
        """Testet Validierung einer gültigen Trigger-Config"""
        valid_config = {
            'poll_interval': 1.0,
            'change_threshold': 0.5,
            'size_change_threshold': 10,
            'double_click_delay': 0.5
        }
        
        is_valid, errors = ConfigValidator.validate_trigger_config(valid_config)
        assert is_valid is True
        assert len(errors) == 0


class TestTriggerConfig:
    """Tests für TriggerConfig"""
    
    def test_load_default_config(self):
        """Testet Laden der Standard-Konfiguration"""
        config = TriggerConfig()
        
        assert config.poll_interval > 0
        assert config.change_threshold > 0
        assert config.size_change_threshold > 0
    
    def test_load_from_file(self, tmp_path):
        """Testet Laden aus YAML-Datei"""
        import yaml
        
        config_file = tmp_path / "trigger_config.yml"
        config_data = {
            'poll_interval': 2.0,
            'change_threshold': 0.7,
            'size_change_threshold': 20,
            'double_click_delay': 0.3
        }
        config_file.write_text(yaml.dump(config_data))
        
        config = TriggerConfig(config_file)
        
        assert config.poll_interval == 2.0
        assert config.change_threshold == 0.7
        assert config.size_change_threshold == 20
        assert config.double_click_delay == 0.3
    
    def test_save_config(self, tmp_path):
        """Testet Speichern der Konfiguration"""
        config_file = tmp_path / "trigger_config.yml"
        config = TriggerConfig()
        config.poll_interval = 3.0
        
        config.save(config_file)
        
        assert config_file.exists()
        loaded_config = TriggerConfig(config_file)
        assert loaded_config.poll_interval == 3.0

