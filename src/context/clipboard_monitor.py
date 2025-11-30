"""
Clipboard Monitor - Monitors clipboard for context capture.
Part of Feature 1: Smart Context Capture
"""

import threading
import time
from typing import Optional, Callable, List
from dataclasses import dataclass
from datetime import datetime

from src.utils.logger import get_logger

logger = get_logger(__name__)

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False


@dataclass
class ClipboardEntry:
    """A clipboard history entry."""
    content: str
    timestamp: datetime
    content_type: str  # "text", "image", "file"


class ClipboardMonitor:
    """
    Monitors clipboard changes for context capture.
    Tracks clipboard history during documentation sessions.
    """
    
    def __init__(
        self,
        history_size: int = 20,
        poll_interval: float = 0.5
    ):
        """
        Initialize clipboard monitor.
        
        Args:
            history_size: Maximum history entries
            poll_interval: Polling interval in seconds
        """
        if not PYPERCLIP_AVAILABLE:
            logger.warning("pyperclip not available - clipboard monitoring disabled")
        
        self.history_size = history_size
        self.poll_interval = poll_interval
        
        self._history: List[ClipboardEntry] = []
        self._current: Optional[str] = None
        self._is_monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._on_change: Optional[Callable[[str], None]] = None
        
        logger.info("ClipboardMonitor initialized")
    
    def start_monitoring(
        self,
        on_change: Optional[Callable[[str], None]] = None
    ) -> bool:
        """
        Start monitoring clipboard changes.
        
        Args:
            on_change: Callback when clipboard changes
            
        Returns:
            True if started successfully
        """
        if not PYPERCLIP_AVAILABLE:
            return False
        
        if self._is_monitoring:
            return True
        
        self._on_change = on_change
        self._is_monitoring = True
        
        # Get initial clipboard content
        try:
            self._current = pyperclip.paste()
        except:
            self._current = None
        
        # Start monitoring thread
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self._monitor_thread.start()
        
        logger.info("Clipboard monitoring started")
        return True
    
    def stop_monitoring(self) -> None:
        """Stop monitoring clipboard."""
        self._is_monitoring = False
        
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
            self._monitor_thread = None
        
        logger.info("Clipboard monitoring stopped")
    
    def get_current(self) -> Optional[str]:
        """Get current clipboard content."""
        if not PYPERCLIP_AVAILABLE:
            return None
        
        try:
            return pyperclip.paste()
        except Exception as e:
            logger.warning(f"Failed to get clipboard: {e}")
            return None
    
    def get_history(self) -> List[ClipboardEntry]:
        """Get clipboard history."""
        return list(self._history)
    
    def get_recent(self, count: int = 5) -> List[ClipboardEntry]:
        """Get recent clipboard entries."""
        return self._history[-count:] if self._history else []
    
    def clear_history(self) -> None:
        """Clear clipboard history."""
        self._history.clear()
        logger.debug("Clipboard history cleared")
    
    def is_monitoring(self) -> bool:
        """Check if monitoring is active."""
        return self._is_monitoring
    
    def _monitor_loop(self) -> None:
        """Internal monitoring loop."""
        while self._is_monitoring:
            try:
                current = pyperclip.paste()
                
                if current != self._current and current:
                    self._current = current
                    
                    # Add to history
                    entry = ClipboardEntry(
                        content=current,
                        timestamp=datetime.now(),
                        content_type="text"
                    )
                    
                    self._history.append(entry)
                    
                    # Trim history
                    if len(self._history) > self.history_size:
                        self._history.pop(0)
                    
                    # Trigger callback
                    if self._on_change:
                        try:
                            self._on_change(current)
                        except Exception as e:
                            logger.error(f"Clipboard callback error: {e}")
                    
                    logger.debug(f"Clipboard changed: {current[:50]}...")
            
            except Exception as e:
                logger.debug(f"Clipboard poll error: {e}")
            
            time.sleep(self.poll_interval)

