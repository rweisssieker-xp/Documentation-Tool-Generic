"""
Base Plugin Class - Basis für alle Plugins
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PluginMetadata:
    """Plugin metadata"""
    id: str
    name: str
    version: str
    description: str
    author: str
    dependencies: Optional[Dict[str, str]] = None


class BasePlugin(ABC):
    """Base class for all plugins"""
    
    def __init__(self, metadata: Dict[str, Any]):
        """
        Initialize plugin.
        
        Args:
            metadata: Plugin metadata
        """
        self.metadata = PluginMetadata(
            id=metadata.get('id', 'unknown'),
            name=metadata.get('name', 'Unknown Plugin'),
            version=metadata.get('version', '1.0.0'),
            description=metadata.get('description', ''),
            author=metadata.get('author', 'Unknown'),
            dependencies=metadata.get('dependencies'),
        )
        self.logger = get_logger(f"plugin.{self.metadata.id}")
    
    @abstractmethod
    def on_load(self):
        """Called when plugin is loaded"""
        pass
    
    @abstractmethod
    def on_unload(self):
        """Called when plugin is unloaded"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return {
            'id': self.metadata.id,
            'name': self.metadata.name,
            'version': self.metadata.version,
            'description': self.metadata.description,
            'author': self.metadata.author,
        }

