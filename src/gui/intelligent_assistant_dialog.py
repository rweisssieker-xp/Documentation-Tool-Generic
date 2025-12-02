"""Intelligent Assistant Dialog"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from src.intelligent_assistant import IntelligentDocumentationAssistant
from src.utils.logger import get_logger

logger = get_logger(__name__)


class IntelligentAssistantDialog:
    """Dialog für Intelligent Assistant"""
    
    def __init__(self, parent):
        self.parent = parent
        self.assistant = IntelligentDocumentationAssistant("user")
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Intelligent Documentation Assistant")
        self.dialog.geometry("800x600")
        self._create_widgets()
    
    def _create_widgets(self):
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        chat_frame = ttk.Frame(notebook)
        notebook.add(chat_frame, text="Assistant")
        
        self.chat_text = scrolledtext.ScrolledText(chat_frame)
        self.chat_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.input_entry = ttk.Entry(input_frame)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.bind("<Return>", self._send_message)
        
        ttk.Button(input_frame, text="Send", command=self._send_message).pack(side=tk.RIGHT)
    
    def _send_message(self, event=None):
        question = self.input_entry.get()
        if question:
            self.chat_text.insert(tk.END, f"You: {question}\n")
            answer = self.assistant.help(question)
            self.chat_text.insert(tk.END, f"Assistant: {answer}\n")
            self.input_entry.delete(0, tk.END)
