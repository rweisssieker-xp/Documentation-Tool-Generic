"""Self-Learning AI Engine Dialog"""

import tkinter as tk
from tkinter import ttk, messagebox
from src.self_learning import SelfLearningEngine
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SelfLearningDialog:
    """Dialog für Self-Learning AI Engine"""
    
    def __init__(self, parent):
        self.parent = parent
        self.engine = SelfLearningEngine()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Self-Learning AI Engine")
        self.dialog.geometry("800x600")
        self._create_widgets()
    
    def _create_widgets(self):
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Learning Tab
        learning_frame = ttk.Frame(notebook)
        notebook.add(learning_frame, text="Learning")
        self._create_learning_tab(learning_frame)
        
        # Style Tab
        style_frame = ttk.Frame(notebook)
        notebook.add(style_frame, text="Style")
        self._create_style_tab(style_frame)
        
        # Patterns Tab
        patterns_frame = ttk.Frame(notebook)
        notebook.add(patterns_frame, text="Patterns")
        self._create_patterns_tab(patterns_frame)
    
    def _create_learning_tab(self, parent):
        ttk.Label(parent, text="Learning Configuration").pack(pady=10)
        ttk.Button(parent, text="Load Models", command=self._load_models).pack(pady=5)
        ttk.Button(parent, text="Save Models", command=self._save_models).pack(pady=5)
    
    def _create_style_tab(self, parent):
        ttk.Label(parent, text="Style Transfer").pack(pady=10)
    
    def _create_patterns_tab(self, parent):
        ttk.Label(parent, text="Pattern Learning").pack(pady=10)
    
    def _load_models(self):
        if self.engine.load_models():
            messagebox.showinfo("Success", "Models loaded")
        else:
            messagebox.showerror("Error", "Failed to load models")
    
    def _save_models(self):
        if self.engine.save_models():
            messagebox.showinfo("Success", "Models saved")
        else:
            messagebox.showerror("Error", "Failed to save models")
