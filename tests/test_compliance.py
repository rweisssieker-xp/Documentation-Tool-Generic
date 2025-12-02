"""Tests für Compliance Automation"""

import pytest
from src.compliance import ComplianceEngine


def test_compliance_engine():
    """Test Compliance Engine"""
    engine = ComplianceEngine()
    result = engine.check_compliance("Test content", ["GDPR"])
    assert result['compliant'] is not None
