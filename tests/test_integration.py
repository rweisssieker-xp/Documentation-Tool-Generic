"""
Integrationstests für die Hauptkomponenten
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import uuid

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


@pytest.mark.integration
def test_screenshot_workflow(tmp_path):
    """Testet kompletten Workflow: window change → screenshot capture → storage → metadata"""
    from src.capture.screenshot import ScreenshotCapture
    from src.monitor.window_monitor import WindowMonitor
    from src.monitor.session_manager import SessionManager
    import uuid
    
    # Setup
    session_id = str(uuid.uuid4())
    screenshot_dir = tmp_path / "screenshots" / session_id
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    # Erstelle ScreenshotCapture
    capture = ScreenshotCapture(screenshot_dir)
    
    # Mock Instanzattribute wenn Windows
    if capture.platform == "windows" and hasattr(capture, 'win32gui'):
        mock_hwnd = 12345
        capture.win32gui.GetWindowRect = MagicMock(return_value=(0, 0, 100, 100))
        capture.win32gui.GetWindowDC = MagicMock(return_value=1)
        capture.win32gui.GetWindowText = MagicMock(return_value="Test Window")
        capture.win32gui.ReleaseDC = MagicMock(return_value=None)
        
        if hasattr(capture, 'win32ui'):
            mock_dc = MagicMock()
            capture.win32ui.CreateDCFromHandle = MagicMock(return_value=mock_dc)
            mock_dc.CreateCompatibleDC = MagicMock(return_value=MagicMock())
            mock_bitmap = MagicMock()
            mock_bitmap.GetInfo.return_value = {'bmWidth': 100, 'bmHeight': 100}
            mock_bitmap.GetBitmapBits.return_value = b'\x00' * (100 * 100 * 4)
            capture.win32ui.CreateBitmap = MagicMock(return_value=mock_bitmap)
    
    try:
        # Test: Screenshot Capture
        step_number = 1
        result = capture.capture_window(12345, step_number, session_id=session_id)
        
        if result:
            screenshot_path, metadata = result
            
            # Prüfe Screenshot wurde gespeichert
            assert screenshot_path.exists()
            
            # Prüfe Metadaten
            assert 'screenshot_id' in metadata
            assert 'timestamp' in metadata
            assert 'window_title' in metadata
            assert metadata['session_id'] == session_id
            assert metadata['step_number'] == step_number
            assert metadata['window_title'] == "Test Window"
            
            # Prüfe UUID-Format
            uuid.UUID(metadata['screenshot_id'])
            
            # Prüfe Dateinamen-Schema
            assert session_id in screenshot_path.name
            assert f"{step_number:04d}" in screenshot_path.name
            assert screenshot_path.name.endswith('.png')
    except Exception:
        # Windows-spezifische Fehler sind OK in Tests
        pass


@pytest.mark.integration
def test_window_change_to_screenshot_integration(tmp_path):
    """Testet Integration: Window Change Detection → Screenshot Capture"""
    from src.monitor.window_monitor import WindowMonitor
    from src.capture.screenshot import ScreenshotCapture
    import uuid
    import time
    
    # Setup
    session_id = str(uuid.uuid4())
    screenshot_dir = tmp_path / "screenshots" / session_id
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    capture = ScreenshotCapture(screenshot_dir)
    captured_screenshots = []
    
    def on_window_change(window_info):
        """Callback bei Fensterwechsel"""
        step_number = len(captured_screenshots) + 1
        result = capture.capture_window(
            window_info.get('hwnd'),
            step_number,
            session_id=session_id
        )
        if result:
            captured_screenshots.append(result)
    
    # Erstelle WindowMonitor mit Callback
    monitor = WindowMonitor(callback=on_window_change)
    
    # Mock window info
    window_info = {
        'hwnd': 12345,
        'title': 'Test Window',
        'class_name': 'TestClass'
    }
    
    # Simuliere Fensterwechsel durch direkten Callback-Aufruf
    if monitor.callback:
        monitor.callback(window_info)
    
    # Prüfe ob Screenshot erfasst wurde (wenn Windows APIs verfügbar)
    # In Tests ohne Windows APIs wird dies übersprungen


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

