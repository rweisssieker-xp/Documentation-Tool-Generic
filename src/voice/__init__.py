# Voice-First Documentation Module
# Feature 7: Voice-First Documentation

from .voice_capture import VoiceCapture
from .whisper_client import WhisperClient
from .voice_commands import VoiceCommandProcessor
from .voice_annotator import VoiceAnnotator

__all__ = [
    'VoiceCapture',
    'WhisperClient',
    'VoiceCommandProcessor',
    'VoiceAnnotator'
]

