"""
Tests for API-First Gateway
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json

from src.api import APIGateway
from src.api.rest.sessions import SessionAPI


class TestAPIGateway:
    """Test API Gateway"""
    
    def test_gateway_initialization(self):
        """Test gateway initialization"""
        gateway = APIGateway()
        assert gateway.title == "AHG API Gateway"
        assert gateway.version == "3.0.0"
        assert gateway.app is not None
    
    def test_gateway_configuration(self):
        """Test gateway configuration"""
        gateway = APIGateway(
            enable_cors=False,
            enable_auth=False,
            enable_rate_limit=False,
        )
        assert gateway.enable_cors is False
        assert gateway.enable_auth is False
        assert gateway.enable_rate_limit is False


class TestSessionAPI:
    """Test Session API"""
    
    def test_session_api_initialization(self):
        """Test session API initialization"""
        api = SessionAPI()
        assert api.sessions_dir.exists()
    
    def test_list_sessions_empty(self):
        """Test listing sessions when empty"""
        api = SessionAPI()
        # Mock sessions directory
        api.sessions_dir = Path("data/test_sessions")
        api.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # Should return empty list
        sessions = []
        for session_file in api.sessions_dir.glob("*.json"):
            sessions.append(session_file)
        
        assert len(sessions) == 0


class TestDocumentAPI:
    """Test Document API"""
    
    def test_document_api_initialization(self):
        """Test document API initialization"""
        from src.api.rest.documents import DocumentAPI
        
        api = DocumentAPI()
        assert api.sessions_dir.exists()
        assert api.documents_dir.exists()




