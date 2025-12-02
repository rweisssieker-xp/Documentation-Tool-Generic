"""Agentic Documentation Automation Dialog"""

import tkinter as tk
from tkinter import ttk, messagebox
from src.agentic import AgentOrchestrator
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AgenticDialog:
    """Dialog für Agentic Automation"""
    
    def __init__(self, parent):
        self.parent = parent
        self.orchestrator = AgentOrchestrator()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Agentic Documentation Automation")
        self.dialog.geometry("800x600")
        self._create_widgets()
    
    def _create_widgets(self):
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Agents Tab
        agents_frame = ttk.Frame(notebook)
        notebook.add(agents_frame, text="Agents")
        self._create_agents_tab(agents_frame)
        
        # Tasks Tab
        tasks_frame = ttk.Frame(notebook)
        notebook.add(tasks_frame, text="Tasks")
        self._create_tasks_tab(tasks_frame)
    
    def _create_agents_tab(self, parent):
        ttk.Label(parent, text="Available Agents").pack(pady=10)
        agents_list = ttk.Treeview(parent)
        agents_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        agents_list.insert("", "end", values=("Documentation Agent", "Active"))
        agents_list.insert("", "end", values=("Update Agent", "Active"))
        agents_list.insert("", "end", values=("Quality Agent", "Active"))
    
    def _create_tasks_tab(self, parent):
        ttk.Label(parent, text="Task Execution").pack(pady=10)
        ttk.Button(parent, text="Execute Task", command=self._execute_task).pack(pady=5)
    
    def _execute_task(self):
        result = self.orchestrator.execute_task('documentation', {'type': 'generate'})
        if result:
            messagebox.showinfo("Success", "Task executed")
        else:
            messagebox.showerror("Error", "Task failed")
