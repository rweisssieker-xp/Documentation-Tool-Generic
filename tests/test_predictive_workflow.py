"""Tests für Predictive Workflow"""

import pytest
from src.predictive_workflow import PredictiveWorkflowAutomator


def test_predictive_workflow():
    """Test Predictive Workflow"""
    automator = PredictiveWorkflowAutomator()
    result = automator.predict_next_action({})
    assert result is not None
