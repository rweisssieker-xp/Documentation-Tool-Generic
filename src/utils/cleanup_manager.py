"""
Automatische Bereinigung von alten Screenshots und Sessions
"""

import os
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime, timedelta
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CleanupManager:
    """Verwaltet automatische Bereinigung von alten Daten"""
    
    def __init__(
        self,
        screenshots_dir: Optional[Path] = None,
        sessions_dir: Optional[Path] = None,
        retention_days_screenshots: int = 30,
        retention_days_sessions: int = 90
    ):
        """
        Initialisiert den Cleanup Manager
        
        Args:
            screenshots_dir: Verzeichnis für Screenshots
            sessions_dir: Verzeichnis für Sessions
            retention_days_screenshots: Tage bis Screenshots gelöscht werden
            retention_days_sessions: Tage bis Sessions gelöscht werden
        """
        if screenshots_dir is None:
            screenshots_dir = Path("data") / "screenshots"
        self.screenshots_dir = Path(screenshots_dir)
        
        if sessions_dir is None:
            sessions_dir = Path("data") / "sessions"
        self.sessions_dir = Path(sessions_dir)
        
        self.retention_days_screenshots = retention_days_screenshots
        self.retention_days_sessions = retention_days_sessions
    
    def cleanup_old_screenshots(self, dry_run: bool = False) -> Dict[str, int]:
        """
        Bereinigt alte Screenshots
        
        Args:
            dry_run: Wenn True, werden keine Dateien gelöscht
            
        Returns:
            Dictionary mit Statistiken (deleted_count, total_size_deleted)
        """
        deleted_count = 0
        total_size = 0
        cutoff_date = datetime.now() - timedelta(days=self.retention_days_screenshots)
        
        if not self.screenshots_dir.exists():
            return {'deleted_count': 0, 'total_size_deleted': 0}
        
        for session_dir in self.screenshots_dir.iterdir():
            if not session_dir.is_dir():
                continue
            
            for screenshot_file in session_dir.glob("*.png"):
                try:
                    file_time = datetime.fromtimestamp(screenshot_file.stat().st_mtime)
                    
                    if file_time < cutoff_date:
                        file_size = screenshot_file.stat().st_size
                        
                        if not dry_run:
                            screenshot_file.unlink()
                            logger.debug(f"Gelöscht: {screenshot_file}")
                        
                        deleted_count += 1
                        total_size += file_size
                
                except Exception as e:
                    logger.warning(f"Fehler beim Löschen von {screenshot_file}: {e}", exc_info=True)
            
            # Lösche leere Session-Verzeichnisse
            try:
                if not any(session_dir.iterdir()):
                    if not dry_run:
                        session_dir.rmdir()
                        logger.debug(f"Leeres Verzeichnis gelöscht: {session_dir}")
            except Exception as e:
                logger.warning(f"Fehler beim Löschen von {session_dir}: {e}", exc_info=True)
        
        if deleted_count > 0:
            logger.info(f"Bereinigung Screenshots: {deleted_count} Dateien ({total_size / 1024 / 1024:.2f} MB)")
        else:
            logger.info("Keine alten Screenshots zum Löschen gefunden")
        
        return {'deleted_count': deleted_count, 'total_size_deleted': total_size}
    
    def cleanup_old_sessions(self, dry_run: bool = False) -> Dict[str, int]:
        """
        Bereinigt alte Sessions
        
        Args:
            dry_run: Wenn True, werden keine Dateien gelöscht
            
        Returns:
            Dictionary mit Statistiken (deleted_count, total_size_deleted)
        """
        deleted_count = 0
        total_size = 0
        cutoff_date = datetime.now() - timedelta(days=self.retention_days_sessions)
        
        if not self.sessions_dir.exists():
            return {'deleted_count': 0, 'total_size_deleted': 0}
        
        # Lösche alte State-Dateien
        for state_file in self.sessions_dir.glob("*_state.json"):
            try:
                file_time = datetime.fromtimestamp(state_file.stat().st_mtime)
                
                if file_time < cutoff_date:
                    file_size = state_file.stat().st_size
                    
                    if not dry_run:
                        state_file.unlink()
                        logger.debug(f"Gelöscht: {state_file}")
                    
                    deleted_count += 1
                    total_size += file_size
            
            except Exception as e:
                logger.warning(f"Fehler beim Löschen von {state_file}: {e}", exc_info=True)
        
        # Lösche alte Audit-Logs
        for audit_file in self.sessions_dir.glob("*.json"):
            if audit_file.name.endswith('_state.json'):
                continue
            
            try:
                file_time = datetime.fromtimestamp(audit_file.stat().st_mtime)
                
                if file_time < cutoff_date:
                    file_size = audit_file.stat().st_size
                    
                    if not dry_run:
                        audit_file.unlink()
                        logger.debug(f"Gelöscht: {audit_file}")
                    
                    deleted_count += 1
                    total_size += file_size
            
            except Exception as e:
                logger.warning(f"Fehler beim Löschen von {audit_file}: {e}", exc_info=True)
        
        if deleted_count > 0:
            logger.info(f"Bereinigung Sessions: {deleted_count} Dateien ({total_size / 1024 / 1024:.2f} MB)")
        else:
            logger.info("Keine alten Sessions zum Löschen gefunden")
        
        return {'deleted_count': deleted_count, 'total_size_deleted': total_size}
    
    def cleanup_all(self, dry_run: bool = False) -> Dict[str, Dict[str, int]]:
        """
        Bereinigt sowohl Screenshots als auch Sessions
        
        Args:
            dry_run: Wenn True, werden keine Dateien gelöscht
            
        Returns:
            Dictionary mit Statistiken für beide Bereiche
        """
        screenshots_stats = self.cleanup_old_screenshots(dry_run=dry_run)
        sessions_stats = self.cleanup_old_sessions(dry_run=dry_run)
        
        return {
            'screenshots': screenshots_stats,
            'sessions': sessions_stats
        }
    
    def get_cleanup_stats(self) -> Dict[str, Dict]:
        """
        Gibt Statistiken über zu bereinigende Dateien zurück (ohne zu löschen)
        
        Returns:
            Dictionary mit Statistiken
        """
        screenshots_stats = self.cleanup_old_screenshots(dry_run=True)
        sessions_stats = self.cleanup_old_sessions(dry_run=True)
        
        return {
            'screenshots': {
                **screenshots_stats,
                'retention_days': self.retention_days_screenshots
            },
            'sessions': {
                **sessions_stats,
                'retention_days': self.retention_days_sessions
            }
        }

