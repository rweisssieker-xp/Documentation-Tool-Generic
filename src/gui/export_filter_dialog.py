"""
Dialog zur Export-Filter-Konfiguration
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import threading

from src.document.export_filter import (
    FilterManager, DateRangeFilter, WindowTitleFilter,
    StepIndexFilter, CompositeFilter, ExportFilter
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ExportFilterDialog:
    """Dialog zur Konfiguration von Export-Filtern"""
    
    def __init__(self, parent, steps: List[Dict]):
        """
        Initialisiert den Export-Filter-Dialog
        
        Args:
            parent: Parent-Window
            steps: Liste von Schritten zum Filtern
        """
        self.parent = parent
        self.steps = steps
        self.filtered_steps = steps.copy()
        self.filter_manager = FilterManager()
        self.current_filter: Optional[ExportFilter] = None
        
        # Erstelle Dialog-Fenster
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Export-Filter")
        self.dialog.geometry("900x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Zentriere Dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self._setup_ui()
        self._update_preview()
    
    def _setup_ui(self):
        """Erstellt die UI-Komponenten"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Linke Seite: Filter-Konfiguration
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Filter-Typ Auswahl
        filter_type_frame = ttk.LabelFrame(left_frame, text="Filter-Typ", padding="5")
        filter_type_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.filter_type_var = tk.StringVar(value="date_range")
        filter_types = [
            ("Datumsbereich", "date_range"),
            ("Fenster-Titel", "window_title"),
            ("Schritt-Indizes", "step_index"),
            ("Gespeicherte Filter", "saved")
        ]
        
        for text, value in filter_types:
            ttk.Radiobutton(
                filter_type_frame,
                text=text,
                variable=self.filter_type_var,
                value=value,
                command=self._on_filter_type_change
            ).pack(anchor=tk.W, pady=2)
        
        # Filter-Konfiguration
        self.config_frame = ttk.LabelFrame(left_frame, text="Filter-Konfiguration", padding="5")
        self.config_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self._setup_filter_config()
        
        # Filter-Aktionen
        filter_action_frame = ttk.Frame(left_frame)
        filter_action_frame.pack(fill=tk.X)
        
        ttk.Button(
            filter_action_frame,
            text="Filter anwenden",
            command=self._apply_filter
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            filter_action_frame,
            text="Zurücksetzen",
            command=self._reset_filter
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            filter_action_frame,
            text="Filter speichern",
            command=self._save_filter
        ).pack(side=tk.LEFT)
        
        # Rechte Seite: Vorschau
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        preview_frame = ttk.LabelFrame(right_frame, text="Vorschau", padding="5")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Vorschau-Statistiken
        self.preview_stats_label = ttk.Label(
            preview_frame,
            text=f"Gesamt: {len(self.steps)} Schritte",
            font=("Arial", 9, "bold")
        )
        self.preview_stats_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Vorschau-Liste
        preview_list_frame = ttk.Frame(preview_frame)
        preview_list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(preview_list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.preview_listbox = tk.Listbox(
            preview_list_frame,
            font=("Arial", 9),
            yscrollcommand=scrollbar.set
        )
        self.preview_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.preview_listbox.yview)
        
        # Button-Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="OK",
            command=self._ok
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="Abbrechen",
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT)
    
    def _setup_filter_config(self):
        """Erstellt Filter-Konfigurations-UI basierend auf Filter-Typ"""
        # Lösche alte Widgets
        for widget in self.config_frame.winfo_children():
            widget.destroy()
        
        filter_type = self.filter_type_var.get()
        
        if filter_type == "date_range":
            self._setup_date_range_config()
        elif filter_type == "window_title":
            self._setup_window_title_config()
        elif filter_type == "step_index":
            self._setup_step_index_config()
        elif filter_type == "saved":
            self._setup_saved_filter_config()
    
    def _setup_date_range_config(self):
        """Erstellt UI für Datumsbereich-Filter"""
        ttk.Label(self.config_frame, text="Start-Datum:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.start_date_var = tk.StringVar()
        ttk.Entry(self.config_frame, textvariable=self.start_date_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=5)
        ttk.Label(self.config_frame, text="(Format: YYYY-MM-DD HH:MM)").grid(row=0, column=2, sticky=tk.W)
        
        ttk.Label(self.config_frame, text="End-Datum:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.end_date_var = tk.StringVar()
        ttk.Entry(self.config_frame, textvariable=self.end_date_var, width=20).grid(row=1, column=1, sticky=tk.W, padx=5)
        ttk.Label(self.config_frame, text="(Format: YYYY-MM-DD HH:MM)").grid(row=1, column=2, sticky=tk.W)
    
    def _setup_window_title_config(self):
        """Erstellt UI für Fenster-Titel-Filter"""
        ttk.Label(self.config_frame, text="Pattern (Regex):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.window_pattern_var = tk.StringVar()
        ttk.Entry(self.config_frame, textvariable=self.window_pattern_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        self.case_sensitive_var = tk.BooleanVar()
        ttk.Checkbutton(
            self.config_frame,
            text="Groß-/Kleinschreibung beachten",
            variable=self.case_sensitive_var
        ).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.invert_window_var = tk.BooleanVar()
        ttk.Checkbutton(
            self.config_frame,
            text="Filter invertieren",
            variable=self.invert_window_var
        ).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
    
    def _setup_step_index_config(self):
        """Erstellt UI für Schritt-Index-Filter"""
        ttk.Label(self.config_frame, text="Schritt-Indizes (kommagetrennt):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.step_indices_var = tk.StringVar()
        ttk.Entry(self.config_frame, textvariable=self.step_indices_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        self.invert_step_var = tk.BooleanVar()
        ttk.Checkbutton(
            self.config_frame,
            text="Filter invertieren",
            variable=self.invert_step_var
        ).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
    
    def _setup_saved_filter_config(self):
        """Erstellt UI für gespeicherte Filter"""
        ttk.Label(self.config_frame, text="Gespeicherte Filter:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.saved_filter_var = tk.StringVar()
        saved_filters = self.filter_manager.list_filters()
        
        if saved_filters:
            filter_combo = ttk.Combobox(
                self.config_frame,
                textvariable=self.saved_filter_var,
                values=saved_filters,
                width=30,
                state="readonly"
            )
            filter_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
            filter_combo.current(0)
        else:
            ttk.Label(
                self.config_frame,
                text="Keine gespeicherten Filter",
                foreground="gray"
            ).grid(row=0, column=1, sticky=tk.W, padx=5)
    
    def _on_filter_type_change(self):
        """Wird aufgerufen wenn Filter-Typ geändert wird"""
        self._setup_filter_config()
    
    def _apply_filter(self):
        """Wendet Filter an"""
        try:
            filter_type = self.filter_type_var.get()
            
            if filter_type == "date_range":
                filter_obj = self._create_date_range_filter()
            elif filter_type == "window_title":
                filter_obj = self._create_window_title_filter()
            elif filter_type == "step_index":
                filter_obj = self._create_step_index_filter()
            elif filter_type == "saved":
                filter_name = self.saved_filter_var.get()
                if not filter_name:
                    messagebox.showwarning("Fehler", "Bitte wählen Sie einen gespeicherten Filter aus.")
                    return
                filter_obj = self.filter_manager.get_filter(filter_name)
                if not filter_obj:
                    messagebox.showerror("Fehler", f"Filter '{filter_name}' nicht gefunden.")
                    return
            else:
                messagebox.showerror("Fehler", "Ungültiger Filter-Typ.")
                return
            
            if filter_obj:
                self.current_filter = filter_obj
                self.filtered_steps = filter_obj.filter(self.steps.copy())
                self._update_preview()
                messagebox.showinfo("Erfolg", f"Filter angewendet: {len(self.filtered_steps)} von {len(self.steps)} Schritten")
        
        except Exception as e:
            logger.error(f"Fehler beim Anwenden des Filters: {e}", exc_info=True)
            messagebox.showerror("Fehler", f"Fehler beim Anwenden des Filters:\n{str(e)}")
    
    def _create_date_range_filter(self) -> DateRangeFilter:
        """Erstellt Datumsbereich-Filter"""
        start_date = None
        end_date = None
        
        start_str = self.start_date_var.get().strip()
        end_str = self.end_date_var.get().strip()
        
        if start_str:
            try:
                start_date = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
            except ValueError:
                try:
                    start_date = datetime.strptime(start_str, "%Y-%m-%d")
                except ValueError:
                    raise ValueError(f"Ungültiges Start-Datum-Format: {start_str}")
        
        if end_str:
            try:
                end_date = datetime.strptime(end_str, "%Y-%m-%d %H:%M")
            except ValueError:
                try:
                    end_date = datetime.strptime(end_str, "%Y-%m-%d")
                except ValueError:
                    raise ValueError(f"Ungültiges End-Datum-Format: {end_str}")
        
        return DateRangeFilter(start_date, end_date)
    
    def _create_window_title_filter(self) -> WindowTitleFilter:
        """Erstellt Fenster-Titel-Filter"""
        pattern = self.window_pattern_var.get().strip()
        if not pattern:
            raise ValueError("Pattern darf nicht leer sein.")
        
        return WindowTitleFilter(
            pattern=pattern,
            case_sensitive=self.case_sensitive_var.get(),
            invert=self.invert_window_var.get()
        )
    
    def _create_step_index_filter(self) -> StepIndexFilter:
        """Erstellt Schritt-Index-Filter"""
        indices_str = self.step_indices_var.get().strip()
        if not indices_str:
            raise ValueError("Schritt-Indizes dürfen nicht leer sein.")
        
        try:
            indices = [int(x.strip()) for x in indices_str.split(',')]
        except ValueError:
            raise ValueError("Ungültiges Format für Schritt-Indizes. Verwenden Sie kommagetrennte Zahlen.")
        
        return StepIndexFilter(indices=indices, invert=self.invert_step_var.get())
    
    def _reset_filter(self):
        """Setzt Filter zurück"""
        self.current_filter = None
        self.filtered_steps = self.steps.copy()
        self._update_preview()
    
    def _save_filter(self):
        """Speichert aktuellen Filter"""
        if not self.current_filter:
            messagebox.showwarning("Kein Filter", "Bitte wenden Sie zuerst einen Filter an.")
            return
        
        filter_name = tk.simpledialog.askstring(
            "Filter speichern",
            "Geben Sie einen Namen für den Filter ein:",
            parent=self.dialog
        )
        
        if filter_name:
            self.filter_manager.add_filter(filter_name, self.current_filter)
            messagebox.showinfo("Erfolg", f"Filter '{filter_name}' gespeichert.")
            self._setup_filter_config()
    
    def _update_preview(self):
        """Aktualisiert die Vorschau"""
        self.preview_listbox.delete(0, tk.END)
        
        # Update Statistiken
        self.preview_stats_label.config(
            text=f"Gefiltert: {len(self.filtered_steps)} von {len(self.steps)} Schritten"
        )
        
        # Zeige gefilterte Schritte
        for step in self.filtered_steps[:100]:  # Begrenze auf 100 für Performance
            step_num = step.get('step_number', '?')
            window_title = step.get('window_title', 'Unbekannt')
            timestamp = step.get('timestamp', '')
            
            try:
                if timestamp:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime('%H:%M:%S')
                else:
                    time_str = ''
            except:
                time_str = timestamp
            
            display_text = f"Schritt {step_num}: {window_title} ({time_str})"
            self.preview_listbox.insert(tk.END, display_text)
        
        if len(self.filtered_steps) > 100:
            self.preview_listbox.insert(tk.END, f"... und {len(self.filtered_steps) - 100} weitere")
    
    def _ok(self):
        """Wird aufgerufen wenn OK geklickt wird"""
        self.dialog.destroy()
    
    def get_filtered_steps(self) -> List[Dict]:
        """Gibt die gefilterten Schritte zurück"""
        return self.filtered_steps

