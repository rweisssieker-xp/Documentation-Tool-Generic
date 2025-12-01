"""Video Synthesis Dialog - GUI for video generation"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

from src.video import VideoSynthesizer, VideoConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)


class VideoSynthesisDialog:
    """Dialog for video tutorial generation."""
    
    def __init__(self, parent, session_data=None, screenshot_paths=None):
        self.parent = parent
        self.session_data = session_data or {}
        self.screenshot_paths = screenshot_paths or []
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Video Tutorial Generator")
        self.dialog.geometry("600x500")
        
        self._create_widgets()
    
    def _create_widgets(self):
        ttk.Label(self.dialog, text="Video Tutorial Generator", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Config
        config_frame = ttk.LabelFrame(self.dialog, text="Einstellungen")
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(config_frame, text="Frame Rate:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.frame_rate_var = tk.IntVar(value=30)
        ttk.Spinbox(config_frame, from_=24, to=60, textvariable=self.frame_rate_var, width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(config_frame, text="Dauer pro Screenshot (s):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.duration_var = tk.DoubleVar(value=3.0)
        ttk.Spinbox(config_frame, from_=1.0, to=10.0, increment=0.5, textvariable=self.duration_var, width=10).grid(row=1, column=1, padx=5)
        
        ttk.Label(config_frame, text="Sprache:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.language_var = tk.StringVar(value="de")
        ttk.Combobox(config_frame, textvariable=self.language_var, values=["de", "en"], state="readonly", width=10).grid(row=2, column=1, padx=5)
        
        self.include_narration_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(config_frame, text="Narration einschließen", variable=self.include_narration_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5)
        
        self.include_subtitles_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(config_frame, text="Untertitel einschließen", variable=self.include_subtitles_var).grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=5)
        
        # Output
        output_frame = ttk.LabelFrame(self.dialog, text="Ausgabe")
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(output_frame, text="Ausgabedatei:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.output_var = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_var, width=40).grid(row=0, column=1, padx=5)
        ttk.Button(output_frame, text="Durchsuchen...", command=self._browse_output).grid(row=0, column=2, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Generieren", command=self._generate).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Abbrechen", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _browse_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4", "*.mp4")])
        if path:
            self.output_var.set(path)
    
    def _generate(self):
        output_path = Path(self.output_var.get())
        if not output_path:
            messagebox.showwarning("Warnung", "Bitte wählen Sie eine Ausgabedatei")
            return
        
        try:
            config = VideoConfig(
                frame_rate=self.frame_rate_var.get(),
                frame_duration=self.duration_var.get(),
                language=self.language_var.get(),
                include_narration=self.include_narration_var.get(),
                include_subtitles=self.include_subtitles_var.get()
            )
            
            synthesizer = VideoSynthesizer(config)
            success = synthesizer.generate_video(
                self.session_data,
                [Path(p) for p in self.screenshot_paths],
                output_path
            )
            
            if success:
                messagebox.showinfo("Erfolg", f"Video generiert: {output_path}")
                self.dialog.destroy()
            else:
                messagebox.showerror("Fehler", "Video-Generierung fehlgeschlagen")
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            messagebox.showerror("Fehler", f"Fehler: {e}")

