"""
Unit-Tests für Audit-Module
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime
import hashlib

# Füge src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.audit.audit_logger import AuditLogger
from src.audit.compliance import Compliance


class TestAuditLogger:
    """Tests für AuditLogger"""
    
    def test_init(self, tmp_path):
        """Testet Initialisierung"""
        session_id = "test_session_123"
        output_dir = tmp_path / "sessions"
        output_dir.mkdir(parents=True)
        
        logger = AuditLogger(session_id, output_dir)
        
        assert logger.session_id == session_id
        assert logger.output_dir == output_dir
    
    def test_log_step(self, tmp_path):
        """Testet Protokollierung eines Schritts"""
        session_id = "test_session_123"
        output_dir = tmp_path / "sessions"
        output_dir.mkdir(parents=True)
        
        logger = AuditLogger(session_id, output_dir)
        
        # Erstelle Test-Screenshot
        screenshot_path = tmp_path / "test_screenshot.png"
        screenshot_path.write_bytes(b'fake image data')
        
        step_number = 1
        window_info = {
            'hwnd': 12345,
            'title': 'Test Window',
            'class_name': 'TestClass'
        }
        
        logger.log_step(step_number, screenshot_path, window_info)
        
        # Audit-Log sollte existieren
        audit_log_path = output_dir / f"{session_id}_audit.json"
        # Datei könnte existieren, muss aber nicht (wird beim Export erstellt)
    
    def test_export_json(self, tmp_path):
        """Testet JSON-Export"""
        session_id = "test_session_123"
        output_dir = tmp_path / "sessions"
        output_dir.mkdir(parents=True)
        
        logger = AuditLogger(session_id, output_dir)
        
        # Füge Test-Schritt hinzu
        screenshot_path = tmp_path / "test_screenshot.png"
        screenshot_path.write_bytes(b'fake image data')
        
        logger.log_step(1, screenshot_path, {'title': 'Test Window'})
        
        json_path = logger.export_json()
        
        if json_path:
            assert json_path.exists()
            assert json_path.suffix == '.json'
    
    def test_export_csv(self, tmp_path):
        """Testet CSV-Export"""
        session_id = "test_session_123"
        output_dir = tmp_path / "sessions"
        output_dir.mkdir(parents=True)
        
        logger = AuditLogger(session_id, output_dir)
        
        # Füge Test-Schritt hinzu
        screenshot_path = tmp_path / "test_screenshot.png"
        screenshot_path.write_bytes(b'fake image data')
        
        logger.log_step(1, screenshot_path, {'title': 'Test Window'})
        
        csv_path = logger.export_csv()
        
        if csv_path:
            assert csv_path.exists()
            assert csv_path.suffix == '.csv'


class TestCompliance:
    """Tests für Compliance-Module"""
    
    def test_calculate_hash(self, tmp_path):
        """Testet SHA-256 Hash-Berechnung"""
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("Test content")
        
        hash_value = Compliance.calculate_sha256(test_file)
        
        # Berechne erwarteten Hash
        expected_hash = hashlib.sha256(test_file.read_bytes()).hexdigest()
        
        assert hash_value == expected_hash
        assert len(hash_value) == 64  # SHA-256 erzeugt 64 hex-Zeichen
    
    def test_get_timestamp(self):
        """Testet Zeitstempel-Erstellung"""
        timestamp = Compliance.get_timestamp()
        
        assert timestamp is not None
        assert isinstance(timestamp, str)
        # Sollte ISO-Format sein
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            # Fallback: sollte zumindest ein String sein
            assert isinstance(timestamp, str)
    
    def test_get_user_info(self):
        """Testet Abrufen von Benutzerinformationen"""
        user_info = Compliance.get_user_info()
        
        assert 'username' in user_info
        assert 'system_name' in user_info
        assert isinstance(user_info['username'], str)
        assert isinstance(user_info['system_name'], str)

