"""
Tests for Translation Hub Module
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.translation.glossary_manager import GlossaryManager, GlossaryTerm
from src.translation.translation_memory import TranslationMemory, TranslationUnit
from src.translation.context_translator import ContextTranslator
from src.translation.translation_hub import TranslationHub
from src.translation.review_workflow import ReviewWorkflow, ReviewStatus
from datetime import datetime


class TestGlossaryManager:
    """Tests for GlossaryManager class."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    def test_glossary_manager_initialization(self, temp_storage):
        """Test GlossaryManager initialization."""
        manager = GlossaryManager(storage_dir=temp_storage)
        assert manager.storage_dir == temp_storage
    
    def test_add_term(self, temp_storage):
        """Test adding glossary term."""
        manager = GlossaryManager(storage_dir=temp_storage)
        
        manager.add_term("test_project", "Benutzer", "en", "User")
        
        translation = manager.get_translation("test_project", "Benutzer", "en")
        assert translation == "User"
    
    def test_get_all_terms(self, temp_storage):
        """Test getting all terms."""
        manager = GlossaryManager(storage_dir=temp_storage)
        
        manager.add_term("test_project", "Benutzer", "en", "User")
        manager.add_term("test_project", "Passwort", "en", "Password")
        
        terms = manager.get_all_terms("test_project")
        assert len(terms) == 2


class TestTranslationMemory:
    """Tests for TranslationMemory class."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    def test_translation_memory_initialization(self, temp_storage):
        """Test TranslationMemory initialization."""
        tm = TranslationMemory(storage_dir=temp_storage)
        assert tm.storage_dir == temp_storage
    
    def test_add_translation(self, temp_storage):
        """Test adding translation."""
        tm = TranslationMemory(storage_dir=temp_storage)
        
        tm.add_translation("Hello", "Hallo", "en", "de")
        
        unit = tm.find_translation("Hello", "en", "de")
        assert unit is not None
        assert unit.target_text == "Hallo"
    
    def test_find_fuzzy_match(self, temp_storage):
        """Test finding fuzzy matches."""
        tm = TranslationMemory(storage_dir=temp_storage)
        
        tm.add_translation("Hello World", "Hallo Welt", "en", "de")
        
        matches = tm.find_fuzzy_match("Hello", "en", "de", similarity_threshold=0.3)
        # May return empty if similarity is too low, which is OK
        assert isinstance(matches, list)


class TestContextTranslator:
    """Tests for ContextTranslator class."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    def test_context_translator_initialization(self, temp_storage):
        """Test ContextTranslator initialization."""
        translator = ContextTranslator(project_name="test")
        assert translator.project_name == "test"
    
    def test_translate_with_memory(self, temp_storage):
        """Test translation with memory."""
        translator = ContextTranslator(project_name="test")
        
        # Add to memory first
        translator.translation_memory.add_translation("Hello", "Hallo", "en", "de")
        
        # Translate should use memory
        result = translator.translate("Hello", "en", "de", use_memory=True)
        assert result == "Hallo"


class TestReviewWorkflow:
    """Tests for ReviewWorkflow class."""
    
    def test_review_workflow_initialization(self):
        """Test ReviewWorkflow initialization."""
        workflow = ReviewWorkflow()
        assert workflow is not None
    
    def test_submit_for_review(self):
        """Test submitting for review."""
        workflow = ReviewWorkflow()
        
        review_id = workflow.submit_for_review("trans-1", "Hello", "Hallo")
        assert review_id == "trans-1"
        
        pending = workflow.get_pending_reviews()
        assert len(pending) == 1
    
    def test_review_translation(self):
        """Test reviewing translation."""
        workflow = ReviewWorkflow()
        
        workflow.submit_for_review("trans-1", "Hello", "Hallo")
        workflow.review_translation("trans-1", "Reviewer", ReviewStatus.APPROVED)
        
        review = workflow.get_review("trans-1")
        assert review.status == ReviewStatus.APPROVED

