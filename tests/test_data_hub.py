"""Tests für Universal Data Hub"""

import pytest
from src.data_hub import UniversalDataHub


def test_data_hub():
    """Test Universal Data Hub"""
    hub = UniversalDataHub()
    result = hub.connect_system("CRM", {})
    assert result is True
