"""
Dialog für Test-Checkliste Generator
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import List, Dict
import threading

from src.document.test_checklist_generator import TestChecklistGenerator
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TestChecklistDialog:
    """Dialog für Test-Checkliste Generator"""
    
    def __init__(self, parent, steps: List[Dict]):
        """
        Initialisiert den Test-Checkliste Dialog
        
        Args:
            parent: Parent-Window
            steps: Liste von Schritten
        """
        self.parent = parent
        self.steps = steps
        self.generator = TestChecklistGenerator()
        self.exporting = False
        
        # Erstelle Dialog-Fenster
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Test-Checkliste generieren")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Zentriere Dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Erstellt die UI-Komponenten"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Format-Auswahl
        format_frame = ttk.LabelFrame(main_frame, text="Export-Format", padding="10")
        format_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.format_var = tk.StringVar(value="csv")
        
        ttk.Radiobutton(
            format_frame,
            text="CSV",
            variable=self.format_var,
            value="csv"
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(
            format_frame,
            text="Excel (XLSX)",
            variable=self.format_var,
            value="excel"
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(
            format_frame,
            text="Markdown",
            variable=self.format_var,
            value="markdown"
        ).pack(anchor=tk.W, pady=2)
        
        # Optionen
        options_frame = ttk.LabelFrame(main_frame, text="Optionen", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.include_test_data_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Test-Daten-Spalte einschließen",
            variable=self.include_test_data_var
        ).pack(anchor=tk.W, pady=2)
        
        # Ausgabe-Datei
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(output_frame, text="Ausgabe-Datei:").pack(anchor=tk.W)
        
        output_file_frame = ttk.Frame(output_frame)
        output_file_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.output_file_var = tk.StringVar(value=str(Path("data/output/test_checklist.csv")))
        output_entry = ttk.Entry(output_file_frame, textvariable=self.output_file_var)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(
            output_file_frame,
            text="Durchsuchen...",
            command=self._browse_output_file
        ).pack(side=tk.RIGHT)
        
        # Progress-Bar
        self.progress_var = tk.StringVar(value="Bereit")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.pack(pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="Generieren",
            command=self._start_generation
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="Abbrechen",
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT)
    
    def _browse_output_file(self):
        """Öffnet Dateiauswahl-Dialog"""
        format_type = self.format_var.get()
        
        if format_type == "excel":
            filetypes = [("Excel-Dateien", "*.xlsx"), ("Alle Dateien", "*.*")]
            default_ext = ".xlsx"
        elif format_type == "markdown":
            filetypes = [("Markdown-Dateien", "*.md"), ("Alle Dateien", "*.*")]
            default_ext = ".md"
        else:
            filetypes = [("CSV-Dateien", "*.csv"), ("Alle Dateien", "*.*")]
            default_ext = ".csv"
        
        filename = filedialog.asksaveasfilename(
            defaultextension=default_ext,
            filetypes=filetypes,
            initialfile=self.output_file_var.get()
        )
        
        if filename:
            self.output_file_var.set(filename)
    
    def _start_generation(self):
        """Startet die Generierung"""
        output_path = Path(self.output_file_var.get())
        if not output_path.parent.exists():
            messagebox.showerror("Fehler", "Ungültiger Ausgabe-Pfad.")
            return
        
        # Starte Generierung in separatem Thread
        self.exporting = True
        self.progress_bar.start()
        self.progress_var.set("Generiere Test-Checkliste...")
        
        thread = threading.Thread(target=self._generate_thread, daemon=True)
        thread.start()
    
    def _generate_thread(self):
        """Generierungs-Thread"""
        try:
            output_path = Path(self.output_file_var.get())
            format_type = self.format_var.get()
            include_test_data = self.include_test_data_var.get()
            
            result_path = self.generator.generate_checklist(
                steps=self.steps,
                output_path=output_path,
                format=format_type,
                include_test_data=include_test_data
            )
            
            # Update UI im Hauptthread
            self.dialog.after(0, lambda: self._generation_completed(result_path))
        
        except Exception as e:
            logger.error(f"Fehler beim Generieren der Test-Checkliste: {e}", exc_info=True)
            self.dialog.after(0, lambda: self._generation_failed(str(e)))
    
    def _generation_completed(self, output_path: Path):
        """Wird aufgerufen wenn Generierung abgeschlossen ist"""
        self.progress_bar.stop()
        self.exporting = False
        
        message = f"Test-Checkliste erfolgreich generiert!\n\n"
        message += f"Datei: {output_path}"
        
        messagebox.showinfo("Erfolg", message)
        self.dialog.destroy()
    
    def _generation_failed(self, error_msg: str):
        """Wird aufgerufen wenn Generierung fehlgeschlagen ist"""
        self.progress_bar.stop()
        self.exporting = False
        
        messagebox.showerror(
            "Fehler",
            f"Generierung fehlgeschlagen:\n{error_msg}"
        )

