"""Tests für Intelligent Assistant"""

import pytest
from src.intelligent_assistant import IntelligentDocumentationAssistant


def test_intelligent_assistant():
    """Test Intelligent Assistant"""
    assistant = IntelligentDocumentationAssistant("user")
    result = assistant.help("How to document?")
    assert result is not None
