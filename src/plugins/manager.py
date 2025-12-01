"""
Plugin Manager - Zentrale Plugin-Verwaltung
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import importlib.util
import json

from .loader import PluginLoader
from .security.sandbox import SandboxExecutor
from .marketplace.registry import PluginRegistry
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PluginManager:
    """Zentrale Plugin-Manager-Klasse"""
    
    def __init__(self, plugins_dir: str = "plugins"):
        """
        Initialize Plugin Manager.
        
        Args:
            plugins_dir: Directory for plugins
        """
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        
        self.loader = PluginLoader()
        self.sandbox = SandboxExecutor()
        self.registry = PluginRegistry()
        
        self.loaded_plugins: Dict[str, Any] = {}
        self.plugin_metadata: Dict[str, Dict] = {}
    
    def load_plugin(self, plugin_path: str) -> bool:
        """Load plugin from path"""
        try:
            plugin_file = Path(plugin_path)
            if not plugin_file.exists():
                logger.error(f"Plugin file not found: {plugin_path}")
                return False
            
            # Load plugin metadata
            metadata = self._load_metadata(plugin_file)
            if not metadata:
                logger.error(f"Failed to load metadata for: {plugin_path}")
                return False
            
            plugin_id = metadata.get('id')
            if not plugin_id:
                logger.error(f"Plugin metadata missing 'id': {plugin_path}")
                return False
            
            # Load plugin in sandbox
            plugin_instance = self.loader.load_plugin(plugin_file, metadata)
            
            if plugin_instance:
                self.loaded_plugins[plugin_id] = plugin_instance
                self.plugin_metadata[plugin_id] = metadata
                logger.info(f"Plugin loaded: {plugin_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_path}: {e}")
            return False
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload plugin"""
        if plugin_id in self.loaded_plugins:
            del self.loaded_plugins[plugin_id]
            if plugin_id in self.plugin_metadata:
                del self.plugin_metadata[plugin_id]
            logger.info(f"Plugin unloaded: {plugin_id}")
            return True
        return False
    
    def get_plugin(self, plugin_id: str) -> Optional[Any]:
        """Get plugin instance"""
        return self.loaded_plugins.get(plugin_id)
    
    def list_plugins(self) -> List[Dict]:
        """List all loaded plugins"""
        return [
            {
                'id': plugin_id,
                'metadata': metadata,
                'loaded': True,
            }
            for plugin_id, metadata in self.plugin_metadata.items()
        ]
    
    def execute_plugin_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Execute hook across all plugins"""
        results = []
        
        for plugin_id, plugin_instance in self.loaded_plugins.items():
            try:
                if hasattr(plugin_instance, hook_name):
                    hook_method = getattr(plugin_instance, hook_name)
                    result = hook_method(*args, **kwargs)
                    results.append({
                        'plugin_id': plugin_id,
                        'result': result,
                    })
            except Exception as e:
                logger.error(f"Error executing hook {hook_name} in plugin {plugin_id}: {e}")
        
        return results
    
    def _load_metadata(self, plugin_file: Path) -> Optional[Dict]:
        """Load plugin metadata"""
        # Try to load metadata.json in same directory
        metadata_file = plugin_file.parent / "metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading metadata: {e}")
        
        # Try to extract from plugin file docstring
        try:
            spec = importlib.util.spec_from_file_location("plugin", plugin_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'PLUGIN_METADATA'):
                return module.PLUGIN_METADATA
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
        
        return None
    
    def load_all_plugins(self):
        """Load all plugins from plugins directory"""
        for plugin_file in self.plugins_dir.rglob("*.py"):
            if plugin_file.name != "__init__.py":
                self.load_plugin(str(plugin_file))

