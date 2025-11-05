"""
Conftest.py - Shared pytest fixtures
"""

import sys
import pytest
from pathlib import Path
import tempfile
import shutil

# Füge src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(scope="session")
def project_root():
    """Gibt das Projekt-Root-Verzeichnis zurück"""
    return Path(__file__).parent.parent


@pytest.fixture
def temp_dir():
    """Erstellt temporäres Verzeichnis für Tests"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_config_dir(temp_dir):
    """Erstellt Mock Config-Verzeichnis"""
    config_dir = temp_dir / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "prompt_profiles").mkdir()
    (config_dir / "document_templates").mkdir()
    return config_dir


@pytest.fixture
def mock_data_dir(temp_dir):
    """Erstellt Mock Data-Verzeichnis"""
    data_dir = temp_dir / "data"
    data_dir.mkdir(parents=True)
    (data_dir / "sessions").mkdir()
    (data_dir / "screenshots").mkdir()
    (data_dir / "output").mkdir()
    return data_dir

