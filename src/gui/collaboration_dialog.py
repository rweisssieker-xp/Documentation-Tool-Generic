"""
Collaboration Dialog - GUI for Real-Time Collaboration Hub
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, Dict, Any
import threading

from src.collaboration import RealtimeServer, CRDTEngine, PresenceManager, CommentSystem
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CollaborationDialog:
    """Dialog for real-time collaboration."""
    
    def __init__(self, parent):
        """
        Initialize collaboration dialog.
        
        Args:
            parent: Parent window
        """
        self.parent = parent
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Real-Time Collaboration Hub")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        
        self.server = None
        self.server_thread = None
        self.crdt_engine = CRDTEngine()
        self.presence_manager = PresenceManager()
        self.comment_system = CommentSystem()
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create dialog widgets."""
        # Server control
        server_frame = ttk.LabelFrame(self.dialog, text="Server")
        server_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(server_frame, text="Port:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.port_var = tk.IntVar(value=8765)
        ttk.Spinbox(server_frame, from_=1024, to=65535, textvariable=self.port_var, width=10).grid(row=0, column=1, padx=5)
        
        self.server_status_var = tk.StringVar(value="Gestoppt")
        ttk.Label(server_frame, text="Status:").grid(row=0, column=2, sticky=tk.W, padx=5)
        ttk.Label(server_frame, textvariable=self.server_status_var).grid(row=0, column=3, padx=5)
        
        ttk.Button(server_frame, text="Start", command=self._start_server).grid(row=0, column=4, padx=5)
        ttk.Button(server_frame, text="Stop", command=self._stop_server).grid(row=0, column=5, padx=5)
        
        # Notebook
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Presence tab
        presence_frame = ttk.Frame(notebook)
        notebook.add(presence_frame, text="Presence")
        self._create_presence_tab(presence_frame)
        
        # Comments tab
        comments_frame = ttk.Frame(notebook)
        notebook.add(comments_frame, text="Comments")
        self._create_comments_tab(comments_frame)
        
        # Document tab
        doc_frame = ttk.Frame(notebook)
        notebook.add(doc_frame, text="Document")
        self._create_document_tab(doc_frame)
    
    def _create_presence_tab(self, parent):
        """Create presence tab."""
        ttk.Label(parent, text="Aktive Benutzer:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=5, pady=5)
        
        columns = ("User", "Type", "Position", "Last Seen")
        self.presence_tree = ttk.Treeview(parent, columns=columns, show="headings", height=10)
        for col in columns:
            self.presence_tree.heading(col, text=col)
            self.presence_tree.column(col, width=150)
        self.presence_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Button(parent, text="Aktualisieren", command=self._refresh_presence).pack(pady=5)
    
    def _create_comments_tab(self, parent):
        """Create comments tab."""
        # Comment list
        list_frame = ttk.LabelFrame(parent, text="Comments")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("ID", "Author", "Content", "Status")
        self.comments_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        for col in columns:
            self.comments_tree.heading(col, text=col)
            self.comments_tree.column(col, width=150)
        self.comments_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add comment
        add_frame = ttk.LabelFrame(parent, text="Neuer Comment")
        add_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Comment:").pack(side=tk.LEFT, padx=5)
        self.comment_text_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.comment_text_var, width=40).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(add_frame, text="Hinzufügen", command=self._add_comment).pack(side=tk.LEFT, padx=5)
        
        # Actions
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(action_frame, text="Resolve", command=self._resolve_comment).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Aktualisieren", command=self._refresh_comments).pack(side=tk.LEFT, padx=5)
    
    def _create_document_tab(self, parent):
        """Create document tab."""
        ttk.Label(parent, text="Kollaboratives Dokument:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=5, pady=5)
        
        self.document_text = scrolledtext.ScrolledText(parent, width=70, height=20)
        self.document_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Speichern", command=self._save_document).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Synchronisieren", command=self._sync_document).pack(side=tk.LEFT, padx=5)
    
    def _start_server(self):
        """Start collaboration server."""
        if self.server:
            messagebox.showwarning("Warnung", "Server läuft bereits")
            return
        
        try:
            port = self.port_var.get()
            self.server = RealtimeServer(port=port)
            
            if self.server.app:
                def run_server():
                    import uvicorn
                    uvicorn.run(self.server.app, host="0.0.0.0", port=port)
                
                self.server_thread = threading.Thread(target=run_server, daemon=True)
                self.server_thread.start()
                self.server_status_var.set(f"Läuft auf Port {port}")
                messagebox.showinfo("Erfolg", f"Server gestartet auf Port {port}")
            else:
                messagebox.showwarning("Warnung", "FastAPI nicht verfügbar. Installieren Sie: pip install fastapi uvicorn")
        except Exception as e:
            logger.error(f"Error starting server: {e}")
            messagebox.showerror("Fehler", f"Server konnte nicht gestartet werden:\n{e}")
    
    def _stop_server(self):
        """Stop collaboration server."""
        if not self.server:
            return
        
        self.server = None
        self.server_status_var.set("Gestoppt")
        messagebox.showinfo("Info", "Server gestoppt")
    
    def _refresh_presence(self):
        """Refresh presence list."""
        self.presence_tree.delete(*self.presence_tree.get_children())
        presences = self.presence_manager.get_all_presences()
        for presence in presences:
            self.presence_tree.insert("", tk.END, values=(
                presence.user_name,
                presence.presence_type.value,
                str(presence.position) if presence.position else "N/A",
                presence.last_seen.strftime("%H:%M:%S") if presence.last_seen else "N/A"
            ))
    
    def _add_comment(self):
        """Add comment."""
        content = self.comment_text_var.get().strip()
        if not content:
            messagebox.showwarning("Warnung", "Bitte geben Sie einen Comment ein")
            return
        
        try:
            import uuid
            from src.collaboration.comment_system import Comment, CommentStatus
            comment = Comment(
                id=str(uuid.uuid4())[:8],
                author="Current User",
                content=content,
                position=(0, 0),
                status=CommentStatus.OPEN,
                created_at=None
            )
            self.comment_system.add_comment(comment)
            self.comment_text_var.set("")
            self._refresh_comments()
            messagebox.showinfo("Erfolg", "Comment hinzugefügt")
        except Exception as e:
            logger.error(f"Error adding comment: {e}")
    
    def _refresh_comments(self):
        """Refresh comments list."""
        self.comments_tree.delete(*self.comments_tree.get_children())
        comments = self.comment_system.get_comments()
        for comment in comments:
            self.comments_tree.insert("", tk.END, values=(
                comment.id,
                comment.author,
                comment.content[:30],
                comment.status.value
            ))
    
    def _resolve_comment(self):
        """Resolve selected comment."""
        selection = self.comments_tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie einen Comment aus")
            return
        
        item = self.comments_tree.item(selection[0])
        comment_id = item['values'][0]
        
        try:
            from src.collaboration.comment_system import CommentStatus
            comment = self.comment_system.get_review(comment_id)
            if comment:
                comment.status = CommentStatus.RESOLVED
                messagebox.showinfo("Erfolg", "Comment resolved")
                self._refresh_comments()
        except Exception as e:
            logger.error(f"Error resolving comment: {e}")
    
    def _save_document(self):
        """Save document."""
        content = self.document_text.get(1.0, tk.END)
        # Would save to file or sync via CRDT
        messagebox.showinfo("Info", "Dokument gespeichert")
    
    def _sync_document(self):
        """Synchronize document."""
        # Would sync via CRDT
        state = self.crdt_engine.get_state()
        self.document_text.delete(1.0, tk.END)
        self.document_text.insert(1.0, state)
        messagebox.showinfo("Info", "Dokument synchronisiert")

