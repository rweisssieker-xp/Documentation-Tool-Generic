"""
CRDT Engine - Conflict-free Replicated Data Types for real-time sync.
Part of Feature: Real-Time Collaboration Hub (v2.0)
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import hashlib

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CRDTOperation:
    """A CRDT operation."""
    id: str
    type: str  # "insert", "delete", "update"
    position: int
    content: str
    timestamp: datetime
    user_id: str
    vector_clock: Dict[str, int]


class CRDTEngine:
    """
    CRDT engine for conflict-free real-time collaboration.
    Implements Yjs-like CRDT for text/document editing.
    """
    
    def __init__(self):
        """Initialize CRDT engine."""
        self.operations: List[CRDTOperation] = []
        self.vector_clock: Dict[str, int] = {}
    
    def apply_operation(self, operation: CRDTOperation) -> bool:
        """
        Apply CRDT operation.
        
        Args:
            operation: CRDT operation
            
        Returns:
            True if successful
        """
        # Update vector clock
        self.vector_clock[operation.user_id] = max(
            self.vector_clock.get(operation.user_id, 0),
            operation.vector_clock.get(operation.user_id, 0)
        ) + 1
        
        # Insert operation in sorted order (by timestamp and vector clock)
        self.operations.append(operation)
        self.operations.sort(key=lambda op: (
            op.timestamp,
            op.vector_clock.get(op.user_id, 0)
        ))
        
        return True
    
    def merge_operations(self, remote_operations: List[CRDTOperation]) -> List[CRDTOperation]:
        """
        Merge remote operations with local state.
        
        Args:
            remote_operations: Remote operations to merge
            
        Returns:
            List of new operations to apply
        """
        new_operations = []
        
        for remote_op in remote_operations:
            # Check if operation already exists
            if not any(op.id == remote_op.id for op in self.operations):
                # Check causality (vector clock)
                if self._can_apply(remote_op):
                    new_operations.append(remote_op)
                    self.apply_operation(remote_op)
        
        return new_operations
    
    def _can_apply(self, operation: CRDTOperation) -> bool:
        """Check if operation can be applied based on vector clock."""
        for user_id, clock_value in operation.vector_clock.items():
            local_clock = self.vector_clock.get(user_id, 0)
            if clock_value > local_clock + 1:
                return False  # Gap in sequence
        return True
    
    def get_state(self) -> str:
        """
        Get current document state.
        
        Returns:
            Document content
        """
        # Reconstruct document from operations
        content_parts = []
        for op in sorted(self.operations, key=lambda x: x.position):
            if op.type == "insert":
                content_parts.insert(op.position, op.content)
            elif op.type == "delete":
                if op.position < len(content_parts):
                    content_parts.pop(op.position)
        
        return "".join(content_parts)

