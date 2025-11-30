"""
Tab Tracker - Tracks browser tabs for context capture.
Part of Feature 1: Smart Context Capture
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class BrowserTab:
    """Information about a browser tab."""
    title: str
    url: Optional[str]
    browser: str
    is_active: bool
    window_handle: Optional[int]
    timestamp: datetime


class TabTracker:
    """
    Tracks browser tabs across multiple browsers.
    Provides context about open tabs during documentation.
    """
    
    SUPPORTED_BROWSERS = [
        "chrome.exe",
        "firefox.exe",
        "msedge.exe",
        "brave.exe",
        "opera.exe"
    ]
    
    BROWSER_NAMES = {
        "chrome.exe": "Chrome",
        "firefox.exe": "Firefox",
        "msedge.exe": "Edge",
        "brave.exe": "Brave",
        "opera.exe": "Opera"
    }
    
    def __init__(self):
        """Initialize tab tracker."""
        self._cached_tabs: List[BrowserTab] = []
        self._last_scan: Optional[datetime] = None
        
        logger.info("TabTracker initialized")
    
    def get_active_tabs(self, force_refresh: bool = False) -> List[Dict[str, str]]:
        """
        Get list of active browser tabs.
        
        Args:
            force_refresh: Force rescan of tabs
            
        Returns:
            List of tab information dictionaries
        """
        # Refresh if needed
        if force_refresh or self._should_refresh():
            self._scan_tabs()
        
        return [
            {
                "title": tab.title,
                "url": tab.url or "",
                "browser": tab.browser,
                "is_active": tab.is_active
            }
            for tab in self._cached_tabs
        ]
    
    def get_current_tab(self) -> Optional[Dict[str, str]]:
        """Get the currently active browser tab."""
        tabs = self.get_active_tabs()
        for tab in tabs:
            if tab.get("is_active"):
                return tab
        return None
    
    def get_tabs_by_browser(self, browser: str) -> List[Dict[str, str]]:
        """
        Get tabs for a specific browser.
        
        Args:
            browser: Browser name (Chrome, Firefox, etc.)
            
        Returns:
            List of tabs for that browser
        """
        tabs = self.get_active_tabs()
        return [t for t in tabs if t.get("browser", "").lower() == browser.lower()]
    
    def _should_refresh(self) -> bool:
        """Check if tab cache should be refreshed."""
        if not self._last_scan:
            return True
        
        # Refresh every 5 seconds
        age = (datetime.now() - self._last_scan).total_seconds()
        return age > 5.0
    
    def _scan_tabs(self) -> None:
        """Scan for open browser tabs."""
        self._cached_tabs = []
        self._last_scan = datetime.now()
        
        try:
            import win32gui
            import win32process
            import psutil
            
            def callback(hwnd, tabs):
                if not win32gui.IsWindowVisible(hwnd):
                    return
                
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    proc = psutil.Process(pid)
                    proc_name = proc.name().lower()
                    
                    if proc_name in self.SUPPORTED_BROWSERS:
                        title = win32gui.GetWindowText(hwnd)
                        if title:
                            # Check if this is the active window
                            is_active = hwnd == win32gui.GetForegroundWindow()
                            
                            tab = BrowserTab(
                                title=title,
                                url=None,  # URL extraction would need browser automation
                                browser=self.BROWSER_NAMES.get(proc_name, proc_name),
                                is_active=is_active,
                                window_handle=hwnd,
                                timestamp=datetime.now()
                            )
                            tabs.append(tab)
                except:
                    pass
            
            tabs = []
            win32gui.EnumWindows(callback, tabs)
            self._cached_tabs = tabs
            
            logger.debug(f"Found {len(tabs)} browser tabs")
        
        except ImportError:
            logger.debug("win32gui not available for tab tracking")
        except Exception as e:
            logger.warning(f"Tab scan failed: {e}")

