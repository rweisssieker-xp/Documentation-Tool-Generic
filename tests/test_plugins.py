"""
Tests for Plugin System
"""

import pytest
from pathlib import Path
import tempfile
import json

from src.plugins import PluginManager, BasePlugin
from src.plugins.sdk.base import PluginMetadata


class TestPluginManager:
    """Test Plugin Manager"""
    
    def test_manager_initialization(self):
        """Test plugin manager initialization"""
        manager = PluginManager()
        assert manager.plugins_dir.exists()
        assert len(manager.loaded_plugins) == 0
    
    def test_list_plugins_empty(self):
        """Test listing plugins when empty"""
        manager = PluginManager()
        plugins = manager.list_plugins()
        assert isinstance(plugins, list)
        assert len(plugins) == 0
    
    def test_get_plugin_not_found(self):
        """Test getting non-existent plugin"""
        manager = PluginManager()
        plugin = manager.get_plugin("nonexistent")
        assert plugin is None


class TestBasePlugin:
    """Test Base Plugin"""
    
    def test_plugin_initialization(self):
        """Test plugin initialization"""
        metadata = {
            'id': 'test_plugin',
            'name': 'Test Plugin',
            'version': '1.0.0',
            'description': 'Test',
            'author': 'Test Author',
        }
        
        class TestPlugin(BasePlugin):
            def on_load(self):
                pass
            
            def on_unload(self):
                pass
        
        plugin = TestPlugin(metadata)
        assert plugin.metadata.id == 'test_plugin'
        assert plugin.metadata.name == 'Test Plugin'
    
    def test_plugin_get_info(self):
        """Test plugin get_info"""
        metadata = {
            'id': 'test_plugin',
            'name': 'Test Plugin',
            'version': '1.0.0',
            'description': 'Test',
            'author': 'Test Author',
        }
        
        class TestPlugin(BasePlugin):
            def on_load(self):
                pass
            
            def on_unload(self):
                pass
        
        plugin = TestPlugin(metadata)
        info = plugin.get_info()
        assert info['id'] == 'test_plugin'
        assert info['name'] == 'Test Plugin'

