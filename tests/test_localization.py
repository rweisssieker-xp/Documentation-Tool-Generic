"""Tests für AI Localization"""

import pytest
from src.localization import TranslationEngine


def test_translation_engine():
    """Test Translation Engine"""
    engine = TranslationEngine()
    result = engine.translate("Hello", "de")
    assert result is not None
