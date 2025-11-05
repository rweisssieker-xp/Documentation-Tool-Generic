"""
Dialog zur Wiederherstellung von Sessions
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import datetime
from typing import Optional

from src.monitor.session_recovery import SessionRecovery
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SessionRecoveryDialog:
    """Dialog zur Auswahl und Wiederherstellung von Sessions"""
    
    def __init__(self, parent):
        """
        Initialisiert den Recovery-Dialog
        
        Args:
            parent: Parent-Window
        """
        self.parent = parent
        self.selected_session_id = None
        self.restored_session = None  # Wird gesetzt wenn Session wiederhergestellt wird
        
        # Erstelle Dialog-Fenster
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Session wiederherstellen")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Zentriere Dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self._setup_ui()
        self._load_recoverable_sessions()
    
    def _setup_ui(self):
        """Erstellt die UI-Komponenten"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Info-Label
        info_label = ttk.Label(
            main_frame,
            text="Wählen Sie eine Session zur Wiederherstellung:",
            font=("Arial", 10, "bold")
        )
        info_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Liste mit Scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.session_listbox = tk.Listbox(
            list_frame,
            font=("Arial", 9),
            yscrollcommand=scrollbar.set
        )
        self.session_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.session_listbox.yview)
        
        self.session_listbox.bind('<<ListboxSelect>>', self._on_session_select)
        
        # Details-Frame
        details_frame = ttk.LabelFrame(main_frame, text="Session-Details", padding="5")
        details_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.details_text = tk.Text(details_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
        self.details_text.pack(fill=tk.X)
        
        # Button-Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="Wiederherstellen",
            command=self._restore_session,
            state=tk.DISABLED
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.restore_button = button_frame.winfo_children()[0]
        
        ttk.Button(
            button_frame,
            text="Löschen",
            command=self._delete_session
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.delete_button = button_frame.winfo_children()[1]
        
        ttk.Button(
            button_frame,
            text="Abbrechen",
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT)
        
        # Speichere Session-Daten
        self.recoverable_sessions = []
    
    def _load_recoverable_sessions(self):
        """Lädt wiederherstellbare Sessions"""
        try:
            recovery = SessionRecovery()
            self.recoverable_sessions = recovery.list_recoverable_sessions()
            
            self.session_listbox.delete(0, tk.END)
            
            if not self.recoverable_sessions:
                self.session_listbox.insert(0, "Keine wiederherstellbaren Sessions gefunden")
                self.details_text.config(state=tk.NORMAL)
                self.details_text.delete(1.0, tk.END)
                self.details_text.insert(1.0, "Es wurden keine abgebrochenen Sessions gefunden.")
                self.details_text.config(state=tk.DISABLED)
            else:
                for session in self.recoverable_sessions:
                    session_id = session.get('session_id', 'Unbekannt')
                    saved_at = session.get('saved_at', 'Unbekannt')
                    step_count = session.get('steps_count', session.get('step_count', 0))
                    
                    display_text = f"{session_id} - {saved_at} ({step_count} Schritte)"
                    self.session_listbox.insert(tk.END, display_text)
        
        except Exception as e:
            logger.error(f"Fehler beim Laden wiederherstellbarer Sessions: {e}", exc_info=True)
            messagebox.showerror(
                "Fehler",
                f"Fehler beim Laden der Sessions:\n{str(e)}"
            )
    
    def _on_session_select(self, event):
        """Wird aufgerufen wenn eine Session ausgewählt wird"""
        selection = self.session_listbox.curselection()
        if not selection or not self.recoverable_sessions:
            self.restore_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)
            return
        
        index = selection[0]
        if index >= len(self.recoverable_sessions):
            return
        
        session = self.recoverable_sessions[index]
        self.selected_session_id = session.get('session_id')
        
        # Zeige Details
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        
        details_lines = [
            f"Session-ID: {session.get('session_id', 'N/A')}",
            f"Gespeichert am: {session.get('saved_at', 'N/A')}",
            f"Schritte: {session.get('steps_count', session.get('step_count', 0))}",
            f"Profil: {session.get('prompt_profile', 'N/A')}",
            f"Status: {'Abgeschlossen' if session.get('is_complete', False) else 'Abgebrochen'}",
        ]
        
        self.details_text.insert(1.0, "\n".join(details_lines))
        self.details_text.config(state=tk.DISABLED)
        
        # Aktiviere Buttons
        self.restore_button.config(state=tk.NORMAL)
        self.delete_button.config(state=tk.NORMAL)
    
    def _restore_session(self):
        """Stellt die ausgewählte Session wieder her"""
        if not self.selected_session_id:
            return
        
        try:
            from src.monitor.session_manager import SessionManager
            
            # Frage Bestätigung
            if not messagebox.askyesno(
                "Session wiederherstellen",
                f"Möchten Sie die Session '{self.selected_session_id}' wirklich wiederherstellen?\n"
                "Die aktuelle Session wird dabei beendet (falls aktiv)."
            ):
                return
            
            # Stelle Session wieder her
            session_manager = SessionManager.restore_from_state(self.selected_session_id)
            
            if session_manager:
                # Setze restored_session Attribut für Zugriff von außen
                self.restored_session = session_manager
                
                logger.info(f"Session wiederhergestellt: {self.selected_session_id}")
                messagebox.showinfo(
                    "Erfolg",
                    f"Session '{self.selected_session_id}' erfolgreich wiederhergestellt.\n"
                    "Die Session wurde geladen und ist bereit zur Verwendung."
                )
                self.dialog.destroy()
            else:
                messagebox.showerror(
                    "Fehler",
                    f"Die Session '{self.selected_session_id}' konnte nicht wiederhergestellt werden."
                )
        
        except Exception as e:
            logger.error(f"Fehler bei Session-Wiederherstellung: {e}", exc_info=True)
            messagebox.showerror(
                "Fehler",
                f"Fehler bei der Wiederherstellung:\n{str(e)}"
            )
    
    def _delete_session(self):
        """Löscht die ausgewählte Session"""
        if not self.selected_session_id:
            return
        
        if not messagebox.askyesno(
            "Session löschen",
            f"Möchten Sie die Session '{self.selected_session_id}' wirklich löschen?\n"
            "Diese Aktion kann nicht rückgängig gemacht werden."
        ):
            return
        
        try:
            recovery = SessionRecovery()
            if recovery.delete_session_state(self.selected_session_id):
                messagebox.showinfo("Erfolg", "Session gelöscht.")
                self._load_recoverable_sessions()
                self.selected_session_id = None
                self.restore_button.config(state=tk.DISABLED)
                self.delete_button.config(state=tk.DISABLED)
                self.details_text.config(state=tk.NORMAL)
                self.details_text.delete(1.0, tk.END)
                self.details_text.config(state=tk.DISABLED)
            else:
                messagebox.showerror("Fehler", "Session konnte nicht gelöscht werden.")
        
        except Exception as e:
            logger.error(f"Fehler beim Löschen der Session: {e}", exc_info=True)
            messagebox.showerror("Fehler", f"Fehler beim Löschen:\n{str(e)}")

