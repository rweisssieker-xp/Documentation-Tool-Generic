"""
Session-Wiederherstellung: Speichert und stellt Session-Zustand wieder her
"""

import json
import pickle
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SessionRecovery:
    """Verwaltet Session-Wiederherstellung nach Absturz"""
    
    def __init__(self, sessions_dir: Optional[Path] = None):
        """
        Initialisiert Session Recovery
        
        Args:
            sessions_dir: Verzeichnis für Session-Daten
        """
        if sessions_dir is None:
            sessions_dir = Path("data") / "sessions"
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
    
    def save_session_state(self, session_id: str, session_data: Dict) -> Path:
        """
        Speichert Session-Zustand
        
        Args:
            session_id: Session-ID
            session_data: Session-Daten (steps, metadata, etc.)
            
        Returns:
            Pfad zur gespeicherten State-Datei
        """
        try:
            state_file = self.sessions_dir / f"{session_id}_state.json"
            
            # Erstelle serialisierbares Dictionary
            serializable_data = {
                'session_id': session_data.get('session_id'),
                'prompt_profile': session_data.get('prompt_profile'),
                'start_time': session_data.get('start_time'),
                'steps': session_data.get('steps', []),
                'screenshot_dir': str(session_data.get('screenshot_dir', '')),
                'metadata': session_data.get('metadata', {}),
                'saved_at': datetime.now().isoformat()
            }
            
            # Speichere als JSON
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Session-Zustand gespeichert: {state_file}")
            return state_file
        
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Session-Zustands: {e}", exc_info=True)
            raise
    
    def list_recoverable_sessions(self) -> List[Dict]:
        """
        Listet alle wiederherstellbaren Sessions auf
        
        Returns:
            Liste von Session-Informationen
        """
        recoverable = []
        
        for state_file in self.sessions_dir.glob("*_state.json"):
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                
                session_id = state_data.get('session_id', state_file.stem.replace('_state', ''))
                
                # Prüfe ob Session abgeschlossen ist
                steps = state_data.get('steps', [])
                is_complete = len(steps) > 0 and state_data.get('metadata', {}).get('completed', False)
                
                recoverable.append({
                    'session_id': session_id,
                    'state_file': str(state_file),
                    'steps_count': len(steps),
                    'step_count': len(steps),  # Alias für Kompatibilität
                    'start_time': state_data.get('start_time'),
                    'saved_at': state_data.get('saved_at'),
                    'is_complete': is_complete,
                    'prompt_profile': state_data.get('prompt_profile'),
                    'active': state_data.get('metadata', {}).get('active', False)
                })
            
            except Exception as e:
                logger.warning(f"Fehler beim Lesen von {state_file}: {e}", exc_info=True)
        
        # Sortiere nach saved_at (neueste zuerst)
        recoverable.sort(key=lambda x: x.get('saved_at', ''), reverse=True)
        return recoverable
    
    def load_session_state(self, session_id: str) -> Optional[Dict]:
        """
        Lädt Session-Zustand
        
        Args:
            session_id: Session-ID
            
        Returns:
            Session-Daten oder None wenn nicht gefunden
        """
        state_file = self.sessions_dir / f"{session_id}_state.json"
        
        if not state_file.exists():
            logger.warning(f"Session-Zustand nicht gefunden: {state_file}")
            return None
        
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            # Konvertiere Pfade zurück zu Path-Objekten
            if 'screenshot_dir' in state_data:
                state_data['screenshot_dir'] = Path(state_data['screenshot_dir'])
            
            logger.info(f"Session-Zustand geladen: {session_id}")
            return state_data
        
        except Exception as e:
            logger.error(f"Fehler beim Laden des Session-Zustands: {e}", exc_info=True)
            return None
    
    def delete_session_state(self, session_id: str) -> bool:
        """
        Löscht Session-Zustand
        
        Args:
            session_id: Session-ID
            
        Returns:
            True wenn erfolgreich gelöscht
        """
        state_file = self.sessions_dir / f"{session_id}_state.json"
        
        try:
            if state_file.exists():
                state_file.unlink()
                logger.info(f"Session-Zustand gelöscht: {session_id}")
                return True
            return False
        
        except Exception as e:
            logger.error(f"Fehler beim Löschen des Session-Zustands: {e}", exc_info=True)
            return False
    
    def validate_session_state(self, session_id: str) -> tuple[bool, List[str]]:
        """
        Validiert Session-Zustand
        
        Args:
            session_id: Session-ID
            
        Returns:
            Tuple (is_valid, list_of_errors)
        """
        errors = []
        
        state_data = self.load_session_state(session_id)
        if not state_data:
            return False, ["Session-Zustand nicht gefunden"]
        
        # Prüfe erforderliche Felder
        required_fields = ['session_id', 'steps']
        for field in required_fields:
            if field not in state_data:
                errors.append(f"Fehlendes Feld: '{field}'")
        
        # Prüfe ob Screenshots vorhanden sind
        if 'screenshot_dir' in state_data:
            screenshot_dir = Path(state_data['screenshot_dir'])
            if screenshot_dir.exists():
                steps = state_data.get('steps', [])
                for step in steps:
                    screenshot_path = Path(step.get('screenshot_path', ''))
                    if screenshot_path and not screenshot_path.exists():
                        errors.append(f"Screenshot nicht gefunden: {screenshot_path}")
        
        return len(errors) == 0, errors

