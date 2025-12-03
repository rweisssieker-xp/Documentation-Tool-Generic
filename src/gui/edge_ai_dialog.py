"""
Edge AI Dialog - GUI für Edge AI Engine
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional

from src.edge_ai import EdgeAIEngine, ModelType
from src.utils.logger import get_logger

logger = get_logger(__name__)


class EdgeAIDialog:
    """Dialog for Edge AI Engine configuration"""
    
    def __init__(self, parent):
        """
        Initialize Edge AI Dialog.
        
        Args:
            parent: Parent window
        """
        self.parent = parent
        self.engine = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edge AI Engine")
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
        
        # Test Tab
        test_frame = ttk.Frame(notebook)
        notebook.add(test_frame, text="Test")
        self._create_test_tab(test_frame)
    
    def _create_config_tab(self, parent):
        """Create configuration tab"""
        # Model Type
        model_frame = ttk.LabelFrame(parent, text="Model Selection")
        model_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.model_type_var = tk.StringVar(value="llama")
        ttk.Radiobutton(model_frame, text="Llama", variable=self.model_type_var, value="llama").pack(anchor=tk.W, padx=5)
        ttk.Radiobutton(model_frame, text="Mistral", variable=self.model_type_var, value="mistral").pack(anchor=tk.W, padx=5)
        
        # Model Path
        path_frame = ttk.Frame(parent)
        path_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(path_frame, text="Model Path:").pack(side=tk.LEFT)
        self.model_path_var = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.model_path_var, width=40).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Use GPU
        self.use_gpu_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, text="Use GPU Acceleration", variable=self.use_gpu_var).pack(anchor=tk.W, padx=10, pady=5)
        
        # Initialize Button
        ttk.Button(parent, text="Initialize Engine", command=self._initialize_engine).pack(pady=10)
        
        # Status
        status_frame = ttk.LabelFrame(parent, text="Status")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=10, wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.status_text.insert(tk.END, "Edge AI Engine Status\n")
        self.status_text.insert(tk.END, "=" * 50 + "\n")
        self.status_text.insert(tk.END, "Status: Not Initialized\n")
    
    def _create_test_tab(self, parent):
        """Create test tab"""
        # Text Generation
        text_frame = ttk.LabelFrame(parent, text="Text Generation")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ttk.Label(text_frame, text="Prompt:").pack(anchor=tk.W, padx=5, pady=2)
        self.prompt_text = scrolledtext.ScrolledText(text_frame, height=5, wrap=tk.WORD)
        self.prompt_text.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(text_frame, text="Generate", command=self._generate_text).pack(pady=5)
        
        ttk.Label(text_frame, text="Generated Text:").pack(anchor=tk.W, padx=5, pady=2)
        self.generated_text = scrolledtext.ScrolledText(text_frame, height=10, wrap=tk.WORD)
        self.generated_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
    
    def _initialize_engine(self):
        """Initialize Edge AI Engine"""
        try:
            model_type_str = self.model_type_var.get()
            model_type = ModelType.LLAMA if model_type_str == "llama" else ModelType.MISTRAL
            model_path = self.model_path_var.get() if self.model_path_var.get() else None
            
            self.engine = EdgeAIEngine(
                model_type=model_type,
                model_path=model_path,
                use_gpu=self.use_gpu_var.get(),
            )
            
            available = self.engine.is_available()
            
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, "Edge AI Engine Status\n")
            self.status_text.insert(tk.END, "=" * 50 + "\n")
            self.status_text.insert(tk.END, f"Status: {'Initialized' if available else 'Not Available'}\n")
            self.status_text.insert(tk.END, f"Model Type: {model_type_str}\n")
            self.status_text.insert(tk.END, f"Model Path: {model_path or 'Default'}\n")
            self.status_text.insert(tk.END, f"GPU: {'Enabled' if self.use_gpu_var.get() else 'Disabled'}\n")
            
            if available:
                messagebox.showinfo("Success", "Edge AI Engine initialized successfully")
            else:
                messagebox.showwarning("Warning", "Edge AI Engine initialized but models not available")
        except Exception as e:
            logger.error(f"Error initializing engine: {e}")
            messagebox.showerror("Error", f"Failed to initialize engine: {e}")
    
    def _generate_text(self):
        """Generate text using Edge AI"""
        if not self.engine or not self.engine.is_available():
            messagebox.showwarning("Warning", "Please initialize Edge AI Engine first")
            return
        
        prompt = self.prompt_text.get(1.0, tk.END).strip()
        if not prompt:
            messagebox.showwarning("Warning", "Please enter a prompt")
            return
        
        try:
            generated = self.engine.generate_text(prompt, max_tokens=200)
            self.generated_text.delete(1.0, tk.END)
            self.generated_text.insert(tk.END, generated)
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            messagebox.showerror("Error", f"Failed to generate text: {e}")





