"""
Export-Filter System: Filtert Schritte vor dem Export
"""

import re
from datetime import datetime
from typing import List, Dict, Optional, Callable
from pathlib import Path
import json

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ExportFilter:
    """Basis-Klasse für Export-Filter"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialisiert den Filter
        
        Args:
            config: Optional Filter-Konfiguration
        """
        self.config = config or {}
    
    def filter(self, steps: List[Dict]) -> List[Dict]:
        """
        Filtert Schritte
        
        Args:
            steps: Liste von Schritt-Dictionaries
            
        Returns:
            Gefilterte Liste von Schritten
        """
        return steps
    
    def matches(self, step: Dict) -> bool:
        """
        Prüft ob ein Schritt dem Filter entspricht
        
        Args:
            step: Schritt-Dictionary
            
        Returns:
            True wenn Schritt dem Filter entspricht
        """
        return True


class DateRangeFilter(ExportFilter):
    """Filter nach Datumsbereich"""
    
    def __init__(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
        """
        Initialisiert den Datums-Filter
        
        Args:
            start_date: Start-Datum (inclusive)
            end_date: End-Datum (inclusive)
        """
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
    
    def matches(self, step: Dict) -> bool:
        """Prüft ob Schritt im Datumsbereich liegt"""
        if not self.start_date and not self.end_date:
            return True
        
        try:
            step_timestamp = step.get('timestamp')
            if not step_timestamp:
                return False
            
            # Parse Timestamp
            if isinstance(step_timestamp, str):
                step_dt = datetime.fromisoformat(step_timestamp.replace('Z', '+00:00'))
            else:
                step_dt = step_timestamp
            
            # Prüfe Start-Datum
            if self.start_date and step_dt < self.start_date:
                return False
            
            # Prüfe End-Datum
            if self.end_date and step_dt > self.end_date:
                return False
            
            return True
        
        except Exception as e:
            logger.warning(f"Fehler beim Prüfen des Datums für Schritt: {e}")
            return False
    
    def filter(self, steps: List[Dict]) -> List[Dict]:
        """Filtert Schritte nach Datumsbereich"""
        return [step for step in steps if self.matches(step)]


class WindowTitleFilter(ExportFilter):
    """Filter nach Fenster-Titel (Regex-Support)"""
    
    def __init__(self, pattern: str, case_sensitive: bool = False, invert: bool = False):
        """
        Initialisiert den Fenster-Titel-Filter
        
        Args:
            pattern: Regex-Pattern oder einfacher String
            case_sensitive: Ob Groß-/Kleinschreibung beachtet werden soll
            invert: Ob Filter invertiert werden soll (alle außer Pattern)
        """
        super().__init__()
        self.pattern = pattern
        self.case_sensitive = case_sensitive
        self.invert = invert
        
        # Kompiliere Regex
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            self.regex = re.compile(pattern, flags)
        except re.error:
            # Falls kein gültiges Regex, verwende einfache String-Suche
            self.regex = None
    
    def matches(self, step: Dict) -> bool:
        """Prüft ob Schritt dem Fenster-Titel-Pattern entspricht"""
        window_title = step.get('window_title', '')
        
        if not window_title:
            return False if not self.invert else True
        
        if self.regex:
            match = self.regex.search(window_title)
        else:
            # Einfache String-Suche
            if self.case_sensitive:
                match = self.pattern in window_title
            else:
                match = self.pattern.lower() in window_title.lower()
        
        if self.invert:
            return not match
        
        return bool(match)
    
    def filter(self, steps: List[Dict]) -> List[Dict]:
        """Filtert Schritte nach Fenster-Titel"""
        return [step for step in steps if self.matches(step)]


class StepIndexFilter(ExportFilter):
    """Filter nach bestimmten Schritt-Indizes"""
    
    def __init__(self, indices: List[int], invert: bool = False):
        """
        Initialisiert den Schritt-Index-Filter
        
        Args:
            indices: Liste von Schritt-Indizes (1-basiert)
            invert: Ob Filter invertiert werden soll
        """
        super().__init__()
        self.indices = set(indices)
        self.invert = invert
    
    def matches(self, step: Dict) -> bool:
        """Prüft ob Schritt-Index in Liste enthalten ist"""
        step_number = step.get('step_number', 0)
        
        if self.invert:
            return step_number not in self.indices
        
        return step_number in self.indices
    
    def filter(self, steps: List[Dict]) -> List[Dict]:
        """Filtert Schritte nach Indizes"""
        filtered = [step for step in steps if self.matches(step)]
        
        # Aktualisiere Schritt-Nummern nach Filterung
        for i, step in enumerate(filtered, start=1):
            step['step_number'] = i
        
        return filtered


class SessionIDFilter(ExportFilter):
    """Filter nach Session-ID"""
    
    def __init__(self, session_ids: List[str], invert: bool = False):
        """
        Initialisiert den Session-ID-Filter
        
        Args:
            session_ids: Liste von Session-IDs
            invert: Ob Filter invertiert werden soll
        """
        super().__init__()
        self.session_ids = set(session_ids)
        self.invert = invert
    
    def matches(self, step: Dict) -> bool:
        """Prüft ob Schritt zur Session-ID gehört"""
        # Diese Methode ist für Session-Level-Filterung gedacht
        # Schritte haben normalerweise keine Session-ID direkt
        # Aber sie können aus Session-Kontext kommen
        return True  # Wird auf Session-Level angewendet
    
    def filter(self, steps: List[Dict]) -> List[Dict]:
        """Filtert Schritte (wird auf Session-Level verwendet)"""
        return steps


class CompositeFilter(ExportFilter):
    """Kombiniert mehrere Filter mit AND/OR Logik"""
    
    def __init__(self, filters: List[ExportFilter], logic: str = 'AND'):
        """
        Initialisiert den Composite-Filter
        
        Args:
            filters: Liste von Filtern
            logic: Logik ('AND' oder 'OR')
        """
        super().__init__()
        self.filters = filters
        self.logic = logic.upper()
        
        if self.logic not in ['AND', 'OR']:
            raise ValueError(f"Ungültige Logik: {logic}. Muss 'AND' oder 'OR' sein.")
    
    def matches(self, step: Dict) -> bool:
        """Prüft ob Schritt allen/einem Filter entspricht"""
        if not self.filters:
            return True
        
        if self.logic == 'AND':
            return all(f.matches(step) for f in self.filters)
        else:  # OR
            return any(f.matches(step) for f in self.filters)
    
    def filter(self, steps: List[Dict]) -> List[Dict]:
        """Filtert Schritte mit kombinierten Filtern"""
        if not self.filters:
            return steps
        
        if self.logic == 'AND':
            # Wende alle Filter sequenziell an
            filtered = steps
            for f in self.filters:
                filtered = f.filter(filtered)
            return filtered
        else:  # OR
            # Vereinige Ergebnisse aller Filter
            result_set = set()
            result_list = []
            for f in self.filters:
                for step in f.filter(steps):
                    # Verwende step_number als eindeutigen Identifier
                    step_id = step.get('step_number', id(step))
                    if step_id not in result_set:
                        result_set.add(step_id)
                        result_list.append(step)
            return result_list


class FilterManager:
    """Verwaltet Filter-Konfigurationen"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialisiert den Filter-Manager
        
        Args:
            config_path: Pfad zur Filter-Konfigurationsdatei
        """
        self.config_path = config_path or Path("config") / "export_filters.json"
        self.filters: Dict[str, ExportFilter] = {}
        self.load_config()
    
    def load_config(self):
        """Lädt Filter-Konfiguration aus Datei"""
        if not self.config_path.exists():
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Lade gespeicherte Filter
            saved_filters = config.get('filters', {})
            for name, filter_config in saved_filters.items():
                self.filters[name] = self._create_filter_from_config(filter_config)
        
        except Exception as e:
            logger.warning(f"Fehler beim Laden der Filter-Konfiguration: {e}", exc_info=True)
    
    def save_config(self):
        """Speichert Filter-Konfiguration in Datei"""
        try:
            config = {
                'filters': {}
            }
            
            for name, filter_obj in self.filters.items():
                config['filters'][name] = self._filter_to_config(filter_obj)
            
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Filter-Konfiguration: {e}", exc_info=True)
    
    def add_filter(self, name: str, filter_obj: ExportFilter):
        """
        Fügt einen Filter hinzu
        
        Args:
            name: Filter-Name
            filter_obj: Filter-Objekt
        """
        self.filters[name] = filter_obj
        self.save_config()
    
    def get_filter(self, name: str) -> Optional[ExportFilter]:
        """
        Holt einen Filter
        
        Args:
            name: Filter-Name
            
        Returns:
            Filter-Objekt oder None
        """
        return self.filters.get(name)
    
    def list_filters(self) -> List[str]:
        """Gibt Liste aller Filter-Namen zurück"""
        return list(self.filters.keys())
    
    def remove_filter(self, name: str):
        """Entfernt einen Filter"""
        if name in self.filters:
            del self.filters[name]
            self.save_config()
    
    def apply_filter(self, filter_name: str, steps: List[Dict]) -> List[Dict]:
        """
        Wendet einen Filter auf Schritte an
        
        Args:
            filter_name: Name des Filters
            steps: Liste von Schritten
            
        Returns:
            Gefilterte Schritte
        """
        filter_obj = self.get_filter(filter_name)
        if filter_obj:
            return filter_obj.filter(steps)
        return steps
    
    def _create_filter_from_config(self, config: Dict) -> ExportFilter:
        """Erstellt Filter aus Konfiguration"""
        filter_type = config.get('type')
        
        if filter_type == 'date_range':
            start_date = None
            end_date = None
            
            if config.get('start_date'):
                start_date = datetime.fromisoformat(config['start_date'])
            if config.get('end_date'):
                end_date = datetime.fromisoformat(config['end_date'])
            
            return DateRangeFilter(start_date, end_date)
        
        elif filter_type == 'window_title':
            return WindowTitleFilter(
                pattern=config.get('pattern', ''),
                case_sensitive=config.get('case_sensitive', False),
                invert=config.get('invert', False)
            )
        
        elif filter_type == 'step_index':
            return StepIndexFilter(
                indices=config.get('indices', []),
                invert=config.get('invert', False)
            )
        
        elif filter_type == 'session_id':
            return SessionIDFilter(
                session_ids=config.get('session_ids', []),
                invert=config.get('invert', False)
            )
        
        elif filter_type == 'composite':
            sub_filters = [
                self._create_filter_from_config(fc) for fc in config.get('filters', [])
            ]
            return CompositeFilter(
                filters=sub_filters,
                logic=config.get('logic', 'AND')
            )
        
        else:
            raise ValueError(f"Unbekannter Filter-Typ: {filter_type}")
    
    def _filter_to_config(self, filter_obj: ExportFilter) -> Dict:
        """Konvertiert Filter zu Konfiguration"""
        if isinstance(filter_obj, DateRangeFilter):
            return {
                'type': 'date_range',
                'start_date': filter_obj.start_date.isoformat() if filter_obj.start_date else None,
                'end_date': filter_obj.end_date.isoformat() if filter_obj.end_date else None
            }
        
        elif isinstance(filter_obj, WindowTitleFilter):
            return {
                'type': 'window_title',
                'pattern': filter_obj.pattern,
                'case_sensitive': filter_obj.case_sensitive,
                'invert': filter_obj.invert
            }
        
        elif isinstance(filter_obj, StepIndexFilter):
            return {
                'type': 'step_index',
                'indices': list(filter_obj.indices),
                'invert': filter_obj.invert
            }
        
        elif isinstance(filter_obj, SessionIDFilter):
            return {
                'type': 'session_id',
                'session_ids': list(filter_obj.session_ids),
                'invert': filter_obj.invert
            }
        
        elif isinstance(filter_obj, CompositeFilter):
            return {
                'type': 'composite',
                'logic': filter_obj.logic,
                'filters': [self._filter_to_config(f) for f in filter_obj.filters]
            }
        
        else:
            return {'type': 'unknown'}

