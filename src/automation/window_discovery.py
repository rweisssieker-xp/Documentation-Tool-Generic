"""
Window Discovery Service: Erkennt alle laufenden Windows-Fenster
"""

import win32gui
import win32process
import win32con
import psutil
from typing import List, Dict, Optional
from collections import defaultdict

from src.utils.logger import get_logger

logger = get_logger(__name__)


class WindowDiscovery:
    """Erkennt alle laufenden Windows-Fenster"""
    
    def __init__(self):
        """Initialisiert den Window Discovery Service"""
        self.windows = []
    
    def discover_all_windows(self, filter_minimized: bool = True, filter_hidden: bool = True) -> List[Dict]:
        """
        Erkennt alle laufenden Windows-Fenster
        
        Args:
            filter_minimized: Ob minimierte Fenster herausgefiltert werden sollen
            filter_hidden: Ob versteckte Fenster herausgefiltert werden sollen
            
        Returns:
            Liste von Fenster-Informationen
        """
        windows = []
        
        def enum_callback(hwnd, windows_list):
            """Callback für EnumWindows"""
            try:
                # Prüfe ob Fenster sichtbar ist
                if not win32gui.IsWindowVisible(hwnd):
                    if filter_hidden:
                        return
                
                # Prüfe ob Fenster minimiert ist
                if win32gui.IsIconic(hwnd):
                    if filter_minimized:
                        return
                
                # Hole Fenster-Informationen
                window_info = self._get_window_info(hwnd)
                
                # Filtere leere/minimale Fenster
                if window_info['position']['width'] < 50 or window_info['position']['height'] < 50:
                    return
                
                # Filtere System-Fenster (Desktop, Taskbar, etc.)
                if self._is_system_window(window_info):
                    return
                
                windows_list.append(window_info)
            
            except Exception as e:
                logger.debug(f"Fehler beim Verarbeiten von Fenster {hwnd}: {e}")
        
        # Enumere alle Fenster
        win32gui.EnumWindows(enum_callback, windows)
        
        self.windows = windows
        logger.info(f"{len(windows)} Fenster erkannt")
        return windows
    
    def _get_window_info(self, hwnd: int) -> Dict:
        """
        Extrahiert Informationen über ein Fenster
        
        Args:
            hwnd: Window Handle
            
        Returns:
            Dictionary mit Fenster-Informationen
        """
        try:
            # Fenstertitel
            title = win32gui.GetWindowText(hwnd)
            
            # Fensterklasse
            class_name = win32gui.GetClassName(hwnd)
            
            # Fensterposition und Größe
            rect = win32gui.GetWindowRect(hwnd)
            left, top, right, bottom = rect
            width = right - left
            height = bottom - top
            
            # Prüfe ob Fenster minimiert ist
            is_minimized = win32gui.IsIconic(hwnd)
            
            # Prüfe ob Fenster maximiert ist
            # Verwende GetWindowPlacement oder Fallback auf Größenprüfung
            is_maximized = False
            try:
                placement = win32gui.GetWindowPlacement(hwnd)
                # showCmd ist das zweite Element im Tuple
                # SW_SHOWMAXIMIZED = 3
                if len(placement) > 1:
                    is_maximized = placement[1] == 3  # SW_SHOWMAXIMIZED
            except Exception:
                # Fallback: Prüfe ob Fenstergröße der Bildschirmgröße entspricht
                try:
                    import win32api
                    screen_width = win32api.GetSystemMetrics(0)
                    screen_height = win32api.GetSystemMetrics(1)
                    # Fenster ist maximiert wenn Größe nahezu Bildschirmgröße entspricht
                    is_maximized = (width >= screen_width - 10 and height >= screen_height - 10)
                except Exception:
                    is_maximized = False
            
            # Prozess-Informationen
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process_name = None
            executable_path = None
            
            try:
                process = psutil.Process(pid)
                process_name = process.name()
                executable_path = process.exe()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            
            return {
                'hwnd': hwnd,
                'title': title,
                'class_name': class_name,
                'pid': pid,
                'process_name': process_name,
                'executable_path': executable_path,
                'position': {
                    'left': left,
                    'top': top,
                    'right': right,
                    'bottom': bottom,
                    'width': width,
                    'height': height
                },
                'is_minimized': is_minimized,
                'is_maximized': is_maximized
            }
        
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Fenster-Informationen: {e}", exc_info=True)
            return {
                'hwnd': hwnd,
                'title': 'Unbekannt',
                'class_name': 'Unbekannt',
                'pid': None,
                'process_name': None,
                'executable_path': None,
                'position': {
                    'left': 0,
                    'top': 0,
                    'right': 0,
                    'bottom': 0,
                    'width': 0,
                    'height': 0
                },
                'is_minimized': False,
                'is_maximized': False
            }
    
    def _is_system_window(self, window_info: Dict) -> bool:
        """
        Prüft ob es sich um ein System-Fenster handelt
        
        Args:
            window_info: Fenster-Informationen
            
        Returns:
            True wenn System-Fenster
        """
        title = window_info.get('title', '').lower()
        class_name = window_info.get('class_name', '').lower()
        
        # System-Fenster-Klassen
        system_classes = [
            'progman',  # Desktop
            'shell_traywnd',  # Taskbar
            'button',  # Start-Button
            'rebarwindow32',  # Taskbar-Toolbar
            'mstasklistwndclass',  # Task-Liste
            'shelldll_defview',  # Desktop-Ansicht
        ]
        
        if class_name in system_classes:
            return True
        
        # Leere Titel oder nur Leerzeichen
        if not title or title.strip() == '':
            return True
        
        # Spezielle System-Fenster-Titel
        if title in ['Program Manager', 'Desktop']:
            return True
        
        return False
    
    def group_by_process(self, windows: Optional[List[Dict]] = None) -> Dict[str, List[Dict]]:
        """
        Gruppiert Fenster nach Prozess
        
        Args:
            windows: Liste von Fenstern (None = verwendet self.windows)
            
        Returns:
            Dictionary gruppiert nach Prozessname
        """
        if windows is None:
            windows = self.windows
        
        grouped = defaultdict(list)
        
        for window in windows:
            process_name = window.get('process_name', 'Unbekannt')
            grouped[process_name].append(window)
        
        return dict(grouped)
    
    def get_window_by_hwnd(self, hwnd: int) -> Optional[Dict]:
        """
        Gibt Fenster-Informationen für ein bestimmtes Handle zurück
        
        Args:
            hwnd: Window Handle
            
        Returns:
            Fenster-Informationen oder None
        """
        return self._get_window_info(hwnd)
    
    def refresh(self) -> List[Dict]:
        """
        Aktualisiert die Liste der Fenster
        
        Returns:
            Aktualisierte Liste von Fenstern
        """
        return self.discover_all_windows()

