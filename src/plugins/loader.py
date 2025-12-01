"""
Plugin Loader - Lädt Plugins sicher
"""

import importlib.util
from pathlib import Path
from typing import Optional, Dict, Any

from .sdk.base import BasePlugin
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PluginLoader:
    """Plugin Loader"""
    
    def load_plugin(self, plugin_file: Path, metadata: Dict[str, Any]) -> Optional[BasePlugin]:
        """
        Load plugin from file.
        
        Args:
            plugin_file: Path to plugin file
            metadata: Plugin metadata
        
        Returns:
            Plugin instance or None
        """
        try:
            spec = importlib.util.spec_from_file_location(
                metadata.get('id', 'plugin'),
                plugin_file
            )
            
            if spec is None or spec.loader is None:
                logger.error(f"Failed to create spec for: {plugin_file}")
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin class
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, BasePlugin) and 
                    attr != BasePlugin):
                    plugin_class = attr
                    break
            
            if plugin_class is None:
                logger.error(f"No plugin class found in: {plugin_file}")
                return None
            
            # Instantiate plugin
            plugin_instance = plugin_class(metadata)
            return plugin_instance
        
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_file}: {e}")
            return None

