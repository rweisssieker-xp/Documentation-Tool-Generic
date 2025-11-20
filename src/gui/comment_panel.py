"""
Kommentar-System: Fügt Kommentare zu Schritten hinzu
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import json
import os

from src.utils.logger import get_logger

logger = get_logger(__name__)


class CommentPanel:
    """Panel für Kommentare zu Schritten"""
    
    def __init__(self, parent):
        """
        Initialisiert das Comment Panel
        
        Args:
            parent: Parent-Window
        """
        self.parent = parent
        self.comments: Dict[int, List[Dict]] = {}  # step_number -> List of comments
        self.comments_file = Path("data") / "comments.json"
        self._load_comments()
        
        # Erstelle Panel
        self.panel = ttk.LabelFrame(parent, text="Kommentare", padding="5")
        self.panel.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Erstellt die UI-Komponenten"""
        # Kommentar-Liste
        list_frame = ttk.Frame(self.panel)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.comment_listbox = tk.Listbox(
            list_frame,
            font=("Arial", 9),
            yscrollcommand=scrollbar.set
        )
        self.comment_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.comment_listbox.yview)
        
        self.comment_listbox.bind('<<ListboxSelect>>', self._on_comment_select)
        
        # Kommentar-Eingabe
        input_frame = ttk.Frame(self.panel)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="Kommentar:").pack(anchor=tk.W)
        
        self.comment_text = tk.Text(input_frame, height=3, wrap=tk.WORD)
        self.comment_text.pack(fill=tk.X, pady=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(self.panel)
        button_frame.pack(fill=tk.X)
        
        self.add_button = ttk.Button(
            button_frame,
            text="Hinzufügen",
            command=self._add_comment
        )
        self.add_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.edit_button = ttk.Button(
            button_frame,
            text="Bearbeiten",
            command=self._edit_comment,
            state=tk.DISABLED
        )
        self.edit_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.delete_button = ttk.Button(
            button_frame,
            text="Löschen",
            command=self._delete_comment,
            state=tk.DISABLED
        )
        self.delete_button.pack(side=tk.LEFT)
        
        # Aktueller Schritt
        self.current_step_number = None
    
    def set_current_step(self, step_number: int):
        """
        Setzt aktuellen Schritt für Kommentare
        
        Args:
            step_number: Schritt-Nummer
        """
        self.current_step_number = step_number
        self._update_comment_list()
        self.add_button.config(state=tk.NORMAL)
    
    def _update_comment_list(self):
        """Aktualisiert die Kommentar-Liste"""
        self.comment_listbox.delete(0, tk.END)
        
        if self.current_step_number is None:
            return
        
        step_comments = self.comments.get(self.current_step_number, [])
        
        for comment in step_comments:
            author = comment.get('author', 'Unbekannt')
            timestamp = comment.get('timestamp', '')
            text = comment.get('text', '')
            
            try:
                if timestamp:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime('%d.%m.%Y %H:%M')
                else:
                    time_str = ''
            except:
                time_str = timestamp
            
            display_text = f"[{time_str}] {author}: {text[:50]}"
            self.comment_listbox.insert(tk.END, display_text)
    
    def _add_comment(self):
        """Fügt neuen Kommentar hinzu"""
        if self.current_step_number is None:
            messagebox.showwarning("Kein Schritt", "Bitte wählen Sie zuerst einen Schritt aus.")
            return
        
        comment_text = self.comment_text.get(1.0, tk.END).strip()
        
        if not comment_text:
            messagebox.showwarning("Leerer Kommentar", "Bitte geben Sie einen Kommentar ein.")
            return
        
        comment = {
            'step_number': self.current_step_number,
            'author': os.getenv('USERNAME', 'Unbekannt'),
            'timestamp': datetime.now().isoformat(),
            'text': comment_text
        }
        
        if self.current_step_number not in self.comments:
            self.comments[self.current_step_number] = []
        
        self.comments[self.current_step_number].append(comment)
        
        self._save_comments()
        self._update_comment_list()
        self.comment_text.delete(1.0, tk.END)
        
        logger.info(f"Kommentar hinzugefügt für Schritt {self.current_step_number}")
    
    def _edit_comment(self):
        """Bearbeitet ausgewählten Kommentar"""
        selection = self.comment_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        step_comments = self.comments.get(self.current_step_number, [])
        
        if index >= len(step_comments):
            return
        
        comment = step_comments[index]
        
        # Zeige Edit-Dialog
        edit_text = self.comment_text.get(1.0, tk.END).strip()
        if not edit_text:
            edit_text = comment['text']
        
        # Aktualisiere Kommentar
        comment['text'] = edit_text
        comment['edited'] = True
        comment['edit_timestamp'] = datetime.now().isoformat()
        
        self._save_comments()
        self._update_comment_list()
        self.comment_text.delete(1.0, tk.END)
    
    def _delete_comment(self):
        """Löscht ausgewählten Kommentar"""
        selection = self.comment_listbox.curselection()
        if not selection:
            return
        
        if not messagebox.askyesno("Kommentar löschen", "Möchten Sie diesen Kommentar wirklich löschen?"):
            return
        
        index = selection[0]
        step_comments = self.comments.get(self.current_step_number, [])
        
        if index < len(step_comments):
            del step_comments[index]
            
            if not step_comments:
                del self.comments[self.current_step_number]
            
            self._save_comments()
            self._update_comment_list()
            self.comment_text.delete(1.0, tk.END)
    
    def _on_comment_select(self, event):
        """Wird aufgerufen wenn Kommentar ausgewählt wird"""
        selection = self.comment_listbox.curselection()
        if not selection:
            self.edit_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)
            return
        
        index = selection[0]
        step_comments = self.comments.get(self.current_step_number, [])
        
        if index < len(step_comments):
            comment = step_comments[index]
            self.comment_text.delete(1.0, tk.END)
            self.comment_text.insert(1.0, comment['text'])
            self.edit_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)
    
    def get_comments_for_step(self, step_number: int) -> List[Dict]:
        """
        Gibt Kommentare für einen Schritt zurück
        
        Args:
            step_number: Schritt-Nummer
            
        Returns:
            Liste von Kommentaren
        """
        return self.comments.get(step_number, [])
    
    def get_all_comments(self) -> Dict[int, List[Dict]]:
        """Gibt alle Kommentare zurück"""
        return self.comments.copy()
    
    def _load_comments(self):
        """Lädt Kommentare aus Datei"""
        if not self.comments_file.exists():
            return
        
        try:
            with open(self.comments_file, 'r', encoding='utf-8') as f:
                comments_data = json.load(f)
            
            # Konvertiere Schlüssel zu int
            self.comments = {int(k): v for k, v in comments_data.items()}
        
        except Exception as e:
            logger.warning(f"Fehler beim Laden der Kommentare: {e}", exc_info=True)
            self.comments = {}
    
    def _save_comments(self):
        """Speichert Kommentare in Datei"""
        try:
            self.comments_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.comments_file, 'w', encoding='utf-8') as f:
                json.dump(self.comments, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Kommentare: {e}", exc_info=True)

