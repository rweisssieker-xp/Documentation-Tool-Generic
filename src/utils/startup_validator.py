"""
Startup-Validierung für die Anwendung
"""

from pathlib import Path
from typing import List, Tuple
import sys
import os

# Füge src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.logger import get_logger

logger = get_logger(__name__)


class StartupValidator:
    """Validiert die Umgebung beim Start"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """
        Führt alle Validierungen durch
        
        Returns:
            Tuple (is_valid, errors, warnings)
        """
        self.errors.clear()
        self.warnings.clear()
        
        # Python-Version prüfen
        self._validate_python_version()
        
        # Verzeichnisse prüfen/erstellen
        self._validate_directories()
        
        # Dependencies prüfen
        self._validate_dependencies()
        
        # Config-Dateien prüfen
        self._validate_config_files()
        
        # Environment-Variablen prüfen
        self._validate_environment()
        
        # Externe Tools prüfen
        self._validate_external_tools()
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _validate_python_version(self):
        """Prüft Python-Version"""
        if sys.version_info < (3, 10):
            self.errors.append(
                f"Python 3.10+ erforderlich, aktuell: {sys.version_info.major}.{sys.version_info.minor}"
            )
    
    def _validate_directories(self):
        """Prüft und erstellt notwendige Verzeichnisse"""
        required_dirs = [
            Path("data"),
            Path("data/sessions"),
            Path("data/screenshots"),
            Path("data/output"),
            Path("config"),
            Path("config/prompt_profiles"),
            Path("config/document_templates"),
            Path("logs")
        ]
        
        for dir_path in required_dirs:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.errors.append(f"Konnte Verzeichnis nicht erstellen {dir_path}: {e}")
    
    def _validate_dependencies(self):
        """Prüft wichtige Python-Dependencies"""
        required_modules = [
            ('tkinter', 'GUI-Framework'),
            ('PIL', 'Pillow'),
            ('yaml', 'PyYAML'),
            ('openai', 'OpenAI SDK'),
            ('docx', 'python-docx'),
            ('win32gui', 'pywin32'),
        ]
        
        for module_name, description in required_modules:
            try:
                __import__(module_name)
            except ImportError:
                self.errors.append(f"Fehlendes Modul: {module_name} ({description})")
    
    def _validate_config_files(self):
        """Prüft Config-Dateien"""
        # Prompt-Profile prüfen
        profiles_dir = Path("config/prompt_profiles")
        if profiles_dir.exists():
            profiles = list(profiles_dir.glob("*.yml"))
            if not profiles:
                self.warnings.append("Keine Prompt-Profile gefunden in config/prompt_profiles/")
        else:
            self.warnings.append("Prompt-Profile-Verzeichnis nicht gefunden")
        
        # Template-Verzeichnis prüfen
        templates_dir = Path("config/document_templates")
        if not templates_dir.exists():
            self.warnings.append("Document-Templates-Verzeichnis nicht gefunden")
    
    def _validate_environment(self):
        """Prüft Environment-Variablen"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your_openai_api_key_here':
            self.warnings.append(
                "OPENAI_API_KEY nicht gesetzt oder ungültig. "
                "Bitte konfigurieren Sie den API-Key in .env oder als Umgebungsvariable."
            )
        
        # Tesseract ist optional, daher nur Warnung
        tesseract_cmd = os.getenv('TESSERACT_CMD')
        if not tesseract_cmd:
            self.warnings.append(
                "TESSERACT_CMD nicht gesetzt. OCR-Funktionalität ist möglicherweise nicht verfügbar."
            )
    
    def _validate_external_tools(self):
        """Prüft externe Tools"""
        # Tesseract OCR prüfen
        try:
            from src.capture.ocr_engine import OCREngine
            ocr = OCREngine()
            if not ocr.is_available():
                self.warnings.append("Tesseract OCR nicht verfügbar. OCR-Funktionalität ist deaktiviert.")
        except Exception as e:
            self.warnings.append(f"Fehler beim Prüfen von Tesseract OCR: {e}")
    
    def print_summary(self):
        """Gibt eine Zusammenfassung aus"""
        is_valid, errors, warnings = self.validate_all()
        
        print("=" * 60)
        print("AHG Startup-Validierung")
        print("=" * 60)
        
        if errors:
            print(f"\n❌ FEHLER ({len(errors)}):")
            for error in errors:
                print(f"   • {error}")
        
        if warnings:
            print(f"\n⚠️  WARNUNGEN ({len(warnings)}):")
            for warning in warnings:
                print(f"   • {warning}")
        
        if not errors and not warnings:
            print("\n✅ Alle Validierungen erfolgreich!")
        
        print("=" * 60)
        
        return is_valid

