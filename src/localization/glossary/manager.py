"""Glossary Manager"""

import logging

logger = logging.getLogger(__name__)


class GlossaryManager:
    """Verwaltet Glossare"""
    
    def add_term(self, term: str, translation: str, language: str) -> bool:
        """Fügt Begriff hinzu"""
        return True
