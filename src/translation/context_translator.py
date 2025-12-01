"""
Context Translator - Context-aware translation using AI.
Part of Feature: Intelligent Translation Hub (v2.0)
"""

import os
from typing import Optional, Dict, Any, List

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from src.translation.glossary_manager import GlossaryManager
from src.translation.translation_memory import TranslationMemory
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ContextTranslator:
    """
    Performs context-aware translation using AI.
    Integrates with glossary and translation memory for consistency.
    """
    
    def __init__(
        self,
        glossary_manager: Optional[GlossaryManager] = None,
        translation_memory: Optional[TranslationMemory] = None,
        model: str = "gpt-4o",
        project_name: str = "default"
    ):
        """
        Initialize context translator.
        
        Args:
            glossary_manager: Optional GlossaryManager instance
            translation_memory: Optional TranslationMemory instance
            model: OpenAI model to use
            project_name: Project name for glossary lookup
        """
        self.glossary_manager = glossary_manager or GlossaryManager()
        self.translation_memory = translation_memory or TranslationMemory()
        self.model = model
        self.project_name = project_name
        
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
            else:
                self.client = None
                logger.warning("OPENAI_API_KEY not set, translation will use memory only")
        else:
            self.client = None
    
    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        context: Optional[str] = None,
        use_glossary: bool = True,
        use_memory: bool = True
    ) -> str:
        """
        Translate text with context awareness.
        
        Args:
            text: Text to translate
            source_language: Source language code
            target_language: Target language code
            context: Optional context
            use_glossary: Whether to use glossary
            use_memory: Whether to use translation memory
            
        Returns:
            Translated text
        """
        # Check translation memory first
        if use_memory:
            tm_match = self.translation_memory.find_translation(text, source_language, target_language)
            if tm_match:
                logger.debug(f"Translation found in memory: {tm_match.target_text[:50]}...")
                return tm_match.target_text
        
        # Check glossary for terms
        glossary_terms = {}
        if use_glossary:
            # Extract potential terms (simplified - would use NLP in production)
            words = text.split()
            for word in words:
                clean_word = word.strip('.,!?;:()[]{}"\'')
                term = self.glossary_manager.get_translation(
                    self.project_name,
                    clean_word,
                    target_language
                )
                if term:
                    glossary_terms[clean_word] = term
        
        # Translate with AI
        if self.client:
            translated = self._ai_translate(text, source_language, target_language, context, glossary_terms)
        else:
            # Fallback: return original or basic translation
            translated = text
        
        # Store in translation memory
        if use_memory and translated != text:
            self.translation_memory.add_translation(
                text,
                translated,
                source_language,
                target_language,
                context
            )
        
        return translated
    
    def _ai_translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        context: Optional[str],
        glossary_terms: Dict[str, str]
    ) -> str:
        """Translate using AI with glossary."""
        try:
            # Build prompt
            prompt = f"Translate the following text from {source_language} to {target_language}."
            
            if context:
                prompt += f"\n\nContext: {context}"
            
            if glossary_terms:
                prompt += "\n\nUse these specific translations for technical terms:"
                for source, target in glossary_terms.items():
                    prompt += f"\n- {source} -> {target}"
            
            prompt += f"\n\nText to translate:\n{text}"
            prompt += "\n\nReturn only the translation, no explanations."
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional translator specializing in technical documentation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            translated = response.choices[0].message.content.strip()
            logger.debug(f"Translated: {text[:50]}... -> {translated[:50]}...")
            return translated
        except Exception as e:
            logger.error(f"Error in AI translation: {e}")
            return text
    
    def translate_batch(
        self,
        texts: List[str],
        source_language: str,
        target_language: str,
        context: Optional[str] = None
    ) -> List[str]:
        """
        Translate multiple texts.
        
        Args:
            texts: List of texts to translate
            source_language: Source language
            target_language: Target language
            context: Optional context
            
        Returns:
            List of translations
        """
        return [self.translate(text, source_language, target_language, context) for text in texts]

