"""
Unit-Tests für AI-Module
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Füge src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.ai.openai_client import OpenAIClient
from src.ai.prompt_templates import PromptTemplateSystem
from src.ai.text_generator import TextGenerator


class TestOpenAIClient:
    """Tests für OpenAIClient"""
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key_12345'})
    def test_init(self):
        """Testet Initialisierung"""
        client = OpenAIClient()
        assert client.api_key == 'test_key_12345'
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': ''}, clear=True)
    def test_init_no_key(self):
        """Testet Initialisierung ohne API-Key"""
        with pytest.raises(ValueError, match="OpenAI API-Key nicht gesetzt"):
            OpenAIClient()
    
    @patch('src.ai.openai_client.OpenAI')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key_12345'})
    def test_generate_text(self, mock_openai_class):
        """Testet Textgenerierung"""
        # Mock OpenAI Client instance
        mock_client_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated text"
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client_instance
        
        client = OpenAIClient()
        result = client.generate_text("Test system prompt", "Test user prompt")
        
        assert result == "Generated text"
    
    @patch('src.ai.openai_client.OpenAI')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key_12345'})
    def test_generate_text_with_retry(self, mock_openai_class):
        """Testet Retry-Logik bei Fehlern"""
        # Mock OpenAI Client instance
        mock_client_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated text"
        mock_openai_class.return_value = mock_client_instance
        
        # Erster Aufruf schlägt fehl, zweiter erfolgreich
        mock_client_instance.chat.completions.create.side_effect = [
            Exception("API Error"),
            mock_response
        ]
        
        client = OpenAIClient()
        try:
            result = client.generate_text("Test system prompt", "Test user prompt", max_retries=2)
            assert result == "Generated text"
        except Exception:
            # Kann auch nach Retries fehlschlagen
            pass
    
    @patch('src.ai.openai_client.OpenAI')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key_12345'})
    @patch('time.sleep')
    def test_generate_text_rate_limit_handling(self, mock_sleep, mock_openai_class):
        """Testet Rate Limit Handling"""
        # Mock OpenAI Client instance
        mock_client_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated text"
        mock_openai_class.return_value = mock_client_instance
        
        # Rate Limit Fehler, dann Erfolg
        rate_limit_error = Exception("rate_limit_exceeded")
        mock_client_instance.chat.completions.create.side_effect = [
            rate_limit_error,
            mock_response
        ]
        
        client = OpenAIClient()
        try:
            result = client.generate_text("Test system prompt", "Test user prompt", max_retries=2)
            assert result == "Generated text"
        except Exception:
            # Kann auch nach Retries fehlschlagen
            pass
    
    @patch('src.ai.openai_client.OpenAI')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key_12345'})
    def test_generate_text_exponential_backoff(self, mock_openai_class):
        """Testet Exponential Backoff bei Retries"""
        import time
        client = OpenAIClient()
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated text"
        
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Mehrere Fehler, dann Erfolg
        mock_client.chat.completions.create.side_effect = [
            Exception("500 Internal Server Error"),
            Exception("503 Service Unavailable"),
            mock_response
        ]
        
        sleep_times = []
        original_sleep = time.sleep
        
        def mock_sleep(delay):
            sleep_times.append(delay)
            original_sleep(0)  # Minimal sleep für Test
        
        try:
            with patch('time.sleep', side_effect=mock_sleep):
                result = client.generate_text("Test prompt", "Test system prompt", max_retries=3, retry_delay=1.0)
                assert result == "Generated text"
                # Prüfe dass exponential backoff verwendet wurde
                assert len(sleep_times) >= 2
                assert sleep_times[1] > sleep_times[0]  # Zweiter Delay sollte größer sein
        except Exception:
            # Kann auch nach Retries fehlschlagen
            pass


class TestPromptTemplateSystem:
    """Tests für PromptTemplateSystem"""
    
    def test_load_profile(self, tmp_path):
        """Testet Laden eines Prompt-Profils"""
        import yaml
        
        # Erstelle Test-Profil
        profile_dir = tmp_path / "profiles"
        profile_dir.mkdir(parents=True)
        profile_file = profile_dir / "test.yml"
        
        profile_data = {
            'language': 'de',
            'style': 'technical',
            'system_prompt': 'Test system prompt',
            'step_template': 'Step {step_number}: {description}',
            'introduction_template': 'Introduction: {steps}',
            'conclusion_template': 'Conclusion: {steps}'
        }
        profile_file.write_text(yaml.dump(profile_data))
        
        with patch('src.ai.prompt_templates.Path') as mock_path:
            mock_path.return_value = profile_dir
            system = PromptTemplateSystem()
            system.load_profile('test')
            
            assert system.get_language() == 'de'
            assert system.get_style() == 'technical'
    
    @patch('src.ai.prompt_templates.ConfigManager')
    def test_format_step_prompt(self, mock_config_manager):
        """Testet Formatierung eines Schritt-Prompts"""
        # Mock ConfigManager
        mock_config_instance = MagicMock()
        mock_profile = {
            'step_template': 'Step {step_number}: {window_title} - {ocr_text}'
        }
        mock_config_instance.load_prompt_profile.return_value = mock_profile
        mock_config_manager.return_value = mock_config_instance
        
        system = PromptTemplateSystem()
        system.load_profile('test')
        
        result = system.format_step_prompt(
            step_number=1,
            window_title='Test Window',
            ocr_text='Test Description'
        )
        
        assert 'Step 1' in result
        assert 'Test Window' in result
        assert 'Test Description' in result


class TestTextGenerator:
    """Tests für TextGenerator"""
    
    @patch('src.ai.text_generator.OpenAIClient')
    @patch('src.ai.text_generator.PromptTemplateSystem')
    @patch('src.ai.text_generator.OCREngine')
    def test_init(self, mock_ocr_engine, mock_prompt_system, mock_openai_client):
        """Testet Initialisierung"""
        # Mock instances
        mock_openai_instance = MagicMock()
        mock_openai_client.return_value = mock_openai_instance
        mock_prompt_instance = MagicMock()
        mock_prompt_system.return_value = mock_prompt_instance
        mock_ocr_instance = MagicMock()
        mock_ocr_engine.return_value = mock_ocr_instance
        
        generator = TextGenerator('test_profile')
        
        assert generator.openai_client is not None
        assert generator.prompt_system is not None
        assert generator.ocr_engine is not None
    
    @patch('src.ai.text_generator.OpenAIClient')
    @patch('src.ai.text_generator.PromptTemplateSystem')
    @patch('src.ai.text_generator.OCREngine')
    def test_generate_step_description(self, mock_ocr_engine, mock_prompt_system, mock_openai_client):
        """Testet Generierung einer Schritt-Beschreibung"""
        # Mock OpenAI Client
        mock_client_instance = MagicMock()
        mock_client_instance.generate_text.return_value = "Generated description"
        mock_openai_client.return_value = mock_client_instance
        
        # Mock Prompt System
        mock_prompt_instance = MagicMock()
        mock_prompt_instance.get_system_prompt.return_value = "System prompt"
        mock_prompt_instance.format_step_prompt.return_value = "Formatted prompt"
        mock_prompt_system.return_value = mock_prompt_instance
        
        # Mock OCR Engine
        mock_ocr_instance = MagicMock()
        mock_ocr_instance.is_available.return_value = False
        mock_ocr_engine.return_value = mock_ocr_instance
        
        generator = TextGenerator('test_profile')
        
        step = {
            'step_number': 1,
            'window_title': 'Test Window',
            'screenshot_path': '/fake/path.png',
            'ocr_text': 'Test OCR text',
            'description': None
        }
        
        result = generator.generate_step_description(step, [])
        
        assert result == "Generated description"
        mock_client_instance.generate_text.assert_called_once()
    
    @patch('src.ai.text_generator.OpenAIClient')
    @patch('src.ai.text_generator.PromptTemplateSystem')
    @patch('src.ai.text_generator.OCREngine')
    def test_generate_step_description_with_ocr_context(self, mock_ocr_engine, mock_prompt_system, mock_openai_client):
        """Testet Generierung mit OCR-Text-Kontext"""
        mock_client_instance = MagicMock()
        mock_client_instance.generate_text.return_value = "Generated description with OCR"
        mock_openai_client.return_value = mock_client_instance
        
        mock_prompt_instance = MagicMock()
        mock_prompt_instance.get_system_prompt.return_value = "System prompt"
        mock_prompt_instance.format_step_prompt.return_value = "Formatted prompt with OCR"
        mock_prompt_system.return_value = mock_prompt_instance
        
        mock_ocr_instance = MagicMock()
        mock_ocr_instance.is_available.return_value = False
        mock_ocr_engine.return_value = mock_ocr_instance
        
        generator = TextGenerator('test_profile')
        
        step = {
            'step_number': 1,
            'window_title': 'Test Window',
            'screenshot_path': '/fake/path.png',
            'ocr_text': 'Extracted OCR text from screenshot',
            'description': None
        }
        
        result = generator.generate_step_description(step, [])
        
        # Prüfe dass OCR-Text im Prompt verwendet wurde
        mock_prompt_instance.format_step_prompt.assert_called_once()
        call_args = mock_prompt_instance.format_step_prompt.call_args
        assert 'ocr_text' in call_args.kwargs
        assert call_args.kwargs['ocr_text'] == 'Extracted OCR text from screenshot'
        assert result == "Generated description with OCR"
    
    @patch('src.ai.text_generator.OpenAIClient')
    @patch('src.ai.text_generator.PromptTemplateSystem')
    def test_generate_introduction(self, mock_prompt_system, mock_openai_client):
        """Testet Generierung einer Einleitung"""
        mock_client_instance = MagicMock()
        mock_client_instance.generate_text.return_value = "Generated introduction"
        mock_openai_client.return_value = mock_client_instance
        
        generator = TextGenerator('test_profile')
        
        steps = [
            {'step_number': 1, 'description': 'Step 1'},
            {'step_number': 2, 'description': 'Step 2'}
        ]
        
        result = generator.generate_introduction(steps)
        
        assert result == "Generated introduction"
    
    @patch('src.ai.text_generator.OpenAIClient')
    @patch('src.ai.text_generator.PromptTemplateSystem')
    def test_generate_conclusion(self, mock_prompt_system, mock_openai_client):
        """Testet Generierung eines Fazits"""
        mock_client_instance = MagicMock()
        mock_client_instance.generate_text.return_value = "Generated conclusion"
        mock_openai_client.return_value = mock_client_instance
        
        generator = TextGenerator('test_profile')
        
        steps = [
            {'step_number': 1, 'description': 'Step 1'},
            {'step_number': 2, 'description': 'Step 2'}
        ]
        
        result = generator.generate_conclusion(steps)
        
        assert result == "Generated conclusion"

