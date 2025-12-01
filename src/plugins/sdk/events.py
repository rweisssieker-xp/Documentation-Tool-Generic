"""
Event System - Plugin Events
"""

from typing import Dict, List, Callable, Any
from collections import defaultdict
from enum import Enum

from src.utils.logger import get_logger

logger = get_logger(__name__)


class EventType(Enum):
    """Event types"""
    SESSION_STARTED = "session_started"
    SESSION_STOPPED = "session_stopped"
    STEP_ADDED = "step_added"
    DOCUMENT_GENERATED = "document_generated"
    PLUGIN_LOADED = "plugin_loaded"
    PLUGIN_UNLOADED = "plugin_unloaded"


class EventSystem:
    """Event system for plugins"""
    
    def __init__(self):
        self.listeners: Dict[EventType, List[Callable]] = defaultdict(list)
    
    def subscribe(self, event_type: EventType, callback: Callable):
        """Subscribe to event"""
        self.listeners[event_type].append(callback)
        logger.debug(f"Subscribed to event: {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """Unsubscribe from event"""
        if event_type in self.listeners:
            self.listeners[event_type].remove(callback)
    
    def emit(self, event_type: EventType, *args, **kwargs):
        """Emit event"""
        for callback in self.listeners.get(event_type, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error handling event {event_type.value}: {e}")

