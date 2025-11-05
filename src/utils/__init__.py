"""
Logging-Konfiguration für die gesamte Anwendung
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional


class AppLogger:
    """Zentrales Logging-System für die Anwendung"""
    
    _initialized = False
    _loggers = {}
    
    @classmethod
    def setup_logging(
        cls,
        log_dir: Optional[Path] = None,
        log_level: int = logging.INFO,
        log_to_console: bool = True,
        log_to_file: bool = True,
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5
    ):
        """
        Konfiguriert das Logging-System
        
        Args:
            log_dir: Verzeichnis für Log-Dateien (None = logs/)
            log_level: Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_console: Ob Logs auf Konsole ausgegeben werden sollen
            log_to_file: Ob Logs in Dateien gespeichert werden sollen
            max_bytes: Maximale Größe einer Log-Datei vor Rotation
            backup_count: Anzahl der zu behaltenden Backup-Dateien
        """
        if cls._initialized:
            return
        
        if log_dir is None:
            log_dir = Path("logs")
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Root-Logger konfigurieren
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Entferne vorhandene Handler
        root_logger.handlers.clear()
        
        # Log-Format
        log_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console Handler
        if log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(log_format)
            root_logger.addHandler(console_handler)
        
        # File Handler mit Rotation
        if log_to_file:
            log_file = log_dir / "ahg.log"
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(log_format)
            root_logger.addHandler(file_handler)
            
            # Separate Error-Log-Datei
            error_file = log_dir / "ahg_errors.log"
            error_handler = logging.handlers.RotatingFileHandler(
                error_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(log_format)
            root_logger.addHandler(error_handler)
        
        cls._initialized = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Gibt einen Logger für das angegebene Modul zurück
        
        Args:
            name: Modul-Name (z.B. 'src.gui.main_window')
            
        Returns:
            Logger-Instanz
        """
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger
        
        return cls._loggers[name]


def setup_logging(**kwargs):
    """Kurze Funktion zum Setup des Logging-Systems"""
    AppLogger.setup_logging(**kwargs)


def get_logger(name: str) -> logging.Logger:
    """Kurze Funktion zum Abrufen eines Loggers"""
    return AppLogger.get_logger(name)

