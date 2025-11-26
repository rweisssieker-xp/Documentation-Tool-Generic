"""
Dialog für Schritt-Konsolidierung
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import List, Dict, Optional
import threading

from src.ai.step_consolidator import StepConsolidator
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ConsolidationDialog:
    """Dialog für Schritt-Konsolidierung"""
    
    def __init__(self, parent, steps: List[Dict], session_manager):
        """
        Initialisiert den Konsolidierungs-Dialog
        
        Args:
            parent: Parent-Window
            steps: Liste von Schritten
            session_manager: SessionManager-Instanz
        """
        self.parent = parent
        self.original_steps = steps.copy()
        self.current_steps = steps.copy()
        self.session_manager = session_manager
        self.consolidator = StepConsolidator()
        self.suggestions = []
        self.selected_suggestions = []
        
        # Erstelle Dialog-Fenster
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Schritt-Konsolidierung")
        self.dialog.geometry("900x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Zentriere Dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self._setup_ui()
        self._analyze_steps()
    
    def _setup_ui(self):
        """Erstellt die UI-Komponenten"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Info-Label
        info_label = ttk.Label(
            main_frame,
            text="Ähnliche Schritte wurden gefunden. Wählen Sie aus, welche konsolidiert werden sollen:",
            wraplength=850
        )
        info_label.pack(pady=(0, 10))
        
        # Schwellenwert-Einstellung
        threshold_frame = ttk.Frame(main_frame)
        threshold_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(threshold_frame, text="Ähnlichkeits-Schwellenwert:").pack(side=tk.LEFT, padx=(0, 5))
        self.threshold_var = tk.DoubleVar(value=0.85)
        threshold_scale = ttk.Scale(
            threshold_frame,
            from_=0.5,
            to=1.0,
            variable=self.threshold_var,
            orient=tk.HORIZONTAL,
            length=200,
            command=self._on_threshold_change
        )
        threshold_scale.pack(side=tk.LEFT, padx=(0, 5))
        
        self.threshold_label = ttk.Label(threshold_frame, text="0.85")
        self.threshold_label.pack(side=tk.LEFT)
        
        ttk.Button(
            threshold_frame,
            text="Neu analysieren",
            command=self._analyze_steps
        ).pack(side=tk.RIGHT)
        
        # Vorschläge-Liste
        suggestions_frame = ttk.LabelFrame(main_frame, text="Konsolidierungs-Vorschläge", padding="10")
        suggestions_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Scrollbar für Liste
        scroll_frame = ttk.Frame(suggestions_frame)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.suggestions_tree = ttk.Treeview(
            scroll_frame,
            columns=("similarity", "reason"),
            show="tree headings",
            yscrollcommand=scrollbar.set,
            height=15
        )
        self.suggestions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.suggestions_tree.yview)
        
        # Spalten konfigurieren
        self.suggestions_tree.heading("#0", text="Schritte")
        self.suggestions_tree.heading("similarity", text="Ähnlichkeit")
        self.suggestions_tree.heading("reason", text="Grund")
        
        self.suggestions_tree.column("#0", width=300)
        self.suggestions_tree.column("similarity", width=100)
        self.suggestions_tree.column("reason", width=400)
        
        # Vorschau-Frame
        preview_frame = ttk.LabelFrame(main_frame, text="Vorschau der konsolidierten Schritte", padding="10")
        preview_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.preview_text = tk.Text(preview_frame, height=5, wrap=tk.WORD, state=tk.DISABLED)
        self.preview_text.pack(fill=tk.X)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="Ausgewählte konsolidieren",
            command=self._apply_consolidation
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame,
            text="Alle konsolidieren",
            command=self._apply_all_consolidation
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame,
            text="Abbrechen",
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT)
    
    def _on_threshold_change(self, value):
        """Wird aufgerufen wenn Schwellenwert geändert wird"""
        threshold = float(value)
        self.threshold_label.config(text=f"{threshold:.2f}")
        self.consolidator.similarity_threshold = threshold
    
    def _analyze_steps(self):
        """Analysiert Schritte auf Ähnlichkeiten"""
        self.consolidator.similarity_threshold = self.threshold_var.get()
        
        # Starte Analyse in separatem Thread
        thread = threading.Thread(target=self._analyze_thread, daemon=True)
        thread.start()
    
    def _analyze_thread(self):
        """Analyse-Thread"""
        try:
            self.suggestions = self.consolidator.find_similar_steps(self.current_steps)
            
            # Update UI im Hauptthread
            self.dialog.after(0, self._update_suggestions_list)
        
        except Exception as err:
            logger.error(f"Fehler bei Schritt-Analyse: {err}", exc_info=True)
            self.dialog.after(0, lambda err=err: messagebox.showerror("Fehler", f"Analyse fehlgeschlagen:\n{str(err)}"))
    
    def _update_suggestions_list(self):
        """Aktualisiert die Vorschläge-Liste"""
        # Lösche vorhandene Einträge
        for item in self.suggestions_tree.get_children():
            self.suggestions_tree.delete(item)
        
        # Füge Vorschläge hinzu
        for suggestion in self.suggestions:
            step1 = suggestion['step1']
            step2 = suggestion['step2']
            step1_num = step1.get('step_number', suggestion['step1_index'] + 1)
            step2_num = step2.get('step_number', suggestion['step2_index'] + 1)
            
            item_text = f"Schritt {step1_num} ↔ Schritt {step2_num}"
            similarity = suggestion['similarity']
            reason = suggestion['reason']
            
            item_id = self.suggestions_tree.insert(
                "",
                tk.END,
                text=item_text,
                values=(f"{similarity:.1%}", reason),
                tags=("selectable",)
            )
            
            # Markiere als ausgewählt wenn Ähnlichkeit hoch genug
            if similarity >= self.consolidator.similarity_threshold:
                self.suggestions_tree.selection_add(item_id)
        
        # Aktiviere Checkbox-Verhalten
        self.suggestions_tree.tag_configure("selectable", foreground="black")
        
        if not self.suggestions:
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, "Keine ähnlichen Schritte gefunden.")
            self.preview_text.config(state=tk.DISABLED)
    
    def _apply_consolidation(self):
        """Wendet ausgewählte Konsolidierungen an"""
        selected_items = self.suggestions_tree.selection()
        if not selected_items:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie mindestens einen Vorschlag aus.")
            return
        
        # Finde ausgewählte Vorschläge
        selected_suggestions = []
        for item_id in selected_items:
            item_text = self.suggestions_tree.item(item_id, "text")
            # Extrahiere Schritt-Nummern aus Text
            # Format: "Schritt X ↔ Schritt Y"
            parts = item_text.split(" ↔ ")
            if len(parts) == 2:
                step1_num = int(parts[0].split()[-1])
                step2_num = int(parts[1].split()[-1])
                
                # Finde entsprechenden Vorschlag
                for suggestion in self.suggestions:
                    if (suggestion['step1'].get('step_number') == step1_num and
                        suggestion['step2'].get('step_number') == step2_num):
                        selected_suggestions.append(suggestion)
                        break
        
        if not selected_suggestions:
            messagebox.showwarning("Fehler", "Konnte Vorschläge nicht finden.")
            return
        
        # Konsolidiere Schritte
        try:
            consolidated_steps = self.consolidator.consolidate_steps(
                self.current_steps,
                selected_suggestions
            )
            
            # Update Session-Manager
            if self.session_manager:
                self.session_manager._save_history_state()
                with self.session_manager.lock:
                    self.session_manager.steps = consolidated_steps
            
            self.current_steps = consolidated_steps
            
            # Zeige Erfolg
            messagebox.showinfo(
                "Erfolg",
                f"{len(selected_suggestions)} Konsolidierung(en) angewendet.\n"
                f"Schritte: {len(self.original_steps)} → {len(consolidated_steps)}"
            )
            
            self.dialog.destroy()
        
        except Exception as e:
            logger.error(f"Fehler bei Konsolidierung: {e}", exc_info=True)
            messagebox.showerror("Fehler", f"Konsolidierung fehlgeschlagen:\n{str(e)}")
    
    def _apply_all_consolidation(self):
        """Wendet alle Konsolidierungen an"""
        if not self.suggestions:
            messagebox.showinfo("Info", "Keine Vorschläge verfügbar.")
            return
        
        if not messagebox.askyesno(
            "Bestätigung",
            f"Möchten Sie wirklich alle {len(self.suggestions)} Konsolidierungen anwenden?"
        ):
            return
        
        try:
            consolidated_steps = self.consolidator.consolidate_steps(
                self.current_steps,
                self.suggestions
            )
            
            # Update Session-Manager
            if self.session_manager:
                self.session_manager._save_history_state()
                with self.session_manager.lock:
                    self.session_manager.steps = consolidated_steps
            
            self.current_steps = consolidated_steps
            
            # Zeige Erfolg
            messagebox.showinfo(
                "Erfolg",
                f"Alle Konsolidierungen angewendet.\n"
                f"Schritte: {len(self.original_steps)} → {len(consolidated_steps)}"
            )
            
            self.dialog.destroy()
        
        except Exception as e:
            logger.error(f"Fehler bei Konsolidierung: {e}", exc_info=True)
            messagebox.showerror("Fehler", f"Konsolidierung fehlgeschlagen:\n{str(e)}")

