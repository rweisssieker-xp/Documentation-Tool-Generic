"""
Translation Hub - Main orchestration for translation features.
Part of Feature: Intelligent Translation Hub (v2.0)
"""

from typing import Dict, Any, Optional, List
from pathlib import Path

from src.translation.glossary_manager import GlossaryManager
from src.translation.translation_memory import TranslationMemory
from src.translation.context_translator import ContextTranslator
from src.translation.review_workflow import ReviewWorkflow
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TranslationHub:
    """
    Main hub for translation features.
    Orchestrates glossary, memory, translator, and review workflow.
    """
    
    def __init__(self, project_name: str = "default"):
        """
        Initialize translation hub.
        
        Args:
            project_name: Project name
        """
        self.project_name = project_name
        self.glossary_manager = GlossaryManager()
        self.translation_memory = TranslationMemory()
        self.translator = ContextTranslator(
            glossary_manager=self.glossary_manager,
            translation_memory=self.translation_memory,
            project_name=project_name
        )
        self.review_workflow = ReviewWorkflow()
    
    def translate_document(
        self,
        content: str,
        source_language: str,
        target_language: str,
        context: Optional[str] = None
    ) -> str:
        """
        Translate entire document.
        
        Args:
            content: Document content
            source_language: Source language
            target_language: Target language
            context: Optional context
            
        Returns:
            Translated content
        """
        return self.translator.translate(content, source_language, target_language, context)
    
    def add_glossary_term(
        self,
        source_term: str,
        target_language: str,
        target_term: str,
        context: Optional[str] = None
    ):
        """Add term to glossary."""
        self.glossary_manager.add_term(
            self.project_name,
            source_term,
            target_language,
            target_term,
            context
        )
    
    def get_translation_statistics(self) -> Dict[str, Any]:
        """Get translation statistics."""
        tm_stats = self.translation_memory.get_statistics()
        glossary_terms = len(self.glossary_manager.get_all_terms(self.project_name))
        
        return {
            'translation_memory': tm_stats,
            'glossary_terms': glossary_terms,
            'project': self.project_name
        }

