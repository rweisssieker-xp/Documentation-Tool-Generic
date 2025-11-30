"""
Auto Completer - Auto-completes documentation text.
Part of Feature 3: Predictive Documentation Assistant
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AutoCompletion:
    """An auto-completion suggestion."""
    text: str
    confidence: float
    completion_type: str  # "sentence", "paragraph", "step"


class AutoCompleter:
    """
    Auto-completes documentation text using AI.
    Provides context-aware suggestions.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        language: str = "de"
    ):
        """
        Initialize auto-completer.
        
        Args:
            api_key: OpenAI API key
            model: Model to use for completions
            language: Output language
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai is required")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.language = language
        
        logger.info(f"AutoCompleter initialized: {model}")
    
    def complete_sentence(
        self,
        partial_text: str,
        context: Optional[str] = None,
        max_length: int = 100
    ) -> List[AutoCompletion]:
        """
        Complete a partial sentence.
        
        Args:
            partial_text: Text to complete
            context: Additional context
            max_length: Maximum completion length
            
        Returns:
            List of completion suggestions
        """
        if len(partial_text) < 3:
            return []
        
        prompt = self._build_completion_prompt(
            partial_text,
            context,
            "sentence"
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_length,
                n=3,
                temperature=0.7
            )
            
            completions = []
            for i, choice in enumerate(response.choices):
                text = choice.message.content.strip()
                if text and not text.startswith(partial_text):
                    text = partial_text + text
                
                completions.append(AutoCompletion(
                    text=text,
                    confidence=1.0 - (i * 0.1),
                    completion_type="sentence"
                ))
            
            return completions
        
        except Exception as e:
            logger.error(f"Sentence completion failed: {e}")
            return []
    
    def complete_step_description(
        self,
        screenshot_text: Optional[str],
        window_title: Optional[str],
        previous_steps: Optional[List[str]] = None
    ) -> List[AutoCompletion]:
        """
        Generate step description suggestions.
        
        Args:
            screenshot_text: OCR text from screenshot
            window_title: Current window title
            previous_steps: Previous step descriptions
            
        Returns:
            List of description suggestions
        """
        context_parts = []
        
        if window_title:
            context_parts.append(f"Fenster: {window_title}")
        
        if screenshot_text:
            context_parts.append(f"Screenshot-Text: {screenshot_text[:500]}")
        
        if previous_steps:
            context_parts.append(f"Vorherige Schritte:\n" + "\n".join(previous_steps[-3:]))
        
        context = "\n".join(context_parts)
        
        prompt = f"""Basierend auf dem folgenden Kontext, generiere eine präzise Schritt-Beschreibung für technische Dokumentation.

{context}

Generiere 3 verschiedene Beschreibungen, eine pro Zeile:
1. Kurz und prägnant (eine Aktion)
2. Detailliert (mit UI-Elementen)
3. Benutzerfreundlich (für Anfänger)

Verwende Aktionsverben am Anfang (Klicken, Eingeben, Auswählen, etc.)."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.5
            )
            
            text = response.choices[0].message.content.strip()
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            
            completions = []
            for i, line in enumerate(lines[:3]):
                # Remove numbering if present
                if line[0].isdigit() and line[1] in [".", ")", ":"]:
                    line = line[2:].strip()
                
                completions.append(AutoCompletion(
                    text=line,
                    confidence=0.9 - (i * 0.1),
                    completion_type="step"
                ))
            
            return completions
        
        except Exception as e:
            logger.error(f"Step description generation failed: {e}")
            return []
    
    def enhance_description(
        self,
        description: str,
        style: str = "professional"
    ) -> str:
        """
        Enhance an existing description.
        
        Args:
            description: Original description
            style: Target style (professional, simple, detailed)
            
        Returns:
            Enhanced description
        """
        style_prompts = {
            "professional": "formell und technisch präzise",
            "simple": "einfach und leicht verständlich",
            "detailed": "sehr detailliert mit allen Zwischenschritten"
        }
        
        prompt = f"""Verbessere die folgende Dokumentations-Beschreibung.
Stil: {style_prompts.get(style, style_prompts['professional'])}

Original: {description}

Verbesserte Version:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Description enhancement failed: {e}")
            return description
    
    def suggest_title(
        self,
        steps: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Suggest titles for a documentation session.
        
        Args:
            steps: Session steps
            
        Returns:
            List of title suggestions
        """
        # Extract key information from steps
        descriptions = [s.get("description", "") for s in steps if s.get("description")]
        windows = list(set(s.get("window_title", "") for s in steps if s.get("window_title")))
        
        context = f"""Schritte: {', '.join(descriptions[:5])}
Anwendungen: {', '.join(windows[:3])}"""
        
        prompt = f"""Basierend auf den folgenden Schritten, schlage 3 prägnante Titel für die Dokumentation vor.

{context}

Titel (einer pro Zeile, ohne Nummerierung):"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )
            
            titles = response.choices[0].message.content.strip().split("\n")
            return [t.strip() for t in titles if t.strip()][:3]
        
        except Exception as e:
            logger.error(f"Title suggestion failed: {e}")
            return []
    
    def _build_completion_prompt(
        self,
        partial_text: str,
        context: Optional[str],
        completion_type: str
    ) -> str:
        """Build prompt for completion."""
        if self.language == "de":
            base = f"Vervollständige den folgenden Text für technische Dokumentation:\n\n\"{partial_text}\""
            if context:
                base += f"\n\nKontext: {context}"
            base += "\n\nVervollständigung (nur der fehlende Teil):"
        else:
            base = f"Complete the following text for technical documentation:\n\n\"{partial_text}\""
            if context:
                base += f"\n\nContext: {context}"
            base += "\n\nCompletion (only the missing part):"
        
        return base

