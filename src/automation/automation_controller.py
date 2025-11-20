"""
Automation Controller: Verwaltet pywinauto-Connection zur gewählten App
"""

from typing import List, Dict, Optional, Tuple
import time
import win32gui

try:
    from pywinauto import Application
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False

from src.utils.logger import get_logger

logger = get_logger(__name__)


class AutomationController:
    """Verwaltet pywinauto-Connection zur gewählten App"""
    
    def __init__(self, hwnd: int):
        """
        Initialisiert den Automation Controller
        
        Args:
            hwnd: Window Handle der zu automatisierenden App
        """
        if not PYWINAUTO_AVAILABLE:
            raise ImportError("pywinauto ist nicht verfügbar. Bitte installieren Sie es mit: pip install pywinauto")
        
        self.hwnd = hwnd
        self.app = None
        self.window = None
        
        # Verbinde zur App
        try:
            self.app = Application().connect(handle=hwnd)
            self.window = self.app.window(handle=hwnd)
            logger.info(f"Verbunden mit App (HWND: {hwnd})")
        except Exception as e:
            logger.error(f"Fehler beim Verbinden mit App: {e}", exc_info=True)
            raise
    
    def click_element(self, x: int, y: int) -> bool:
        """
        Klickt auf ein Element an den gegebenen Koordinaten
        
        Args:
            x: X-Koordinate
            y: Y-Koordinate
            
        Returns:
            True wenn erfolgreich
        """
        try:
            # Stelle sicher dass Fenster aktiv ist
            win32gui.SetForegroundWindow(self.hwnd)
            time.sleep(0.2)
            
            # Klicke auf Koordinaten
            self.window.click_input(coords=(x, y))
            logger.debug(f"Geklickt auf ({x}, {y})")
            return True
        
        except Exception as e:
            logger.error(f"Fehler beim Klicken auf ({x}, {y}): {e}", exc_info=True)
            return False
    
    def click_element_by_text(self, text: str, exact: bool = False) -> bool:
        """
        Klickt auf ein Element anhand des Textes
        
        Args:
            text: Text des Elements
            exact: Ob exakte Übereinstimmung erforderlich ist
            
        Returns:
            True wenn erfolgreich
        """
        try:
            # Stelle sicher dass Fenster aktiv ist
            win32gui.SetForegroundWindow(self.hwnd)
            time.sleep(0.2)
            
            # Finde Element
            if exact:
                element = self.window.child_window(title=text)
            else:
                element = self.window.child_window(title_re=text)
            
            if element.exists():
                element.click_input()
                logger.debug(f"Geklickt auf Element mit Text: {text}")
                return True
            else:
                logger.warning(f"Element mit Text '{text}' nicht gefunden")
                return False
        
        except Exception as e:
            logger.error(f"Fehler beim Klicken auf Element '{text}': {e}", exc_info=True)
            return False
    
    def find_clickable_elements(self) -> List[Dict]:
        """
        Findet alle klickbaren Elemente im Fenster
        
        Returns:
            Liste von Element-Informationen
        """
        elements = []
        
        try:
            # Finde alle Buttons
            buttons = self.window.descendants(control_type="Button")
            for button in buttons:
                try:
                    rect = button.rectangle()
                    elements.append({
                        'type': 'button',
                        'text': button.window_text(),
                        'x': (rect.left + rect.right) // 2,
                        'y': (rect.top + rect.bottom) // 2,
                        'bbox': {
                            'left': rect.left,
                            'top': rect.top,
                            'right': rect.right,
                            'bottom': rect.bottom
                        }
                    })
                except Exception:
                    continue
            
            # Finde Menü-Items
            menu_items = self.window.descendants(control_type="MenuItem")
            for item in menu_items:
                try:
                    rect = item.rectangle()
                    elements.append({
                        'type': 'menu_item',
                        'text': item.window_text(),
                        'x': (rect.left + rect.right) // 2,
                        'y': (rect.top + rect.bottom) // 2,
                        'bbox': {
                            'left': rect.left,
                            'top': rect.top,
                            'right': rect.right,
                            'bottom': rect.bottom
                        }
                    })
                except Exception:
                    continue
            
            logger.info(f"{len(elements)} klickbare Elemente gefunden")
        
        except Exception as e:
            logger.error(f"Fehler beim Finden von Elementen: {e}", exc_info=True)
        
        return elements
    
    def get_window_info(self) -> Dict:
        """
        Gibt aktuellen Fenster-Zustand zurück
        
        Returns:
            Fenster-Informationen
        """
        try:
            rect = self.window.rectangle()
            return {
                'hwnd': self.hwnd,
                'title': self.window.window_text(),
                'position': {
                    'left': rect.left,
                    'top': rect.top,
                    'right': rect.right,
                    'bottom': rect.bottom,
                    'width': rect.width(),
                    'height': rect.height()
                },
                'is_minimized': self.window.is_minimized(),
                'is_maximized': self.window.is_maximized()
            }
        
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Fenster-Informationen: {e}", exc_info=True)
            return {
                'hwnd': self.hwnd,
                'title': 'Unbekannt',
                'position': {'left': 0, 'top': 0, 'right': 0, 'bottom': 0, 'width': 0, 'height': 0},
                'is_minimized': False,
                'is_maximized': False
            }
    
    def wait_for_stable(self, timeout: float = 3.0, check_interval: float = 0.5) -> bool:
        """
        Wartet bis UI stabil ist (keine Änderungen mehr)
        
        Args:
            timeout: Maximale Wartezeit in Sekunden
            check_interval: Interval zwischen Prüfungen
            
        Returns:
            True wenn UI stabil ist
        """
        start_time = time.time()
        last_title = self.window.window_text()
        last_rect = self.window.rectangle()
        
        while time.time() - start_time < timeout:
            time.sleep(check_interval)
            
            try:
                current_title = self.window.window_text()
                current_rect = self.window.rectangle()
                
                # Prüfe ob sich Titel oder Größe geändert haben
                if (current_title != last_title or 
                    current_rect.width() != last_rect.width() or
                    current_rect.height() != last_rect.height()):
                    last_title = current_title
                    last_rect = current_rect
                    start_time = time.time()  # Reset timer
                    continue
                
                # UI ist stabil
                return True
            
            except Exception:
                # Fenster existiert möglicherweise nicht mehr
                return False
        
        # Timeout erreicht
        return False
    
    def close(self):
        """Schließt die Verbindung"""
        self.app = None
        self.window = None

