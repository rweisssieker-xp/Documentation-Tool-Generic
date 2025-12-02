"""Universal Data Hub Dialog"""

import tkinter as tk
from tkinter import ttk
from src.data_hub import UniversalDataHub
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataHubDialog:
    """Dialog für Universal Data Hub"""
    
    def __init__(self, parent):
        self.parent = parent
        self.hub = UniversalDataHub()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Universal Data Integration Hub")
        self.dialog.geometry("800x600")
        self._create_widgets()
    
    def _create_widgets(self):
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        connections_frame = ttk.Frame(notebook)
        notebook.add(connections_frame, text="Connections")
        ttk.Label(connections_frame, text="System Connections").pack(pady=10)
