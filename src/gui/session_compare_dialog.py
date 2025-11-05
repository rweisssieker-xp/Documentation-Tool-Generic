"""
Dialog für Session-Vergleich
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import List, Dict, Optional
import threading
import json

from src.document.session_comparator import SessionComparator
from src.monitor.session_manager import SessionManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SessionCompareDialog:
    """Dialog für Session-Vergleich"""
    
    def __init__(self, parent):
        """
        Initialisiert den Session-Vergleich Dialog
        
        Args:
            parent: Parent-Window
        """
        self.parent = parent
        self.comparator = SessionComparator()
        self.session1_steps = []
        self.session2_steps = []
        self.session1_id = None
        self.session2_id = None
        self.comparison_result = None
        
        # Erstelle Dialog-Fenster
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Session-Vergleich")
        self.dialog.geometry("900x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Zentriere Dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self._setup_ui()
        self._load_available_sessions()
    
    def _setup_ui(self):
        """Erstellt die UI-Komponenten"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Session-Auswahl
        selection_frame = ttk.LabelFrame(main_frame, text="Session-Auswahl", padding="10")
        selection_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Session 1
        session1_frame = ttk.Frame(selection_frame)
        session1_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(session1_frame, text="Session 1:").pack(side=tk.LEFT, padx=(0, 5))
        self.session1_var = tk.StringVar()
        self.session1_combo = ttk.Combobox(
            session1_frame,
            textvariable=self.session1_var,
            state="readonly",
            width=40
        )
        self.session1_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.session1_combo.bind("<<ComboboxSelected>>", self._on_session1_selected)
        
        ttk.Button(
            session1_frame,
            text="Laden",
            command=self._load_session1
        ).pack(side=tk.RIGHT)
        
        # Session 2
        session2_frame = ttk.Frame(selection_frame)
        session2_frame.pack(fill=tk.X)
        
        ttk.Label(session2_frame, text="Session 2:").pack(side=tk.LEFT, padx=(0, 5))
        self.session2_var = tk.StringVar()
        self.session2_combo = ttk.Combobox(
            session2_frame,
            textvariable=self.session2_var,
            state="readonly",
            width=40
        )
        self.session2_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.session2_combo.bind("<<ComboboxSelected>>", self._on_session2_selected)
        
        ttk.Button(
            session2_frame,
            text="Laden",
            command=self._load_session2
        ).pack(side=tk.RIGHT)
        
        # Vergleichs-Ergebnisse
        results_frame = ttk.LabelFrame(main_frame, text="Vergleichs-Ergebnisse", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Scrollbar für Ergebnisse
        scroll_frame = ttk.Frame(results_frame)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_text = tk.Text(
            scroll_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            yscrollcommand=scrollbar.set
        )
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_text.yview)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="Vergleichen",
            command=self._compare_sessions
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame,
            text="Diff-Dokument erstellen",
            command=self._generate_diff_document,
            state=tk.DISABLED
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.generate_diff_button = button_frame.winfo_children()[-1]
        
        ttk.Button(
            button_frame,
            text="Abbrechen",
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT)
    
    def _load_available_sessions(self):
        """Lädt verfügbare Sessions"""
        sessions_dir = Path("data") / "sessions"
        if not sessions_dir.exists():
            return
        
        session_list = []
        
        for session_dir in sessions_dir.iterdir():
            if not session_dir.is_dir():
                continue
            
            session_id = session_dir.name
            session_data_file = session_dir / "session_data.json"
            
            if session_data_file.exists():
                try:
                    with open(session_data_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    step_count = len(session_data.get('steps', []))
                    start_time = session_data.get('start_time', '')
                    
                    display_text = f"{session_id} ({step_count} Schritte, {start_time[:10]})"
                    session_list.append(display_text)
                    
                except Exception as e:
                    logger.warning(f"Fehler beim Laden der Session {session_id}: {e}")
                    continue
        
        self.session1_combo['values'] = session_list
        self.session2_combo['values'] = session_list
    
    def _on_session1_selected(self, event=None):
        """Wird aufgerufen wenn Session 1 ausgewählt wird"""
        selection = self.session1_var.get()
        if selection:
            # Extrahiere Session-ID
            self.session1_id = selection.split()[0]
    
    def _on_session2_selected(self, event=None):
        """Wird aufgerufen wenn Session 2 ausgewählt wird"""
        selection = self.session2_var.get()
        if selection:
            # Extrahiere Session-ID
            self.session2_id = selection.split()[0]
    
    def _load_session1(self):
        """Lädt Session 1"""
        if not self.session1_id:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie Session 1 aus.")
            return
        
        try:
            session_manager = SessionManager.restore_from_state(self.session1_id)
            if session_manager:
                self.session1_steps = session_manager.get_steps()
                self.results_text.config(state=tk.NORMAL)
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(1.0, f"Session 1 geladen: {len(self.session1_steps)} Schritte")
                self.results_text.config(state=tk.DISABLED)
            else:
                messagebox.showerror("Fehler", f"Konnte Session 1 nicht laden: {self.session1_id}")
        except Exception as e:
            logger.error(f"Fehler beim Laden von Session 1: {e}", exc_info=True)
            messagebox.showerror("Fehler", f"Fehler beim Laden:\n{str(e)}")
    
    def _load_session2(self):
        """Lädt Session 2"""
        if not self.session2_id:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie Session 2 aus.")
            return
        
        try:
            session_manager = SessionManager.restore_from_state(self.session2_id)
            if session_manager:
                self.session2_steps = session_manager.get_steps()
                self.results_text.config(state=tk.NORMAL)
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(1.0, f"Session 2 geladen: {len(self.session2_steps)} Schritte")
                self.results_text.config(state=tk.DISABLED)
            else:
                messagebox.showerror("Fehler", f"Konnte Session 2 nicht laden: {self.session2_id}")
        except Exception as e:
            logger.error(f"Fehler beim Laden von Session 2: {e}", exc_info=True)
            messagebox.showerror("Fehler", f"Fehler beim Laden:\n{str(e)}")
    
    def _compare_sessions(self):
        """Vergleicht die beiden Sessions"""
        if not self.session1_steps or not self.session2_steps:
            messagebox.showwarning("Fehler", "Bitte laden Sie beide Sessions.")
            return
        
        if not self.session1_id or not self.session2_id:
            messagebox.showwarning("Fehler", "Bitte wählen Sie beide Sessions aus.")
            return
        
        # Starte Vergleich in separatem Thread
        thread = threading.Thread(target=self._compare_thread, daemon=True)
        thread.start()
    
    def _compare_thread(self):
        """Vergleichs-Thread"""
        try:
            comparison = self.comparator.compare_sessions(
                session1_steps=self.session1_steps,
                session2_steps=self.session2_steps,
                session1_id=self.session1_id,
                session2_id=self.session2_id
            )
            
            self.comparison_result = comparison
            
            # Update UI im Hauptthread
            self.dialog.after(0, lambda: self._display_comparison(comparison))
        
        except Exception as e:
            logger.error(f"Fehler beim Session-Vergleich: {e}", exc_info=True)
            self.dialog.after(0, lambda: messagebox.showerror("Fehler", f"Vergleich fehlgeschlagen:\n{str(e)}"))
    
    def _display_comparison(self, comparison: Dict):
        """Zeigt Vergleichs-Ergebnisse an"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        lines = [
            "=" * 70,
            "SESSION-VERGLEICH",
            "=" * 70,
            "",
            f"Session 1: {comparison['session1_id']} ({comparison['session1_step_count']} Schritte)",
            f"Session 2: {comparison['session2_id']} ({comparison['session2_step_count']} Schritte)",
            "",
            f"Unterschiede gefunden: {len(comparison['differences']) + len(comparison['modified_steps'])}",
            f"Hinzugefügte Schritte: {len(comparison['added_steps'])}",
            f"Entfernte Schritte: {len(comparison['removed_steps'])}",
            f"Geänderte Schritte: {len(comparison['modified_steps'])}",
            "",
            "=" * 70,
            ""
        ]
        
        # Geänderte Schritte
        if comparison['modified_steps']:
            lines.append("GEÄNDERTE SCHRITTE:")
            lines.append("-" * 70)
            for mod_step in comparison['modified_steps']:
                step_num = mod_step['step_number']
                lines.append(f"\nSchritt {step_num}:")
                for diff in mod_step['differences']:
                    field = diff['field']
                    if field == 'description':
                        similarity = diff.get('similarity', 0)
                        lines.append(f"  - {field}: Ähnlichkeit {similarity:.1%}")
                    else:
                        lines.append(f"  - {field}: Unterschied erkannt")
            lines.append("")
        
        # Hinzugefügte Schritte
        if comparison['added_steps']:
            lines.append("HINZUGEFÜGTE SCHRITTE:")
            lines.append("-" * 70)
            for added in comparison['added_steps']:
                step_num = added['step_number']
                lines.append(f"  Schritt {step_num} (nur in {added['session']})")
            lines.append("")
        
        # Entfernte Schritte
        if comparison['removed_steps']:
            lines.append("ENTFERNTE SCHRITTE:")
            lines.append("-" * 70)
            for removed in comparison['removed_steps']:
                step_num = removed['step_number']
                lines.append(f"  Schritt {step_num} (nur in {removed['session']})")
            lines.append("")
        
        self.results_text.insert(1.0, "\n".join(lines))
        self.results_text.config(state=tk.DISABLED)
        
        # Aktiviere Diff-Dokument-Button
        self.generate_diff_button.config(state=tk.NORMAL)
    
    def _generate_diff_document(self):
        """Generiert Diff-Dokument"""
        if not self.comparison_result:
            messagebox.showwarning("Kein Vergleich", "Bitte führen Sie zuerst einen Vergleich durch.")
            return
        
        # Frage nach Ausgabe-Pfad
        output_path = filedialog.asksaveasfilename(
            defaultextension=".docx",
            filetypes=[("Word-Dokumente", "*.docx"), ("Alle Dateien", "*.*")],
            title="Diff-Dokument speichern"
        )
        
        if not output_path:
            return
        
        output_path = Path(output_path)
        
        # Starte Generierung in separatem Thread
        thread = threading.Thread(
            target=self._generate_diff_thread,
            args=(output_path,),
            daemon=True
        )
        thread.start()
    
    def _generate_diff_thread(self, output_path: Path):
        """Diff-Dokument-Generierungs-Thread"""
        try:
            result_path = self.comparator.generate_diff_document(
                comparison=self.comparison_result,
                output_path=output_path,
                session1_steps=self.session1_steps,
                session2_steps=self.session2_steps
            )
            
            # Update UI im Hauptthread
            self.dialog.after(0, lambda: self._diff_generated(result_path))
        
        except Exception as e:
            logger.error(f"Fehler bei Diff-Dokument-Generierung: {e}", exc_info=True)
            self.dialog.after(0, lambda: messagebox.showerror("Fehler", f"Generierung fehlgeschlagen:\n{str(e)}"))
    
    def _diff_generated(self, output_path: Path):
        """Wird aufgerufen wenn Diff-Dokument erstellt wurde"""
        messagebox.showinfo(
            "Erfolg",
            f"Diff-Dokument erfolgreich erstellt!\n\n{output_path}"
        )

