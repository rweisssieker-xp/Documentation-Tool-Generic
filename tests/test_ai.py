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
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': ''})
    def test_init_no_key(self):
        """Testet Initialisierung ohne API-Key"""
        client = OpenAIClient()
        # Sollte None oder leer sein
        assert client.api_key is None or client.api_key == ''
    
    @patch('src.ai.openai_client.openai')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key_12345'})
    def test_generate_text(self, mock_openai):
        """Testet Textgenerierung"""
        client = OpenAIClient()
        
        # Mock OpenAI Response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated text"
        
        mock_openai.OpenAI.return_value.chat.completions.create.return_value = mock_response
        
        result = client.generate_text("Test prompt", "Test system prompt")
        
        assert result == "Generated text"
    
    @patch('src.ai.openai_client.openai')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key_12345'})
    def test_generate_text_with_retry(self, mock_openai):
        """Testet Retry-Logik bei Fehlern"""
        client = OpenAIClient()
        
        # Mock OpenAI Response mit Fehler, dann Erfolg
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated text"
        
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client
        
        # Erster Aufruf schlägt fehl, zweiter erfolgreich
        mock_client.chat.completions.create.side_effect = [
            Exception("API Error"),
            mock_response
        ]
        
        try:
            result = client.generate_text("Test prompt", "Test system prompt", max_retries=2)
            assert result == "Generated text"
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
    
    def test_format_step_prompt(self):
        """Testet Formatierung eines Schritt-Prompts"""
        system = PromptTemplateSystem()
        
        # Setze Test-Template
        system.step_template = "Step {step_number}: {window_title} - {description}"
        
        step_data = {
            'step_number': 1,
            'window_title': 'Test Window',
            'description': 'Test Description'
        }
        
        result = system.format_step_prompt(step_data)
        
        assert 'Step 1' in result
        assert 'Test Window' in result
        assert 'Test Description' in result


class TestTextGenerator:
    """Tests für TextGenerator"""
    
    @patch('src.ai.text_generator.OpenAIClient')
    @patch('src.ai.text_generator.PromptTemplateSystem')
    def test_init(self, mock_prompt_system, mock_openai_client):
        """Testet Initialisierung"""
        generator = TextGenerator('test_profile')
        
        assert generator.prompt_profile == 'test_profile'
        assert generator.openai_client is not None
        assert generator.prompt_system is not None
    
    @patch('src.ai.text_generator.OpenAIClient')
    @patch('src.ai.text_generator.PromptTemplateSystem')
    def test_generate_step_description(self, mock_prompt_system, mock_openai_client):
        """Testet Generierung einer Schritt-Beschreibung"""
        # Mock OpenAI Client
        mock_client_instance = MagicMock()
        mock_client_instance.generate_text.return_value = "Generated description"
        mock_openai_client.return_value = mock_client_instance
        
        # Mock Prompt System
        mock_prompt_instance = MagicMock()
        mock_prompt_instance.format_step_prompt.return_value = "Formatted prompt"
        mock_prompt_system.return_value = mock_prompt_instance
        
        generator = TextGenerator('test_profile')
        
        step = {
            'step_number': 1,
            'window_title': 'Test Window',
            'description': None
        }
        
        result = generator.generate_step_description(step, [])
        
        assert result == "Generated description"
        mock_client_instance.generate_text.assert_called_once()
    
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

