"""
Integrationstests für die Hauptkomponenten
"""

import sys
import pytest
from pathlib import Path

# Füge src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.mark.integration
def test_imports():
    """Testet ob alle Module importiert werden können"""
    try:
        from src.config.config_manager import ConfigManager
        from src.audit.audit_logger import AuditLogger
        from src.capture.screenshot import ScreenshotCapture
        from src.capture.ocr_engine import OCREngine
        from src.monitor.window_monitor import WindowMonitor
        from src.monitor.action_detector import ActionDetector
        from src.ai.openai_client import OpenAIClient
        from src.ai.prompt_templates import PromptTemplateSystem
        from src.document.docx_builder import DOCXBuilder
        from src.document.template_engine import TemplateEngine
        from src.utils.logger import setup_logging
        from src.utils.cleanup_manager import CleanupManager
        from src.monitor.session_recovery import SessionRecovery
        
        assert True  # Alle Imports erfolgreich
    except ImportError as e:
        pytest.fail(f"Import-Fehler: {e}")


@pytest.mark.integration
def test_config_manager():
    """Testet ConfigManager"""
    from src.config.config_manager import ConfigManager
    
    config_manager = ConfigManager()
    profiles = config_manager.list_prompt_profiles()
    
    assert isinstance(profiles, list)
    
    if profiles:
        profile = config_manager.load_prompt_profile(profiles[0])
        assert 'language' in profile or 'system_prompt' in profile


@pytest.mark.integration
def test_ocr_engine():
    """Testet OCR-Engine Verfügbarkeit"""
    from src.capture.ocr_engine import OCREngine
    
    ocr = OCREngine()
    is_available = ocr.is_available()
    
    assert isinstance(is_available, bool)


@pytest.mark.integration
def test_logger_setup():
    """Testet Logger-Setup"""
    from src.utils.logger import setup_logging, get_logger
    
    setup_logging()
    logger = get_logger(__name__)
    
    assert logger is not None
    logger.info("Test log message")


@pytest.mark.integration
def test_config_validator():
    """Testet ConfigValidator"""
    from src.config.config_validator import ConfigValidator
    
    # Teste gültiges Prompt-Profil
    valid_profile = {
        'language': 'de',
        'style': 'technical',
        'system_prompt': 'Test',
        'step_template': 'Test',
        'introduction_template': 'Test',
        'conclusion_template': 'Test'
    }
    
    is_valid, errors = ConfigValidator.validate_prompt_profile(valid_profile)
    assert is_valid is True
    assert len(errors) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

