"""
Knowledge Search Dialog - GUI for searching the knowledge base.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
import threading

from src.utils.logger import get_logger

logger = get_logger(__name__)


class KnowledgeSearchDialog(tk.Toplevel):
    """
    Dialog for searching and browsing the knowledge base.
    """
    
    def __init__(self, parent: tk.Widget, knowledge_base=None, rag_engine=None):
        """
        Initialize knowledge search dialog.
        
        Args:
            parent: Parent widget
            knowledge_base: KnowledgeBase instance
            rag_engine: RAGEngine instance for Q&A
        """
        super().__init__(parent)
        
        self.kb = knowledge_base
        self.rag = rag_engine
        
        self.title("🔍 Wissenssuche")
        self.geometry("800x600")
        self.minsize(600, 400)
        
        self._setup_ui()
        self._load_statistics()
    
    def _setup_ui(self):
        """Set up the user interface."""
        # Search frame
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(search_frame, text="Suche:").pack(side=tk.LEFT)
        
        self._search_var = tk.StringVar()
        self._search_entry = ttk.Entry(
            search_frame,
            textvariable=self._search_var,
            width=50
        )
        self._search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self._search_entry.bind("<Return>", lambda e: self._perform_search())
        
        self._search_btn = ttk.Button(
            search_frame,
            text="🔍 Suchen",
            command=self._perform_search
        )
        self._search_btn.pack(side=tk.LEFT, padx=5)
        
        self._ask_btn = ttk.Button(
            search_frame,
            text="❓ Frage stellen",
            command=self._ask_question
        )
        self._ask_btn.pack(side=tk.LEFT, padx=5)
        
        # Options frame
        options_frame = ttk.Frame(self)
        options_frame.pack(fill=tk.X, padx=10)
        
        ttk.Label(options_frame, text="Typ:").pack(side=tk.LEFT)
        
        self._type_var = tk.StringVar(value="Alle")
        type_combo = ttk.Combobox(
            options_frame,
            textvariable=self._type_var,
            values=["Alle", "session", "step", "annotation", "manual"],
            state="readonly",
            width=15
        )
        type_combo.pack(side=tk.LEFT, padx=5)
        
        self._semantic_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Semantische Suche",
            variable=self._semantic_var
        ).pack(side=tk.LEFT, padx=10)
        
        # Results notebook
        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Search results tab
        results_frame = ttk.Frame(self._notebook)
        self._notebook.add(results_frame, text="Suchergebnisse")
        
        self._results_tree = ttk.Treeview(
            results_frame,
            columns=("title", "type", "score"),
            show="headings",
            selectmode="browse"
        )
        self._results_tree.heading("title", text="Titel")
        self._results_tree.heading("type", text="Typ")
        self._results_tree.heading("score", text="Relevanz")
        
        self._results_tree.column("title", width=400)
        self._results_tree.column("type", width=100)
        self._results_tree.column("score", width=100)
        
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self._results_tree.yview)
        self._results_tree.configure(yscrollcommand=scrollbar.set)
        
        self._results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self._results_tree.bind("<Double-1>", self._on_result_double_click)
        
        # Q&A tab
        qa_frame = ttk.Frame(self._notebook)
        self._notebook.add(qa_frame, text="Frage & Antwort")
        
        self._qa_text = tk.Text(qa_frame, wrap=tk.WORD, state=tk.DISABLED)
        self._qa_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Statistics frame
        stats_frame = ttk.Frame(self._notebook)
        self._notebook.add(stats_frame, text="Statistik")
        
        self._stats_text = tk.Text(stats_frame, wrap=tk.WORD, state=tk.DISABLED)
        self._stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self._status_var = tk.StringVar(value="Bereit")
        ttk.Label(self, textvariable=self._status_var).pack(side=tk.BOTTOM, pady=5)
    
    def _perform_search(self):
        """Perform search."""
        query = self._search_var.get().strip()
        if not query:
            messagebox.showwarning("Hinweis", "Bitte Suchbegriff eingeben")
            return
        
        if not self.kb:
            messagebox.showerror("Fehler", "Knowledge Base nicht verfügbar")
            return
        
        self._status_var.set("Suche läuft...")
        self._search_btn.configure(state=tk.DISABLED)
        
        # Run search in background
        threading.Thread(
            target=self._run_search,
            args=(query,),
            daemon=True
        ).start()
    
    def _run_search(self, query: str):
        """Run search in background."""
        try:
            doc_type = None if self._type_var.get() == "Alle" else self._type_var.get()
            
            results = self.kb.search(
                query=query,
                doc_type=doc_type,
                semantic=self._semantic_var.get(),
                limit=50
            )
            
            self.after(0, lambda: self._display_results(results))
        
        except Exception as e:
            logger.error(f"Search failed: {e}")
            self.after(0, lambda: messagebox.showerror("Fehler", f"Suche fehlgeschlagen:\n{e}"))
        
        finally:
            self.after(0, lambda: self._search_btn.configure(state=tk.NORMAL))
            self.after(0, lambda: self._status_var.set("Bereit"))
    
    def _display_results(self, results: List):
        """Display search results."""
        # Clear existing results
        for item in self._results_tree.get_children():
            self._results_tree.delete(item)
        
        # Add new results
        for result in results:
            doc = result.document
            score_str = f"{result.score:.0%}"
            
            self._results_tree.insert(
                "",
                tk.END,
                values=(doc.title, doc.doc_type, score_str),
                tags=(doc.id,)
            )
        
        self._status_var.set(f"{len(results)} Ergebnisse gefunden")
        self._notebook.select(0)  # Switch to results tab
    
    def _ask_question(self):
        """Ask a question using RAG."""
        question = self._search_var.get().strip()
        if not question:
            messagebox.showwarning("Hinweis", "Bitte Frage eingeben")
            return
        
        if not self.rag:
            messagebox.showerror("Fehler", "RAG Engine nicht verfügbar")
            return
        
        self._status_var.set("Verarbeite Frage...")
        self._ask_btn.configure(state=tk.DISABLED)
        
        # Run Q&A in background
        threading.Thread(
            target=self._run_qa,
            args=(question,),
            daemon=True
        ).start()
    
    def _run_qa(self, question: str):
        """Run Q&A in background."""
        try:
            response = self.rag.query(question)
            self.after(0, lambda: self._display_answer(question, response))
        
        except Exception as e:
            logger.error(f"Q&A failed: {e}")
            self.after(0, lambda: messagebox.showerror("Fehler", f"Q&A fehlgeschlagen:\n{e}"))
        
        finally:
            self.after(0, lambda: self._ask_btn.configure(state=tk.NORMAL))
            self.after(0, lambda: self._status_var.set("Bereit"))
    
    def _display_answer(self, question: str, response):
        """Display Q&A response."""
        self._qa_text.configure(state=tk.NORMAL)
        self._qa_text.delete(1.0, tk.END)
        
        text = f"❓ FRAGE:\n{question}\n\n"
        text += f"💡 ANTWORT:\n{response.answer}\n\n"
        text += f"📊 Konfidenz: {response.confidence:.0%}\n\n"
        
        if response.sources:
            text += "📚 QUELLEN:\n"
            for source in response.sources:
                text += f"  • {source.get('title', 'Unbekannt')} ({source.get('score', 0):.0%})\n"
        
        self._qa_text.insert(tk.END, text)
        self._qa_text.configure(state=tk.DISABLED)
        
        self._notebook.select(1)  # Switch to Q&A tab
    
    def _on_result_double_click(self, event):
        """Handle double-click on result."""
        selection = self._results_tree.selection()
        if not selection:
            return
        
        # Get document ID from tags
        item = selection[0]
        tags = self._results_tree.item(item, "tags")
        
        if tags and self.kb:
            doc_id = tags[0]
            doc = self.kb.get_document(doc_id)
            
            if doc:
                self._show_document_details(doc)
    
    def _show_document_details(self, doc):
        """Show document details in popup."""
        detail_window = tk.Toplevel(self)
        detail_window.title(doc.title)
        detail_window.geometry("600x400")
        
        text = tk.Text(detail_window, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        content = f"📄 {doc.title}\n"
        content += f"{'=' * 50}\n\n"
        content += f"Typ: {doc.doc_type}\n"
        content += f"Erstellt: {doc.created_at}\n\n"
        content += f"Inhalt:\n{doc.content}\n\n"
        
        if doc.tags:
            content += f"Tags: {', '.join(doc.tags)}\n"
        
        text.insert(tk.END, content)
        text.configure(state=tk.DISABLED)
    
    def _load_statistics(self):
        """Load and display statistics."""
        if not self.kb:
            return
        
        try:
            stats = self.kb.get_statistics()
            
            self._stats_text.configure(state=tk.NORMAL)
            self._stats_text.delete(1.0, tk.END)
            
            text = "📊 KNOWLEDGE BASE STATISTIK\n"
            text += "=" * 40 + "\n\n"
            text += f"📚 Gesamte Dokumente: {stats.get('total_documents', 0)}\n"
            text += f"📁 Sessions: {stats.get('total_sessions', 0)}\n"
            text += f"🏷️ Einzigartige Tags: {stats.get('unique_tags', 0)}\n\n"
            
            if stats.get('documents_by_type'):
                text += "Dokumente nach Typ:\n"
                for doc_type, count in stats['documents_by_type'].items():
                    text += f"  • {doc_type}: {count}\n"
            
            self._stats_text.insert(tk.END, text)
            self._stats_text.configure(state=tk.DISABLED)
        
        except Exception as e:
            logger.error(f"Failed to load statistics: {e}")

