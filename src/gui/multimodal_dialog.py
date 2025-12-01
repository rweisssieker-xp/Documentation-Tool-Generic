"""
Multi-Modal Capture Dialog - GUI für Multi-Modal Capture Engine
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from pathlib import Path
import threading

from src.multimodal import MultiModalCaptureEngine
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MultiModalDialog:
    """Dialog for Multi-Modal Capture Engine"""
    
    def __init__(self, parent):
        """
        Initialize Multi-Modal Dialog.
        
        Args:
            parent: Parent window
        """
        self.parent = parent
        self.capture_engine = MultiModalCaptureEngine()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Multi-Modal Capture Engine")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create dialog widgets"""
        # Configuration
        config_frame = ttk.LabelFrame(self.dialog, text="Capture Configuration")
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Output Directory
        output_frame = ttk.Frame(config_frame)
        output_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(output_frame, text="Output Directory:").pack(side=tk.LEFT)
        self.output_dir_var = tk.StringVar(value="data/multimodal")
        ttk.Entry(output_frame, textvariable=self.output_dir_var, width=30).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="Browse", command=self._browse_output).pack(side=tk.LEFT, padx=5)
        
        # Capture Options
        options_frame = ttk.Frame(config_frame)
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.video_var = tk.BooleanVar(value=True)
        self.audio_var = tk.BooleanVar(value=True)
        self.mouse_var = tk.BooleanVar(value=True)
        self.keyboard_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="Video", variable=self.video_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(options_frame, text="Audio", variable=self.audio_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(options_frame, text="Mouse", variable=self.mouse_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(options_frame, text="Keyboard", variable=self.keyboard_var).pack(side=tk.LEFT, padx=5)
        
        # Control Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Recording", command=self._start_recording)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop Recording", command=self._stop_recording, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Status
        status_frame = ttk.LabelFrame(self.dialog, text="Status")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=15, wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.status_text.insert(tk.END, "Multi-Modal Capture Status\n")
        self.status_text.insert(tk.END, "=" * 50 + "\n")
        self.status_text.insert(tk.END, "Status: Ready\n")
        self.status_text.insert(tk.END, "Recording: No\n")
    
    def _browse_output(self):
        """Browse for output directory"""
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.output_dir_var.set(dir_path)
    
    def _start_recording(self):
        """Start multi-modal recording"""
        output_dir = self.output_dir_var.get()
        if not output_dir:
            messagebox.showwarning("Warning", "Please select an output directory")
            return
        
        try:
            self.capture_engine.start_recording(output_dir)
            
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            self.status_text.insert(tk.END, f"\nRecording started at: {output_dir}\n")
            self.status_text.insert(tk.END, f"Video: {'Enabled' if self.video_var.get() else 'Disabled'}\n")
            self.status_text.insert(tk.END, f"Audio: {'Enabled' if self.audio_var.get() else 'Disabled'}\n")
            self.status_text.insert(tk.END, f"Mouse: {'Enabled' if self.mouse_var.get() else 'Disabled'}\n")
            self.status_text.insert(tk.END, f"Keyboard: {'Enabled' if self.keyboard_var.get() else 'Disabled'}\n")
            
            messagebox.showinfo("Success", "Multi-modal recording started")
        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            messagebox.showerror("Error", f"Failed to start recording: {e}")
    
    def _stop_recording(self):
        """Stop multi-modal recording"""
        try:
            synchronized = self.capture_engine.stop_recording()
            
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            
            self.status_text.insert(tk.END, "\nRecording stopped\n")
            self.status_text.insert(tk.END, f"Synchronized streams: {len(synchronized)}\n")
            for stream_type, stream_data in synchronized.items():
                self.status_text.insert(tk.END, f"  {stream_type}: {stream_data.get('path', 'N/A')}\n")
            
            messagebox.showinfo("Success", "Recording stopped and synchronized")
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            messagebox.showerror("Error", f"Failed to stop recording: {e}")

