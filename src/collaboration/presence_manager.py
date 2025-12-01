"""Presence Manager - Tracks user presence and cursors"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class PresenceType(Enum):
    """Presence types."""
    CURSOR = "cursor"
    SELECTION = "selection"
    VIEWING = "viewing"


@dataclass
class UserPresence:
    """User presence information."""
    user_id: str
    user_name: str
    presence_type: PresenceType
    position: Optional[tuple] = None  # (x, y) for cursor
    selection: Optional[tuple] = None  # (start, end) for selection
    last_seen: Optional[datetime] = None


class PresenceManager:
    """Manages user presence and cursor tracking."""
    
    def __init__(self):
        """Initialize presence manager."""
        self.presences: Dict[str, UserPresence] = {}
    
    def update_presence(self, presence: UserPresence):
        """Update user presence."""
        presence.last_seen = datetime.now()
        self.presences[presence.user_id] = presence
    
    def remove_presence(self, user_id: str):
        """Remove user presence."""
        self.presences.pop(user_id, None)
    
    def get_all_presences(self) -> List[UserPresence]:
        """Get all active presences."""
        return list(self.presences.values())

