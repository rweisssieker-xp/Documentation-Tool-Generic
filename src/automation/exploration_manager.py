"""
Exploration Manager: Koordiniert die gesamte Erkundung
"""

import time
from typing import Optional, Dict, Callable, List
from pathlib import Path

from src.automation.automation_controller import AutomationController
from src.automation.element_discovery import ElementDiscovery
from src.automation.exploration_strategy import ExplorationStrategy, ExplorationStrategyType
from src.automation.navigation_state import NavigationState
from src.capture.screenshot import ScreenshotCapture
from src.monitor.session_manager import SessionManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ExplorationManager:
    """Koordiniert die gesamte Erkundung"""
    
    def __init__(
        self,
        automation_controller: AutomationController,
        session_manager: SessionManager,
        config: Optional[Dict] = None
    ):
        """
        Initialisiert Exploration Manager
        
        Args:
            automation_controller: Automation Controller Instanz
            session_manager: Session Manager Instanz
            config: Konfiguration (max_depth, max_steps, timeout, etc.)
        """
        self.controller = automation_controller
        self.session_manager = session_manager
        
        # Konfiguration
        self.config = config or {}
        self.max_depth = self.config.get('max_depth', 3)
        self.max_steps = self.config.get('max_steps', 1000)
        self.timeout_seconds = self.config.get('timeout_seconds', 3600)  # 1 Stunde default
        self.wait_between_clicks = self.config.get('wait_between_clicks', 2.0)
        self.ai_confidence_threshold = self.config.get('ai_confidence_threshold', 0.7)
        
        # Navigation State
        self.navigation_state = NavigationState(
            max_depth=self.max_depth,
            max_steps=self.max_steps
        )
        
        # Element Discovery
        self.element_discovery = ElementDiscovery(automation_controller)
        
        # Exploration Strategy
        strategy_type = ExplorationStrategyType(self.config.get('strategy', 'hybrid'))
        self.strategy = ExplorationStrategy(strategy_type)
        
        # Screenshot Capture
        self.screenshot_capture = ScreenshotCapture(
            output_dir=session_manager.screenshot_dir
        )
        
        # Status
        self.running = False
        self.paused = False
        self.start_time = None
        
        # Progress Callback
        self.progress_callback: Optional[Callable] = None
    
    def start(self, progress_callback: Optional[Callable] = None):
        """
        Startet die Erkundung
        
        Args:
            progress_callback: Callback-Funktion für Progress-Updates
        """
        if self.running:
            logger.warning("Erkundung läuft bereits")
            return
        
        self.running = True
        self.paused = False
        self.start_time = time.time()
        self.progress_callback = progress_callback
        
        logger.info("Starte automatische App-Erkundung")
        
        try:
            self._exploration_loop()
        except Exception as e:
            logger.error(f"Fehler bei Erkundung: {e}", exc_info=True)
            raise
        finally:
            self.running = False
    
    def stop(self):
        """Stoppt die Erkundung"""
        self.running = False
        logger.info("Erkundung gestoppt")
    
    def pause(self):
        """Pausiert die Erkundung"""
        self.paused = True
        logger.info("Erkundung pausiert")
    
    def resume(self):
        """Setzt Erkundung fort"""
        self.paused = False
        logger.info("Erkundung fortgesetzt")
    
    def _exploration_loop(self):
        """Hauptschleife für Erkundung"""
        while self.running and self.navigation_state.can_continue():
            # Prüfe Timeout
            if time.time() - self.start_time > self.timeout_seconds:
                logger.info(f"Timeout erreicht ({self.timeout_seconds} Sekunden)")
                break
            
            # Warte wenn pausiert
            while self.paused and self.running:
                time.sleep(0.5)
            
            if not self.running:
                break
            
            # Erstelle Screenshot
            screenshot_path = self._capture_screenshot()
            
            if not screenshot_path:
                logger.warning("Konnte Screenshot nicht erstellen")
                time.sleep(1.0)
                continue
            
            # Prüfe ob bereits besucht
            if not self.navigation_state.add_screenshot(screenshot_path):
                logger.debug("Screenshot bereits besucht, überspringe")
                # Versuche zurückzugehen oder nächstes Element zu finden
                if not self._try_next_element():
                    break
                continue
            
            # Finde nächste Aktion
            next_action = self._get_next_action(screenshot_path)
            
            if not next_action:
                logger.info("Keine weiteren Aktionen gefunden")
                break
            
            # Führe Aktion aus
            success = self._execute_action(next_action)
            
            if success:
                # Warte auf UI-Stabilisierung
                self.controller.wait_for_stable(timeout=self.wait_between_clicks)
                
                # Erstelle neuen Screenshot nach Aktion
                new_screenshot = self._capture_screenshot()
                if new_screenshot:
                    # Füge Schritt zum Session-Manager hinzu
                    window_info = self.controller.get_window_info()
                    self.session_manager._capture_step(window_info)
                
                # Increment Schritt
                self.navigation_state.increment_step()
                self.navigation_state.add_to_path(next_action)
                
                # Update Progress
                if self.progress_callback:
                    stats = self.navigation_state.get_statistics()
                    self.progress_callback(stats)
            
            # Kleine Pause zwischen Aktionen
            time.sleep(0.5)
        
        logger.info("Erkundung abgeschlossen")
        stats = self.navigation_state.get_statistics()
        logger.info(f"Statistiken: {stats}")
    
    def _capture_screenshot(self) -> Optional[Path]:
        """Erstellt Screenshot"""
        try:
            step_number = self.navigation_state.step_count + 1
            capture_result = self.screenshot_capture.capture_window(
                hwnd=self.controller.hwnd,
                step_number=step_number,
                session_id=self.session_manager.session_id
            )
            if capture_result:
                screenshot_path, _ = capture_result
                return screenshot_path
            return None
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Screenshots: {e}", exc_info=True)
            return None
    
    def _get_next_action(self, screenshot_path: Path) -> Optional[Dict]:
        """Bestimmt nächste Aktion"""
        try:
            # Verwende Strategy
            next_element = self.strategy.get_next_element(
                element_discovery=self.element_discovery,
                navigation_state=self.navigation_state,
                screenshot_path=str(screenshot_path)
            )
            
            return next_element
        
        except Exception as e:
            logger.error(f"Fehler beim Bestimmen der nächsten Aktion: {e}", exc_info=True)
            return None
    
    def _execute_action(self, action: Dict) -> bool:
        """Führt Aktion aus"""
        try:
            action_type = action.get('action', 'click')
            
            if action_type == 'click':
                x = action.get('x', 0)
                y = action.get('y', 0)
                
                if x > 0 and y > 0:
                    success = self.controller.click_element(x, y)
                    if success:
                        self.navigation_state.add_clicked_element(action)
                    return success
            
            elif action_type == 'navigate_menu':
                menu_path = action.get('menu_path', [])
                if menu_path:
                    # Navigiere durch Menü-Pfad
                    return self._navigate_menu_path(menu_path)
            
            elif action_type == 'back':
                # Gehe zurück
                self.navigation_state.decrement_depth()
                return True
            
            elif action_type == 'close_dialog':
                # Versuche Dialog zu schließen (ESC oder Close-Button)
                return self._close_dialog()
            
            return False
        
        except Exception as e:
            logger.error(f"Fehler beim Ausführen der Aktion: {e}", exc_info=True)
            return False
    
    def _navigate_menu_path(self, menu_path: List[str]) -> bool:
        """Navigiert durch Menü-Pfad"""
        try:
            for menu_item in menu_path:
                success = self.controller.click_element_by_text(menu_item)
                if not success:
                    return False
                time.sleep(0.5)
            
            self.navigation_state.increment_depth()
            return True
        
        except Exception as e:
            logger.error(f"Fehler bei Menü-Navigation: {e}", exc_info=True)
            return False
    
    def _close_dialog(self) -> bool:
        """Versucht Dialog zu schließen"""
        try:
            # Versuche ESC-Taste
            import win32api
            import win32con
            win32api.keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
            win32api.keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.5)
            return True
        except Exception as e:
            logger.debug(f"Fehler beim Schließen des Dialogs: {e}")
            return False
    
    def _try_next_element(self) -> bool:
        """Versucht nächstes Element zu finden"""
        try:
            elements = self.element_discovery.discover_all_elements()
            clicked_coords = {(e['x'], e['y']) for e in self.navigation_state.clicked_elements}
            
            for element in elements:
                if not element.get('visible', True) or not element.get('enabled', True):
                    continue
                
                coords = (element['x'], element['y'])
                if coords not in clicked_coords:
                    # Klicke auf dieses Element
                    return self.controller.click_element(element['x'], element['y'])
            
            return False
        
        except Exception as e:
            logger.error(f"Fehler beim Suchen nach nächstem Element: {e}", exc_info=True)
            return False
    
    def get_statistics(self) -> Dict:
        """Gibt aktuelle Statistiken zurück"""
        return self.navigation_state.get_statistics()

