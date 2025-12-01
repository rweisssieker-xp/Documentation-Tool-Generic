"""
Plugin Registry - Zentrale Plugin-Registry
"""

from typing import Dict, List, Optional
from pathlib import Path
import json

from src.utils.logger import get_logger

logger = get_logger(__name__)


class PluginRegistry:
    """Plugin Registry"""
    
    def __init__(self, registry_file: str = "data/plugin_registry.json"):
        """
        Initialize Plugin Registry.
        
        Args:
            registry_file: Path to registry file
        """
        self.registry_file = Path(registry_file)
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.registry: Dict[str, Dict] = {}
        self._load_registry()
    
    def _load_registry(self):
        """Load registry from file"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    self.registry = json.load(f)
            except Exception as e:
                logger.error(f"Error loading registry: {e}")
                self.registry = {}
        else:
            self.registry = {}
    
    def _save_registry(self):
        """Save registry to file"""
        try:
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(self.registry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving registry: {e}")
    
    def register_plugin(self, plugin_id: str, metadata: Dict):
        """Register plugin"""
        self.registry[plugin_id] = metadata
        self._save_registry()
        logger.info(f"Plugin registered: {plugin_id}")
    
    def unregister_plugin(self, plugin_id: str):
        """Unregister plugin"""
        if plugin_id in self.registry:
            del self.registry[plugin_id]
            self._save_registry()
            logger.info(f"Plugin unregistered: {plugin_id}")
    
    def get_plugin(self, plugin_id: str) -> Optional[Dict]:
        """Get plugin metadata"""
        return self.registry.get(plugin_id)
    
    def list_plugins(self) -> List[Dict]:
        """List all registered plugins"""
        return list(self.registry.values())
    
    def search_plugins(self, query: str) -> List[Dict]:
        """Search plugins"""
        query_lower = query.lower()
        results = []
        
        for plugin_data in self.registry.values():
            if (query_lower in plugin_data.get('name', '').lower() or
                query_lower in plugin_data.get('description', '').lower()):
                results.append(plugin_data)
        
        return results

