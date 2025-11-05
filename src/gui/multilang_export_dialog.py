"""
Dialog für Multi-Sprach-Export
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import List, Dict, Optional
import threading

from src.document.multilang_exporter import MultiLanguageExporter
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MultiLangExportDialog:
    """Dialog für Multi-Sprach-Export"""
    
    def __init__(self, parent, steps: List[Dict], session_id: str):
        """
        Initialisiert den Multi-Sprach-Export Dialog
        
        Args:
            parent: Parent-Window
            steps: Liste von Schritten
            session_id: Session-ID
        """
        self.parent = parent
        self.steps = steps
        self.session_id = session_id
        self.exporter = MultiLanguageExporter()
        self.selected_languages: List[str] = []
        self.exporting = False
        
        # Erstelle Dialog-Fenster
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Multi-Sprach-Export")
        self.dialog.geometry("500x600")
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
        
        # Info-Label
        info_label = ttk.Label(
            main_frame,
            text="Wählen Sie die Sprachen aus, in die das Dokument exportiert werden soll:",
            wraplength=450
        )
        info_label.pack(pady=(0, 10))
        
        # Sprache-Auswahl Frame
        lang_frame = ttk.LabelFrame(main_frame, text="Verfügbare Sprachen", padding="10")
        lang_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Scrollbar für Sprachen
        scroll_frame = ttk.Frame(lang_frame)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.lang_listbox = tk.Listbox(scroll_frame, selectmode=tk.EXTENDED, yscrollcommand=scrollbar.set)
        self.lang_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.lang_listbox.yview)
        
        # Füge Sprachen hinzu
        for lang_code, lang_name in self.exporter.SUPPORTED_LANGUAGES.items():
            self.lang_listbox.insert(tk.END, f"{lang_name} ({lang_code})")
        
        # Standard-Auswahl: Deutsch und Englisch
        self.lang_listbox.selection_set(0, 1)  # Deutsch und Englisch
        
        # Ausgabe-Verzeichnis
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(output_frame, text="Ausgabe-Verzeichnis:").pack(anchor=tk.W)
        
        output_dir_frame = ttk.Frame(output_frame)
        output_dir_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.output_dir_var = tk.StringVar(value=str(Path("data/output/multilang")))
        output_entry = ttk.Entry(output_dir_frame, textvariable=self.output_dir_var)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(
            output_dir_frame,
            text="Durchsuchen...",
            command=self._browse_output_dir
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
    
    def _browse_output_dir(self):
        """Öffnet Verzeichnisauswahl-Dialog"""
        from tkinter import filedialog
        
        directory = filedialog.askdirectory(
            initialdir=self.output_dir_var.get(),
            title="Ausgabe-Verzeichnis auswählen"
        )
        
        if directory:
            self.output_dir_var.set(directory)
    
    def _start_export(self):
        """Startet den Export-Prozess"""
        # Hole ausgewählte Sprachen
        selected_indices = self.lang_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie mindestens eine Sprache aus.")
            return
        
        # Konvertiere Indizes zu Sprach-Codes
        lang_codes = list(self.exporter.SUPPORTED_LANGUAGES.keys())
        self.selected_languages = [lang_codes[i] for i in selected_indices]
        
        # Prüfe Ausgabe-Verzeichnis
        output_dir = Path(self.output_dir_var.get())
        if not output_dir.parent.exists():
            messagebox.showerror("Fehler", "Ungültiges Ausgabe-Verzeichnis.")
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
            output_dir = Path(self.output_dir_var.get())
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Hole Titel aus Session oder verwende Standard
            title = "Handbuch"
            if self.steps:
                title = self.steps[0].get('window_title', 'Handbuch')
            
            # Exportiere
            exported_files = self.exporter.export_multilang(
                steps=self.steps,
                output_dir=output_dir,
                target_languages=self.selected_languages,
                session_id=self.session_id,
                title=title
            )
            
            # Update UI im Hauptthread
            self.dialog.after(0, lambda: self._export_completed(exported_files))
        
        except Exception as e:
            logger.error(f"Fehler beim Multi-Sprach-Export: {e}", exc_info=True)
            self.dialog.after(0, lambda: self._export_failed(str(e)))
    
    def _export_completed(self, exported_files: Dict[str, Path]):
        """Wird aufgerufen wenn Export abgeschlossen ist"""
        self.progress_bar.stop()
        self.exporting = False
        
        lang_names = [self.exporter.SUPPORTED_LANGUAGES.get(lang, lang) for lang in self.selected_languages]
        
        message = f"Export erfolgreich abgeschlossen!\n\n"
        message += f"Sprachen: {', '.join(lang_names)}\n"
        message += f"Dateien: {len(exported_files)}\n\n"
        message += f"Ausgabe-Verzeichnis:\n{self.output_dir_var.get()}"
        
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
