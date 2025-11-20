"""
App-Selector Dialog: Auswahl einer App aus laufenden Fenstern
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, List
import threading

from src.automation.window_discovery import WindowDiscovery
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AppSelectorDialog:
    """Dialog zur Auswahl einer App aus laufenden Fenstern"""
    
    def __init__(self, parent):
        """
        Initialisiert den App-Selector Dialog
        
        Args:
            parent: Parent-Widget
        """
        self.parent = parent
        self.selected_window = None
        self.window_discovery = WindowDiscovery()
        
        # Erstelle Dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("App für automatische Erkundung auswählen")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Zentriere Dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self._setup_ui()
        self._load_windows()
    
    def _setup_ui(self):
        """Erstellt die UI-Komponenten"""
        # Hauptframe
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titel
        title_label = ttk.Label(
            main_frame,
            text="Wählen Sie eine App aus, die automatisch erkundet werden soll:",
            font=("Arial", 11, "bold")
        )
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Filter-Frame
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Suchen:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.filter_var = tk.StringVar()
        self.filter_var.trace('w', self._on_filter_change)
        filter_entry = ttk.Entry(filter_frame, textvariable=self.filter_var, width=30)
        filter_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        filter_entry.focus()
        
        # Refresh-Button
        refresh_button = ttk.Button(
            filter_frame,
            text="Aktualisieren",
            command=self._refresh_windows
        )
        refresh_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Liste mit Scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview für strukturierte Anzeige
        columns = ('title', 'process', 'pid', 'hwnd')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=20)
        
        # Spalten konfigurieren
        self.tree.heading('#0', text='App')
        self.tree.heading('title', text='Fenstertitel')
        self.tree.heading('process', text='Prozess')
        self.tree.heading('pid', text='PID')
        self.tree.heading('hwnd', text='HWND')
        
        self.tree.column('#0', width=200)
        self.tree.column('title', width=250)
        self.tree.column('process', width=120)
        self.tree.column('pid', width=60)
        self.tree.column('hwnd', width=0, stretch=False)  # Verstecke HWND-Spalte
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Double-Click Event
        self.tree.bind('<Double-1>', self._on_item_double_click)
        
        # Button-Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # Info-Label
        self.info_label = ttk.Label(
            button_frame,
            text="Doppelklick auf eine App oder wählen Sie sie aus und klicken Sie auf 'Auswählen'",
            foreground="gray"
        )
        self.info_label.pack(side=tk.LEFT)
        
        # Buttons
        ttk.Button(
            button_frame,
            text="Abbrechen",
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        self.select_button = ttk.Button(
            button_frame,
            text="Auswählen",
            command=self._select_window,
            state=tk.DISABLED
        )
        self.select_button.pack(side=tk.RIGHT)
        
        # Selection ändert sich
        self.tree.bind('<<TreeviewSelect>>', self._on_selection_change)
    
    def _load_windows(self):
        """Lädt alle Fenster in einem separaten Thread"""
        # Zeige Lade-Indikator
        self.info_label.config(text="Lade Fenster...", foreground="blue")
        self.select_button.config(state=tk.DISABLED)
        
        def load_thread():
            try:
                windows = self.window_discovery.discover_all_windows()
                grouped = self.window_discovery.group_by_process(windows)
                
                # Update UI im Hauptthread
                self.dialog.after(0, lambda: self._populate_tree(grouped))
            except Exception as e:
                logger.error(f"Fehler beim Laden der Fenster: {e}", exc_info=True)
                self.dialog.after(0, lambda: self.info_label.config(
                    text=f"Fehler beim Laden: {str(e)}",
                    foreground="red"
                ))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def _populate_tree(self, grouped_windows: Dict[str, List[Dict]]):
        """Befüllt den Treeview mit Fenstern"""
        # Lösche alte Einträge
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Füge Fenster gruppiert nach Prozess ein
        for process_name, windows in sorted(grouped_windows.items()):
            # Prozess-Knoten
            process_node = self.tree.insert(
                '',
                'end',
                text=process_name,
                values=('', '', ''),
                tags=('process',)
            )
            
            # Einzelne Fenster als Kinder
            for window in windows:
                title = window.get('title', 'Unbekannt')
                pid = window.get('pid', '')
                hwnd = window.get('hwnd')
                
                # Verwende HWND als IID
                item_id = f"hwnd_{hwnd}"
                self.tree.insert(
                    process_node,
                    'end',
                    iid=item_id,
                    text=title[:50] + ('...' if len(title) > 50 else ''),
                    values=(title, process_name, pid, str(hwnd)),  # HWND als zusätzlicher Wert
                    tags=('window',)
                )
        
        # Konfiguriere Tags für Styling
        self.tree.tag_configure('process', font=("Arial", 9, "bold"))
        self.tree.tag_configure('window', font=("Arial", 9))
        
        self.info_label.config(
            text=f"{len(grouped_windows)} Prozesse, {sum(len(w) for w in grouped_windows.values())} Fenster gefunden",
            foreground="gray"
        )
    
    def _on_filter_change(self, *args):
        """Wird aufgerufen wenn Filter sich ändert"""
        filter_text = self.filter_var.get().lower()
        
        if not filter_text:
            # Zeige alle Einträge
            for item in self.tree.get_children():
                self._set_item_visible(item, True)
            return
        
        # Filtere Einträge
        for item in self.tree.get_children():
            process_name = self.tree.item(item, 'text').lower()
            visible = filter_text in process_name
            
            # Prüfe auch Kinder
            for child in self.tree.get_children(item):
                window_title = self.tree.item(child, 'text').lower()
                if filter_text in window_title:
                    visible = True
                self._set_item_visible(child, visible or filter_text in window_title)
            
            self._set_item_visible(item, visible)
    
    def _set_item_visible(self, item, visible):
        """Setzt Sichtbarkeit eines Treeview-Items"""
        if visible:
            self.tree.detach(item)
            parent = self.tree.parent(item)
            if parent:
                self.tree.attach(item, parent, 'end')
            else:
                self.tree.reattach(item, '', 'end')
        else:
            self.tree.detach(item)
    
    def _on_selection_change(self, event):
        """Wird aufgerufen wenn Auswahl sich ändert"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            tags = self.tree.item(item, 'tags')
            if 'window' in tags:
                self.select_button.config(state=tk.NORMAL)
            else:
                self.select_button.config(state=tk.DISABLED)
        else:
            self.select_button.config(state=tk.DISABLED)
    
    def _on_item_double_click(self, event):
        """Wird aufgerufen bei Doppelklick"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            tags = self.tree.item(item, 'tags')
            if 'window' in tags:
                self._select_window()
    
    def _select_window(self):
        """Wählt das ausgewählte Fenster aus"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        tags = self.tree.item(item, 'tags')
        
        if 'window' not in tags:
            return
        
        # Extrahiere HWND aus values (letztes Element) oder aus item ID
        values = self.tree.item(item, 'values')
        if values and len(values) > 3:
            hwnd = int(values[3])  # HWND ist im 4. Wert
        else:
            # Fallback: item selbst ist die IID
            item_id_str = str(item)
            if item_id_str.startswith('hwnd_'):
                hwnd = int(item_id_str.split('_')[1])
            else:
                logger.warning(f"Konnte HWND nicht aus Item extrahieren: {item}")
                return
        
        self.selected_window = self.window_discovery.get_window_by_hwnd(hwnd)
        self.dialog.destroy()
    
    def _refresh_windows(self):
        """Aktualisiert die Liste der Fenster"""
        self._load_windows()
    
    def get_selected_window(self) -> Optional[Dict]:
        """
        Gibt das ausgewählte Fenster zurück
        
        Returns:
            Fenster-Informationen oder None
        """
        return self.selected_window

