"""
Narration Engine - Generates narration scripts and TTS.
Part of Feature: Video Tutorial Synthesizer (v2.0)
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from src.utils.logger import get_logger

logger = get_logger(__name__)


class NarrationEngine:
    """
    Generates narration scripts for video tutorials.
    Creates natural-sounding descriptions of documentation steps.
    """
    
    def __init__(self, model: str = "gpt-4o"):
        """
        Initialize narration engine.
        
        Args:
            model: OpenAI model to use
        """
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
            else:
                self.client = None
        else:
            self.client = None
        
        self.model = model
    
    def generate_narration_script(
        self,
        steps: List[Dict[str, Any]],
        language: str = "de",
        style: str = "professional"
    ) -> List[str]:
        """
        Generate narration script for steps.
        
        Args:
            steps: List of step dictionaries
            language: Language code
            style: Narration style ("professional", "casual", "tutorial")
            
        Returns:
            List of narration texts
        """
        narrations = []
        
        if self.client:
            for step in steps:
                narration = self._generate_step_narration(step, language, style)
                narrations.append(narration)
        else:
            # Fallback: basic narration
            for i, step in enumerate(steps, 1):
                action = step.get('action', 'Schritt')
                narration = f"Schritt {i}: {action}"
                narrations.append(narration)
        
        return narrations
    
    def _generate_step_narration(
        self,
        step: Dict[str, Any],
        language: str,
        style: str
    ) -> str:
        """Generate narration for a single step."""
        try:
            action = step.get('action', '')
            description = step.get('description', '')
            element = step.get('element', '')
            
            prompt = f"""Create a natural, {style} narration for this documentation step.

Action: {action}
Description: {description}
Element: {element}

Write a short, clear narration in {language} (2-3 sentences max).
Speak directly to the viewer, as if explaining the step.
Be concise and friendly."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional voice-over narrator for tutorial videos."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating narration: {e}")
            return f"{action}: {description}"


class TTSClient:
    """
    Text-to-Speech client for generating voice-over.
    Supports multiple TTS providers.
    """
    
    def __init__(self, provider: str = "openai"):
        """
        Initialize TTS client.
        
        Args:
            provider: TTS provider ("openai", "elevenlabs")
        """
        self.provider = provider
        
        if provider == "openai" and OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
            else:
                self.client = None
        else:
            self.client = None
    
    def synthesize_speech(
        self,
        text: str,
        voice: str = "alloy",
        language: str = "de",
        output_path: Optional[Path] = None
    ) -> Optional[bytes]:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            voice: Voice name
            language: Language code
            output_path: Optional output path
            
        Returns:
            Audio bytes or None
        """
        if not self.client:
            logger.warning("TTS client not available")
            return None
        
        try:
            if self.provider == "openai":
                response = self.client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=text,
                    language=language if language != "de" else None  # OpenAI TTS doesn't support DE directly
                )
                
                audio_data = response.content
                
                if output_path:
                    output_path.write_bytes(audio_data)
                
                return audio_data
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            return None

