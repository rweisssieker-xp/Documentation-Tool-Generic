"""
Example Plugin: Custom Export Format
Demonstrates how to create a custom export plugin
"""

from typing import Dict, Any, Optional
from pathlib import Path
import json
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from src.plugins.sdk.base import BasePlugin
except ImportError:
    # Fallback if BasePlugin not available
    BasePlugin = object

PLUGIN_METADATA = {
    "id": "custom_export",
    "name": "Custom Export Plugin",
    "version": "1.0.0",
    "description": "Example plugin for custom export format",
    "author": "AHG Team",
    "dependencies": {}
}


class CustomExportPlugin(BasePlugin):
    """Example Custom Export Plugin"""
    
    def __init__(self, metadata: Dict[str, Any] = None):
        """Initialize plugin"""
        if BasePlugin != object and metadata:
            super().__init__(metadata)
        elif BasePlugin != object:
            super().__init__(PLUGIN_METADATA)
        self.metadata = metadata or PLUGIN_METADATA
    
    def on_load(self):
        """Called when plugin is loaded"""
        if hasattr(self, 'logger'):
            self.logger.info(f"Plugin {self.metadata['name']} loaded")
        else:
            print(f"Plugin {self.metadata['name']} loaded")
    
    def on_unload(self):
        """Called when plugin is unloaded"""
        if hasattr(self, 'logger'):
            self.logger.info(f"Plugin {self.metadata['name']} unloaded")
        else:
            print(f"Plugin {self.metadata['name']} unloaded")
    
    def export_document(self, session_data: Dict[str, Any], output_path: str):
        """Export document in custom format"""
        # Example: Export as JSON with custom structure
        custom_format = {
            "version": "1.0",
            "session_id": session_data.get("session_id", "unknown"),
            "steps": session_data.get("steps", []),
            "metadata": {
                "exported_by": "custom_export_plugin",
                "format": "custom_json"
            }
        }
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(custom_format, f, indent=2, ensure_ascii=False)
        
        return str(output_file)
