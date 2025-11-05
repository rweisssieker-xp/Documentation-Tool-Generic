"""
Startup-Validierung als Standalone-Script
"""

if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Füge src-Verzeichnis zum Python-Pfad hinzu
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
    
    from src.utils.startup_validator import StartupValidator
    
    validator = StartupValidator()
    is_valid = validator.print_summary()
    
    sys.exit(0 if is_valid else 1)

