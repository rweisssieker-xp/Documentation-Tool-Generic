"""
Progress Dialog für lange laufende Operationen
"""

import tkinter as tk
from tkinter import ttk
import threading
from typing import Callable, Optional


class ProgressDialog:
    """Dialog zur Anzeige des Fortschritts für lange laufende Operationen"""
    
    def __init__(self, parent, title: str = "Fortschritt", 
                 max_value: int = 100, show_percentage: bool = True,
                 cancellable: bool = True):
        """
        Initialisiert den Progress Dialog
        
        Args:
            parent: Parent-Widget
            title: Titel des Dialogs
            max_value: Maximaler Wert der Progressbar (default: 100)
            show_percentage: Ob Prozentanzeige gezeigt werden soll
            cancellable: Ob der Dialog abgebrochen werden kann
        """
        self.parent = parent
        self.max_value = max_value
        self.show_percentage = show_percentage
        self.cancellable = cancellable
        self.cancelled = False
        
        # Erstelle Dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x120")
        self.dialog.resizable(False, False)
        
        # Zentriere Dialog
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Positioniere Dialog in der Mitte des Parents
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self._setup_ui()
        
        # Schließe Dialog korrekt
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel if self.cancellable else lambda: None)
    
    def _setup_ui(self):
        """Erstellt die UI-Komponenten"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Fortschritt-Label
        self.status_label = ttk.Label(main_frame, text="Initialisierung...")
        self.status_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Progressbar
        self.progress_var = tk.DoubleVar()
        self.progress_var.set(0)
        
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            variable=self.progress_var,
            maximum=self.max_value,
            length=300
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        if self.show_percentage:
            self.percent_label = ttk.Label(self.progress_frame, text="0%")
            self.percent_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Button-Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # Cancel Button (nur wenn cancellable)
        if self.cancellable:
            self.cancel_button = ttk.Button(
                button_frame,
                text="Abbrechen",
                command=self._on_cancel,
                width=12
            )
            self.cancel_button.pack(side=tk.RIGHT)
        
        # Center the progress bar
        main_frame.columnconfigure(0, weight=1)
    
    def update_progress(self, value: float, status_text: str = None):
        """
        Aktualisiert den Fortschritt
        
        Args:
            value: Aktueller Fortschrittswert
            status_text: Optionaler Status-Text
        """
        # Stelle sicher, dass Wert im gültigen Bereich ist
        value = max(0, min(self.max_value, value))
        
        self.progress_var.set(value)
        
        if status_text:
            self.status_label.config(text=status_text)
        
        if self.show_percentage and hasattr(self, 'percent_label'):
            percent = (value / self.max_value) * 100 if self.max_value > 0 else 0
            self.percent_label.config(text=f"{percent:.1f}%")
        
        # Aktualisiere GUI
        self.dialog.update_idletasks()
    
    def increment_progress(self, increment: float = 1.0, status_text: str = None):
        """
        Erhöht den Fortschritt um einen Wert
        
        Args:
            increment: Wert, um den erhöht werden soll
            status_text: Optionaler Status-Text
        """
        new_value = self.progress_var.get() + increment
        self.update_progress(new_value, status_text)
    
    def is_cancelled(self) -> bool:
        """
        Gibt zurück, ob die Operation abgebrochen wurde
        
        Returns:
            True wenn abgebrochen, sonst False
        """
        return self.cancelled
    
    def _on_cancel(self):
        """Wird aufgerufen wenn abgebrochen wird"""
        self.cancelled = True
        if hasattr(self, 'cancel_callback') and self.cancel_callback:
            self.cancel_callback()
    
    def set_cancel_callback(self, callback: Callable):
        """
        Setzt Callback für Abbruch-Ereignis
        
        Args:
            callback: Funktion die bei Abbruch aufgerufen wird
        """
        self.cancel_callback = callback
    
    def close(self):
        """Schließt den Dialog"""
        if self.dialog.winfo_exists():
            self.dialog.grab_release()
            self.dialog.destroy()
    
    def wait_window(self):
        """Wartet bis der Dialog geschlossen wird"""
        self.dialog.wait_window()