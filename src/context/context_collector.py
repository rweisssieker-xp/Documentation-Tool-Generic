"""
Context Collector - Collects comprehensive context for documentation steps.
Part of Feature 1: Smart Context Capture
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class StepContext:
    """Complete context for a documentation step."""
    step_id: str
    timestamp: datetime
    window_context: Dict[str, Any]
    clipboard_content: Optional[str]
    active_tabs: List[Dict[str, str]]
    running_apps: List[str]
    previous_actions: List[str]
    mouse_position: tuple
    keyboard_state: Dict[str, bool]
    screen_regions: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContextCollector:
    """
    Collects comprehensive context from multiple sources.
    Combines window state, clipboard, active applications, and more.
    """
    
    def __init__(
        self,
        clipboard_monitor: Optional[Any] = None,
        tab_tracker: Optional[Any] = None,
        history_size: int = 10
    ):
        """
        Initialize context collector.
        
        Args:
            clipboard_monitor: ClipboardMonitor instance
            tab_tracker: TabTracker instance
            history_size: Number of previous actions to track
        """
        self.clipboard_monitor = clipboard_monitor
        self.tab_tracker = tab_tracker
        self.history_size = history_size
        
        self._action_history: List[str] = []
        self._context_cache: Dict[str, StepContext] = {}
        
        logger.info("ContextCollector initialized")
    
    def collect_context(
        self,
        step_id: str,
        window_title: Optional[str] = None,
        window_handle: Optional[int] = None
    ) -> StepContext:
        """
        Collect complete context for a step.
        
        Args:
            step_id: Step identifier
            window_title: Current window title
            window_handle: Window handle
            
        Returns:
            StepContext with all collected data
        """
        # Collect window context
        window_context = self._collect_window_context(window_title, window_handle)
        
        # Collect clipboard
        clipboard = None
        if self.clipboard_monitor:
            clipboard = self.clipboard_monitor.get_current()
        
        # Collect active tabs
        tabs = []
        if self.tab_tracker:
            tabs = self.tab_tracker.get_active_tabs()
        
        # Collect running applications
        running_apps = self._get_running_applications()
        
        # Get mouse position
        mouse_pos = self._get_mouse_position()
        
        # Get keyboard state
        keyboard_state = self._get_keyboard_state()
        
        context = StepContext(
            step_id=step_id,
            timestamp=datetime.now(),
            window_context=window_context,
            clipboard_content=clipboard,
            active_tabs=tabs,
            running_apps=running_apps,
            previous_actions=list(self._action_history),
            mouse_position=mouse_pos,
            keyboard_state=keyboard_state,
            screen_regions=[]
        )
        
        # Cache context
        self._context_cache[step_id] = context
        
        logger.debug(f"Collected context for step: {step_id}")
        return context
    
    def record_action(self, action: str) -> None:
        """
        Record an action for history tracking.
        
        Args:
            action: Action description
        """
        self._action_history.append(action)
        if len(self._action_history) > self.history_size:
            self._action_history.pop(0)
    
    def get_context(self, step_id: str) -> Optional[StepContext]:
        """Get cached context for a step."""
        return self._context_cache.get(step_id)
    
    def get_context_summary(self, step_id: str) -> Dict[str, Any]:
        """
        Get a summary of context for display.
        
        Args:
            step_id: Step identifier
            
        Returns:
            Context summary dictionary
        """
        context = self._context_cache.get(step_id)
        if not context:
            return {}
        
        return {
            "window": context.window_context.get("title", "Unknown"),
            "app": context.window_context.get("process", "Unknown"),
            "clipboard_preview": context.clipboard_content[:100] if context.clipboard_content else None,
            "open_tabs": len(context.active_tabs),
            "running_apps": len(context.running_apps),
            "previous_actions": len(context.previous_actions),
            "timestamp": context.timestamp.isoformat()
        }
    
    def export_context(self, step_id: str) -> Dict[str, Any]:
        """Export context as dictionary."""
        context = self._context_cache.get(step_id)
        if not context:
            return {}
        
        return {
            "step_id": context.step_id,
            "timestamp": context.timestamp.isoformat(),
            "window": context.window_context,
            "clipboard": context.clipboard_content,
            "tabs": context.active_tabs,
            "apps": context.running_apps,
            "history": context.previous_actions,
            "mouse": context.mouse_position,
            "keyboard": context.keyboard_state
        }
    
    def clear_history(self) -> None:
        """Clear action history."""
        self._action_history.clear()
    
    def _collect_window_context(
        self,
        window_title: Optional[str],
        window_handle: Optional[int]
    ) -> Dict[str, Any]:
        """Collect detailed window context."""
        context = {
            "title": window_title or "Unknown",
            "handle": window_handle,
            "process": None,
            "class_name": None,
            "rect": None
        }
        
        try:
            import win32gui
            import win32process
            import psutil
            
            if window_handle:
                # Get window rect
                rect = win32gui.GetWindowRect(window_handle)
                context["rect"] = {
                    "left": rect[0],
                    "top": rect[1],
                    "right": rect[2],
                    "bottom": rect[3]
                }
                
                # Get class name
                context["class_name"] = win32gui.GetClassName(window_handle)
                
                # Get process info
                _, pid = win32process.GetWindowThreadProcessId(window_handle)
                try:
                    proc = psutil.Process(pid)
                    context["process"] = proc.name()
                    context["pid"] = pid
                except:
                    pass
        
        except ImportError:
            logger.debug("win32gui not available for window context")
        except Exception as e:
            logger.warning(f"Failed to collect window context: {e}")
        
        return context
    
    def _get_running_applications(self) -> List[str]:
        """Get list of running applications."""
        apps = []
        
        try:
            import psutil
            
            for proc in psutil.process_iter(['name']):
                try:
                    name = proc.info['name']
                    if name and name not in apps:
                        apps.append(name)
                except:
                    pass
        
        except ImportError:
            logger.debug("psutil not available")
        except Exception as e:
            logger.warning(f"Failed to get running apps: {e}")
        
        return apps[:50]  # Limit to 50
    
    def _get_mouse_position(self) -> tuple:
        """Get current mouse position."""
        try:
            import pyautogui
            pos = pyautogui.position()
            return (pos.x, pos.y)
        except:
            return (0, 0)
    
    def _get_keyboard_state(self) -> Dict[str, bool]:
        """Get current keyboard modifier state."""
        state = {
            "shift": False,
            "ctrl": False,
            "alt": False,
            "caps_lock": False
        }
        
        try:
            import win32api
            import win32con
            
            state["shift"] = win32api.GetKeyState(win32con.VK_SHIFT) < 0
            state["ctrl"] = win32api.GetKeyState(win32con.VK_CONTROL) < 0
            state["alt"] = win32api.GetKeyState(win32con.VK_MENU) < 0
            state["caps_lock"] = win32api.GetKeyState(win32con.VK_CAPITAL) == 1
        
        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"Failed to get keyboard state: {e}")
        
        return state

