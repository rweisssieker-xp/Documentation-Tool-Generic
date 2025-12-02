"""
Example Plugin: Jira Integration
Demonstrates how to integrate with external systems
"""

from typing import Dict, Any, Optional
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from src.plugins.sdk.base import BasePlugin
except ImportError:
    # Fallback if BasePlugin not available
    BasePlugin = object

PLUGIN_METADATA = {
    "id": "jira_integration",
    "name": "Jira Integration Plugin",
    "version": "1.0.0",
    "description": "Example plugin for Jira integration",
    "author": "AHG Team",
    "dependencies": {
        "requests": ">=2.31.0"
    }
}


class JiraIntegrationPlugin(BasePlugin):
    """Example Jira Integration Plugin"""
    
    def __init__(self, metadata: Dict[str, Any] = None):
        """Initialize plugin"""
        if BasePlugin != object and metadata:
            super().__init__(metadata)
        elif BasePlugin != object:
            super().__init__(PLUGIN_METADATA)
        self.metadata = metadata or PLUGIN_METADATA
        self.jira_url = None
        self.api_token = None
    
    def on_load(self):
        """Called when plugin is loaded"""
        if hasattr(self, 'logger'):
            self.logger.info(f"Plugin {self.metadata['name']} loaded")
        else:
            print(f"Plugin {self.metadata['name']} loaded")
        # TODO: Load Jira configuration
    
    def on_unload(self):
        """Called when plugin is unloaded"""
        if hasattr(self, 'logger'):
            self.logger.info(f"Plugin {self.metadata['name']} unloaded")
        else:
            print(f"Plugin {self.metadata['name']} unloaded")
    
    def configure(self, jira_url: str, api_token: str):
        """Configure Jira connection"""
        self.jira_url = jira_url
        self.api_token = api_token
    
    def sync_documentation(self, session_data: Dict[str, Any], issue_key: str) -> bool:
        """Sync documentation to Jira issue"""
        # TODO: Implement Jira API integration
        if hasattr(self, 'logger'):
            self.logger.info(f"Syncing documentation to Jira issue: {issue_key}")
        else:
            print(f"Syncing documentation to Jira issue: {issue_key}")
        return True
    
    def create_issue(self, session_data: Dict[str, Any], project_key: str) -> Optional[str]:
        """Create Jira issue from documentation"""
        # TODO: Implement Jira issue creation
        if hasattr(self, 'logger'):
            self.logger.info(f"Creating Jira issue in project: {project_key}")
        else:
            print(f"Creating Jira issue in project: {project_key}")
        return None
