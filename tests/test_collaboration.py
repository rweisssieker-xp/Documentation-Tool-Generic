"""
Tests for Collaboration Hub Module
"""

import pytest
from datetime import datetime

from src.collaboration.crdt_engine import CRDTEngine, CRDTOperation
from src.collaboration.presence_manager import PresenceManager, UserPresence, PresenceType
from src.collaboration.comment_system import CommentSystem, Comment, CommentStatus
from src.collaboration.version_control import VersionControl, Version


class TestCRDTEngine:
    """Tests for CRDTEngine class."""
    
    def test_crdt_engine_initialization(self):
        """Test CRDTEngine initialization."""
        engine = CRDTEngine()
        assert len(engine.operations) == 0
    
    def test_apply_operation(self):
        """Test applying CRDT operation."""
        engine = CRDTEngine()
        
        operation = CRDTOperation(
            id="op-1",
            type="insert",
            position=0,
            content="Hello",
            timestamp=datetime.now(),
            user_id="user-1",
            vector_clock={"user-1": 1}
        )
        
        result = engine.apply_operation(operation)
        assert result == True
        assert len(engine.operations) == 1
    
    def test_get_state(self):
        """Test getting document state."""
        engine = CRDTEngine()
        
        operation = CRDTOperation(
            id="op-1",
            type="insert",
            position=0,
            content="Hello",
            timestamp=datetime.now(),
            user_id="user-1",
            vector_clock={"user-1": 1}
        )
        
        engine.apply_operation(operation)
        state = engine.get_state()
        
        assert "Hello" in state


class TestPresenceManager:
    """Tests for PresenceManager class."""
    
    def test_presence_manager_initialization(self):
        """Test PresenceManager initialization."""
        manager = PresenceManager()
        assert len(manager.presences) == 0
    
    def test_update_presence(self):
        """Test updating presence."""
        manager = PresenceManager()
        
        presence = UserPresence(
            user_id="user-1",
            user_name="Test User",
            presence_type=PresenceType.CURSOR,
            position=(100, 200)
        )
        
        manager.update_presence(presence)
        assert "user-1" in manager.presences
    
    def test_get_all_presences(self):
        """Test getting all presences."""
        manager = PresenceManager()
        
        presence = UserPresence(
            user_id="user-1",
            user_name="Test User",
            presence_type=PresenceType.CURSOR
        )
        
        manager.update_presence(presence)
        presences = manager.get_all_presences()
        
        assert len(presences) == 1


class TestCommentSystem:
    """Tests for CommentSystem class."""
    
    def test_comment_system_initialization(self):
        """Test CommentSystem initialization."""
        system = CommentSystem()
        assert len(system.comments) == 0
    
    def test_add_comment(self):
        """Test adding comment."""
        system = CommentSystem()
        
        comment = Comment(
            id="comment-1",
            author="User",
            content="Test comment",
            position=(10, 20),
            status=CommentStatus.OPEN,
            created_at=datetime.now()
        )
        
        comment_id = system.add_comment(comment)
        assert comment_id == "comment-1"
        assert len(system.comments) == 1
    
    def test_get_comments(self):
        """Test getting comments."""
        system = CommentSystem()
        
        comment = Comment(
            id="comment-1",
            author="User",
            content="Test comment",
            position=(10, 20),
            status=CommentStatus.OPEN,
            created_at=datetime.now()
        )
        
        system.add_comment(comment)
        comments = system.get_comments()
        
        assert len(comments) == 1


class TestVersionControl:
    """Tests for VersionControl class."""
    
    def test_version_control_initialization(self):
        """Test VersionControl initialization."""
        vc = VersionControl()
        assert len(vc.versions) == 0
    
    def test_create_version(self):
        """Test creating version."""
        vc = VersionControl()
        
        version_id = vc.create_version("Content", "Author", ["Change 1", "Change 2"])
        
        assert version_id == "v1"
        assert len(vc.versions) == 1
    
    def test_get_version(self):
        """Test getting version."""
        vc = VersionControl()
        
        version_id = vc.create_version("Content", "Author", ["Change 1"])
        version = vc.get_version(version_id)
        
        assert version is not None
        assert version.content == "Content"

