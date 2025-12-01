"""Comment System - Inline comments and annotations"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class CommentStatus(Enum):
    """Comment status."""
    OPEN = "open"
    RESOLVED = "resolved"
    ARCHIVED = "archived"


@dataclass
class Comment:
    """A comment."""
    id: str
    author: str
    content: str
    position: tuple  # (line, column) or (start, end)
    status: CommentStatus
    created_at: datetime
    replies: List['Comment'] = None
    
    def __post_init__(self):
        if self.replies is None:
            self.replies = []


class CommentSystem:
    """Manages comments and annotations."""
    
    def __init__(self):
        """Initialize comment system."""
        self.comments: Dict[str, Comment] = {}
    
    def add_comment(self, comment: Comment) -> str:
        """Add comment."""
        self.comments[comment.id] = comment
        return comment.id
    
    def get_comments(self, position: Optional[tuple] = None) -> List[Comment]:
        """Get comments, optionally filtered by position."""
        if position:
            return [c for c in self.comments.values() if c.position == position]
        return list(self.comments.values())

