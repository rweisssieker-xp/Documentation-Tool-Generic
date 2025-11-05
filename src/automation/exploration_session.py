"""
Exploration Session: Verwaltet eine automatische Erkundungs-Session
"""

from typing import Optional, Dict
from pathlib import Path

from src.automation.automation_controller import AutomationController
from src.automation.exploration_manager import ExplorationManager
from src.monitor.session_manager import SessionManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ExplorationSession:
    """Verwaltet eine automatische Erkundungs-Session"""
    
    def __init__(
        self,
        window_info: Dict,
        session_manager: SessionManager,
        config: Optional[Dict] = None
    ):
        """
        Initialisiert Exploration Session
        
        Args:
            window_info: Fenster-Informationen
            session_manager: Session Manager Instanz
            config: Konfiguration
        """
        self.window_info = window_info
        self.session_manager = session_manager
        self.config = config or {}
        
        # Automation Controller
        self.automation_controller = None
        self.exploration_manager = None
        
        # Status
        self.active = False
    
    def start(self, progress_callback=None):
        """
        Startet die Erkundungs-Session
        
        Args:
            progress_callback: Callback für Progress-Updates
        """
        if self.active:
            logger.warning("Erkundungs-Session läuft bereits")
            return
        
        try:
            # Erstelle Automation Controller
            hwnd = self.window_info['hwnd']
            self.automation_controller = AutomationController(hwnd)
            
            # Erstelle Exploration Manager
            self.exploration_manager = ExplorationManager(
                automation_controller=self.automation_controller,
                session_manager=self.session_manager,
                config=self.config
            )
            
            # Starte Erkundung
            self.active = True
            self.exploration_manager.start(progress_callback=progress_callback)
            
        except Exception as e:
            logger.error(f"Fehler beim Starten der Erkundungs-Session: {e}", exc_info=True)
            self.stop()
            raise
    
    def stop(self):
        """Stoppt die Erkundungs-Session"""
        if self.exploration_manager:
            self.exploration_manager.stop()
        
        if self.automation_controller:
            self.automation_controller.close()
        
        self.active = False
        logger.info("Erkundungs-Session gestoppt")
    
    def pause(self):
        """Pausiert die Erkundungs-Session"""
        if self.exploration_manager:
            self.exploration_manager.pause()
    
    def resume(self):
        """Setzt Erkundungs-Session fort"""
        if self.exploration_manager:
            self.exploration_manager.resume()
    
    def get_statistics(self) -> Dict:
        """Gibt Statistiken zurück"""
        if self.exploration_manager:
            return self.exploration_manager.get_statistics()
        return {}

