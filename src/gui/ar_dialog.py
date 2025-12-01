"""
AR Documentation Dialog - GUI für AR Documentation Overlay
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional

from src.ar import AROverlayEngine, ARPlatform
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ARDialog:
    """Dialog for AR Documentation Overlay"""
    
    def __init__(self, parent):
        """
        Initialize AR Dialog.
        
        Args:
            parent: Parent window
        """
        self.parent = parent
        self.ar_engine = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("AR Documentation Overlay")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create dialog widgets"""
        # Notebook for tabs
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configuration Tab
        config_frame = ttk.Frame(notebook)
        notebook.add(config_frame, text="Configuration")
        self._create_config_tab(config_frame)
        
        # Overlay Tab
        overlay_frame = ttk.Frame(notebook)
        notebook.add(overlay_frame, text="Overlay")
        self._create_overlay_tab(overlay_frame)
    
    def _create_config_tab(self, parent):
        """Create configuration tab"""
        # Platform Selection
        platform_frame = ttk.LabelFrame(parent, text="AR Platform")
        platform_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.platform_var = tk.StringVar(value="vision_pro")
        ttk.Radiobutton(platform_frame, text="Apple Vision Pro", variable=self.platform_var, value="vision_pro").pack(anchor=tk.W, padx=5)
        ttk.Radiobutton(platform_frame, text="Meta Quest", variable=self.platform_var, value="quest").pack(anchor=tk.W, padx=5)
        ttk.Radiobutton(platform_frame, text="Microsoft HoloLens", variable=self.platform_var, value="hololens").pack(anchor=tk.W, padx=5)
        
        # Initialize Button
        ttk.Button(parent, text="Initialize AR Engine", command=self._initialize_ar).pack(pady=10)
        
        # Status
        status_frame = ttk.LabelFrame(parent, text="Status")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=10, wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.status_text.insert(tk.END, "AR Engine Status\n")
        self.status_text.insert(tk.END, "=" * 50 + "\n")
        self.status_text.insert(tk.END, "Status: Not Initialized\n")
        self.status_text.insert(tk.END, "\nNote: AR features require compatible hardware.\n")
    
    def _create_overlay_tab(self, parent):
        """Create overlay tab"""
        # Content
        content_frame = ttk.LabelFrame(parent, text="Overlay Content")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ttk.Label(content_frame, text="Content:").pack(anchor=tk.W, padx=5, pady=2)
        self.content_text = scrolledtext.ScrolledText(content_frame, height=8, wrap=tk.WORD)
        self.content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # Position
        position_frame = ttk.Frame(parent)
        position_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(position_frame, text="Position (x, y, z):").pack(side=tk.LEFT, padx=5)
        self.x_var = tk.StringVar(value="0")
        self.y_var = tk.StringVar(value="0")
        self.z_var = tk.StringVar(value="0")
        
        ttk.Entry(position_frame, textvariable=self.x_var, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Entry(position_frame, textvariable=self.y_var, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Entry(position_frame, textvariable=self.z_var, width=10).pack(side=tk.LEFT, padx=2)
        
        # Buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Show Overlay", command=self._show_overlay).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Hide Overlay", command=self._hide_overlay).pack(side=tk.LEFT, padx=5)
        
        # Anchor ID
        anchor_frame = ttk.Frame(parent)
        anchor_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(anchor_frame, text="Anchor ID:").pack(side=tk.LEFT, padx=5)
        self.anchor_id_var = tk.StringVar()
        ttk.Entry(anchor_frame, textvariable=self.anchor_id_var, width=30).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def _initialize_ar(self):
        """Initialize AR engine"""
        try:
            platform_str = self.platform_var.get()
            platform = ARPlatform.VISION_PRO if platform_str == "vision_pro" else ARPlatform.QUEST
            
            self.ar_engine = AROverlayEngine(platform=platform)
            
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, "AR Engine Status\n")
            self.status_text.insert(tk.END, "=" * 50 + "\n")
            self.status_text.insert(tk.END, f"Status: Initialized\n")
            self.status_text.insert(tk.END, f"Platform: {platform_str.title()}\n")
            self.status_text.insert(tk.END, "\nNote: AR features require compatible hardware.\n")
            
            messagebox.showinfo("Success", "AR Engine initialized")
        except Exception as e:
            logger.error(f"Error initializing AR: {e}")
            messagebox.showerror("Error", f"Failed to initialize AR: {e}")
    
    def _show_overlay(self):
        """Show AR overlay"""
        if not self.ar_engine:
            messagebox.showwarning("Warning", "Please initialize AR Engine first")
            return
        
        content = self.content_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Warning", "Please enter overlay content")
            return
        
        try:
            x = float(self.x_var.get())
            y = float(self.y_var.get())
            z = float(self.z_var.get())
            position = (x, y, z)
            
            anchor_id = self.anchor_id_var.get() if self.anchor_id_var.get() else None
            
            self.ar_engine.show_overlay(content, position, anchor_id)
            
            if anchor_id:
                messagebox.showinfo("Success", f"Overlay shown with anchor: {anchor_id}")
            else:
                messagebox.showinfo("Success", "Overlay shown")
        except Exception as e:
            logger.error(f"Error showing overlay: {e}")
            messagebox.showerror("Error", f"Failed to show overlay: {e}")
    
    def _hide_overlay(self):
        """Hide AR overlay"""
        if not self.ar_engine:
            messagebox.showwarning("Warning", "Please initialize AR Engine first")
            return
        
        anchor_id = self.anchor_id_var.get()
        if not anchor_id:
            messagebox.showwarning("Warning", "Please enter anchor ID")
            return
        
        try:
            self.ar_engine.hide_overlay(anchor_id)
            messagebox.showinfo("Success", f"Overlay hidden: {anchor_id}")
        except Exception as e:
            logger.error(f"Error hiding overlay: {e}")
            messagebox.showerror("Error", f"Failed to hide overlay: {e}")

