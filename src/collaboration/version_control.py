"""Version Control - History and rollback for collaborative editing"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Version:
    """A version snapshot."""
    id: str
    content: str
    author: str
    timestamp: datetime
    changes: List[str]


class VersionControl:
    """Manages version history."""
    
    def __init__(self):
        """Initialize version control."""
        self.versions: List[Version] = []
    
    def create_version(self, content: str, author: str, changes: List[str]) -> str:
        """Create new version."""
        version = Version(
            id=f"v{len(self.versions) + 1}",
            content=content,
            author=author,
            timestamp=datetime.now(),
            changes=changes
        )
        self.versions.append(version)
        return version.id
    
    def get_version(self, version_id: str) -> Optional[Version]:
        """Get version by ID."""
        return next((v for v in self.versions if v.id == version_id), None)

