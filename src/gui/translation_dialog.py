"""
Translation Dialog - GUI for Intelligent Translation Hub
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from pathlib import Path
from typing import Optional, Dict, Any

from src.translation import TranslationHub, GlossaryManager, TranslationMemory
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TranslationDialog:
    """Dialog for translation management."""
    
    def __init__(self, parent, project_name: str = "default"):
        """
        Initialize translation dialog.
        
        Args:
            parent: Parent window
            project_name: Project name
        """
        self.parent = parent
        self.project_name = project_name
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Intelligent Translation Hub")
        self.dialog.geometry("900x700")
        self.dialog.transient(parent)
        
        self.hub = TranslationHub(project_name)
        
        self._create_widgets()
        self._load_glossary()
    
    def _create_widgets(self):
        """Create dialog widgets."""
        # Notebook for tabs
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Translation tab
        trans_frame = ttk.Frame(notebook)
        notebook.add(trans_frame, text="Übersetzung")
        self._create_translation_tab(trans_frame)
        
        # Glossary tab
        glossary_frame = ttk.Frame(notebook)
        notebook.add(glossary_frame, text="Glossar")
        self._create_glossary_tab(glossary_frame)
        
        # Translation Memory tab
        tm_frame = ttk.Frame(notebook)
        notebook.add(tm_frame, text="Translation Memory")
        self._create_tm_tab(tm_frame)
        
        # Review tab
        review_frame = ttk.Frame(notebook)
        notebook.add(review_frame, text="Review")
        self._create_review_tab(review_frame)
    
    def _create_translation_tab(self, parent):
        """Create translation tab."""
        # Source
        ttk.Label(parent, text="Quelltext:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.source_text = scrolledtext.ScrolledText(parent, width=60, height=10)
        self.source_text.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # Languages
        lang_frame = ttk.Frame(parent)
        lang_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        
        ttk.Label(lang_frame, text="Von:").pack(side=tk.LEFT, padx=5)
        self.source_lang_var = tk.StringVar(value="de")
        ttk.Combobox(lang_frame, textvariable=self.source_lang_var, values=["de", "en", "fr", "es"], state="readonly", width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(lang_frame, text="Nach:").pack(side=tk.LEFT, padx=5)
        self.target_lang_var = tk.StringVar(value="en")
        ttk.Combobox(lang_frame, textvariable=self.target_lang_var, values=["de", "en", "fr", "es"], state="readonly", width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(lang_frame, text="Übersetzen", command=self._translate).pack(side=tk.LEFT, padx=10)
        
        # Target
        ttk.Label(parent, text="Übersetzung:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.target_text = scrolledtext.ScrolledText(parent, width=60, height=10)
        self.target_text.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # Buttons
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=5, column=0, columnspan=2, padx=5, pady=10)
        
        ttk.Button(button_frame, text="Speichern", command=self._save_translation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Zur Review", command=self._submit_review).pack(side=tk.LEFT, padx=5)
    
    def _create_glossary_tab(self, parent):
        """Create glossary tab."""
        # Add term
        add_frame = ttk.LabelFrame(parent, text="Neuer Begriff")
        add_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Quellbegriff:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.term_source_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.term_source_var, width=20).grid(row=0, column=1, padx=5)
        
        ttk.Label(add_frame, text="Sprache:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.term_lang_var = tk.StringVar(value="en")
        ttk.Combobox(add_frame, textvariable=self.term_lang_var, values=["de", "en", "fr", "es"], state="readonly", width=5).grid(row=0, column=3, padx=5)
        
        ttk.Label(add_frame, text="Übersetzung:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.term_target_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.term_target_var, width=20).grid(row=1, column=1, padx=5)
        
        ttk.Button(add_frame, text="Hinzufügen", command=self._add_term).grid(row=1, column=2, columnspan=2, padx=5)
        
        # Glossary list
        list_frame = ttk.LabelFrame(parent, text="Glossar")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("Source", "Target", "Language")
        self.glossary_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.glossary_tree.heading(col, text=col)
            self.glossary_tree.column(col, width=200)
        self.glossary_tree.pack(fill=tk.BOTH, expand=True)
    
    def _create_tm_tab(self, parent):
        """Create translation memory tab."""
        # Search
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Suche:").pack(side=tk.LEFT, padx=5)
        self.tm_search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.tm_search_var, width=30).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Suchen", command=self._search_tm).pack(side=tk.LEFT, padx=5)
        
        # TM list
        tm_frame = ttk.LabelFrame(parent, text="Translation Memory")
        tm_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("Source", "Target", "Quality", "Usage")
        self.tm_tree = ttk.Treeview(tm_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tm_tree.heading(col, text=col)
            self.tm_tree.column(col, width=150)
        self.tm_tree.pack(fill=tk.BOTH, expand=True)
        
        # Stats
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.tm_stats_label = ttk.Label(stats_frame, text="")
        self.tm_stats_label.pack()
        self._update_tm_stats()
    
    def _create_review_tab(self, parent):
        """Create review tab."""
        # Pending reviews
        pending_frame = ttk.LabelFrame(parent, text="Ausstehende Reviews")
        pending_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("ID", "Source", "Target", "Status")
        self.review_tree = ttk.Treeview(pending_frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.review_tree.heading(col, text=col)
            self.review_tree.column(col, width=150)
        self.review_tree.pack(fill=tk.BOTH, expand=True)
        
        # Review actions
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(action_frame, text="Genehmigen", command=self._approve_review).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Ablehnen", command=self._reject_review).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Aktualisieren", command=self._refresh_reviews).pack(side=tk.LEFT, padx=5)
    
    def _translate(self):
        """Translate text."""
        source = self.source_text.get(1.0, tk.END).strip()
        if not source:
            messagebox.showwarning("Warnung", "Bitte geben Sie einen Text ein")
            return
        
        try:
            translated = self.hub.translate_document(
                source,
                self.source_lang_var.get(),
                self.target_lang_var.get()
            )
            self.target_text.delete(1.0, tk.END)
            self.target_text.insert(1.0, translated)
        except Exception as e:
            logger.error(f"Translation error: {e}")
            messagebox.showerror("Fehler", f"Übersetzung fehlgeschlagen:\n{e}")
    
    def _add_term(self):
        """Add glossary term."""
        source = self.term_source_var.get().strip()
        target = self.term_target_var.get().strip()
        lang = self.term_lang_var.get()
        
        if not source or not target:
            messagebox.showwarning("Warnung", "Bitte füllen Sie alle Felder aus")
            return
        
        try:
            self.hub.add_glossary_term(source, lang, target)
            self.term_source_var.set("")
            self.term_target_var.set("")
            self._load_glossary()
            messagebox.showinfo("Erfolg", "Begriff hinzugefügt")
        except Exception as e:
            logger.error(f"Error adding term: {e}")
            messagebox.showerror("Fehler", f"Fehler:\n{e}")
    
    def _load_glossary(self):
        """Load glossary terms."""
        self.glossary_tree.delete(*self.glossary_tree.get_children())
        terms = self.hub.glossary_manager.get_all_terms(self.project_name)
        for term in terms:
            for lang, target in term.target_terms.items():
                self.glossary_tree.insert("", tk.END, values=(term.source_term, target, lang))
    
    def _search_tm(self):
        """Search translation memory."""
        query = self.tm_search_var.get().strip()
        if not query:
            return
        
        self.tm_tree.delete(*self.tm_tree.get_children())
        matches = self.hub.translation_memory.find_fuzzy_match(
            query,
            self.source_lang_var.get(),
            self.target_lang_var.get(),
            similarity_threshold=0.5
        )
        
        for unit, similarity in matches[:20]:
            self.tm_tree.insert("", tk.END, values=(
                unit.source_text[:50],
                unit.target_text[:50],
                f"{unit.quality_score:.2f}",
                unit.usage_count
            ))
    
    def _update_tm_stats(self):
        """Update TM statistics."""
        stats = self.hub.translation_memory.get_statistics()
        self.tm_stats_label.config(
            text=f"Total Units: {stats['total_units']} | "
                 f"Total Usage: {stats['total_usage']} | "
                 f"Avg Quality: {stats['avg_quality']:.2f}"
        )
    
    def _save_translation(self):
        """Save translation to memory."""
        source = self.source_text.get(1.0, tk.END).strip()
        target = self.target_text.get(1.0, tk.END).strip()
        
        if not source or not target:
            messagebox.showwarning("Warnung", "Bitte geben Sie Quelle und Ziel ein")
            return
        
        try:
            self.hub.translation_memory.add_translation(
                source,
                target,
                self.source_lang_var.get(),
                self.target_lang_var.get()
            )
            messagebox.showinfo("Erfolg", "Übersetzung gespeichert")
            self._update_tm_stats()
        except Exception as e:
            logger.error(f"Error saving translation: {e}")
    
    def _submit_review(self):
        """Submit translation for review."""
        source = self.source_text.get(1.0, tk.END).strip()
        target = self.target_text.get(1.0, tk.END).strip()
        
        if not source or not target:
            messagebox.showwarning("Warnung", "Bitte geben Sie Quelle und Ziel ein")
            return
        
        try:
            import uuid
            trans_id = str(uuid.uuid4())[:8]
            self.hub.review_workflow.submit_for_review(trans_id, source, target)
            messagebox.showinfo("Erfolg", f"Zur Review eingereicht: {trans_id}")
            self._refresh_reviews()
        except Exception as e:
            logger.error(f"Error submitting review: {e}")
    
    def _refresh_reviews(self):
        """Refresh review list."""
        self.review_tree.delete(*self.review_tree.get_children())
        pending = self.hub.review_workflow.get_pending_reviews()
        for review in pending:
            self.review_tree.insert("", tk.END, values=(
                review.translation_id,
                review.source_text[:30],
                review.translated_text[:30],
                review.status.value
            ))
    
    def _approve_review(self):
        """Approve selected review."""
        selection = self.review_tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Review aus")
            return
        
        item = self.review_tree.item(selection[0])
        trans_id = item['values'][0]
        
        try:
            from src.translation.review_workflow import ReviewStatus
            self.hub.review_workflow.review_translation(trans_id, "User", ReviewStatus.APPROVED)
            messagebox.showinfo("Erfolg", "Review genehmigt")
            self._refresh_reviews()
        except Exception as e:
            logger.error(f"Error approving review: {e}")
    
    def _reject_review(self):
        """Reject selected review."""
        selection = self.review_tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Review aus")
            return
        
        item = self.review_tree.item(selection[0])
        trans_id = item['values'][0]
        
        try:
            from src.translation.review_workflow import ReviewStatus
            self.hub.review_workflow.review_translation(trans_id, "User", ReviewStatus.REJECTED, "Rejected by user")
            messagebox.showinfo("Erfolg", "Review abgelehnt")
            self._refresh_reviews()
        except Exception as e:
            logger.error(f"Error rejecting review: {e}")

