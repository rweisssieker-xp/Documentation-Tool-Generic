"""
Unit-Tests für Monitor-Module
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import time

# Füge src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.monitor.action_detector import ActionDetector
from src.monitor.session_manager import SessionManager
from src.config.trigger_config import TriggerConfig


class TestActionDetector:
    """Tests für ActionDetector"""
    
    def test_init(self):
        """Testet Initialisierung"""
        trigger_config = TriggerConfig()
        detector = ActionDetector(trigger_config=trigger_config)
        
        assert detector is not None
        assert detector.change_threshold == trigger_config.change_threshold
    
    def test_detect_change_new_window(self):
        """Testet Erkennung eines neuen Fensters"""
        trigger_config = TriggerConfig()
        detector = ActionDetector(trigger_config=trigger_config)
        
        window_info = {
            'hwnd': 12345,
            'title': 'New Window',
            'class_name': 'TestClass'
        }
        
        # Erste Erkennung sollte Änderung melden
        result = detector.detect_change(window_info)
        assert result is True
    
    def test_detect_change_same_window(self):
        """Testet dass gleiches Fenster nicht als Änderung erkannt wird"""
        trigger_config = TriggerConfig()
        detector = ActionDetector(trigger_config=trigger_config)
        
        window_info = {
            'hwnd': 12345,
            'title': 'Same Window',
            'class_name': 'TestClass'
        }
        
        # Erste Erkennung
        detector.detect_change(window_info)
        
        # Zweite Erkennung sollte keine Änderung melden
        result = detector.detect_change(window_info)
        assert result is False
    
    def test_detect_change_title_change(self):
        """Testet Erkennung von Titeländerung"""
        trigger_config = TriggerConfig()
        detector = ActionDetector(trigger_config=trigger_config)
        
        window_info1 = {
            'hwnd': 12345,
            'title': 'Window 1',
            'class_name': 'TestClass'
        }
        
        window_info2 = {
            'hwnd': 12345,
            'title': 'Window 2',  # Titel geändert
            'class_name': 'TestClass'
        }
        
        detector.detect_change(window_info1)
        result = detector.detect_change(window_info2)
        
        assert result is True


class TestSessionManager:
    """Tests für SessionManager"""
    
    @patch('src.monitor.session_manager.WindowMonitor')
    @patch('src.monitor.session_manager.ActionDetector')
    @patch('src.monitor.session_manager.MouseKeyboardMonitor')
    @patch('src.monitor.session_manager.ScreenshotCapture')
    @patch('src.monitor.session_manager.AuditLogger')
    def test_init(self, mock_audit, mock_screenshot, mock_mouse, mock_action, mock_window, tmp_path):
        """Testet Initialisierung"""
        session_id = "test_session_123"
        prompt_profile = "test_profile"
        
        manager = SessionManager(
            session_id=session_id,
            prompt_profile=prompt_profile,
            output_dir=tmp_path
        )
        
        assert manager.session_id == session_id
        assert manager.prompt_profile == prompt_profile
        assert len(manager.steps) == 0
        assert manager.active is False
    
    @patch('src.monitor.session_manager.WindowMonitor')
    @patch('src.monitor.session_manager.ActionDetector')
    @patch('src.monitor.session_manager.MouseKeyboardMonitor')
    @patch('src.monitor.session_manager.ScreenshotCapture')
    @patch('src.monitor.session_manager.AuditLogger')
    def test_start_stop(self, mock_audit, mock_screenshot, mock_mouse, mock_action, mock_window, tmp_path):
        """Testet Start und Stop einer Session"""
        manager = SessionManager(
            session_id="test_session",
            prompt_profile="test_profile",
            output_dir=tmp_path
        )
        
        # Mock Monitor-Methoden
        manager.window_monitor.start_monitoring = Mock()
        manager.window_monitor.stop_monitoring = Mock()
        manager.mouse_keyboard_monitor.start_monitoring = Mock()
        manager.mouse_keyboard_monitor.stop_monitoring = Mock()
        
        manager.start()
        assert manager.active is True
        
        manager.stop()
        assert manager.active is False
    
    @patch('src.monitor.session_manager.WindowMonitor')
    @patch('src.monitor.session_manager.ActionDetector')
    @patch('src.monitor.session_manager.MouseKeyboardMonitor')
    @patch('src.monitor.session_manager.ScreenshotCapture')
    @patch('src.monitor.session_manager.AuditLogger')
    def test_pause_resume(self, mock_audit, mock_screenshot, mock_mouse, mock_action, mock_window, tmp_path):
        """Testet Pause und Resume"""
        manager = SessionManager(
            session_id="test_session",
            prompt_profile="test_profile",
            output_dir=tmp_path
        )
        
        manager.window_monitor.start_monitoring = Mock()
        manager.window_monitor.stop_monitoring = Mock()
        manager.mouse_keyboard_monitor.start_monitoring = Mock()
        manager.mouse_keyboard_monitor.stop_monitoring = Mock()
        
        manager.start()
        manager.pause()
        assert manager.paused is True
        
        manager.resume()
        assert manager.paused is False
    
    @patch('src.monitor.session_manager.WindowMonitor')
    @patch('src.monitor.session_manager.ActionDetector')
    @patch('src.monitor.session_manager.MouseKeyboardMonitor')
    @patch('src.monitor.session_manager.ScreenshotCapture')
    @patch('src.monitor.session_manager.AuditLogger')
    def test_get_steps(self, mock_audit, mock_screenshot, mock_mouse, mock_action, mock_window, tmp_path):
        """Testet Abrufen von Schritten"""
        manager = SessionManager(
            session_id="test_session",
            prompt_profile="test_profile",
            output_dir=tmp_path
        )
        
        # Füge Test-Schritt hinzu
        test_step = {
            'step_number': 1,
            'timestamp': '2024-01-01T00:00:00',
            'window_title': 'Test Window'
        }
        manager.steps.append(test_step)
        
        steps = manager.get_steps()
        assert len(steps) == 1
        assert steps[0]['step_number'] == 1
    
    @patch('src.monitor.session_manager.WindowMonitor')
    @patch('src.monitor.session_manager.ActionDetector')
    @patch('src.monitor.session_manager.MouseKeyboardMonitor')
    @patch('src.monitor.session_manager.ScreenshotCapture')
    @patch('src.monitor.session_manager.AuditLogger')
    def test_undo_redo(self, mock_audit, mock_screenshot, mock_mouse, mock_action, mock_window, tmp_path):
        """Testet Undo/Redo-Funktionalität"""
        manager = SessionManager(
            session_id="test_session",
            prompt_profile="test_profile",
            output_dir=tmp_path
        )
        
        # Füge ersten Schritt hinzu
        step1 = {'step_number': 1, 'window_title': 'Window 1'}
        manager.steps.append(step1)
        manager._save_history_state()
        
        # Füge zweiten Schritt hinzu
        step2 = {'step_number': 2, 'window_title': 'Window 2'}
        manager.steps.append(step2)
        manager._save_history_state()
        
        # Teste Undo
        assert len(manager.steps) == 2
        assert manager.can_undo() is True
        
        manager.undo()
        assert len(manager.steps) == 1
        assert manager.can_redo() is True
        
        # Teste Redo
        manager.redo()
        assert len(manager.steps) == 2
    
    @patch('src.monitor.session_manager.WindowMonitor')
    @patch('src.monitor.session_manager.ActionDetector')
    @patch('src.monitor.session_manager.MouseKeyboardMonitor')
    @patch('src.monitor.session_manager.ScreenshotCapture')
    @patch('src.monitor.session_manager.AuditLogger')
    def test_get_session_statistics(self, mock_audit, mock_screenshot, mock_mouse, mock_action, mock_window, tmp_path):
        """Testet Session-Statistiken"""
        manager = SessionManager(
            session_id="test_session",
            prompt_profile="test_profile",
            output_dir=tmp_path
        )
        
        manager.session_start_time = time.time() - 120  # 2 Minuten vorher
        
        # Füge Test-Schritte hinzu
        manager.steps = [
            {'step_number': 1, 'window_title': 'Window 1', 'process_name': 'Process1', 'screenshot_path': 'test1.png'},
            {'step_number': 2, 'window_title': 'Window 1', 'process_name': 'Process1', 'screenshot_path': 'test2.png'},
            {'step_number': 3, 'window_title': 'Window 2', 'process_name': 'Process2', 'screenshot_path': 'test3.png'},
        ]
        
        stats = manager.get_session_statistics()
        
        assert stats['step_count'] == 3
        assert stats['screenshot_count'] == 3
        assert stats['windows_used'] == 2
        assert stats['processes_used'] == 2
        assert stats['duration_seconds'] is not None
        assert stats['duration_formatted'] is not None

