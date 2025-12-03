"""
Acceptance Criteria validation tests
Maps tests to specific Acceptance Criteria from stories
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import uuid

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestStory11AcceptanceCriteria:
    """Story 1-1: Automatic Screenshot Capture - AC Validation"""
    
    def test_ac1_automatic_capture_on_window_change(self, tmp_path):
        """AC1: Given a documentation session is active, when the active window changes, then a screenshot is automatically captured"""
        from src.capture.screenshot import ScreenshotCapture
        
        screenshot_dir = tmp_path / "screenshots"
        capture = ScreenshotCapture(screenshot_dir)
        
        # Mock Windows calls
        if capture.platform == "windows" and hasattr(capture, 'win32gui'):
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
                mock_dc.CreateCompatibleBitmap = MagicMock(return_value=mock_bitmap)
                mock_dc.SelectObject = MagicMock(return_value=None)
                mock_dc.BitBlt = MagicMock(return_value=None)
        
        result = capture.capture_window(step_number=1, session_id="test-session")
        
        assert result is not None, "Screenshot should be captured"
        screenshot_path, metadata = result
        assert screenshot_path.exists(), "Screenshot file should exist"
    
    def test_ac2_unique_identifier_uuid_format(self, tmp_path):
        """AC2: Given a screenshot has been captured, then the screenshot is stored with a unique identifier (UUID format)"""
        from src.capture.screenshot import ScreenshotCapture
        
        screenshot_dir = tmp_path / "screenshots"
        capture = ScreenshotCapture(screenshot_dir)
        
        # Mock Windows calls
        if capture.platform == "windows" and hasattr(capture, 'win32gui'):
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
                mock_dc.CreateCompatibleBitmap = MagicMock(return_value=mock_bitmap)
                mock_dc.SelectObject = MagicMock(return_value=None)
                mock_dc.BitBlt = MagicMock(return_value=None)
        
        result = capture.capture_window(step_number=1, session_id="test-session")
        screenshot_path, metadata = result
        
        assert 'screenshot_id' in metadata, "Metadata should contain screenshot_id"
        screenshot_id = metadata['screenshot_id']
        
        # Validate UUID format
        try:
            uuid.UUID(screenshot_id)
        except ValueError:
            pytest.fail(f"screenshot_id '{screenshot_id}' is not a valid UUID")
    
    def test_ac3_session_step_association(self, tmp_path):
        """AC3: Given a screenshot has been captured, then the screenshot is associated with the current session step"""
        from src.capture.screenshot import ScreenshotCapture
        
        screenshot_dir = tmp_path / "screenshots"
        capture = ScreenshotCapture(screenshot_dir)
        
        # Mock Windows calls
        if capture.platform == "windows" and hasattr(capture, 'win32gui'):
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
                mock_dc.CreateCompatibleBitmap = MagicMock(return_value=mock_bitmap)
                mock_dc.SelectObject = MagicMock(return_value=None)
                mock_dc.BitBlt = MagicMock(return_value=None)
        
        step_number = 5
        session_id = "test-session-123"
        
        result = capture.capture_window(step_number=step_number, session_id=session_id)
        screenshot_path, metadata = result
        
        assert metadata['step_number'] == step_number, "Metadata should contain step_number"
        assert metadata['session_id'] == session_id, "Metadata should contain session_id"
        assert step_number in str(screenshot_path), "Screenshot filename should contain step_number"
    
    def test_ac4_metadata_recording(self, tmp_path):
        """AC4: Given a screenshot has been captured, then the screenshot metadata (timestamp, window title) is recorded"""
        from src.capture.screenshot import ScreenshotCapture
        
        screenshot_dir = tmp_path / "screenshots"
        capture = ScreenshotCapture(screenshot_dir)
        
        # Mock Windows calls
        if capture.platform == "windows" and hasattr(capture, 'win32gui'):
            capture.win32gui.GetWindowRect = MagicMock(return_value=(0, 0, 100, 100))
            capture.win32gui.GetWindowDC = MagicMock(return_value=1)
            capture.win32gui.GetWindowText = MagicMock(return_value="Test Window Title")
            capture.win32gui.ReleaseDC = MagicMock(return_value=None)
            
            if hasattr(capture, 'win32ui'):
                mock_dc = MagicMock()
                capture.win32ui.CreateDCFromHandle = MagicMock(return_value=mock_dc)
                mock_dc.CreateCompatibleDC = MagicMock(return_value=MagicMock())
                mock_bitmap = MagicMock()
                mock_bitmap.GetInfo.return_value = {'bmWidth': 100, 'bmHeight': 100}
                mock_bitmap.GetBitmapBits.return_value = b'\x00' * (100 * 100 * 4)
                mock_dc.CreateCompatibleBitmap = MagicMock(return_value=mock_bitmap)
                mock_dc.SelectObject = MagicMock(return_value=None)
                mock_dc.BitBlt = MagicMock(return_value=None)
        
        result = capture.capture_window(step_number=1, session_id="test-session")
        screenshot_path, metadata = result
        
        assert 'timestamp' in metadata, "Metadata should contain timestamp"
        assert 'window_title' in metadata, "Metadata should contain window_title"
        assert metadata['window_title'] is not None, "Window title should not be None"
        assert len(metadata['timestamp']) > 0, "Timestamp should not be empty"
    
    def test_ac5_performance_target(self, tmp_path):
        """AC5: Given a window change is detected, then screenshot capture completes within 100ms of window change detection"""
        from src.capture.screenshot import ScreenshotCapture
        import time
        
        screenshot_dir = tmp_path / "screenshots"
        capture = ScreenshotCapture(screenshot_dir)
        
        # Mock Windows calls
        if capture.platform == "windows" and hasattr(capture, 'win32gui'):
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
                mock_dc.CreateCompatibleBitmap = MagicMock(return_value=mock_bitmap)
                mock_dc.SelectObject = MagicMock(return_value=None)
                mock_dc.BitBlt = MagicMock(return_value=None)
        
        start_time = time.perf_counter()
        result = capture.capture_window(step_number=1, session_id="test-session")
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        assert duration_ms <= 100, f"Screenshot capture took {duration_ms:.2f}ms, exceeds 100ms target"
        assert result is not None, "Screenshot should be captured"
        
        screenshot_path, metadata = result
        assert 'performance' in metadata, "Metadata should include performance metrics"
        assert metadata['performance']['target_ms'] == 100, "Target should be 100ms"


class TestStory12AcceptanceCriteria:
    """Story 1-2: OCR Text Extraction - AC Validation"""
    
    @pytest.mark.skipif(not __import__('src.capture.ocr_engine', fromlist=['OCREngine']).OCREngine().is_available(), reason="Tesseract OCR not available")
    def test_ac1_ocr_extraction(self, tmp_path):
        """AC1: Given a screenshot has been captured, when OCR processing is triggered, then text is extracted using Tesseract OCR"""
        from src.capture.ocr_engine import OCREngine
        from PIL import Image
        
        # Create test image with text
        test_image = Image.new('RGB', (800, 600), color='white')
        test_image_path = tmp_path / "test_image.png"
        test_image.save(test_image_path)
        
        ocr_engine = OCREngine()
        result = ocr_engine.extract_text(test_image_path)
        
        assert result is not None, "OCR should return result"
        assert isinstance(result, str), "OCR result should be string"
    
    def test_ac3_error_handling(self, tmp_path):
        """AC3: Given OCR processing encounters an error, then OCR errors are handled gracefully with user-friendly messages"""
        from src.capture.ocr_engine import OCREngine
        
        ocr_engine = OCREngine()
        
        # Test with non-existent file
        non_existent_path = tmp_path / "non_existent.png"
        result = ocr_engine.extract_text(non_existent_path)
        
        # Should handle error gracefully (return empty string or None, not raise exception)
        assert result is not None or result == "", "OCR should handle errors gracefully"
    
    def test_ac6_async_processing(self):
        """AC6: Given OCR processing is triggered, then OCR processing runs asynchronously to avoid UI blocking"""
        from src.capture.ocr_engine import OCREngine
        
        ocr_engine = OCREngine()
        
        # Verify ThreadPoolExecutor is initialized
        assert hasattr(ocr_engine, 'executor'), "OCREngine should have executor for async processing"
        assert ocr_engine.executor is not None, "Executor should be initialized"
