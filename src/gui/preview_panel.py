"""
Preview-Panel für Live-Vorschau der erfassten Schritte
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Dict
from PIL import Image, ImageTk

from src.gui.comment_panel import CommentPanel


class PreviewPanel:
    """Panel zur Anzeige der erfassten Schritte"""
    
    def __init__(self, parent):
        """
        Initialisiert das Preview-Panel
        
        Args:
            parent: Parent-Widget
        """
        self.parent = parent
        self.steps = []
        
        # Erstelle Hauptframe das als Widget verwendet werden kann
        self.main_frame = ttk.Frame(self.parent)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Erstellt die UI-Komponenten"""
        # Hauptframe
        main_frame = self.main_frame
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Splitter für zwei Bereiche
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Konfiguriere Grid-Gewichtung für main_frame
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Linke Seite: Schritt-Liste
        list_frame = ttk.Frame(paned)
        paned.add(list_frame, weight=1)
        
        # Kopfzeile mit Label und Löschen-Button
        list_header = ttk.Frame(list_frame)
        list_header.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(list_header, text="Erfasste Schritte:", font=("Arial", 10, "bold")).pack(
            side=tk.LEFT
        )
        
        self.delete_step_button = ttk.Button(
            list_header,
            text="Löschen",
            command=self._delete_selected_step,
            state=tk.DISABLED
        )
        self.delete_step_button.pack(side=tk.RIGHT)
        
        # Verschieben-Buttons
        self.move_up_button = ttk.Button(
            list_header,
            text="↑",
            command=self._move_step_up,
            state=tk.DISABLED,
            width=3
        )
        self.move_up_button.pack(side=tk.RIGHT, padx=(0, 5))
        
        self.move_down_button = ttk.Button(
            list_header,
            text="↓",
            command=self._move_step_down,
            state=tk.DISABLED,
            width=3
        )
        self.move_down_button.pack(side=tk.RIGHT, padx=(0, 5))
        
        self.reorder_callback = None  # Wird von außen gesetzt
        
        # Liste mit Scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.steps_listbox = tk.Listbox(list_container, font=("Arial", 9))
        self.steps_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        list_scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.steps_listbox.yview)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.steps_listbox.config(yscrollcommand=list_scrollbar.set)
        
        self.steps_listbox.bind('<<ListboxSelect>>', self._on_step_select)
        self.delete_callback = None  # Wird von außen gesetzt
        
        # Rechte Seite: Schritt-Details
        detail_frame = ttk.Frame(paned)
        paned.add(detail_frame, weight=2)
        
        ttk.Label(detail_frame, text="Schritt-Details:", font=("Arial", 10, "bold")).pack(
            anchor=tk.W, padx=5, pady=5
        )
        
        # Screenshot-Anzeige
        self.screenshot_label = ttk.Label(detail_frame, text="Kein Screenshot verfügbar")
        self.screenshot_label.pack(padx=5, pady=5)
        
        # Beschreibung
        desc_frame = ttk.LabelFrame(detail_frame, text="Beschreibung", padding="5")
        desc_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.description_text = tk.Text(desc_frame, wrap=tk.WORD, height=10, state=tk.DISABLED)
        self.description_text.pack(fill=tk.BOTH, expand=True)
        
        desc_scrollbar = ttk.Scrollbar(desc_frame, orient=tk.VERTICAL, command=self.description_text.yview)
        desc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.description_text.config(yscrollcommand=desc_scrollbar.set)
        
        # Metadaten
        meta_frame = ttk.LabelFrame(detail_frame, text="Metadaten", padding="5")
        meta_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.metadata_text = tk.Text(meta_frame, wrap=tk.WORD, height=4, state=tk.DISABLED)
        self.metadata_text.pack(fill=tk.X)
        
        # Qualitäts-Indikatoren
        quality_frame = ttk.LabelFrame(detail_frame, text="Qualitäts-Indikatoren", padding="5")
        quality_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.quality_indicators_frame = ttk.Frame(quality_frame)
        self.quality_indicators_frame.pack(fill=tk.X)
        
        # UI-Element-Vorschau (falls aktiviert)
        self.ui_elements_frame = None  # Wird bei Bedarf erstellt
        
        # Kommentar-Panel
        self.comment_panel = CommentPanel(detail_frame)
        self.comment_panel.panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def update_steps(self, steps: list):
        """
        Aktualisiert die Liste der Schritte
        
        Args:
            steps: Liste von Schritt-Dictionaries
        """
        self.steps = steps
        
        # Aktualisiere Listbox
        self.steps_listbox.delete(0, tk.END)
        
        for i, step in enumerate(steps, 1):
            window_title = step.get('window_title', 'Unbekannt')
            step_text = f"Schritt {i}: {window_title}"
            self.steps_listbox.insert(tk.END, step_text)
        
        # Wenn neue Schritte vorhanden, selektiere den letzten
        if steps:
            self.steps_listbox.selection_clear(0, tk.END)
            self.steps_listbox.selection_set(len(steps) - 1)
            self.steps_listbox.see(len(steps) - 1)
            self._show_step_details(len(steps) - 1)
    
    def _on_step_select(self, event):
        """Wird aufgerufen wenn ein Schritt ausgewählt wird"""
        selection = self.steps_listbox.curselection()
        if selection:
            index = selection[0]
            self._show_step_details(index)
            # Aktiviere Buttons wenn Schritt ausgewählt
            self.delete_step_button.config(state=tk.NORMAL)
            
            # Verschieben-Buttons aktivieren/deaktivieren
            if index > 0:
                self.move_up_button.config(state=tk.NORMAL)
            else:
                self.move_up_button.config(state=tk.DISABLED)
            
            if index < len(self.steps) - 1:
                self.move_down_button.config(state=tk.NORMAL)
            else:
                self.move_down_button.config(state=tk.DISABLED)
        else:
            self.delete_step_button.config(state=tk.DISABLED)
            self.move_up_button.config(state=tk.DISABLED)
            self.move_down_button.config(state=tk.DISABLED)
    
    def set_delete_callback(self, callback):
        """
        Setzt Callback-Funktion für Schritt-Löschung
        
        Args:
            callback: Funktion die mit Schritt-Index aufgerufen wird
        """
        self.delete_callback = callback
    
    def set_reorder_callback(self, callback):
        """
        Setzt Callback-Funktion für Schritt-Reihenfolge-Änderung
        
        Args:
            callback: Funktion die mit (from_index, to_index) aufgerufen wird
        """
        self.reorder_callback = callback
    
    def _move_step_up(self):
        """Verschiebt ausgewählten Schritt nach oben"""
        selection = self.steps_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if index == 0:
            return
        
        # Verschiebe Schritt
        if self.reorder_callback:
            self.reorder_callback(index, index - 1)
        else:
            # Lokales Verschieben falls kein Callback
            if index > 0:
                self.steps[index], self.steps[index - 1] = self.steps[index - 1], self.steps[index]
                self.update_steps(self.steps)
                # Selektiere verschobenen Schritt
                self.steps_listbox.selection_set(index - 1)
                self.steps_listbox.see(index - 1)
    
    def _move_step_down(self):
        """Verschiebt ausgewählten Schritt nach unten"""
        selection = self.steps_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if index >= len(self.steps) - 1:
            return
        
        # Verschiebe Schritt
        if self.reorder_callback:
            self.reorder_callback(index, index + 1)
        else:
            # Lokales Verschieben falls kein Callback
            if index < len(self.steps) - 1:
                self.steps[index], self.steps[index + 1] = self.steps[index + 1], self.steps[index]
                self.update_steps(self.steps)
                # Selektiere verschobenen Schritt
                self.steps_listbox.selection_set(index + 1)
                self.steps_listbox.see(index + 1)
    
    def _delete_selected_step(self):
        """Löscht den ausgewählten Schritt"""
        selection = self.steps_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        
        # Frage Bestätigung ab
        if messagebox.askyesno(
            "Schritt löschen",
            f"Möchten Sie Schritt {index + 1} wirklich löschen?"
        ):
            if self.delete_callback:
                self.delete_callback(index)
            else:
                # Falls kein Callback, lösche lokal
                if index < len(self.steps):
                    del self.steps[index]
                    self.update_steps(self.steps)
    
    def _show_step_details(self, index: int):
        """
        Zeigt Details eines Schritts an
        
        Args:
            index: Index des Schritts
        """
        if not self.steps or index >= len(self.steps):
            return
        
        step = self.steps[index]
        step_number = step.get('step_number', index + 1)
        
        # Aktualisiere Kommentar-Panel mit aktueller Schritt-Nummer
        if hasattr(self, 'comment_panel'):
            self.comment_panel.set_current_step(step_number)
        
        # Zeige Screenshot
        screenshot_path = step.get('screenshot_path')
        if screenshot_path and Path(screenshot_path).exists():
            try:
                img = Image.open(screenshot_path)
                # Skaliere Bild für Anzeige
                max_width = 600
                max_height = 400
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                photo = ImageTk.PhotoImage(img)
                self.screenshot_label.config(image=photo, text="")
                self.screenshot_label.image = photo  # Keep a reference
            except Exception as e:
                self.screenshot_label.config(
                    text=f"Fehler beim Laden des Screenshots: {str(e)}",
                    image=""
                )
        else:
            self.screenshot_label.config(text="Screenshot wird geladen...", image="")
        
        # Zeige Beschreibung
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete(1.0, tk.END)
        description = step.get('description', 'Noch keine Beschreibung generiert.')
        self.description_text.insert(1.0, description)
        self.description_text.config(state=tk.DISABLED)
        
        # Zeige Metadaten
        self.metadata_text.config(state=tk.NORMAL)
        self.metadata_text.delete(1.0, tk.END)
        
        metadata_lines = [
            f"Schritt-Nummer: {step.get('step_number', 'N/A')}",
            f"Fenster-Titel: {step.get('window_title', 'N/A')}",
            f"Zeitstempel: {step.get('timestamp', 'N/A')}",
            f"Fenster-Klasse: {step.get('window_class', 'N/A')}",
        ]
        
        self.metadata_text.insert(1.0, "\n".join(metadata_lines))
        self.metadata_text.config(state=tk.DISABLED)
        
        # Aktualisiere Qualitäts-Indikatoren
        self._update_quality_indicators(step)
        
        # Aktualisiere UI-Element-Vorschau falls aktiviert
        self._update_ui_elements_preview(step)
    
    def _update_quality_indicators(self, step: Dict):
        """Aktualisiert Qualitäts-Indikatoren für einen Schritt"""
        # Lösche vorhandene Indikatoren
        for widget in self.quality_indicators_frame.winfo_children():
            widget.destroy()
        
        try:
            from src.document.quality_checker import QualityChecker
            
            quality_checker = QualityChecker()
            steps = [step]  # Prüfe nur diesen Schritt
            metrics = quality_checker.check_quality(steps)
            
            # Screenshot-Qualität
            screenshot_issues = metrics.get('screenshot_quality', [])
            if screenshot_issues:
                ttk.Label(
                    self.quality_indicators_frame,
                    text="⚠ Screenshot-Probleme gefunden",
                    foreground="orange"
                ).pack(side=tk.LEFT, padx=(0, 5))
            else:
                ttk.Label(
                    self.quality_indicators_frame,
                    text="✓ Screenshot OK",
                    foreground="green"
                ).pack(side=tk.LEFT, padx=(0, 5))
            
            # Text-Qualität
            text_issues = metrics.get('text_quality', [])
            if text_issues:
                ttk.Label(
                    self.quality_indicators_frame,
                    text="⚠ Text-Probleme gefunden",
                    foreground="orange"
                ).pack(side=tk.LEFT, padx=(0, 5))
            else:
                ttk.Label(
                    self.quality_indicators_frame,
                    text="✓ Text OK",
                    foreground="green"
                ).pack(side=tk.LEFT, padx=(0, 5))
        
        except Exception as e:
            # Bei Fehler einfach keine Indikatoren anzeigen
            pass
    
    def _update_ui_elements_preview(self, step: Dict):
        """Aktualisiert UI-Element-Vorschau falls aktiviert"""
        import os
        
        ui_element_detection = os.getenv('UI_ELEMENT_DETECTION', 'false').lower() == 'true'
        
        if not ui_element_detection:
            # Entferne UI-Element-Frame falls vorhanden
            if self.ui_elements_frame and self.ui_elements_frame.winfo_exists():
                self.ui_elements_frame.pack_forget()
            return
        
        screenshot_path = Path(step.get('screenshot_path', ''))
        if not screenshot_path.exists():
            return
        
        # Erstelle UI-Element-Frame falls noch nicht vorhanden
        if self.ui_elements_frame is None:
            detail_frame = self.comment_panel.panel.master
            self.ui_elements_frame = ttk.LabelFrame(detail_frame, text="Erkannte UI-Elemente", padding="5")
            # Packe vor dem Kommentar-Panel
            self.ui_elements_frame.pack(fill=tk.X, padx=5, pady=5, before=self.comment_panel.panel)
        
        # Lösche vorhandene Elemente
        for widget in self.ui_elements_frame.winfo_children():
            widget.destroy()
        
        try:
            from src.capture.ui_element_detector import UIElementDetector
            
            detector = UIElementDetector()
            elements = detector.detect_elements(screenshot_path)
            
            if elements:
                elements_text = f"{len(elements)} Element(e) erkannt: "
                element_types = {}
                for element in elements:
                    elem_type = element.get('type', 'unknown')
                    element_types[elem_type] = element_types.get(elem_type, 0) + 1
                
                type_list = [f"{count}x {type}" for type, count in element_types.items()]
                elements_text += ", ".join(type_list)
                
                ttk.Label(
                    self.ui_elements_frame,
                    text=elements_text,
                    foreground="blue"
                ).pack(side=tk.LEFT)
            else:
                ttk.Label(
                    self.ui_elements_frame,
                    text="Keine UI-Elemente erkannt",
                    foreground="gray"
                ).pack(side=tk.LEFT)
        
        except Exception as e:
            ttk.Label(
                self.ui_elements_frame,
                text="UI-Element-Erkennung nicht verfügbar",
                foreground="gray"
            ).pack(side=tk.LEFT)
    
    def clear(self):
        """Löscht alle angezeigten Schritte"""
        self.steps = []
        self.steps_listbox.delete(0, tk.END)
        self.screenshot_label.config(text="Kein Screenshot verfügbar", image="")
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete(1.0, tk.END)
        self.description_text.config(state=tk.DISABLED)
        self.metadata_text.config(state=tk.NORMAL)
        self.metadata_text.delete(1.0, tk.END)
        self.metadata_text.config(state=tk.DISABLED)
    
    def toggle_preview_visibility(self):
        """Schaltet die Sichtbarkeit der Vorschau um"""
        # Toggelt die Sichtbarkeit des gesamten Frames
        if self.main_frame.winfo_viewable():
            self.main_frame.pack_forget()
        else:
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


