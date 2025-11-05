"""
Exploration Progress Dialog: Zeigt Progress während automatischer Erkundung
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Optional, Dict
import threading
from PIL import Image, ImageTk

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ExplorationProgressDialog:
    """Zeigt Progress während automatischer Erkundung"""
    
    def __init__(self, parent, exploration_session):
        """
        Initialisiert Exploration Progress Dialog
        
        Args:
            parent: Parent-Widget
            exploration_session: Exploration Session Instanz
        """
        self.parent = parent
        self.exploration_session = exploration_session
        self.running = True
        
        # Erstelle Dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Automatische Erkundung läuft...")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Zentriere Dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self._setup_ui()
        self._start_update_loop()
    
    def _setup_ui(self):
        """Erstellt die UI-Komponenten"""
        # Hauptframe
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titel
        title_label = ttk.Label(
            main_frame,
            text="Automatische App-Erkundung läuft",
            font=("Arial", 12, "bold")
        )
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Status-Frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(
            status_frame,
            text="Initialisiere...",
            font=("Arial", 10)
        )
        self.status_label.pack(anchor=tk.W)
        
        # Screenshot-Vorschau
        screenshot_frame = ttk.LabelFrame(main_frame, text="Aktueller Screenshot", padding="10")
        screenshot_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.screenshot_label = ttk.Label(
            screenshot_frame,
            text="Kein Screenshot verfügbar",
            image=""
        )
        self.screenshot_label.pack(fill=tk.BOTH, expand=True)
        
        # Statistiken
        stats_frame = ttk.LabelFrame(main_frame, text="Statistiken", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        stats_inner = ttk.Frame(stats_frame)
        stats_inner.pack(fill=tk.X)
        
        self.steps_label = ttk.Label(stats_inner, text="Schritte: 0")
        self.steps_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.screenshots_label = ttk.Label(stats_inner, text="Screenshots: 0")
        self.screenshots_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.elements_label = ttk.Label(stats_inner, text="Elemente geklickt: 0")
        self.elements_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.depth_label = ttk.Label(stats_inner, text="Tiefe: 0")
        self.depth_label.pack(side=tk.LEFT)
        
        # Erkundete Bereiche
        areas_frame = ttk.LabelFrame(main_frame, text="Erkundete Bereiche", padding="10")
        areas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Liste mit Scrollbar
        list_container = ttk.Frame(areas_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.areas_listbox = tk.Listbox(list_container, yscrollcommand=scrollbar.set)
        self.areas_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.areas_listbox.yview)
        
        # Button-Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self.pause_button = ttk.Button(
            button_frame,
            text="Pausieren",
            command=self._pause
        )
        self.pause_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.resume_button = ttk.Button(
            button_frame,
            text="Fortsetzen",
            command=self._resume,
            state=tk.DISABLED
        )
        self.resume_button.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame,
            text="Abbrechen",
            command=self._cancel
        ).pack(side=tk.RIGHT)
    
    def _start_update_loop(self):
        """Startet Update-Loop"""
        def update_loop():
            while self.running:
                try:
                    if self.exploration_session and self.exploration_session.exploration_manager:
                        stats = self.exploration_session.exploration_manager.get_statistics()
                        self.dialog.after(0, lambda: self._update_stats(stats))
                    
                    # Update Screenshot
                    if self.exploration_session and self.exploration_session.session_manager:
                        steps = self.exploration_session.session_manager.get_steps()
                        if steps:
                            last_step = steps[-1]
                            screenshot_path = last_step.get('screenshot_path')
                            if screenshot_path:
                                self.dialog.after(0, lambda: self._update_screenshot(screenshot_path))
                except Exception as e:
                    logger.debug(f"Fehler im Update-Loop: {e}")
                
                threading.Event().wait(1.0)  # Update alle 1 Sekunde
        
        threading.Thread(target=update_loop, daemon=True).start()
    
    def _update_stats(self, stats: Dict):
        """Aktualisiert Statistiken"""
        steps = stats.get('steps', 0)
        screenshots = stats.get('visited_screenshots', 0)
        elements = stats.get('clicked_elements', 0)
        depth = stats.get('current_depth', 0)
        
        self.steps_label.config(text=f"Schritte: {steps}")
        self.screenshots_label.config(text=f"Screenshots: {screenshots}")
        self.elements_label.config(text=f"Elemente geklickt: {elements}")
        self.depth_label.config(text=f"Tiefe: {depth}")
        
        # Update Status
        if self.exploration_session and self.exploration_session.exploration_manager:
            if self.exploration_session.exploration_manager.paused:
                self.status_label.config(text="Pausiert", foreground="orange")
            elif self.exploration_session.exploration_manager.running:
                self.status_label.config(text="Erkundung läuft...", foreground="green")
            else:
                self.status_label.config(text="Erkundung abgeschlossen", foreground="blue")
    
    def _update_screenshot(self, screenshot_path: str):
        """Aktualisiert Screenshot-Vorschau"""
        try:
            path = Path(screenshot_path)
            if not path.exists():
                return
            
            # Lade Bild
            img = Image.open(path)
            
            # Resize für Anzeige (max. 400x300)
            max_width, max_height = 400, 300
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Konvertiere zu PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Update Label
            self.screenshot_label.config(image=photo, text="")
            self.screenshot_label.image = photo  # Keep a reference
        
        except Exception as e:
            logger.debug(f"Fehler beim Aktualisieren des Screenshots: {e}")
    
    def _pause(self):
        """Pausiert Erkundung"""
        if self.exploration_session:
            self.exploration_session.pause()
            self.pause_button.config(state=tk.DISABLED)
            self.resume_button.config(state=tk.NORMAL)
    
    def _resume(self):
        """Setzt Erkundung fort"""
        if self.exploration_session:
            self.exploration_session.resume()
            self.pause_button.config(state=tk.NORMAL)
            self.resume_button.config(state=tk.DISABLED)
    
    def _cancel(self):
        """Bricht Erkundung ab"""
        if self.exploration_session:
            self.exploration_session.stop()
        self.running = False
        self.dialog.destroy()
    
    def _on_close(self):
        """Wird aufgerufen beim Schließen"""
        if self.exploration_session and self.exploration_session.exploration_manager:
            if self.exploration_session.exploration_manager.running:
                # Frage ob wirklich abbrechen
                import tkinter.messagebox as messagebox
                if messagebox.askyesno("Abbrechen", "Erkundung wirklich abbrechen?"):
                    self._cancel()
            else:
                self.dialog.destroy()
        else:
            self.dialog.destroy()

