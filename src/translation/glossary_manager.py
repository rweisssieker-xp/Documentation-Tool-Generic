"""
Glossary Manager - Manages project-specific terminology.
Part of Feature: Intelligent Translation Hub (v2.0)
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class GlossaryTerm:
    """A glossary term."""
    source_term: str
    target_terms: Dict[str, str]  # language -> translation
    context: Optional[str] = None
    category: Optional[str] = None  # "technical", "ui", "domain"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class GlossaryManager:
    """
    Manages project-specific terminology glossaries.
    Ensures consistent translation of domain-specific terms.
    """
    
    def __init__(self, storage_dir: Path = Path("data/translation/glossaries")):
        """
        Initialize glossary manager.
        
        Args:
            storage_dir: Directory for storing glossaries
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.glossaries: Dict[str, Dict[str, GlossaryTerm]] = {}  # project -> {term -> GlossaryTerm}
        self._load_glossaries()
    
    def _load_glossaries(self):
        """Load glossaries from storage."""
        for glossary_file in self.storage_dir.glob("*.json"):
            try:
                project_name = glossary_file.stem
                data = json.loads(glossary_file.read_text(encoding='utf-8'))
                
                terms = {}
                for term_data in data.get('terms', []):
                    term = GlossaryTerm(**term_data)
                    terms[term.source_term] = term
                
                self.glossaries[project_name] = terms
                logger.debug(f"Loaded glossary: {project_name} ({len(terms)} terms)")
            except Exception as e:
                logger.warning(f"Could not load glossary {glossary_file}: {e}")
    
    def _save_glossary(self, project_name: str):
        """Save glossary to storage."""
        if project_name not in self.glossaries:
            return
        
        glossary_file = self.storage_dir / f"{project_name}.json"
        
        try:
            terms_data = [asdict(term) for term in self.glossaries[project_name].values()]
            for term_data in terms_data:
                # Convert datetime to ISO string
                if term_data.get('created_at'):
                    term_data['created_at'] = term_data['created_at'].isoformat() if isinstance(term_data['created_at'], datetime) else term_data['created_at']
                if term_data.get('updated_at'):
                    term_data['updated_at'] = term_data['updated_at'].isoformat() if isinstance(term_data['updated_at'], datetime) else term_data['updated_at']
            
            glossary_file.write_text(
                json.dumps({'terms': terms_data}, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
        except Exception as e:
            logger.error(f"Error saving glossary: {e}")
    
    def add_term(
        self,
        project_name: str,
        source_term: str,
        target_language: str,
        target_term: str,
        context: Optional[str] = None,
        category: Optional[str] = None
    ):
        """
        Add or update a glossary term.
        
        Args:
            project_name: Project name
            source_term: Source language term
            target_language: Target language code
            target_term: Translation
            context: Optional context
            category: Optional category
        """
        if project_name not in self.glossaries:
            self.glossaries[project_name] = {}
        
        if source_term in self.glossaries[project_name]:
            # Update existing term
            term = self.glossaries[project_name][source_term]
            term.target_terms[target_language] = target_term
            term.updated_at = datetime.now()
            if context:
                term.context = context
            if category:
                term.category = category
        else:
            # Create new term
            term = GlossaryTerm(
                source_term=source_term,
                target_terms={target_language: target_term},
                context=context,
                category=category,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.glossaries[project_name][source_term] = term
        
        self._save_glossary(project_name)
        logger.debug(f"Added term to {project_name}: {source_term} -> {target_term}")
    
    def get_translation(
        self,
        project_name: str,
        source_term: str,
        target_language: str
    ) -> Optional[str]:
        """
        Get translation for a term.
        
        Args:
            project_name: Project name
            source_term: Source term
            target_language: Target language
            
        Returns:
            Translation or None
        """
        if project_name not in self.glossaries:
            return None
        
        term = self.glossaries[project_name].get(source_term)
        if term:
            return term.target_terms.get(target_language)
        
        return None
    
    def get_all_terms(self, project_name: str) -> List[GlossaryTerm]:
        """
        Get all terms for a project.
        
        Args:
            project_name: Project name
            
        Returns:
            List of glossary terms
        """
        if project_name not in self.glossaries:
            return []
        
        return list(self.glossaries[project_name].values())
    
    def search_terms(
        self,
        project_name: str,
        query: str,
        language: Optional[str] = None
    ) -> List[GlossaryTerm]:
        """
        Search for terms.
        
        Args:
            project_name: Project name
            query: Search query
            language: Optional language filter
            
        Returns:
            List of matching terms
        """
        if project_name not in self.glossaries:
            return []
        
        query_lower = query.lower()
        results = []
        
        for term in self.glossaries[project_name].values():
            if query_lower in term.source_term.lower():
                if not language or language in term.target_terms:
                    results.append(term)
            else:
                # Check target terms
                for lang, target in term.target_terms.items():
                    if query_lower in target.lower():
                        if not language or lang == language:
                            results.append(term)
                            break
        
        return results

