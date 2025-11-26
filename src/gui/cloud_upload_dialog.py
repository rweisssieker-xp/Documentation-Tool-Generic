"""
Dialog für Cloud-Upload zu OneDrive, SharePoint, Google Drive
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional, List
import threading
import os

from src.document.cloud_exporter import CloudExporter
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CloudUploadDialog:
    """Dialog für Cloud-Upload"""
    
    def __init__(self, parent, file_paths: List[Path]):
        """
        Initialisiert den Cloud-Upload Dialog
        
        Args:
            parent: Parent-Window
            file_paths: Liste von Dateipfaden zum Hochladen
        """
        self.parent = parent
        self.file_paths = file_paths
        self.exporter = CloudExporter()
        self.uploading = False
        
        # Erstelle Dialog-Fenster
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Cloud-Upload")
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
        
        # Tab 1: OneDrive
        onedrive_frame = ttk.Frame(notebook, padding="10")
        notebook.add(onedrive_frame, text="OneDrive")
        self._setup_onedrive_tab(onedrive_frame)
        
        # Tab 2: SharePoint
        sharepoint_frame = ttk.Frame(notebook, padding="10")
        notebook.add(sharepoint_frame, text="SharePoint")
        self._setup_sharepoint_tab(sharepoint_frame)
        
        # Tab 3: Google Drive
        gdrive_frame = ttk.Frame(notebook, padding="10")
        notebook.add(gdrive_frame, text="Google Drive")
        self._setup_gdrive_tab(gdrive_frame)
        
        # Datei-Liste
        files_frame = ttk.LabelFrame(main_frame, text="Zu uploadende Dateien", padding="10")
        files_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        files_listbox = tk.Listbox(files_frame, height=4)
        files_listbox.pack(fill=tk.BOTH, expand=True)
        
        for file_path in self.file_paths:
            files_listbox.insert(tk.END, file_path.name)
        
        # Progress-Bar
        self.progress_var = tk.StringVar(value="Bereit")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.pack(pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self.upload_button = ttk.Button(
            button_frame,
            text="Upload starten",
            command=self._start_upload
        )
        self.upload_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="Abbrechen",
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT)
    
    def _setup_onedrive_tab(self, parent):
        """Erstellt OneDrive-Tab"""
        ttk.Label(parent, text="Access Token:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.onedrive_token_var = tk.StringVar(value=os.getenv('ONEDRIVE_ACCESS_TOKEN', ''))
        ttk.Entry(parent, textvariable=self.onedrive_token_var, show="*", width=50).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        
        ttk.Label(parent, text="Ordner-Pfad:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.onedrive_folder_var = tk.StringVar(value="/Documentation")
        ttk.Entry(parent, textvariable=self.onedrive_folder_var, width=50).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        
        parent.columnconfigure(1, weight=1)
        self.current_service = 'onedrive'
    
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
    
    def _setup_gdrive_tab(self, parent):
        """Erstellt Google Drive-Tab"""
        ttk.Label(parent, text="Access Token:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.gdrive_token_var = tk.StringVar(value=os.getenv('GOOGLE_DRIVE_ACCESS_TOKEN', ''))
        ttk.Entry(parent, textvariable=self.gdrive_token_var, show="*", width=50).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        
        ttk.Label(parent, text="Ordner-ID (optional):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.gdrive_folder_var = tk.StringVar(value=os.getenv('GOOGLE_DRIVE_FOLDER_ID', ''))
        ttk.Entry(parent, textvariable=self.gdrive_folder_var, width=50).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        
        parent.columnconfigure(1, weight=1)
    
    def _start_upload(self):
        """Startet den Upload-Prozess"""
        # Bestimme aktiven Tab
        notebook = None
        for widget in self.dialog.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Notebook):
                        notebook = child
                        break
        
        if notebook:
            current_tab = notebook.index(notebook.select())
            service = ['onedrive', 'sharepoint', 'google_drive'][current_tab]
        else:
            service = 'onedrive'
        
        # Validiere Konfiguration
        if service == 'onedrive':
            token = self.onedrive_token_var.get().strip()
            if not token:
                messagebox.showerror("Fehler", "OneDrive Access Token erforderlich.")
                return
        
        elif service == 'sharepoint':
            url = self.sharepoint_url_var.get().strip()
            token = self.sharepoint_token_var.get().strip()
            if not url or not token:
                messagebox.showerror("Fehler", "SharePoint Site URL und Access Token erforderlich.")
                return
        
        elif service == 'google_drive':
            token = self.gdrive_token_var.get().strip()
            if not token:
                messagebox.showerror("Fehler", "Google Drive Access Token erforderlich.")
                return
        
        # Starte Upload in separatem Thread
        self.uploading = True
        self.upload_button.config(state=tk.DISABLED)
        self.progress_bar['maximum'] = len(self.file_paths)
        self.progress_bar['value'] = 0
        
        thread = threading.Thread(target=self._upload_thread, args=(service,), daemon=True)
        thread.start()
    
    def _upload_thread(self, service: str):
        """Upload-Thread"""
        try:
            successful = []
            failed = []
            
            for i, file_path in enumerate(self.file_paths):
                self.dialog.after(0, lambda i=i, fp=file_path: self.progress_var.set(f"Lade hoch: {fp.name}"))
                self.dialog.after(0, lambda i=i: self.progress_bar.config(value=i))
                
                try:
                    if service == 'onedrive':
                        result = self.exporter.upload_to_onedrive(
                            file_path=file_path,
                            folder_path=self.onedrive_folder_var.get(),
                            access_token=self.onedrive_token_var.get()
                        )
                    elif service == 'sharepoint':
                        result = self.exporter.upload_to_sharepoint(
                            file_path=file_path,
                            site_url=self.sharepoint_url_var.get(),
                            folder_path=self.sharepoint_folder_var.get(),
                            access_token=self.sharepoint_token_var.get()
                        )
                    elif service == 'google_drive':
                        folder_id = self.gdrive_folder_var.get().strip() or None
                        result = self.exporter.upload_to_google_drive(
                            file_path=file_path,
                            folder_id=folder_id,
                            access_token=self.gdrive_token_var.get()
                        )
                    else:
                        raise ValueError(f"Unbekannter Service: {service}")
                    
                    if result.get('success'):
                        successful.append(str(file_path))
                    else:
                        failed.append({'file': str(file_path), 'error': result.get('error', 'Unbekannter Fehler')})
                
                except Exception as e:
                    failed.append({'file': str(file_path), 'error': str(e)})
            
            # Update UI im Hauptthread
            self.dialog.after(0, lambda: self._upload_completed(successful, failed))
        
        except Exception as err:
            logger.error(f"Fehler beim Cloud-Upload: {err}", exc_info=True)
            self.dialog.after(0, lambda err=err: self._upload_failed(str(err)))
    
    def _upload_completed(self, successful: List[str], failed: List[dict]):
        """Wird aufgerufen wenn Upload abgeschlossen ist"""
        self.uploading = False
        self.upload_button.config(state=tk.NORMAL)
        self.progress_bar['value'] = len(self.file_paths)
        self.progress_var.set("Upload abgeschlossen")
        
        message = f"Upload abgeschlossen!\n\n"
        message += f"Erfolgreich: {len(successful)}\n"
        if failed:
            message += f"Fehlgeschlagen: {len(failed)}\n\n"
            for item in failed:
                message += f"- {item['file']}: {item['error']}\n"
        
        messagebox.showinfo("Ergebnis", message)
        self.dialog.destroy()
    
    def _upload_failed(self, error_msg: str):
        """Wird aufgerufen wenn Upload fehlgeschlagen ist"""
        self.uploading = False
        self.upload_button.config(state=tk.NORMAL)
        
        messagebox.showerror("Fehler", f"Upload fehlgeschlagen:\n{error_msg}")

