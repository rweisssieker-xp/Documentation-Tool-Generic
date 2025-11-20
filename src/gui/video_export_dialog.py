"""
Dialog für Video-Export
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import List, Dict
import threading

from src.document.video_exporter import VideoExporter
from src.utils.logger import get_logger

logger = get_logger(__name__)


class VideoExportDialog:
    """Dialog für Video-Export"""
    
    def __init__(self, parent, steps: List[Dict]):
        """
        Initialisiert den Video-Export Dialog
        
        Args:
            parent: Parent-Window
            steps: Liste von Schritten
        """
        self.parent = parent
        self.steps = steps
        self.exporter = None
        self.exporting = False
        
        # Erstelle Dialog-Fenster
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Video-Export")
        self.dialog.geometry("500x450")
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
        format_frame = ttk.LabelFrame(main_frame, text="Video-Format", padding="10")
        format_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.format_var = tk.StringVar(value="mp4")
        
        ttk.Radiobutton(
            format_frame,
            text="MP4 (Video)",
            variable=self.format_var,
            value="mp4"
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(
            format_frame,
            text="GIF (Animiert)",
            variable=self.format_var,
            value="gif"
        ).pack(anchor=tk.W, pady=2)
        
        # Video-Einstellungen
        settings_frame = ttk.LabelFrame(main_frame, text="Video-Einstellungen", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # FPS
        fps_frame = ttk.Frame(settings_frame)
        fps_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(fps_frame, text="Frames pro Sekunde (FPS):").pack(side=tk.LEFT)
        self.fps_var = tk.IntVar(value=2)
        fps_spinbox = ttk.Spinbox(
            fps_frame,
            from_=1,
            to=30,
            textvariable=self.fps_var,
            width=10
        )
        fps_spinbox.pack(side=tk.RIGHT)
        
        # Dauer pro Schritt
        duration_frame = ttk.Frame(settings_frame)
        duration_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(duration_frame, text="Dauer pro Schritt (Sekunden):").pack(side=tk.LEFT)
        self.duration_var = tk.DoubleVar(value=3.0)
        duration_spinbox = ttk.Spinbox(
            duration_frame,
            from_=1.0,
            to=10.0,
            increment=0.5,
            textvariable=self.duration_var,
            width=10
        )
        duration_spinbox.pack(side=tk.RIGHT)
        
        # Optionen
        options_frame = ttk.LabelFrame(main_frame, text="Optionen", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.include_transitions_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Übergänge zwischen Schritten",
            variable=self.include_transitions_var
        ).pack(anchor=tk.W, pady=2)
        
        self.include_voice_over_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Voice-Over (Text-to-Speech)",
            variable=self.include_voice_over_var
        ).pack(anchor=tk.W, pady=2)
        
        # Titel
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="Video-Titel:").pack(side=tk.LEFT, padx=(0, 5))
        self.title_var = tk.StringVar(value="Handbuch-Video")
        ttk.Entry(title_frame, textvariable=self.title_var, width=35).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Ausgabe-Datei
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(output_frame, text="Ausgabe-Datei:").pack(anchor=tk.W)
        
        output_file_frame = ttk.Frame(output_frame)
        output_file_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.output_file_var = tk.StringVar(value=str(Path("data/output/video.mp4")))
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
        
        if format_type == "mp4":
            filetypes = [("MP4-Dateien", "*.mp4"), ("Alle Dateien", "*.*")]
            default_ext = ".mp4"
        else:
            filetypes = [("GIF-Dateien", "*.gif"), ("Alle Dateien", "*.*")]
            default_ext = ".gif"
        
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
        self.progress_var.set("Exportiere Video...")
        
        thread = threading.Thread(target=self._export_thread, daemon=True)
        thread.start()
    
    def _export_thread(self):
        """Export-Thread"""
        try:
            output_path = Path(self.output_file_var.get())
            format_type = self.format_var.get()
            title = self.title_var.get() or "Handbuch-Video"
            fps = self.fps_var.get()
            duration_per_step = self.duration_var.get()
            include_transitions = self.include_transitions_var.get()
            include_voice_over = self.include_voice_over_var.get()
            
            # Erstelle Exporter mit Einstellungen
            self.exporter = VideoExporter(fps=fps, duration_per_step=duration_per_step)
            
            # Setze Ausgabe-Pfad entsprechend Format
            if format_type == "gif":
                output_path = output_path.with_suffix('.gif')
            
            result_path = self.exporter.export_video(
                steps=self.steps,
                output_path=output_path,
                title=title,
                include_transitions=include_transitions,
                include_voice_over=include_voice_over
            )
            
            # Update UI im Hauptthread
            self.dialog.after(0, lambda: self._export_completed(result_path))
        
        except Exception as e:
            logger.error(f"Fehler beim Video-Export: {e}", exc_info=True)
            self.dialog.after(0, lambda: self._export_failed(str(e)))
    
    def _export_completed(self, output_path: Path):
        """Wird aufgerufen wenn Export abgeschlossen ist"""
        self.progress_bar.stop()
        self.exporting = False
        
        message = f"Video-Export erfolgreich abgeschlossen!\n\n"
        message += f"Datei: {output_path}"
        
        messagebox.showinfo("Erfolg", message)
        self.dialog.destroy()
    
    def _export_failed(self, error_msg: str):
        """Wird aufgerufen wenn Export fehlgeschlagen ist"""
        self.progress_bar.stop()
        self.exporting = False
        
        messagebox.showerror(
            "Fehler",
            f"Video-Export fehlgeschlagen:\n{error_msg}"
        )

