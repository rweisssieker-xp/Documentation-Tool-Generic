"""
Session-Manager: Verwaltet den Lifecycle einer Aufzeichnungssession
"""

import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import threading

from src.monitor.window_monitor import WindowMonitor
from src.monitor.action_detector import ActionDetector
from src.monitor.mouse_keyboard_monitor import MouseKeyboardMonitor
from src.capture.screenshot import ScreenshotCapture
from src.capture.privacy_mask import PrivacyMask
from src.capture.ocr_engine import OCREngine
from src.audit.audit_logger import AuditLogger
from src.config.trigger_config import TriggerConfig
from src.utils.logger import get_logger
from src.monitor.session_recovery import SessionRecovery

logger = get_logger(__name__)


class SessionManager:
    """Verwaltet eine Aufzeichnungssession"""
    
    def __init__(self, session_id: str, prompt_profile: str, output_dir: Optional[Path] = None):
        """
        Initialisiert den Session Manager
        
        Args:
            session_id: Eindeutige Session-ID
            prompt_profile: Name des Prompt-Profils
            output_dir: Ausgabeverzeichnis
        """
        self.session_id = session_id
        self.prompt_profile = prompt_profile
        
        if output_dir is None:
            output_dir = Path("data") / "sessions"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.screenshot_dir = Path("data") / "screenshots" / session_id
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Lade Trigger-Konfiguration
        trigger_config_path = Path("config") / "trigger_config.yml"
        trigger_config = TriggerConfig(trigger_config_path if trigger_config_path.exists() else None)
        
        # Komponenten
        self.window_monitor = WindowMonitor(callback=self._on_window_change, trigger_config=trigger_config)
        self.action_detector = ActionDetector(trigger_config=trigger_config)
        
        # Mouse/Keyboard Monitor
        self.mouse_keyboard_monitor = MouseKeyboardMonitor(
            mouse_callback=self._on_mouse_click,
            keyboard_callback=self._on_keyboard_input,
            trigger_config=trigger_config
        )
        
        # Privacy-Mask initialisieren
        privacy_mask_config = Path("config") / "privacy_mask.yml"
        privacy_mask = None
        if privacy_mask_config.exists():
            privacy_mask = PrivacyMask(privacy_mask_config, auto_detect_enabled=True)
        else:
            privacy_mask = PrivacyMask(auto_detect_enabled=True)
        
        # OCR-Engine für automatische Erkennung
        self.ocr_engine = OCREngine()
        
        self.screenshot_capture = ScreenshotCapture(self.screenshot_dir, privacy_mask=privacy_mask)
        self.audit_logger = AuditLogger(session_id, self.output_dir)
        
        # Session Recovery
        self.session_recovery = SessionRecovery(self.output_dir)
        
        # Session-Daten
        self.steps: List[Dict] = []
        self.active = False
        self.paused = False
        self.lock = threading.Lock()
        
        # Undo/Redo History
        self.history: List[List[Dict]] = []  # History-Stack für Undo
        self.redo_stack: List[List[Dict]] = []  # Redo-Stack
        self.max_history_size = 50  # Maximale Anzahl von History-Einträgen
        
        # Metadaten
        self.session_start_time = None
        self.session_end_time = None
    
    def pause(self):
        """Pausiert die Session"""
        if not self.active:
            return
        
        self.paused = True
        
        # Stoppe Monitoring temporär
        self.window_monitor.stop_monitoring()
        self.mouse_keyboard_monitor.stop_monitoring()
    
    def resume(self):
        """Setzt die Session fort"""
        if not self.active or not self.paused:
            return
        
        self.paused = False
        
        # Starte Monitoring wieder
        self.window_monitor.start_monitoring()
        self.mouse_keyboard_monitor.start_monitoring()
    
    def start(self):
        """Startet die Session"""
        if self.active:
            return
        
        self.active = True
        self.session_start_time = datetime.now()
        self.action_detector.reset()
        
        # Speichere Session-Zustand
        self._save_state()
        
        # Starte Monitoring
        self.window_monitor.start_monitoring()
        
        # Starte Mouse/Keyboard Monitoring
        self.mouse_keyboard_monitor.start_monitoring()
        
        # Erfasse ersten Screenshot
        self._capture_current_step()
    
    def stop(self):
        """Beendet die Session"""
        if not self.active:
            return
        
        self.active = False
        self.session_end_time = datetime.now()
        
        # Stoppe Monitoring
        self.window_monitor.stop_monitoring()
        self.mouse_keyboard_monitor.stop_monitoring()
        
        # Speichere finalen Session-Zustand
        self._save_state(final=True)
    
    def _on_window_change(self, window_info: Dict):
        """
        Callback bei Fensterwechsel
        
        Args:
            window_info: Fenster-Informationen
        """
        if not self.active or self.paused:
            return
        
        # Prüfe ob Änderung signifikant ist
        if self.action_detector.detect_change(window_info):
            self._capture_step(window_info)
    
    def _on_mouse_click(self, click_info: Dict):
        """
        Callback bei Mausklick
        
        Args:
            click_info: Mausklick-Informationen
        """
        if not self.active or self.paused:
            return
        
        # Bei Mausklick in neuem Fenster: Screenshot erstellen
        window_info = click_info.get('window_info', {})
        if window_info:
            # Prüfe ob sich das Fenster geändert hat
            if self.action_detector.detect_change(window_info):
                self._capture_step(window_info)
    
    def _on_keyboard_input(self, key_info: Dict):
        """
        Callback bei Tastatureingabe
        
        Args:
            key_info: Tastatur-Informationen
        """
        if not self.active or self.paused:
            return
        
        # Nur relevante Tasten für Dokumentation erfassen (Enter, Tab, Escape, etc.)
        important_keys = {'Enter', 'Tab', 'Escape', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'}
        key_name = key_info.get('key_name', '')
        
        # Wenn wichtige Taste gedrückt wurde, logge es für Kontext
        if key_name in important_keys:
            logger.debug(f"Wichtige Taste gedrückt: {key_name} in Fenster: {key_info.get('window_info', {}).get('title', 'Unbekannt')}")
            
            # Optional: Bei bestimmten Tasten (z.B. Enter) könnte ein Screenshot erstellt werden
            # Dies ist konfigurierbar, aktuell nur Logging
            if key_name == 'Enter':
                # Bei Enter könnte ein Screenshot sinnvoll sein (z.B. Formular-Absendung)
                window_info = key_info.get('window_info')
                if window_info:
                    self._capture_step(window_info)
    
    def _capture_current_step(self):
        """Erfasst einen Schritt für das aktuelle Fenster"""
        window_info = self.window_monitor.get_current_window()
        if window_info:
            self._capture_step(window_info)
    
    def _capture_step(self, window_info: Dict):
        """
        Erfasst einen Schritt mit Screenshot
        
        Args:
            window_info: Fenster-Informationen
        """
        try:
            step_number = len(self.steps) + 1
            
            # Performance-Messung: Start-Zeit für 100ms-Target
            capture_start_time = time.time()
            
            # Erstelle Screenshot mit Metadaten
            capture_result = self.screenshot_capture.capture_window(
                window_info.get('hwnd'),
                step_number,
                session_id=self.session_id
            )
            
            # Performance-Messung: Prüfe ob 100ms-Target eingehalten wurde
            capture_duration = (time.time() - capture_start_time) * 1000  # in ms
            if capture_duration > 100:
                logger.warning(f"Screenshot-Capture dauerte {capture_duration:.2f}ms (Target: 100ms) für Schritt {step_number}")
            else:
                logger.debug(f"Screenshot-Capture abgeschlossen in {capture_duration:.2f}ms für Schritt {step_number}")
            
            if not capture_result:
                logger.warning(f"Screenshot konnte nicht erstellt werden für Schritt {step_number}")
                return
            
            screenshot_path, screenshot_metadata = capture_result
            
            if not screenshot_path or not screenshot_path.exists():
                logger.warning(f"Screenshot konnte nicht erstellt werden für Schritt {step_number}")
                return
            
            # Extrahiere OCR-Text für automatische Privacy-Erkennung
            ocr_text = ""
            ocr_confidence = 0.0
            
            # Performance-Messung: Start-Zeit für 2s-Target
            ocr_start_time = time.time()
            
            if self.ocr_engine.is_available():
                try:
                    # OCR-Verarbeitung mit Timeout
                    ocr_text = self.ocr_engine.extract_text(screenshot_path, timeout=2.0)
                    
                    # Hole Konfidenz-Informationen wenn Text extrahiert wurde
                    if ocr_text:
                        ocr_result = self.ocr_engine.extract_text_with_confidence(screenshot_path, timeout=2.0)
                        ocr_confidence = ocr_result.get('confidence', 0.0)
                    
                    # Performance-Messung: Prüfe ob 2s-Target eingehalten wurde
                    ocr_duration = time.time() - ocr_start_time
                    if ocr_duration > 2.0:
                        logger.warning(f"OCR-Verarbeitung dauerte {ocr_duration:.2f}s (Target: 2.0s) für Schritt {step_number}")
                    else:
                        logger.debug(f"OCR-Verarbeitung abgeschlossen in {ocr_duration:.2f}s für Schritt {step_number}")
                    
                except Exception as e:
                    logger.warning(f"OCR-Fehler für Schritt {step_number}: {e}", exc_info=True)
                    ocr_text = ""
            else:
                logger.warning("Tesseract OCR nicht verfügbar. OCR-Text wird nicht extrahiert.")
            
            # Wende Privacy-Mask mit automatischer Erkennung an
            if self.screenshot_capture.privacy_mask and ocr_text:
                self.screenshot_capture.privacy_mask.apply_mask(screenshot_path, ocr_text=ocr_text)
            
            # Erstelle Schritt-Datenstruktur mit Screenshot-Metadaten
            step = {
                'step_number': step_number,
                'timestamp': screenshot_metadata.get('timestamp', datetime.now().isoformat()),
                'window_title': screenshot_metadata.get('window_title', window_info.get('title', 'Unbekannt')),
                'window_class': window_info.get('class_name', 'Unbekannt'),
                'process_name': window_info.get('process_name', 'Unbekannt'),
                'executable_path': window_info.get('executable_path'),
                'position': window_info.get('position', {}),
                'screenshot_path': str(screenshot_path),
                'screenshot_id': screenshot_metadata.get('screenshot_id'),  # UUID-Format
                'screenshot_metadata': screenshot_metadata,
                'ocr_text': ocr_text,  # OCR-Text wird asynchron aktualisiert
                'ocr_confidence': ocr_confidence,
                'metadata': window_info,
                'description': None  # Wird später durch AI generiert
            }
            
            # Protokolliere im Audit-Log
            self.audit_logger.log_step(step_number, screenshot_path, window_info)
            
            # Speichere Schritt
            with self.lock:
                # Speichere aktuellen Zustand für Undo
                self._save_history_state()
                self.steps.append(step)
            
            logger.info(f"Schritt {step_number} erfasst: {window_info.get('title', 'Unbekannt')}")
            
            # Speichere Session-Zustand nach jedem Schritt
            self._save_state()
        
        except Exception as e:
            logger.error(f"Fehler beim Erfassen des Schritts: {e}", exc_info=True)
    
    def get_steps(self) -> List[Dict]:
        """
        Gibt alle erfassten Schritte zurück
        
        Returns:
            Liste von Schritt-Dictionaries
        """
        with self.lock:
            return self.steps.copy()
    
    def get_step_count(self) -> int:
        """
        Gibt die Anzahl der erfassten Schritte zurück
        
        Returns:
            Anzahl der Schritte
        """
        with self.lock:
            return len(self.steps)
    
    def get_audit_logger(self) -> AuditLogger:
        """
        Gibt den Audit Logger zurück
        
        Returns:
            AuditLogger-Instanz
        """
        return self.audit_logger
    
    def get_session_info(self) -> Dict:
        """
        Gibt Session-Informationen zurück
        
        Returns:
            Dictionary mit Session-Info
        """
        duration = None
        if self.session_start_time:
            end_time = self.session_end_time if self.session_end_time else datetime.now()
            duration = (end_time - self.session_start_time).total_seconds()
        
        screenshot_count = sum(1 for step in self.steps if step.get('screenshot_path'))
        
        return {
            'session_id': self.session_id,
            'prompt_profile': self.prompt_profile,
            'start_time': self.session_start_time.isoformat() if self.session_start_time else None,
            'end_time': self.session_end_time.isoformat() if self.session_end_time else None,
            'duration_seconds': duration,
            'duration_formatted': self._format_duration(duration) if duration else None,
            'step_count': len(self.steps),
            'screenshot_count': screenshot_count,
            'active': self.active,
            'paused': self.paused
        }
    
    def get_session_statistics(self) -> Dict:
        """
        Gibt detaillierte Session-Statistiken zurück
        
        Returns:
            Dictionary mit detaillierten Statistiken
        """
        info = self.get_session_info()
        
        # Fenster-Statistiken
        window_titles = {}
        for step in self.steps:
            title = step.get('window_title', 'Unbekannt')
            window_titles[title] = window_titles.get(title, 0) + 1
        
        most_common_window = max(window_titles.items(), key=lambda x: x[1]) if window_titles else None
        
        # Prozess-Statistiken
        processes = {}
        for step in self.steps:
            process = step.get('process_name', 'Unbekannt')
            processes[process] = processes.get(process, 0) + 1
        
        most_common_process = max(processes.items(), key=lambda x: x[1]) if processes else None
        
        stats = {
            **info,
            'windows_used': len(window_titles),
            'most_common_window': most_common_window[0] if most_common_window else None,
            'most_common_window_count': most_common_window[1] if most_common_window else 0,
            'processes_used': len(processes),
            'most_common_process': most_common_process[0] if most_common_process else None,
            'most_common_process_count': most_common_process[1] if most_common_process else 0,
            'average_steps_per_minute': (
                (len(self.steps) / (info['duration_seconds'] / 60))
                if info['duration_seconds'] and info['duration_seconds'] > 0 else 0
            )
        }
        
        return stats
    
    def _format_duration(self, seconds: float) -> str:
        """
        Formatiert Dauer in lesbares Format
        
        Args:
            seconds: Dauer in Sekunden
            
        Returns:
            Formatierte Dauer (z.B. "1h 23m 45s")
        """
        if not seconds:
            return "0s"
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")
        
        return " ".join(parts)
    
    def _save_history_state(self):
        """Speichert aktuellen Zustand für Undo/Redo"""
        with self.lock:
            # Speichere Kopie des aktuellen Zustands
            state_copy = self.steps.copy()
            self.history.append(state_copy)
            
            # Begrenze History-Größe
            if len(self.history) > self.max_history_size:
                self.history.pop(0)
            
            # Leere Redo-Stack wenn neue Änderung gemacht wird
            self.redo_stack.clear()
    
    def undo(self) -> bool:
        """
        Macht den letzten Schritt rückgängig
        
        Returns:
            True wenn Undo erfolgreich war, False wenn keine History vorhanden
        """
        with self.lock:
            if not self.history or len(self.history) <= 1:
                logger.debug("Keine History für Undo vorhanden")
                return False
            
            # Speichere aktuellen Zustand für Redo
            self.redo_stack.append(self.steps.copy())
            
            # Stelle vorherigen Zustand wieder her
            self.history.pop()  # Entferne aktuellen Zustand
            previous_state = self.history[-1] if self.history else []
            self.steps = previous_state.copy()
            
            logger.info(f"Undo durchgeführt: {len(self.steps)} Schritte verbleibend")
            return True
    
    def redo(self) -> bool:
        """
        Stellt den letzten Undo wieder her
        
        Returns:
            True wenn Redo erfolgreich war, False wenn kein Redo verfügbar
        """
        with self.lock:
            if not self.redo_stack:
                logger.debug("Kein Redo verfügbar")
                return False
            
            # Speichere aktuellen Zustand für Undo
            self.history.append(self.steps.copy())
            
            # Stelle nächsten Zustand wieder her
            next_state = self.redo_stack.pop()
            self.steps = next_state.copy()
            
            logger.info(f"Redo durchgeführt: {len(self.steps)} Schritte")
            return True
    
    def can_undo(self) -> bool:
        """
        Prüft ob Undo möglich ist
        
        Returns:
            True wenn Undo möglich ist
        """
        with self.lock:
            return len(self.history) > 1
    
    def can_redo(self) -> bool:
        """
        Prüft ob Redo möglich ist
        
        Returns:
            True wenn Redo möglich ist
        """
        with self.lock:
            return len(self.redo_stack) > 0
    
    def _save_state(self, final: bool = False):
        """Speichert Session-Zustand"""
        try:
            session_data = {
                'session_id': self.session_id,
                'prompt_profile': self.prompt_profile,
                'start_time': self.session_start_time.isoformat() if self.session_start_time else None,
                'end_time': self.session_end_time.isoformat() if self.session_end_time else None,
                'steps': self.steps.copy(),
                'screenshot_dir': str(self.screenshot_dir),
                'metadata': {
                    'completed': final,
                    'paused': self.paused,
                    'active': self.active
                }
            }
            
            self.session_recovery.save_session_state(self.session_id, session_data)
        
        except Exception as e:
            logger.warning(f"Fehler beim Speichern des Session-Zustands: {e}", exc_info=True)
    
    @classmethod
    def restore_from_state(cls, session_id: str, output_dir: Optional[Path] = None) -> Optional['SessionManager']:
        """
        Stellt Session aus gespeichertem Zustand wieder her
        
        Args:
            session_id: Session-ID
            output_dir: Ausgabeverzeichnis
            
        Returns:
            SessionManager-Instanz oder None wenn Wiederherstellung fehlschlägt
        """
        try:
            recovery = SessionRecovery(output_dir)
            
            # Validiere Session-Zustand
            is_valid, errors = recovery.validate_session_state(session_id)
            if not is_valid:
                logger.error(f"Ungültiger Session-Zustand für {session_id}: {errors}")
                return None
            
            # Lade Session-Zustand
            state_data = recovery.load_session_state(session_id)
            if not state_data:
                return None
            
            # Erstelle neue SessionManager-Instanz
            session_manager = cls(
                session_id=state_data['session_id'],
                prompt_profile=state_data['prompt_profile'],
                output_dir=output_dir
            )
            
            # Stelle Zustand wieder her
            session_manager.steps = state_data.get('steps', [])
            
            if state_data.get('start_time'):
                session_manager.session_start_time = datetime.fromisoformat(state_data['start_time'])
            if state_data.get('end_time'):
                session_manager.session_end_time = datetime.fromisoformat(state_data['end_time'])
            
            metadata = state_data.get('metadata', {})
            session_manager.active = metadata.get('active', False)
            session_manager.paused = metadata.get('paused', False)
            
            logger.info(f"Session wiederhergestellt: {session_id}")
            return session_manager
        
        except Exception as e:
            logger.error(f"Fehler bei Session-Wiederherstellung: {e}", exc_info=True)
            return None

