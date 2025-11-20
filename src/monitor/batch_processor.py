"""
Batch-Processing für mehrere Sessions
"""

import threading
from queue import Queue
from typing import List, Dict, Optional, Callable
from pathlib import Path
from datetime import datetime
import time

from src.monitor.session_manager import SessionManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SessionQueue:
    """Queue-System für Session-Verarbeitung"""
    
    def __init__(self):
        """Initialisiert die Session-Queue"""
        self.queue = Queue()
        self.active_sessions: Dict[str, SessionManager] = {}
        self.completed_sessions: List[Dict] = []
        self.failed_sessions: List[Dict] = []
        self.lock = threading.Lock()
        
        # Processing-Status
        self.processing = False
        self.processing_thread = None
        self.progress_callback: Optional[Callable] = None
    
    def add_session(self, session_id: str, session_manager: SessionManager, export_formats: Optional[Dict[str, bool]] = None):
        """
        Fügt eine Session zur Queue hinzu
        
        Args:
            session_id: Eindeutige Session-ID
            session_manager: SessionManager-Instanz
            export_formats: Optional Export-Format-Optionen
        """
        with self.lock:
            self.queue.put({
                'session_id': session_id,
                'session_manager': session_manager,
                'export_formats': export_formats,
                'added_at': datetime.now()
            })
            self.active_sessions[session_id] = session_manager
    
    def start_processing(self, callback: Optional[Callable] = None):
        """
        Startet die Batch-Verarbeitung
        
        Args:
            callback: Callback-Funktion für Progress-Updates
        """
        if self.processing:
            return
        
        self.processing = True
        self.progress_callback = callback
        
        self.processing_thread = threading.Thread(
            target=self._process_queue,
            daemon=True
        )
        self.processing_thread.start()
    
    def stop_processing(self):
        """Stoppt die Batch-Verarbeitung"""
        self.processing = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5.0)
    
    def _process_queue(self):
        """Verarbeitet die Queue"""
        while self.processing or not self.queue.empty():
            try:
                if self.queue.empty():
                    time.sleep(0.5)
                    continue
                
                item = self.queue.get(timeout=1.0)
                session_id = item['session_id']
                session_manager = item['session_manager']
                export_formats = item.get('export_formats')
                
                # Update Progress
                if self.progress_callback:
                    self.progress_callback({
                        'session_id': session_id,
                        'status': 'processing',
                        'queue_size': self.queue.qsize()
                    })
                
                try:
                    # Generiere Dokumente für diese Session
                    from src.document.template_engine import TemplateEngine
                    
                    template_engine = TemplateEngine(session_manager)
                    output_path = template_engine.generate_document(export_formats=export_formats)
                    
                    # Markiere als erfolgreich
                    with self.lock:
                        self.completed_sessions.append({
                            'session_id': session_id,
                            'status': 'completed',
                            'output_path': str(output_path),
                            'completed_at': datetime.now().isoformat()
                        })
                        if session_id in self.active_sessions:
                            del self.active_sessions[session_id]
                    
                    # Update Progress
                    if self.progress_callback:
                        self.progress_callback({
                            'session_id': session_id,
                            'status': 'completed',
                            'output_path': str(output_path),
                            'queue_size': self.queue.qsize()
                        })
                
                except Exception as e:
                    # Markiere als fehlgeschlagen
                    with self.lock:
                        self.failed_sessions.append({
                            'session_id': session_id,
                            'status': 'failed',
                            'error': str(e),
                            'failed_at': datetime.now().isoformat()
                        })
                        if session_id in self.active_sessions:
                            del self.active_sessions[session_id]
                    
                    # Update Progress
                    if self.progress_callback:
                        self.progress_callback({
                            'session_id': session_id,
                            'status': 'failed',
                            'error': str(e),
                            'queue_size': self.queue.qsize()
                        })
                
                finally:
                    self.queue.task_done()
            
            except Exception as e:
                logger.error(f"Fehler in Queue-Verarbeitung: {e}", exc_info=True)
                time.sleep(1.0)
    
    def get_progress(self) -> Dict:
        """
        Gibt den aktuellen Verarbeitungs-Status zurück
        
        Returns:
            Dictionary mit Progress-Informationen
        """
        with self.lock:
            return {
                'queue_size': self.queue.qsize(),
                'active_count': len(self.active_sessions),
                'completed_count': len(self.completed_sessions),
                'failed_count': len(self.failed_sessions),
                'processing': self.processing,
                'completed_sessions': self.completed_sessions.copy(),
                'failed_sessions': self.failed_sessions.copy()
            }
    
    def clear(self):
        """Löscht alle Sessions aus der Queue"""
        with self.lock:
            while not self.queue.empty():
                try:
                    self.queue.get_nowait()
                except:
                    pass
            self.active_sessions.clear()
            self.completed_sessions.clear()
            self.failed_sessions.clear()


class BatchProcessor:
    """Verwaltet Batch-Processing mehrerer Sessions"""
    
    def __init__(self):
        """Initialisiert den Batch Processor"""
        self.session_queue = SessionQueue()
        self.max_concurrent = 1  # Standard: sequenziell, kann erhöht werden
    
    def add_session(self, session_id: str, session_manager: SessionManager, export_formats: Optional[Dict[str, bool]] = None):
        """
        Fügt eine Session zur Verarbeitung hinzu
        
        Args:
            session_id: Eindeutige Session-ID
            session_manager: SessionManager-Instanz
            export_formats: Optional Export-Format-Optionen
        """
        self.session_queue.add_session(session_id, session_manager, export_formats)
    
    def process_all(self, progress_callback: Optional[Callable] = None):
        """
        Startet die Verarbeitung aller Sessions
        
        Args:
            progress_callback: Callback-Funktion für Progress-Updates
        """
        self.session_queue.start_processing(progress_callback)
    
    def stop_processing(self):
        """Stoppt die Verarbeitung"""
        self.session_queue.stop_processing()
    
    def get_progress(self) -> Dict:
        """
        Gibt den aktuellen Progress zurück
        
        Returns:
            Dictionary mit Progress-Informationen
        """
        return self.session_queue.get_progress()
    
    def wait_for_completion(self, timeout: Optional[float] = None):
        """
        Wartet auf Abschluss der Verarbeitung
        
        Args:
            timeout: Timeout in Sekunden (None = unbegrenzt)
        """
        start_time = time.time()
        
        while self.session_queue.processing or not self.session_queue.queue.empty():
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError("Batch-Processing Timeout")
            time.sleep(0.5)

