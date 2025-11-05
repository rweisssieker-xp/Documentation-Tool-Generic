"""
Automatischer Handbuch-Generator (AHG)
Entry-Point der Anwendung
"""

import sys
import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

# Lade Environment-Variablen
load_dotenv()

# Füge src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Setup Logging
from src.utils.logger import setup_logging, get_logger
setup_logging()

logger = get_logger(__name__)

from src.gui.main_window import MainWindow
from src.utils.cleanup_manager import CleanupManager
from src.utils.startup_validator import StartupValidator
import tkinter as tk


def validate_startup() -> bool:
    """
    Validiert die Umgebung beim Start
    
    Returns:
        True wenn Validierung erfolgreich, False bei kritischen Fehlern
    """
    validator = StartupValidator()
    is_valid, errors, warnings = validator.validate_all()
    
    if errors:
        logger.error("Kritische Fehler bei Startup-Validierung:")
        for error in errors:
            logger.error(f"  • {error}")
        logger.error("Bitte beheben Sie die Fehler bevor Sie fortfahren.")
        return False
    
    if warnings:
        logger.warning("Warnungen bei Startup-Validierung:")
        for warning in warnings:
            logger.warning(f"  • {warning}")
    
    return True


def run_cleanup_on_startup():
    """Führt automatische Bereinigung beim Start aus"""
    try:
        # Lade Cleanup-Konfiguration
        cleanup_config_path = Path("config") / "cleanup_config.yml"
        retention_days_screenshots = 30
        retention_days_sessions = 90
        auto_cleanup_enabled = True
        
        if cleanup_config_path.exists():
            try:
                with open(cleanup_config_path, 'r', encoding='utf-8') as f:
                    cleanup_config = yaml.safe_load(f)
                    if cleanup_config:
                        retention_days_screenshots = cleanup_config.get('retention_days_screenshots', 30)
                        retention_days_sessions = cleanup_config.get('retention_days_sessions', 90)
                        auto_cleanup_enabled = cleanup_config.get('auto_cleanup_enabled', True)
            except Exception as e:
                logger.warning(f"Fehler beim Laden der Cleanup-Konfiguration: {e}")
        
        if auto_cleanup_enabled:
            cleanup_manager = CleanupManager(
                retention_days_screenshots=retention_days_screenshots,
                retention_days_sessions=retention_days_sessions
            )
            stats = cleanup_manager.cleanup_all(dry_run=False)
            
            screenshots_stats = stats.get('screenshots', {})
            sessions_stats = stats.get('sessions', {})
            
            total_deleted = screenshots_stats.get('deleted_count', 0) + sessions_stats.get('deleted_count', 0)
            if total_deleted > 0:
                logger.info(
                    f"Automatische Bereinigung abgeschlossen: "
                    f"{screenshots_stats.get('deleted_count', 0)} Screenshots, "
                    f"{sessions_stats.get('deleted_count', 0)} Sessions gelöscht"
                )
            else:
                logger.debug("Keine alten Dateien zum Löschen gefunden")
        else:
            logger.debug("Automatische Bereinigung ist deaktiviert")
    
    except Exception as e:
        logger.error(f"Fehler bei der automatischen Bereinigung: {e}", exc_info=True)


def main():
    """Hauptfunktion - Startet die GUI-Anwendung"""
    logger.info("Starte Automatischer Handbuch-Generator (AHG)")
    
    # Validiere Startup-Umgebung
    if not validate_startup():
        print("\n❌ Startup-Validierung fehlgeschlagen!")
        print("Bitte beheben Sie die oben genannten Fehler.")
        print("\nSie können die Validierung auch manuell ausführen:")
        print("  python scripts/validate_startup.py")
        sys.exit(1)
    
    # Erstelle notwendige Verzeichnisse
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    (data_dir / "sessions").mkdir(exist_ok=True)
    (data_dir / "screenshots").mkdir(exist_ok=True)
    (data_dir / "output").mkdir(exist_ok=True)
    
    # Erstelle Config-Verzeichnis falls nicht vorhanden
    config_dir = Path("config") / "prompt_profiles"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Führe automatische Bereinigung beim Start aus
    run_cleanup_on_startup()
    
    logger.info("GUI wird gestartet...")
    
    # Starte GUI
    try:
        root = tk.Tk()
        app = MainWindow(root)
        root.mainloop()
    except Exception as e:
        logger.critical(f"Kritischer Fehler beim Starten der GUI: {e}", exc_info=True)
        print(f"\n❌ Kritischer Fehler: {e}")
        print("Bitte überprüfen Sie die Log-Datei in logs/ahg.log für Details.")
        sys.exit(1)


if __name__ == "__main__":
    main()

