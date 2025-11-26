"""
Dialog für Quick-Reference Export (Checkliste, Cheat-Sheet, One-Pager)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import List, Dict
import threading

from src.document.quickref_exporter import QuickReferenceExporter
from src.utils.logger import get_logger

logger = get_logger(__name__)


class QuickRefExportDialog:
    """Dialog für Quick-Reference Export"""
    
    def __init__(self, parent, steps: List[Dict]):
        """
        Initialisiert den Quick-Reference Export Dialog
        
        Args:
            parent: Parent-Window
            steps: Liste von Schritten
        """
        self.parent = parent
        self.steps = steps
        self.exporter = QuickReferenceExporter()
        self.exporting = False
        
        # Erstelle Dialog-Fenster
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Quick-Reference Export")
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
        
        self.format_var = tk.StringVar(value="checklist")
        
        ttk.Radiobutton(
            format_frame,
            text="Checkliste (Markdown)",
            variable=self.format_var,
            value="checklist"
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(
            format_frame,
            text="Cheat-Sheet (PDF, 1 Seite)",
            variable=self.format_var,
            value="cheatsheet"
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(
            format_frame,
            text="One-Pager (Markdown)",
            variable=self.format_var,
            value="onepager"
        ).pack(anchor=tk.W, pady=2)
        
        # Optionen
        options_frame = ttk.LabelFrame(main_frame, text="Optionen", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.include_screenshots_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Screenshots einschließen",
            variable=self.include_screenshots_var
        ).pack(anchor=tk.W, pady=2)
        
        # Titel
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="Titel:").pack(side=tk.LEFT, padx=(0, 5))
        self.title_var = tk.StringVar(value="Quick Reference")
        ttk.Entry(title_frame, textvariable=self.title_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Ausgabe-Datei
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(output_frame, text="Ausgabe-Datei:").pack(anchor=tk.W)
        
        output_file_frame = ttk.Frame(output_frame)
        output_file_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.output_file_var = tk.StringVar(value=str(Path("data/output/quickref.md")))
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
            text="Exportieren",
            command=self._start_export
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="Abbrechen",
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT)
    
    def _browse_output_file(self):
        """Öffnet Dateiauswahl-Dialog"""
        format_type = self.format_var.get()
        
        if format_type == "cheatsheet":
            filetypes = [("PDF-Dateien", "*.pdf"), ("Alle Dateien", "*.*")]
            default_ext = ".pdf"
        else:
            filetypes = [("Markdown-Dateien", "*.md"), ("Alle Dateien", "*.*")]
            default_ext = ".md"
        
        filename = filedialog.asksaveasfilename(
            defaultextension=default_ext,
            filetypes=filetypes,
            initialfile=self.output_file_var.get()
        )
        
        if filename:
            self.output_file_var.set(filename)
    
    def _start_export(self):
        """Startet den Export-Prozess"""
        output_path = Path(self.output_file_var.get())
        if not output_path.parent.exists():
            messagebox.showerror("Fehler", "Ungültiger Ausgabe-Pfad.")
            return
        
        # Starte Export in separatem Thread
        self.exporting = True
        self.progress_bar.start()
        self.progress_var.set("Exportiere...")
        
        thread = threading.Thread(target=self._export_thread, daemon=True)
        thread.start()
    
    def _export_thread(self):
        """Export-Thread"""
        try:
            output_path = Path(self.output_file_var.get())
            format_type = self.format_var.get()
            title = self.title_var.get() or "Quick Reference"
            include_screenshots = self.include_screenshots_var.get()
            
            if format_type == "checklist":
                result_path = self.exporter.export_checklist(
                    steps=self.steps,
                    output_path=output_path,
                    title=title,
                    include_screenshots=include_screenshots
                )
            elif format_type == "cheatsheet":
                result_path = self.exporter.export_cheat_sheet(
                    steps=self.steps,
                    output_path=output_path,
                    title=title
                )
            elif format_type == "onepager":
                result_path = self.exporter.export_one_pager(
                    steps=self.steps,
                    output_path=output_path,
                    title=title
                )
            else:
                raise ValueError(f"Unbekanntes Format: {format_type}")
            
            # Update UI im Hauptthread
            self.dialog.after(0, lambda: self._export_completed(result_path))
        
        except Exception as err:
            logger.error(f"Fehler beim Quick-Reference Export: {err}", exc_info=True)
            self.dialog.after(0, lambda err=err: self._export_failed(str(err)))
    
    def _export_completed(self, output_path: Path):
        """Wird aufgerufen wenn Export abgeschlossen ist"""
        self.progress_bar.stop()
        self.exporting = False
        
        message = f"Export erfolgreich abgeschlossen!\n\n"
        message += f"Datei: {output_path}"
        
        messagebox.showinfo("Erfolg", message)
        self.dialog.destroy()
    
    def _export_failed(self, error_msg: str):
        """Wird aufgerufen wenn Export fehlgeschlagen ist"""
        self.progress_bar.stop()
        self.exporting = False
        
        messagebox.showerror(
            "Fehler",
            f"Export fehlgeschlagen:\n{error_msg}"
        )

