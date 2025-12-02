"""Tests für Adaptive UX"""

import pytest
from src.adaptive_ux import AdaptiveUXEngine


def test_adaptive_ux_engine():
    """Test Adaptive UX Engine"""
    engine = AdaptiveUXEngine()
    result = engine.adapt_ui("user1", {})
    assert result is not None
