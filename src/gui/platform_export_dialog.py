"""
Dialog für Platform-Export (Confluence, Notion, SharePoint)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import List, Dict
import threading
import os

from src.document.platform_exporters import PlatformExporters
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PlatformExportDialog:
    """Dialog für Platform-Export"""
    
    def __init__(self, parent, steps: List[Dict]):
        """
        Initialisiert den Platform-Export Dialog
        
        Args:
            parent: Parent-Window
            steps: Liste von Schritten
        """
        self.parent = parent
        self.steps = steps
        self.exporter = PlatformExporters()
        self.exporting = False
        
        # Erstelle Dialog-Fenster
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Platform-Export")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Zentriere Dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Erstellt die UI-Komponenten"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook für Tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Tab 1: Confluence
        confluence_frame = ttk.Frame(notebook, padding="10")
        notebook.add(confluence_frame, text="Confluence")
        self._setup_confluence_tab(confluence_frame)
        
        # Tab 2: Notion
        notion_frame = ttk.Frame(notebook, padding="10")
        notebook.add(notion_frame, text="Notion")
        self._setup_notion_tab(notion_frame)
        
        # Tab 3: SharePoint
        sharepoint_frame = ttk.Frame(notebook, padding="10")
        notebook.add(sharepoint_frame, text="SharePoint")
        self._setup_sharepoint_tab(sharepoint_frame)
        
        # Titel
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="Seiten-Titel:").pack(side=tk.LEFT, padx=(0, 5))
        self.title_var = tk.StringVar(value="Handbuch")
        ttk.Entry(title_frame, textvariable=self.title_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Progress-Bar
        self.progress_var = tk.StringVar(value="Bereit")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.pack(pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self.export_button = ttk.Button(
            button_frame,
            text="Exportieren",
            command=self._start_export
        )
        self.export_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="Abbrechen",
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT)
        
        self.current_platform = 'confluence'
        notebook.bind("<<NotebookTabChanged>>", lambda e: self._on_tab_changed(notebook))
    
    def _on_tab_changed(self, notebook):
        """Wird aufgerufen wenn Tab gewechselt wird"""
        selected = notebook.index(notebook.select())
        platforms = ['confluence', 'notion', 'sharepoint']
        self.current_platform = platforms[selected]
    
    def _setup_confluence_tab(self, parent):
        """Erstellt Confluence-Tab"""
        ttk.Label(parent, text="Base URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.confluence_url_var = tk.StringVar(value=os.getenv('CONFLUENCE_BASE_URL', ''))
        ttk.Entry(parent, textvariable=self.confluence_url_var, width=50).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        
        ttk.Label(parent, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.confluence_username_var = tk.StringVar(value=os.getenv('CONFLUENCE_USERNAME', ''))
        ttk.Entry(parent, textvariable=self.confluence_username_var, width=50).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        
        ttk.Label(parent, text="API Token:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.confluence_token_var = tk.StringVar(value=os.getenv('CONFLUENCE_API_TOKEN', ''))
        ttk.Entry(parent, textvariable=self.confluence_token_var, show="*", width=50).grid(
            row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        
        ttk.Label(parent, text="Space Key:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.confluence_space_var = tk.StringVar(value="")
        ttk.Entry(parent, textvariable=self.confluence_space_var, width=50).grid(
            row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        
        ttk.Label(parent, text="Parent Page ID (optional):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.confluence_parent_var = tk.StringVar(value="")
        ttk.Entry(parent, textvariable=self.confluence_parent_var, width=50).grid(
            row=4, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        
        parent.columnconfigure(1, weight=1)
    
    def _setup_notion_tab(self, parent):
        """Erstellt Notion-Tab"""
        ttk.Label(parent, text="Notion Token:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.notion_token_var = tk.StringVar(value=os.getenv('NOTION_TOKEN', ''))
        ttk.Entry(parent, textvariable=self.notion_token_var, show="*", width=50).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        
        ttk.Label(parent, text="Database ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.notion_database_var = tk.StringVar(value="")
        ttk.Entry(parent, textvariable=self.notion_database_var, width=50).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        
        parent.columnconfigure(1, weight=1)
    
    def _setup_sharepoint_tab(self, parent):
        """Erstellt SharePoint-Tab"""
        ttk.Label(parent, text="Site URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.sharepoint_url_var = tk.StringVar(value=os.getenv('SHAREPOINT_SITE_URL', ''))
        ttk.Entry(parent, textvariable=self.sharepoint_url_var, width=50).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        
        ttk.Label(parent, text="Access Token:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.sharepoint_token_var = tk.StringVar(value=os.getenv('SHAREPOINT_ACCESS_TOKEN', ''))
        ttk.Entry(parent, textvariable=self.sharepoint_token_var, show="*", width=50).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        
        ttk.Label(parent, text="Ordner-Pfad:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.sharepoint_folder_var = tk.StringVar(value="/Documentation")
        ttk.Entry(parent, textvariable=self.sharepoint_folder_var, width=50).grid(
            row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        
        parent.columnconfigure(1, weight=1)
    
    def _start_export(self):
        """Startet den Export-Prozess"""
        title = self.title_var.get().strip()
        if not title:
            messagebox.showerror("Fehler", "Bitte geben Sie einen Titel ein.")
            return
        
        # Validiere Plattform-spezifische Konfiguration
        if self.current_platform == 'confluence':
            if not all([
                self.confluence_url_var.get().strip(),
                self.confluence_username_var.get().strip(),
                self.confluence_token_var.get().strip(),
                self.confluence_space_var.get().strip()
            ]):
                messagebox.showerror("Fehler", "Bitte füllen Sie alle Confluence-Felder aus.")
                return
        
        elif self.current_platform == 'notion':
            if not all([
                self.notion_token_var.get().strip(),
                self.notion_database_var.get().strip()
            ]):
                messagebox.showerror("Fehler", "Bitte füllen Sie alle Notion-Felder aus.")
                return
        
        elif self.current_platform == 'sharepoint':
            if not all([
                self.sharepoint_url_var.get().strip(),
                self.sharepoint_token_var.get().strip()
            ]):
                messagebox.showerror("Fehler", "Bitte füllen Sie alle SharePoint-Felder aus.")
                return
        
        # Starte Export in separatem Thread
        self.exporting = True
        self.export_button.config(state=tk.DISABLED)
        self.progress_bar.start()
        self.progress_var.set("Exportiere...")
        
        thread = threading.Thread(target=self._export_thread, daemon=True)
        thread.start()
    
    def _export_thread(self):
        """Export-Thread"""
        try:
            title = self.title_var.get()
            
            if self.current_platform == 'confluence':
                result = self.exporter.export_to_confluence(
                    steps=self.steps,
                    space_key=self.confluence_space_var.get(),
                    title=title,
                    parent_id=self.confluence_parent_var.get() or None,
                    base_url=self.confluence_url_var.get(),
                    username=self.confluence_username_var.get(),
                    api_token=self.confluence_token_var.get()
                )
            
            elif self.current_platform == 'notion':
                result = self.exporter.export_to_notion(
                    steps=self.steps,
                    database_id=self.notion_database_var.get(),
                    title=title,
                    notion_token=self.notion_token_var.get()
                )
            
            elif self.current_platform == 'sharepoint':
                result = self.exporter.export_to_sharepoint(
                    steps=self.steps,
                    site_url=self.sharepoint_url_var.get(),
                    folder_path=self.sharepoint_folder_var.get(),
                    title=title,
                    access_token=self.sharepoint_token_var.get()
                )
            
            else:
                raise ValueError(f"Unbekannte Plattform: {self.current_platform}")
            
            # Update UI im Hauptthread
            self.dialog.after(0, lambda: self._export_completed(result))
        
        except Exception as e:
            logger.error(f"Fehler beim Platform-Export: {e}", exc_info=True)
            self.dialog.after(0, lambda: self._export_failed(str(e)))
    
    def _export_completed(self, result: Dict):
        """Wird aufgerufen wenn Export abgeschlossen ist"""
        self.progress_bar.stop()
        self.exporting = False
        self.export_button.config(state=tk.NORMAL)
        
        if result.get('success'):
            message = f"Export erfolgreich abgeschlossen!\n\n"
            message += f"Plattform: {result.get('platform', 'unbekannt')}\n"
            
            if result.get('page_url'):
                message += f"URL: {result.get('page_url')}"
            elif result.get('page_id'):
                message += f"Page ID: {result.get('page_id')}"
            
            messagebox.showinfo("Erfolg", message)
            self.dialog.destroy()
        else:
            error_msg = result.get('error', 'Unbekannter Fehler')
            messagebox.showerror("Fehler", f"Export fehlgeschlagen:\n{error_msg}")
    
    def _export_failed(self, error_msg: str):
        """Wird aufgerufen wenn Export fehlgeschlagen ist"""
        self.progress_bar.stop()
        self.exporting = False
        self.export_button.config(state=tk.NORMAL)
        
        messagebox.showerror(
            "Fehler",
            f"Export fehlgeschlagen:\n{error_msg}"
        )

