"""
Einstellungsdialog für Prompt-Profile und API-Konfiguration
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
from pathlib import Path
from dotenv import load_dotenv

from src.config.config_manager import ConfigManager


class SettingsDialog:
    """Dialog für Anwendungseinstellungen"""
    
    def __init__(self, parent, main_window):
        """
        Initialisiert den Einstellungsdialog
        
        Args:
            parent: Parent-Window
            main_window: Referenz zum Hauptfenster
        """
        self.parent = parent
        self.main_window = main_window
        self.config_manager = ConfigManager()
        
        # Lade Environment-Variablen
        load_dotenv()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Einstellungen")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._setup_ui()
        self._load_current_settings()
    
    def _setup_ui(self):
        """Erstellt die UI-Komponenten"""
        # Notebook für Tabs
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: OpenAI API
        api_frame = ttk.Frame(notebook, padding="10")
        notebook.add(api_frame, text="OpenAI API")
        
        ttk.Label(api_frame, text="API-Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.api_key_var = tk.StringVar()
        api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, width=50, show="*")
        api_key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        ttk.Label(api_frame, text="(Gespeichert in .env Datei)", foreground="gray").grid(
            row=1, column=1, sticky=tk.W, padx=5
        )
        
        ttk.Label(api_frame, text="Modell:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar()
        model_combo = ttk.Combobox(
            api_frame,
            textvariable=self.model_var,
            values=["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
            state="readonly",
            width=47
        )
        model_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        model_combo.set("gpt-4o")
        
        # Tab 2: Prompt-Profile
        profile_frame = ttk.Frame(notebook, padding="10")
        notebook.add(profile_frame, text="Prompt-Profile")
        
        ttk.Label(profile_frame, text="Verfügbare Profile:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Liste der Profile
        profile_list_frame = ttk.Frame(profile_frame)
        profile_list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.profile_listbox = tk.Listbox(profile_list_frame, height=10)
        self.profile_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(profile_list_frame, orient=tk.VERTICAL, command=self.profile_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.profile_listbox.config(yscrollcommand=scrollbar.set)
        
        self.profile_listbox.bind('<<ListboxSelect>>', self._on_profile_select)
        
        # Aktuelles Profil anzeigen
        ttk.Label(profile_frame, text="Aktuelles Profil:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.current_profile_label = ttk.Label(profile_frame, text="Kein Profil ausgewählt", foreground="gray")
        self.current_profile_label.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # Tab 3: Ausgabeformate
        output_frame = ttk.Frame(notebook, padding="10")
        notebook.add(output_frame, text="Ausgabeformate")
        
        ttk.Label(output_frame, text="Ausgabeformate:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.output_docx_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(output_frame, text="DOCX (Word)", variable=self.output_docx_var).grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        
        self.output_pdf_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(output_frame, text="PDF", variable=self.output_pdf_var).grid(
            row=2, column=0, sticky=tk.W, pady=2
        )
        
        self.output_markdown_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(output_frame, text="Markdown", variable=self.output_markdown_var).grid(
            row=3, column=0, sticky=tk.W, pady=2
        )
        
        self.output_html_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(output_frame, text="HTML", variable=self.output_html_var).grid(
            row=4, column=0, sticky=tk.W, pady=2
        )
        
        self.output_json_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(output_frame, text="JSON (Audit-Trail)", variable=self.output_json_var).grid(
            row=5, column=0, sticky=tk.W, pady=2
        )
        
        self.output_csv_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(output_frame, text="CSV (Audit-Trail)", variable=self.output_csv_var).grid(
            row=6, column=0, sticky=tk.W, pady=2
        )
        
        # Tab 4: Dokument-Metadaten
        metadata_frame = ttk.Frame(notebook, padding="10")
        notebook.add(metadata_frame, text="Dokument-Metadaten")
        
        ttk.Label(metadata_frame, text="Abteilung:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.department_var = tk.StringVar()
        ttk.Entry(metadata_frame, textvariable=self.department_var, width=40).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        
        ttk.Label(metadata_frame, text="Projekt:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.project_var = tk.StringVar()
        ttk.Entry(metadata_frame, textvariable=self.project_var, width=40).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        
        ttk.Label(metadata_frame, text="Kontakt:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.contact_var = tk.StringVar()
        ttk.Entry(metadata_frame, textvariable=self.contact_var, width=40).grid(
            row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        
        ttk.Label(metadata_frame, text="Dokument-ID:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.document_id_var = tk.StringVar()
        ttk.Entry(metadata_frame, textvariable=self.document_id_var, width=40).grid(
            row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        
        metadata_frame.columnconfigure(1, weight=1)
        
        # Tab 5: Dokumentvorlagen
        template_frame = ttk.Frame(notebook, padding="10")
        notebook.add(template_frame, text="Dokumentvorlagen")
        
        from src.document.template_manager import TemplateManager
        
        self.template_manager = TemplateManager()
        
        ttk.Label(template_frame, text="Verfügbare Vorlagen:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Liste der Vorlagen
        template_list_frame = ttk.Frame(template_frame)
        template_list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.template_listbox = tk.Listbox(template_list_frame, height=8)
        self.template_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar_template = ttk.Scrollbar(template_list_frame, orient=tk.VERTICAL, command=self.template_listbox.yview)
        scrollbar_template.pack(side=tk.RIGHT, fill=tk.Y)
        self.template_listbox.config(yscrollcommand=scrollbar_template.set)
        
        # Aktuelle Vorlage anzeigen
        ttk.Label(template_frame, text="Aktuelle Vorlage:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.current_template_label = ttk.Label(template_frame, text="Standard", foreground="gray")
        self.current_template_label.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # Vorlagen-Buttons
        template_button_frame = ttk.Frame(template_frame)
        template_button_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Button(template_button_frame, text="Neu", command=self._create_template).pack(side=tk.LEFT, padx=2)
        ttk.Button(template_button_frame, text="Bearbeiten", command=self._edit_template).pack(side=tk.LEFT, padx=2)
        ttk.Button(template_button_frame, text="Löschen", command=self._delete_template).pack(side=tk.LEFT, padx=2)
        
        # Tab 6: Trigger-Einstellungen
        trigger_frame = ttk.Frame(notebook, padding="10")
        notebook.add(trigger_frame, text="Trigger-Einstellungen")
        
        from src.config.trigger_config import TriggerConfig
        
        trigger_config_path = Path("config") / "trigger_config.yml"
        self.trigger_config = TriggerConfig(trigger_config_path if trigger_config_path.exists() else None)
        
        ttk.Label(trigger_frame, text="Polling-Intervall (Sekunden):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.poll_interval_var = tk.DoubleVar(value=self.trigger_config.poll_interval)
        poll_interval_spinbox = ttk.Spinbox(
            trigger_frame,
            from_=0.1,
            to=5.0,
            increment=0.1,
            textvariable=self.poll_interval_var,
            width=10
        )
        poll_interval_spinbox.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(trigger_frame, text="Änderungs-Schwellenwert (Sekunden):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.change_threshold_var = tk.DoubleVar(value=self.trigger_config.change_threshold)
        change_threshold_spinbox = ttk.Spinbox(
            trigger_frame,
            from_=0.1,
            to=5.0,
            increment=0.1,
            textvariable=self.change_threshold_var,
            width=10
        )
        change_threshold_spinbox.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(trigger_frame, text="Größenänderung-Schwellenwert (Pixel):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.size_change_threshold_var = tk.IntVar(value=self.trigger_config.size_change_threshold)
        size_change_spinbox = ttk.Spinbox(
            trigger_frame,
            from_=10,
            to=500,
            increment=10,
            textvariable=self.size_change_threshold_var,
            width=10
        )
        size_change_spinbox.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(trigger_frame, text="Doppelklick-Verzögerung (Sekunden):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.double_click_delay_var = tk.DoubleVar(value=self.trigger_config.double_click_delay)
        double_click_spinbox = ttk.Spinbox(
            trigger_frame,
            from_=0.1,
            to=2.0,
            increment=0.1,
            textvariable=self.double_click_delay_var,
            width=10
        )
        double_click_spinbox.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Buttons am unteren Rand
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Übernehmen", command=self._apply_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Abbrechen", command=self.dialog.destroy).pack(side=tk.RIGHT)
    
    def _load_current_settings(self):
        """Lädt aktuelle Einstellungen"""
        # Lade API-Key aus Environment
        api_key = os.getenv('OPENAI_API_KEY', '')
        if api_key and api_key != 'your_openai_api_key_here':
            self.api_key_var.set(api_key)
        
        # Lade Modell
        model = os.getenv('OPENAI_MODEL', 'gpt-4o')
        self.model_var.set(model)
        
        # Lade verfügbare Profile
        profiles = self.config_manager.list_prompt_profiles()
        for profile in profiles:
            self.profile_listbox.insert(tk.END, profile)
        
        # Lade verfügbare Dokumentvorlagen
        templates = self.template_manager.list_templates()
        for template in templates:
            self.template_listbox.insert(tk.END, template)
        
        # Setze aktuelle Vorlage falls vorhanden
        current_template = getattr(self.main_window, 'current_template', None)
        if current_template and current_template in templates:
            try:
                index = templates.index(current_template)
                self.template_listbox.selection_set(index)
                self.current_template_label.config(
                    text=current_template,
                    foreground="black"
                )
            except ValueError:
                pass
        
        # Lade Export-Formate aus Config falls vorhanden
        export_formats_path = Path("config") / "export_formats.yml"
        if export_formats_path.exists():
            try:
                with open(export_formats_path, 'r', encoding='utf-8') as f:
                    export_formats = yaml.safe_load(f)
                
                self.output_docx_var.set(export_formats.get('docx', True))
                self.output_pdf_var.set(export_formats.get('pdf', True))
                self.output_markdown_var.set(export_formats.get('markdown', False))
                self.output_html_var.set(export_formats.get('html', False))
                self.output_json_var.set(export_formats.get('json', True))
                self.output_csv_var.set(export_formats.get('csv', False))
            except Exception:
                pass
        
        # Lade Metadaten aus Config falls vorhanden
        metadata_config_path = Path("config") / "document_metadata.yml"
        if metadata_config_path.exists():
            try:
                import yaml
                with open(metadata_config_path, 'r', encoding='utf-8') as f:
                    metadata_config = yaml.safe_load(f)
                
                self.department_var.set(metadata_config.get('department', ''))
                self.project_var.set(metadata_config.get('project', ''))
                self.contact_var.set(metadata_config.get('contact', ''))
                self.document_id_var.set(metadata_config.get('document_id', ''))
            except Exception:
                pass
        
        # Setze aktuelles Profil
        if self.main_window.current_profile:
            try:
                index = profiles.index(self.main_window.current_profile)
                self.profile_listbox.selection_set(index)
                self.current_profile_label.config(
                    text=self.main_window.current_profile,
                    foreground="black"
                )
            except ValueError:
                pass
    
    def _on_profile_select(self, event):
        """Wird aufgerufen wenn ein Profil ausgewählt wird"""
        selection = self.profile_listbox.curselection()
        if selection:
            profile_name = self.profile_listbox.get(selection[0])
            self.current_profile_label.config(
                text=profile_name,
                foreground="black"
            )
    
    def _create_template(self):
        """Erstellt eine neue Dokumentvorlage"""
        from tkinter import simpledialog
        
        name = simpledialog.askstring("Neue Vorlage", "Vorlagen-Name:")
        if name:
            description = simpledialog.askstring("Neue Vorlage", "Beschreibung (optional):", initialvalue="")
            template = self.template_manager.create_template(name, description or "")
            self.template_listbox.insert(tk.END, name)
            messagebox.showinfo("Erfolg", f"Vorlage '{name}' erstellt!")
    
    def _edit_template(self):
        """Bearbeitet eine Dokumentvorlage"""
        selection = self.template_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie eine Vorlage aus.")
            return
        
        template_name = self.template_listbox.get(selection[0])
        template = self.template_manager.get_template(template_name)
        
        if template:
            # Öffne einfachen Editor-Dialog
            # In einer vollständigen Implementierung würde hier ein vollständiger Editor geöffnet
            messagebox.showinfo("Info", f"Vorlage '{template_name}' bearbeiten.\n\nVollständiger Editor wird in zukünftiger Version implementiert.")
    
    def _delete_template(self):
        """Löscht eine Dokumentvorlage"""
        selection = self.template_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie eine Vorlage aus.")
            return
        
        template_name = self.template_listbox.get(selection[0])
        
        if messagebox.askyesno("Bestätigung", f"Möchten Sie die Vorlage '{template_name}' wirklich löschen?"):
            if self.template_manager.delete_template(template_name):
                self.template_listbox.delete(selection[0])
                messagebox.showinfo("Erfolg", f"Vorlage '{template_name}' gelöscht!")
            else:
                messagebox.showerror("Fehler", "Fehler beim Löschen der Vorlage!")
    
    def _apply_settings(self):
        """Wendet die Einstellungen an"""
        try:
            # Speichere API-Key in .env
            api_key = self.api_key_var.get().strip()
            if api_key:
                self._save_env_file('OPENAI_API_KEY', api_key)
                os.environ['OPENAI_API_KEY'] = api_key
            
            # Speichere Modell
            model = self.model_var.get()
            self._save_env_file('OPENAI_MODEL', model)
            os.environ['OPENAI_MODEL'] = model
            
            # Setze ausgewähltes Profil
            selection = self.profile_listbox.curselection()
            if selection:
                profile_name = self.profile_listbox.get(selection[0])
                self.main_window.set_prompt_profile(profile_name)
            
            # Setze ausgewählte Dokumentvorlage
            template_selection = self.template_listbox.curselection()
            if template_selection:
                template_name = self.template_listbox.get(template_selection[0])
                if hasattr(self.main_window, 'set_document_template'):
                    self.main_window.set_document_template(template_name)
            
            # Speichere Export-Formate
            export_formats_path = Path("config") / "export_formats.yml"
            export_formats = {
                'docx': self.output_docx_var.get(),
                'pdf': self.output_pdf_var.get(),
                'markdown': self.output_markdown_var.get(),
                'html': self.output_html_var.get(),
                'json': self.output_json_var.get(),
                'csv': self.output_csv_var.get()
            }
            export_formats_path.parent.mkdir(parents=True, exist_ok=True)
            with open(export_formats_path, 'w', encoding='utf-8') as f:
                yaml.dump(export_formats, f, default_flow_style=False, allow_unicode=True)
            
            # Speichere Dokument-Metadaten
            metadata_config_path = Path("config") / "document_metadata.yml"
            import yaml
            metadata_config = {
                'department': self.department_var.get().strip(),
                'project': self.project_var.get().strip(),
                'contact': self.contact_var.get().strip(),
                'document_id': self.document_id_var.get().strip()
            }
            metadata_config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(metadata_config_path, 'w', encoding='utf-8') as f:
                yaml.dump(metadata_config, f, default_flow_style=False, allow_unicode=True)
            
            # Speichere Trigger-Einstellungen
            trigger_config_path = Path("config") / "trigger_config.yml"
            self.trigger_config.poll_interval = self.poll_interval_var.get()
            self.trigger_config.change_threshold = self.change_threshold_var.get()
            self.trigger_config.size_change_threshold = self.size_change_threshold_var.get()
            self.trigger_config.double_click_delay = self.double_click_delay_var.get()
            self.trigger_config.save_config(trigger_config_path)
            
            messagebox.showinfo("Erfolg", "Einstellungen gespeichert!")
            self.dialog.destroy()
        
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern der Einstellungen:\n{str(e)}")
    
    def _save_env_file(self, key: str, value: str):
        """
        Speichert eine Environment-Variable in .env Datei
        
        Args:
            key: Variable-Name
            value: Variable-Wert
        """
        env_path = Path('.env')
        
        # Lade bestehende .env oder erstelle neue
        env_vars = {}
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        env_vars[k.strip()] = v.strip()
        
        # Update Variable
        env_vars[key] = value
        
        # Schreibe zurück
        with open(env_path, 'w', encoding='utf-8') as f:
            for k, v in env_vars.items():
                f.write(f"{k}={v}\n")

