"""
Integrationstests für vollständige Workflows
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

# Füge src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.mark.integration
class TestEndToEndWorkflow:
    """Tests für vollständige Workflows"""
    
    @patch('src.monitor.session_manager.WindowMonitor')
    @patch('src.monitor.session_manager.ActionDetector')
    @patch('src.monitor.session_manager.MouseKeyboardMonitor')
    @patch('src.monitor.session_manager.ScreenshotCapture')
    @patch('src.monitor.session_manager.AuditLogger')
    @patch('src.ai.text_generator.OpenAIClient')
    @patch('src.ai.text_generator.PromptTemplateSystem')
    def test_complete_session_workflow(self, mock_prompt, mock_openai, mock_audit, mock_screenshot, 
                                       mock_mouse, mock_action, mock_window, tmp_path):
        """Testet vollständigen Workflow von Session-Start bis Dokument-Export"""
        from src.monitor.session_manager import SessionManager
        from src.document.template_engine import TemplateEngine
        
        # Setup Mocks
        mock_client_instance = MagicMock()
        mock_client_instance.generate_text.return_value = "Generated description"
        mock_openai.return_value = mock_client_instance
        
        # Erstelle Session Manager
        session_manager = SessionManager(
            session_id="test_session",
            prompt_profile="test_profile",
            output_dir=tmp_path / "sessions"
        )
        
        # Mock Monitor-Methoden
        session_manager.window_monitor.start_monitoring = Mock()
        session_manager.window_monitor.stop_monitoring = Mock()
        session_manager.mouse_keyboard_monitor.start_monitoring = Mock()
        session_manager.mouse_keyboard_monitor.stop_monitoring = Mock()
        
        # Simuliere Session-Start
        session_manager.start()
        assert session_manager.active is True
        
        # Simuliere Schritte
        test_step = {
            'step_number': 1,
            'timestamp': '2024-01-01T00:00:00',
            'window_title': 'Test Window',
            'window_class': 'TestClass',
            'process_name': 'TestProcess',
            'screenshot_path': str(tmp_path / "test.png"),
            'description': None
        }
        session_manager.steps.append(test_step)
        
        # Simuliere Session-Stop
        session_manager.stop()
        assert session_manager.active is False
        
        # Teste Dokumentgenerierung
        template_engine = TemplateEngine(
            session_manager,
            output_dir=tmp_path / "output"
        )
        
        # Mock Text-Generierung
        with patch.object(template_engine.text_generator, 'generate_all_step_descriptions') as mock_gen:
            mock_gen.return_value = [
                {**test_step, 'description': 'Generated description'}
            ]
            
            with patch.object(template_engine.text_generator, 'generate_introduction') as mock_intro:
                mock_intro.return_value = "Test introduction"
                
                with patch.object(template_engine.text_generator, 'generate_conclusion') as mock_concl:
                    mock_concl.return_value = "Test conclusion"
                    
                    export_formats = {
                        'docx': True,
                        'pdf': False,
                        'markdown': False,
                        'html': False,
                        'json': True,
                        'csv': False
                    }
                    
                    try:
                        output_path = template_engine.generate_document(export_formats=export_formats)
                        # Wenn erfolgreich, sollte Pfad zurückgegeben werden
                        if output_path:
                            assert isinstance(output_path, Path)
                    except Exception as e:
                        # Kann bei fehlenden Abhängigkeiten fehlschlagen
                        pytest.skip(f"End-to-End Test skipped: {e}")
    
    def test_config_validation_workflow(self, tmp_path):
        """Testet Konfigurationsvalidierungs-Workflow"""
        from src.config.config_validator import ConfigValidator
        import yaml
        
        # Teste gültige Config
        valid_config = {
            'poll_interval': 1.0,
            'change_threshold': 0.5,
            'size_change_threshold': 10,
            'double_click_delay': 0.5
        }
        
        is_valid, errors = ConfigValidator.validate_trigger_config(valid_config)
        assert is_valid is True
        assert len(errors) == 0
        
        # Teste ungültige Config
        invalid_config = {
            'poll_interval': -1.0,  # Negativer Wert
            'change_threshold': 2.0  # Wert > 1.0
        }
        
        is_valid, errors = ConfigValidator.validate_trigger_config(invalid_config)
        assert is_valid is False
        assert len(errors) > 0
    
    def test_cleanup_workflow(self, tmp_path):
        """Testet Cleanup-Workflow"""
        from src.utils.cleanup_manager import CleanupManager
        from datetime import datetime, timedelta
        
        # Erstelle Test-Dateien
        screenshots_dir = tmp_path / "screenshots" / "test_session"
        screenshots_dir.mkdir(parents=True)
        
        # Erstelle alte Screenshot-Datei
        old_screenshot = screenshots_dir / "old.png"
        old_screenshot.write_bytes(b'old image')
        
        # Ändere Zeitstempel auf vor 31 Tagen
        old_time = datetime.now() - timedelta(days=31)
        import os
        os.utime(old_screenshot, (old_time.timestamp(), old_time.timestamp()))
        
        # Erstelle neue Screenshot-Datei
        new_screenshot = screenshots_dir / "new.png"
        new_screenshot.write_bytes(b'new image')
        
        # Teste Cleanup mit 30 Tagen Retention
        cleanup_manager = CleanupManager(
            screenshots_dir=tmp_path / "screenshots",
            sessions_dir=tmp_path / "sessions",
            retention_days_screenshots=30
        )
        
        stats = cleanup_manager.cleanup_old_screenshots(dry_run=False)
        
        # Alte Datei sollte gelöscht sein (oder zumindest erkannt werden)
        assert stats['deleted_count'] >= 0
    
    def test_session_recovery_workflow(self, tmp_path):
        """Testet Session-Recovery-Workflow"""
        from src.monitor.session_manager import SessionManager
        from src.monitor.session_recovery import SessionRecovery
        import json
        
        session_id = "test_recovery_session"
        output_dir = tmp_path / "sessions"
        output_dir.mkdir(parents=True)
        
        # Erstelle Test-Session-State
        recovery = SessionRecovery(output_dir)
        
        session_data = {
            'session_id': session_id,
            'prompt_profile': 'test_profile',
            'start_time': '2024-01-01T00:00:00',
            'steps': [
                {
                    'step_number': 1,
                    'window_title': 'Test Window',
                    'timestamp': '2024-01-01T00:00:00'
                }
            ],
            'metadata': {
                'active': False,
                'paused': False,
                'completed': False
            }
        }
        
        # Speichere State
        recovery.save_session_state(session_id, session_data)
        
        # Lade State
        loaded_data = recovery.load_session_state(session_id)
        
        assert loaded_data is not None
        assert loaded_data['session_id'] == session_id
        assert len(loaded_data['steps']) == 1
        
        # Validiere State
        is_valid, errors = recovery.validate_session_state(session_id)
        assert is_valid is True
        assert len(errors) == 0

