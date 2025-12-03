"""
Performance tests for critical workflows
Validates performance requirements from stories
"""

import sys
import pytest
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.capture.screenshot import ScreenshotCapture
from src.capture.ocr_engine import OCREngine
from src.ai.text_generator import TextGenerator


class TestScreenshotPerformance:
    """Performance tests for Story 1-1: Screenshot capture must complete within 100ms"""
    
    @pytest.mark.performance
    def test_screenshot_capture_performance(self, tmp_path):
        """Test that screenshot capture completes within 100ms target"""
        screenshot_dir = tmp_path / "screenshots"
        capture = ScreenshotCapture(screenshot_dir)
        
        # Mock Windows-specific calls
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
                mock_dc.CreateCompatibleBitmap = MagicMock(return_value=mock_bitmap)
                mock_dc.SelectObject = MagicMock(return_value=None)
                mock_dc.BitBlt = MagicMock(return_value=None)
        
        start_time = time.perf_counter()
        result = capture.capture_window(step_number=1, session_id="test-session")
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        # Performance requirement: must complete within 100ms
        assert duration_ms <= 100, f"Screenshot capture took {duration_ms:.2f}ms, exceeds 100ms target"
        assert result is not None, "Screenshot capture should return result"
        
        if result:
            screenshot_path, metadata = result
            assert 'performance' in metadata, "Metadata should include performance metrics"
            assert metadata['performance']['target_ms'] == 100, "Target should be 100ms"
            assert metadata['performance']['within_target'] == (duration_ms <= 100), "Within target flag should match actual performance"
    
    @pytest.mark.performance
    def test_screenshot_capture_performance_multiple(self, tmp_path):
        """Test performance with multiple rapid captures (Story 1-1 requirement)"""
        screenshot_dir = tmp_path / "screenshots"
        capture = ScreenshotCapture(screenshot_dir)
        
        # Mock Windows-specific calls
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
                mock_dc.CreateCompatibleBitmap = MagicMock(return_value=mock_bitmap)
                mock_dc.SelectObject = MagicMock(return_value=None)
                mock_dc.BitBlt = MagicMock(return_value=None)
        
        durations = []
        for i in range(5):
            start_time = time.perf_counter()
            result = capture.capture_window(step_number=i, session_id="test-session")
            duration_ms = (time.perf_counter() - start_time) * 1000
            durations.append(duration_ms)
            assert result is not None, f"Capture {i} should succeed"
        
        # All captures should meet 100ms target
        max_duration = max(durations)
        avg_duration = sum(durations) / len(durations)
        
        assert max_duration <= 100, f"Maximum capture time {max_duration:.2f}ms exceeds 100ms target"
        assert avg_duration <= 100, f"Average capture time {avg_duration:.2f}ms exceeds 100ms target"


class TestOCRPerformance:
    """Performance tests for Story 1-2: OCR processing must complete within 2 seconds"""
    
    @pytest.mark.performance
    @pytest.mark.skipif(not OCREngine().is_available(), reason="Tesseract OCR not available")
    def test_ocr_processing_performance(self, tmp_path):
        """Test that OCR processing completes within 2 seconds target"""
        from PIL import Image
        
        # Create a test image
        test_image = Image.new('RGB', (800, 600), color='white')
        test_image_path = tmp_path / "test_image.png"
        test_image.save(test_image_path)
        
        ocr_engine = OCREngine()
        
        start_time = time.perf_counter()
        result = ocr_engine.extract_text(test_image_path, timeout=2.0)
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        # Performance requirement: must complete within 2 seconds (2000ms)
        assert duration_ms <= 2000, f"OCR processing took {duration_ms:.2f}ms, exceeds 2000ms target"
        assert result is not None, "OCR processing should return result"
    
    @pytest.mark.performance
    def test_ocr_timeout_handling(self, tmp_path):
        """Test that OCR respects timeout (Story 1-2 requirement)"""
        from PIL import Image
        
        # Create a test image
        test_image = Image.new('RGB', (800, 600), color='white')
        test_image_path = tmp_path / "test_image.png"
        test_image.save(test_image_path)
        
        ocr_engine = OCREngine()
        
        # Test with very short timeout
        start_time = time.perf_counter()
        result = ocr_engine.extract_text(test_image_path, timeout=0.1)
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        # Should respect timeout
        assert duration_ms <= 200, f"OCR with timeout should complete quickly, took {duration_ms:.2f}ms"


class TestAIPerformance:
    """Performance tests for Story 1-3: AI text generation must complete within 5 seconds"""
    
    @pytest.mark.performance
    @patch('src.ai.openai_client.OpenAI')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key_12345'})
    def test_ai_generation_performance(self, mock_openai_class):
        """Test that AI text generation completes within 5 seconds target"""
        # Mock OpenAI Client
        mock_client_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated text description"
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client_instance
        
        text_generator = TextGenerator(prompt_profile="technical")
        
        step = {
            'step_number': 1,
            'window_title': 'Test Window',
            'ocr_text': 'Sample OCR text',
            'metadata': {}
        }
        
        start_time = time.perf_counter()
        result = text_generator.generate_step_description(step)
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        # Performance requirement: must complete within 5 seconds (5000ms)
        # Note: Actual API calls may take longer, but mocked calls should be fast
        assert duration_ms <= 5000, f"AI generation took {duration_ms:.2f}ms, exceeds 5000ms target"
        assert result is not None, "AI generation should return result"
        assert len(result) > 0, "Generated text should not be empty"
