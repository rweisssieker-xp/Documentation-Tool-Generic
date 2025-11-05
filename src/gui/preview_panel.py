"""
Preview-Panel für Live-Vorschau der erfassten Schritte
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from PIL import Image, ImageTk


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
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Erstellt die UI-Komponenten"""
        # Hauptframe
        main_frame = ttk.Frame(self.parent)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Splitter für zwei Bereiche
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
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
            # Aktiviere Löschen-Button wenn Schritt ausgewählt
            self.delete_step_button.config(state=tk.NORMAL)
        else:
            self.delete_step_button.config(state=tk.DISABLED)
    
    def set_delete_callback(self, callback):
        """
        Setzt Callback-Funktion für Schritt-Löschung
        
        Args:
            callback: Funktion die mit Schritt-Index aufgerufen wird
        """
        self.delete_callback = callback
    
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


