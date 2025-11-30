"""
Tests for Voice-First Documentation Module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


class TestVoiceCapture:
    """Tests for VoiceCapture class."""
    
    @patch('src.voice.voice_capture.SOUNDDEVICE_AVAILABLE', True)
    @patch('src.voice.voice_capture.sd')
    def test_voice_capture_initialization(self, mock_sd):
        """Test VoiceCapture initialization."""
        from src.voice.voice_capture import VoiceCapture
        
        capture = VoiceCapture(sample_rate=16000, channels=1)
        
        assert capture.sample_rate == 16000
        assert capture.channels == 1
        assert capture.is_recording() == False
    
    @patch('src.voice.voice_capture.SOUNDDEVICE_AVAILABLE', True)
    @patch('src.voice.voice_capture.sd')
    def test_start_stop_recording(self, mock_sd):
        """Test start and stop recording."""
        from src.voice.voice_capture import VoiceCapture
        
        capture = VoiceCapture()
        
        # Start recording
        result = capture.start_recording("test_session")
        assert result == True
        assert capture._is_recording == True
        
        # Stop recording
        capture._is_recording = False  # Simulate stop
    
    @patch('src.voice.voice_capture.SOUNDDEVICE_AVAILABLE', True)
    @patch('src.voice.voice_capture.sd')
    def test_pause_resume(self, mock_sd):
        """Test pause and resume recording."""
        from src.voice.voice_capture import VoiceCapture
        
        capture = VoiceCapture()
        capture._is_recording = True
        
        capture.pause_recording()
        assert capture._is_paused == True
        
        capture.resume_recording()
        assert capture._is_paused == False
    
    @patch('src.voice.voice_capture.SOUNDDEVICE_AVAILABLE', False)
    def test_raises_without_sounddevice(self):
        """Test that VoiceCapture raises without sounddevice."""
        with pytest.raises(ImportError):
            from src.voice.voice_capture import VoiceCapture
            VoiceCapture()


class TestWhisperClient:
    """Tests for WhisperClient class."""
    
    @patch('src.voice.whisper_client.OPENAI_AVAILABLE', True)
    @patch('src.voice.whisper_client.OpenAI')
    def test_whisper_client_initialization(self, mock_openai):
        """Test WhisperClient initialization."""
        from src.voice.whisper_client import WhisperClient
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
            client = WhisperClient()
            assert client.model == "whisper-1"
    
    @patch('src.voice.whisper_client.OPENAI_AVAILABLE', True)
    @patch('src.voice.whisper_client.OpenAI')
    def test_transcribe_file_not_found(self, mock_openai):
        """Test transcription with non-existent file."""
        from src.voice.whisper_client import WhisperClient
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
            client = WhisperClient()
            
            with pytest.raises(FileNotFoundError):
                client.transcribe_file("nonexistent.wav")


class TestVoiceCommands:
    """Tests for VoiceCommandProcessor class."""
    
    def test_command_processor_initialization(self):
        """Test VoiceCommandProcessor initialization."""
        from src.voice.voice_commands import VoiceCommandProcessor
        
        processor = VoiceCommandProcessor(primary_language='de')
        assert processor.primary_language == 'de'
    
    def test_parse_german_commands(self):
        """Test parsing German voice commands."""
        from src.voice.voice_commands import VoiceCommandProcessor, CommandType
        
        processor = VoiceCommandProcessor(primary_language='de')
        
        # Test start command
        cmd = processor.parse_command("starte die aufnahme")
        assert cmd is not None
        assert cmd.type == CommandType.SESSION_CONTROL
        assert cmd.action == "start"
        
        # Test stop command
        cmd = processor.parse_command("stoppe die session")
        assert cmd is not None
        assert cmd.action == "stop"
    
    def test_parse_english_commands(self):
        """Test parsing English voice commands."""
        from src.voice.voice_commands import VoiceCommandProcessor, CommandType
        
        processor = VoiceCommandProcessor(primary_language='en')
        
        # Test start command
        cmd = processor.parse_command("start recording")
        assert cmd is not None
        assert cmd.type == CommandType.SESSION_CONTROL
        assert cmd.action == "start"
    
    def test_parse_annotation_command(self):
        """Test parsing annotation commands."""
        from src.voice.voice_commands import VoiceCommandProcessor, CommandType
        
        processor = VoiceCommandProcessor(primary_language='de')
        
        cmd = processor.parse_command("notiz: Das ist wichtig")
        assert cmd is not None
        assert cmd.type == CommandType.ANNOTATION
        assert cmd.parameters.get('content') == "Das ist wichtig"
    
    def test_no_command_found(self):
        """Test when no command is found."""
        from src.voice.voice_commands import VoiceCommandProcessor
        
        processor = VoiceCommandProcessor()
        cmd = processor.parse_command("Das ist ein normaler Satz")
        assert cmd is None
    
    def test_get_help_text(self):
        """Test help text generation."""
        from src.voice.voice_commands import VoiceCommandProcessor
        
        processor = VoiceCommandProcessor()
        
        help_de = processor.get_help_text('de')
        assert "SESSION-STEUERUNG" in help_de
        
        help_en = processor.get_help_text('en')
        assert "SESSION CONTROL" in help_en


class TestVoiceAnnotator:
    """Tests for VoiceAnnotator class."""
    
    def test_annotator_initialization(self, tmp_path):
        """Test VoiceAnnotator initialization."""
        from src.voice.voice_annotator import VoiceAnnotator
        
        annotator = VoiceAnnotator(
            session_id="test_session",
            storage_dir=str(tmp_path)
        )
        
        assert annotator.session_id == "test_session"
    
    def test_add_annotation(self, tmp_path):
        """Test adding annotation."""
        from src.voice.voice_annotator import VoiceAnnotator
        
        annotator = VoiceAnnotator(
            session_id="test_session",
            storage_dir=str(tmp_path)
        )
        
        annotator.set_current_step("step_1")
        
        annotation = annotator.add_annotation(
            text="Test annotation",
            duration=5.0,
            language="de"
        )
        
        assert annotation.text == "Test annotation"
        assert annotation.step_id == "step_1"
    
    def test_get_annotations_for_step(self, tmp_path):
        """Test retrieving annotations for a step."""
        from src.voice.voice_annotator import VoiceAnnotator
        
        annotator = VoiceAnnotator(
            session_id="test_session",
            storage_dir=str(tmp_path)
        )
        
        annotator.set_current_step("step_1")
        annotator.add_annotation(text="Annotation 1")
        annotator.add_annotation(text="Annotation 2")
        
        annotations = annotator.get_annotations_for_step("step_1")
        assert len(annotations) == 2
    
    def test_export_annotations(self, tmp_path):
        """Test exporting annotations."""
        from src.voice.voice_annotator import VoiceAnnotator
        
        annotator = VoiceAnnotator(
            session_id="test_session",
            storage_dir=str(tmp_path)
        )
        
        annotator.set_current_step("step_1")
        annotator.add_annotation(text="Test")
        
        # Export as JSON
        json_export = annotator.export_annotations(format="json")
        assert "test_session" in json_export
        
        # Export as Markdown
        md_export = annotator.export_annotations(format="markdown")
        assert "# Voice Annotations" in md_export

