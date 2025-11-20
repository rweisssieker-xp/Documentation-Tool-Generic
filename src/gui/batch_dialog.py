"""
Dialog zur Batch-Verarbeitung mehrerer Sessions
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import json
import threading

from src.monitor.batch_processor import BatchProcessor
from src.monitor.session_manager import SessionManager
from src.monitor.session_recovery import SessionRecovery
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BatchDialog:
    """Dialog zur Batch-Verarbeitung mehrerer Sessions"""
    
    def __init__(self, parent):
        """
        Initialisiert den Batch-Dialog
        
        Args:
            parent: Parent-Window
        """
        self.parent = parent
        self.batch_processor = BatchProcessor()
        self.selected_sessions: List[str] = []
        self.all_sessions: List[Dict] = []
        self.export_formats = {
            'docx': True,
            'pdf': True,
            'markdown': False,
            'html': False,
            'json': True,
            'csv': False
        }
        self.processing = False
        
        # Erstelle Dialog-Fenster
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Batch-Verarbeitung")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Zentriere Dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self._setup_ui()
        self._load_sessions()
        
        # Update-Thread für Progress
        self.update_thread = None
        self.stop_updates = False
    
    def _setup_ui(self):
        """Erstellt die UI-Komponenten"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Info-Label
        info_label = ttk.Label(
            main_frame,
            text="Wählen Sie Sessions zur Batch-Verarbeitung:",
            font=("Arial", 10, "bold")
        )
        info_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Session-Liste mit Checkboxes
        list_frame = ttk.LabelFrame(main_frame, text="Verfügbare Sessions", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Scrollbar für Liste
        scroll_frame = ttk.Frame(list_frame)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas für Scrollable Frame
        canvas = tk.Canvas(scroll_frame, yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=canvas.yview)
        
        # Inner Frame für Checkboxes
        self.checkbox_frame = ttk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=self.checkbox_frame, anchor="nw")
        
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def configure_canvas_width(event):
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        self.checkbox_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_canvas_width)
        
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        
        # Buttons für Auswahl
        select_frame = ttk.Frame(main_frame)
        select_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(select_frame, text="Alle auswählen", command=self._select_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(select_frame, text="Alle abwählen", command=self._deselect_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(select_frame, text="Aktualisieren", command=self._load_sessions).pack(side=tk.LEFT)
        
        # Export-Formate
        format_frame = ttk.LabelFrame(main_frame, text="Export-Formate", padding="5")
        format_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.format_vars = {}
        formats_grid = ttk.Frame(format_frame)
        formats_grid.pack(fill=tk.X)
        
        formats = [
            ('docx', 'DOCX'),
            ('pdf', 'PDF'),
            ('markdown', 'Markdown'),
            ('html', 'HTML'),
            ('json', 'JSON (Audit)'),
            ('csv', 'CSV (Audit)')
        ]
        
        for i, (key, label) in enumerate(formats):
            var = tk.BooleanVar(value=self.export_formats.get(key, False))
            self.format_vars[key] = var
            ttk.Checkbutton(
                formats_grid,
                text=label,
                variable=var
            ).grid(row=i // 3, column=i % 3, sticky=tk.W, padx=5, pady=2)
        
        # Progress-Anzeige
        progress_frame = ttk.LabelFrame(main_frame, text="Fortschritt", padding="5")
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_var = tk.StringVar(value="Bereit")
        ttk.Label(progress_frame, textvariable=self.progress_var).pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            length=300
        )
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        
        # Ergebnis-Anzeige
        result_frame = ttk.LabelFrame(main_frame, text="Ergebnisse", padding="5")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        result_scroll = ttk.Scrollbar(result_frame)
        result_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.result_text = tk.Text(
            result_frame,
            height=8,
            wrap=tk.WORD,
            state=tk.DISABLED,
            yscrollcommand=result_scroll.set
        )
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        result_scroll.config(command=self.result_text.yview)
        
        # Button-Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self.start_button = ttk.Button(
            button_frame,
            text="Verarbeitung starten",
            command=self._start_processing
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(
            button_frame,
            text="Abbrechen",
            command=self._stop_processing,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame,
            text="Schließen",
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT)
        
        # Speichere Checkbox-Variablen
        self.checkbox_vars: Dict[str, tk.BooleanVar] = {}
    
    def _load_sessions(self):
        """Lädt verfügbare Sessions"""
        try:
            sessions_dir = Path("data") / "sessions"
            if not sessions_dir.exists():
                self._update_result("Kein Sessions-Verzeichnis gefunden.")
                return
            
            self.all_sessions = []
            self.checkbox_vars.clear()
            
            # Lösche alte Checkboxes
            for widget in self.checkbox_frame.winfo_children():
                widget.destroy()
            
            # Lade alle Sessions
            for session_dir in sessions_dir.iterdir():
                if not session_dir.is_dir():
                    continue
                
                session_id = session_dir.name
                session_data_file = session_dir / "session_data.json"
                
                if not session_data_file.exists():
                    continue
                
                try:
                    with open(session_data_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    step_count = len(session_data.get('steps', []))
                    start_time = session_data.get('start_time', '')
                    prompt_profile = session_data.get('prompt_profile', 'N/A')
                    status = 'Abgeschlossen' if session_data.get('end_time') else 'Abgebrochen'
                    
                    self.all_sessions.append({
                        'session_id': session_id,
                        'step_count': step_count,
                        'start_time': start_time,
                        'prompt_profile': prompt_profile,
                        'status': status,
                        'session_data': session_data
                    })
                    
                except Exception as e:
                    logger.warning(f"Fehler beim Laden der Session {session_id}: {e}")
                    continue
            
            # Sortiere nach Datum (neueste zuerst)
            self.all_sessions.sort(key=lambda x: x.get('start_time', ''), reverse=True)
            
            # Erstelle Checkboxes
            for session in self.all_sessions:
                var = tk.BooleanVar(value=False)
                self.checkbox_vars[session['session_id']] = var
                
                session_id = session['session_id']
                step_count = session['step_count']
                start_time = session['start_time']
                status = session['status']
                
                # Formatiere Zeit
                try:
                    if start_time:
                        dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                        time_str = dt.strftime('%d.%m.%Y %H:%M')
                    else:
                        time_str = 'Unbekannt'
                except:
                    time_str = start_time
                
                display_text = f"{session_id} | {time_str} | {step_count} Schritte | {status}"
                
                checkbox = ttk.Checkbutton(
                    self.checkbox_frame,
                    text=display_text,
                    variable=var
                )
                checkbox.pack(anchor=tk.W, pady=2)
            
            if not self.all_sessions:
                ttk.Label(
                    self.checkbox_frame,
                    text="Keine Sessions gefunden",
                    foreground="gray"
                ).pack(anchor=tk.W, pady=10)
            
            self._update_result(f"{len(self.all_sessions)} Sessions geladen.")
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der Sessions: {e}", exc_info=True)
            messagebox.showerror(
                "Fehler",
                f"Fehler beim Laden der Sessions:\n{str(e)}"
            )
    
    def _select_all(self):
        """Wählt alle Sessions aus"""
        for var in self.checkbox_vars.values():
            var.set(True)
    
    def _deselect_all(self):
        """Wählt alle Sessions ab"""
        for var in self.checkbox_vars.values():
            var.set(False)
    
    def _get_selected_sessions(self) -> List[str]:
        """Gibt die ausgewählten Session-IDs zurück"""
        selected = []
        for session_id, var in self.checkbox_vars.items():
            if var.get():
                selected.append(session_id)
        return selected
    
    def _start_processing(self):
        """Startet die Batch-Verarbeitung"""
        selected = self._get_selected_sessions()
        
        if not selected:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie mindestens eine Session aus.")
            return
        
        # Sammle Export-Formate
        self.export_formats = {key: var.get() for key, var in self.format_vars.items()}
        
        if not any(self.export_formats.values()):
            messagebox.showwarning("Keine Formate", "Bitte wählen Sie mindestens ein Export-Format aus.")
            return
        
        # Frage Bestätigung
        if not messagebox.askyesno(
            "Batch-Verarbeitung starten",
            f"Möchten Sie {len(selected)} Session(s) verarbeiten?\n\n"
            f"Export-Formate: {', '.join([k.upper() for k, v in self.export_formats.items() if v])}"
        ):
            return
        
        # Aktiviere/Deaktiviere Buttons
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.processing = True
        self.stop_updates = False
        
        # Starte Progress-Bar
        self.progress_bar.start()
        self.progress_var.set(f"Verarbeite {len(selected)} Session(s)...")
        
        # Leere Ergebnis-Text
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        
        # Lade Session-Manager für jede Session
        try:
            for session_id in selected:
                session_data = next(
                    (s['session_data'] for s in self.all_sessions if s['session_id'] == session_id),
                    None
                )
                
                if not session_data:
                    self._update_result(f"Fehler: Session {session_id} nicht gefunden.")
                    continue
                
                # Stelle Session wieder her
                try:
                    session_manager = SessionManager.restore_from_state(session_id)
                    if session_manager:
                        self.batch_processor.add_session(session_id, session_manager, self.export_formats)
                    else:
                        self._update_result(f"Fehler: Session {session_id} konnte nicht wiederhergestellt werden.")
                except Exception as e:
                    logger.error(f"Fehler beim Wiederherstellen der Session {session_id}: {e}", exc_info=True)
                    self._update_result(f"Fehler: {session_id} - {str(e)}")
            
            # Starte Verarbeitung
            self.batch_processor.process_all(progress_callback=self._on_progress_update)
            
            # Starte Update-Thread
            self.update_thread = threading.Thread(target=self._update_progress_loop, daemon=True)
            self.update_thread.start()
            
        except Exception as e:
            logger.error(f"Fehler beim Starten der Batch-Verarbeitung: {e}", exc_info=True)
            messagebox.showerror("Fehler", f"Fehler beim Starten:\n{str(e)}")
            self._stop_processing()
    
    def _stop_processing(self):
        """Stoppt die Batch-Verarbeitung"""
        self.stop_updates = True
        self.batch_processor.stop_processing()
        self.progress_bar.stop()
        self.processing = False
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_var.set("Verarbeitung abgebrochen")
    
    def _on_progress_update(self, progress_info: Dict):
        """Callback für Progress-Updates"""
        session_id = progress_info.get('session_id', '')
        status = progress_info.get('status', '')
        
        if status == 'processing':
            self.progress_var.set(f"Verarbeite: {session_id}...")
        elif status == 'completed':
            output_path = progress_info.get('output_path', '')
            self._update_result(f"✓ {session_id} erfolgreich verarbeitet\n   → {output_path}")
        elif status == 'failed':
            error = progress_info.get('error', 'Unbekannter Fehler')
            self._update_result(f"✗ {session_id} fehlgeschlagen: {error}")
    
    def _update_progress_loop(self):
        """Update-Loop für Progress-Anzeige"""
        while not self.stop_updates:
            try:
                progress = self.batch_processor.get_progress()
                
                if not progress.get('processing') and progress.get('queue_size', 0) == 0:
                    # Verarbeitung abgeschlossen
                    self.dialog.after(0, self._on_processing_complete, progress)
                    break
                
                completed = progress.get('completed_count', 0)
                failed = progress.get('failed_count', 0)
                total = completed + failed + progress.get('queue_size', 0)
                
                if total > 0:
                    status_text = f"Fortschritt: {completed} erfolgreich, {failed} fehlgeschlagen, {progress.get('queue_size', 0)} in Warteschlange"
                    self.dialog.after(0, lambda: self.progress_var.set(status_text))
                
                threading.Event().wait(1.0)
                
            except Exception as e:
                logger.error(f"Fehler im Progress-Update-Loop: {e}", exc_info=True)
                break
    
    def _on_processing_complete(self, progress: Dict):
        """Wird aufgerufen wenn Verarbeitung abgeschlossen ist"""
        self.progress_bar.stop()
        self.processing = False
        self.stop_updates = True
        
        completed = progress.get('completed_count', 0)
        failed = progress.get('failed_count', 0)
        
        self.progress_var.set(f"Abgeschlossen: {completed} erfolgreich, {failed} fehlgeschlagen")
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        # Zeige Zusammenfassung
        self._update_result(f"\n{'='*50}\n")
        self._update_result(f"Verarbeitung abgeschlossen:\n")
        self._update_result(f"  ✓ Erfolgreich: {completed}\n")
        self._update_result(f"  ✗ Fehlgeschlagen: {failed}\n")
        
        if completed > 0:
            messagebox.showinfo(
                "Batch-Verarbeitung abgeschlossen",
                f"Verarbeitung abgeschlossen!\n\n"
                f"Erfolgreich: {completed}\n"
                f"Fehlgeschlagen: {failed}"
            )
    
    def _update_result(self, text: str):
        """Aktualisiert den Ergebnis-Text"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.insert(tk.END, text + "\n")
        self.result_text.see(tk.END)
        self.result_text.config(state=tk.DISABLED)
        
        # Auto-Scroll
        self.dialog.update_idletasks()

