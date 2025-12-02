"""Tests für Hyperautomation"""

import pytest
from src.hyperautomation import WorkflowOrchestrator


def test_workflow_orchestrator():
    """Test Workflow Orchestrator"""
    orchestrator = WorkflowOrchestrator()
    assert orchestrator is not None
