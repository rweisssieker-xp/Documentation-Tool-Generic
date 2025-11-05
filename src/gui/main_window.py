"""
Hauptfenster der GUI-Anwendung
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import os
from datetime import datetime
import threading

from src.gui.settings_dialog import SettingsDialog
from src.gui.preview_panel import PreviewPanel
from src.gui.recovery_dialog import SessionRecoveryDialog
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MainWindow:
    """Hauptfenster mit Session-Steuerung"""
    
    def __init__(self, root: tk.Tk):
        """
        Initialisiert das Hauptfenster
        
        Args:
            root: Tkinter Root-Window
        """
        self.root = root
        self.root.title("Automatischer Handbuch-Generator (AHG)")
        self.root.geometry("1000x700")
        
        # Status-Variablen
        self.session_active = False
        self.session_manager = None  # Wird später zugewiesen
        self.current_profile = None
        self.current_template = None
        self.batch_processor = None
        
        self._setup_menu()
        self._setup_ui()
        self._load_settings()
        self._setup_hotkeys()
    
    def _setup_menu(self):
        """Erstellt die Menüleiste"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Datei-Menü
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Datei", menu=file_menu)
        file_menu.add_command(label="Einstellungen...", command=self._open_settings, accelerator="F1")
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.root.quit, accelerator="Alt+F4")
        
        # Session-Menü
        session_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Session", menu=session_menu)
        session_menu.add_command(label="Session starten", command=self._start_session, accelerator="Ctrl+S")
        session_menu.add_command(label="Session beenden", command=self._stop_session, accelerator="Ctrl+Shift+S")
        session_menu.add_separator()
        session_menu.add_command(label="Pause/Fortsetzen", command=self._pause_session, accelerator="Ctrl+P")
        session_menu.add_separator()
        session_menu.add_command(label="Rückgängig", command=self._undo_step, accelerator="Ctrl+Z")
        session_menu.add_command(label="Wiederholen", command=self._redo_step, accelerator="Ctrl+Y")
        session_menu.add_separator()
        session_menu.add_command(label="Session wiederherstellen...", command=self._show_recovery_dialog)
        
        # Hilfe-Menü
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Hilfe", menu=help_menu)
        help_menu.add_command(label="Tastenkürzel...", command=self._show_shortcuts)
        help_menu.add_command(label="Über...", command=self._show_about)
        
        # Tools-Menü
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Bereinigung ausführen...", command=self._run_manual_cleanup)
    
    def _show_shortcuts(self):
        """Zeigt Dialog mit Tastenkürzeln"""
        shortcuts_text = """
Tastenkürzel (Hotkeys)

Session-Steuerung:
  Ctrl+S              - Session starten
  Ctrl+Shift+S        - Session beenden
  Ctrl+P              - Pause/Fortsetzen
  ESC                 - Session beenden (wenn aktiv)

Bearbeitung:
  Ctrl+Z              - Rückgängig (Undo)
  Ctrl+Y              - Wiederholen (Redo)
  Ctrl+Shift+Z        - Wiederholen (Redo, alternativ)

Allgemein:
  F1                  - Einstellungen öffnen
  Alt+F4              - Anwendung beenden
"""
        messagebox.showinfo("Tastenkürzel", shortcuts_text.strip())
    
    def _show_about(self):
        """Zeigt Info-Dialog"""
        about_text = """
Automatischer Handbuch-Generator (AHG)
Version 1.0.0

Vollautomatische Erstellung bebilderter technischer Handbücher 
aus realen Nutzungsszenarien von Software-Anwendungen.

Features:
• Automatische Beobachtung von Benutzeraktionen
• Screenshot-Erstellung mit OCR
• AI-Textgenerierung mit OpenAI GPT-5
• Revisionssichere Dokumentation
• Mehrere Export-Formate (DOCX, PDF, Markdown, HTML)
• Privacy-Maskierung für sensible Daten
• Session-Wiederherstellung und automatische Bereinigung

Für weitere Informationen siehe README.md
"""
        messagebox.showinfo("Über AHG", about_text.strip())
    
    def _setup_hotkeys(self):
        """Konfiguriert Tastenkürzel"""
        # Ctrl+S: Session starten
        self.root.bind('<Control-s>', lambda e: self._start_session() if not self.session_active else None)
        
        # Ctrl+Shift+S: Session beenden
        self.root.bind('<Control-Shift-S>', lambda e: self._stop_session() if self.session_active else None)
        
        # Ctrl+P: Pause/Resume
        self.root.bind('<Control-p>', lambda e: self._pause_session() if self.session_active else None)
        
        # Ctrl+Z: Undo
        self.root.bind('<Control-z>', lambda e: self._undo_step() if self.session_active else None)
        
        # Ctrl+Y oder Ctrl+Shift+Z: Redo
        self.root.bind('<Control-y>', lambda e: self._redo_step() if self.session_active else None)
        self.root.bind('<Control-Shift-Z>', lambda e: self._redo_step() if self.session_active else None)
        
        # F1: Einstellungen
        self.root.bind('<F1>', lambda e: self._open_settings())
        
        # ESC: Session beenden (wenn aktiv)
        self.root.bind('<Escape>', lambda e: self._stop_session() if self.session_active else None)
    
    def _setup_ui(self):
        """Erstellt die UI-Komponenten"""
        # Hauptcontainer
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Kopfzeile mit Buttons
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Session-Buttons
        self.start_button = ttk.Button(
            header_frame,
            text="Session starten",
            command=self._start_session,
            style="Accent.TButton"
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(
            header_frame,
            text="Session beenden",
            command=self._stop_session,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.pause_button = ttk.Button(
            header_frame,
            text="Pause",
            command=self._pause_session,
            state=tk.DISABLED
        )
        self.pause_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Undo/Redo Buttons
        self.undo_button = ttk.Button(
            header_frame,
            text="Rückgängig",
            command=self._undo_step,
            state=tk.DISABLED
        )
        self.undo_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.redo_button = ttk.Button(
            header_frame,
            text="Wiederholen",
            command=self._redo_step,
            state=tk.DISABLED
        )
        self.redo_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Einstellungen-Button
        settings_button = ttk.Button(
            header_frame,
            text="Einstellungen",
            command=self._open_settings
        )
        settings_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self._setup_hotkeys()
        
        # Status-Anzeige
        status_frame = ttk.Frame(header_frame)
        status_frame.pack(side=tk.RIGHT)
        
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT, padx=(10, 5))
        self.status_label = ttk.Label(
            status_frame,
            text="Bereit",
            foreground="green"
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Preview-Panel
        self.preview_panel = PreviewPanel(main_frame)
        self.preview_panel.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Infobereich am unteren Rand
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.info_label = ttk.Label(
            info_frame,
            text="Bereit zum Starten einer neuen Session",
            foreground="gray"
        )
        self.info_label.pack(side=tk.LEFT)
        
        # Statistiken-Frame
        stats_frame = ttk.Frame(info_frame)
        stats_frame.pack(side=tk.RIGHT)
        
        # Schritt-Zähler
        self.step_counter_label = ttk.Label(
            stats_frame,
            text="Schritte: 0",
            foreground="gray"
        )
        self.step_counter_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Dauer-Anzeige
        self.duration_label = ttk.Label(
            stats_frame,
            text="Dauer: 0s",
            foreground="gray"
        )
        self.duration_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Screenshot-Zähler
        self.screenshot_counter_label = ttk.Label(
            stats_frame,
            text="Screenshots: 0",
            foreground="gray"
        )
        self.screenshot_counter_label.pack(side=tk.LEFT)
    
    def _load_settings(self):
        """Lädt Einstellungen aus Environment-Variablen"""
        # Lade API-Key aus Environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your_openai_api_key_here':
            self._update_status("Warnung: OpenAI API-Key nicht gesetzt", "orange")
            self.info_label.config(
                text="Bitte konfigurieren Sie den OpenAI API-Key in den Einstellungen",
                foreground="orange"
            )
        
        # Lade Standard-Profil
        from src.config.config_manager import ConfigManager
        config_manager = ConfigManager()
        profiles = config_manager.list_prompt_profiles()
        if profiles:
            self.current_profile = profiles[0]
            self.info_label.config(
                text=f"Aktuelles Profil: {self.current_profile}",
                foreground="gray"
            )
    
    def _start_session(self):
        """Startet eine neue Aufzeichnungssession"""
        if self.session_active:
            return
        
        # Prüfe API-Key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your_openai_api_key_here':
            messagebox.showerror(
                "Fehler",
                "OpenAI API-Key nicht konfiguriert!\nBitte konfigurieren Sie den API-Key in den Einstellungen."
            )
            return
        
        # Prüfe Profil
        if not self.current_profile:
            messagebox.showerror(
                "Fehler",
                "Kein Prompt-Profil ausgewählt!\nBitte wählen Sie ein Profil in den Einstellungen."
            )
            return
        
        try:
            # Importiere Session-Manager
            from src.monitor.session_manager import SessionManager
            
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.session_manager = SessionManager(
                session_id=session_id,
                prompt_profile=self.current_profile
            )
            
            # Starte Session in separatem Thread
            threading.Thread(target=self._run_session, daemon=True).start()
            
            self.session_active = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.NORMAL, text="Pause")
            self.undo_button.config(state=tk.NORMAL)
            self.redo_button.config(state=tk.NORMAL)
            self._update_status("Aufzeichnung läuft...", "green")
            self.info_label.config(
                text=f"Session '{session_id}' gestartet - Erfasse Schritte...",
                foreground="green"
            )
            self.preview_panel.clear()
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Starten der Session:\n{str(e)}")
    
    def _run_session(self):
        """Führt die Session aus (in separatem Thread)"""
        if self.session_manager:
            self.session_manager.start()
            # Update UI periodisch
            self.root.after(1000, self._update_session_status)
    
    def _update_session_status(self):
        """Aktualisiert den Session-Status in der UI"""
        if self.session_active and self.session_manager:
            step_count = self.session_manager.get_step_count()
            self.step_counter_label.config(text=f"Schritte: {step_count}")
            
            # Update Statistiken
            stats = self.session_manager.get_session_statistics()
            if stats.get('duration_formatted'):
                self.duration_label.config(text=f"Dauer: {stats['duration_formatted']}")
            if stats.get('screenshot_count') is not None:
                self.screenshot_counter_label.config(text=f"Screenshots: {stats['screenshot_count']}")
            
            # Update Undo/Redo Buttons
            self._update_undo_redo_buttons()
            
            # Update Preview mit neuen Schritten
            steps = self.session_manager.get_steps()
            self.preview_panel.update_steps(steps)
            
            # Weiter prüfen
            if self.session_active:
                self.root.after(1000, self._update_session_status)
    
    def _stop_session(self):
        """Beendet die aktuelle Session"""
        if not self.session_active:
            return
        
        try:
            if self.session_manager:
                self.session_manager.stop()
                
                # Generiere Dokumente (in separatem Thread)
                threading.Thread(
                    target=self._generate_documents,
                    daemon=True
                ).start()
            
            self.session_active = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.DISABLED, text="Pause")
            self.undo_button.config(state=tk.DISABLED)
            self.redo_button.config(state=tk.DISABLED)
            self._update_status("Generiere Dokumente...", "blue")
            self.info_label.config(
                text="Dokumente werden generiert, bitte warten...",
                foreground="blue"
            )
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Beenden der Session:\n{str(e)}")
    
    def _generate_documents(self):
        """Generiert die Dokumente nach Session-Ende"""
        try:
            if self.session_manager:
                # Generiere Dokumente
                from src.document.template_engine import TemplateEngine
                
                template_engine = TemplateEngine(
                    self.session_manager,
                    template_name=self.current_template
                )
                
                # Lade Export-Formate aus Config
                export_formats = {
                    'docx': True,
                    'pdf': True,
                    'markdown': False,
                    'html': False,
                    'json': True,
                    'csv': False
                }
                
                from pathlib import Path
                import yaml
                export_config_path = Path("config") / "export_formats.yml"
                if export_config_path.exists():
                    try:
                        with open(export_config_path, 'r', encoding='utf-8') as f:
                            export_config = yaml.safe_load(f)
                            export_formats.update(export_config or {})
                    except Exception:
                        pass
                
                output_path = template_engine.generate_document(export_formats=export_formats)
                
                # Update UI
                self.root.after(0, lambda: self._on_documents_generated(output_path))
        
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Fehler",
                f"Fehler bei der Dokumentgenerierung:\n{str(e)}"
            ))
    
    def _on_documents_generated(self, output_path: Path):
        """Callback nach erfolgreicher Dokumentgenerierung"""
        self._update_status("Bereit", "green")
        
        # Zeige Session-Statistiken
        if self.session_manager:
            stats = self.session_manager.get_session_statistics()
            stats_text = (
                f"Session abgeschlossen!\n\n"
                f"Statistiken:\n"
                f"- Dauer: {stats.get('duration_formatted', 'N/A')}\n"
                f"- Schritte: {stats.get('step_count', 0)}\n"
                f"- Screenshots: {stats.get('screenshot_count', 0)}\n"
                f"- Fenster verwendet: {stats.get('windows_used', 0)}\n"
                f"- Prozesse verwendet: {stats.get('processes_used', 0)}\n"
                f"- Schritte/Minute: {stats.get('average_steps_per_minute', 0):.1f}\n\n"
                f"Dokument: {output_path}"
            )
            self.info_label.config(text=stats_text, foreground="green")
            messagebox.showinfo("Erfolg", stats_text)
        else:
            self.info_label.config(
                text=f"Dokument erfolgreich generiert: {output_path}",
                foreground="green"
            )
            messagebox.showinfo(
                "Erfolg",
                f"Dokument erfolgreich generiert!\n\n{output_path}"
            )
    
    def _pause_session(self):
        """Pausiert oder setzt die Session fort"""
        if not self.session_active or not self.session_manager:
            return
        
        if self.session_manager.paused:
            # Resume
            self.session_manager.resume()
            self.pause_button.config(text="Pause")
            self._update_status("Aufzeichnung läuft...", "green")
            self.info_label.config(
                text="Session fortgesetzt",
                foreground="green"
            )
        else:
            # Pause
            self.session_manager.pause()
            self.pause_button.config(text="Fortsetzen")
            self._update_status("Aufzeichnung pausiert", "orange")
            self.info_label.config(
                text="Session pausiert",
                foreground="orange"
            )
    
    def _undo_step(self):
        """Macht den letzten Schritt rückgängig"""
        if not self.session_manager:
            return
        
        if self.session_manager.undo():
            # Aktualisiere UI
            steps = self.session_manager.get_steps()
            self.preview_panel.update_steps(steps)
            self._update_undo_redo_buttons()
            self._update_session_status()
            logger.info("Schritt rückgängig gemacht")
        else:
            messagebox.showinfo("Info", "Keine Schritte zum Rückgängig machen verfügbar.")
    
    def _redo_step(self):
        """Stellt den letzten Undo wieder her"""
        if not self.session_manager:
            return
        
        if self.session_manager.redo():
            # Aktualisiere UI
            steps = self.session_manager.get_steps()
            self.preview_panel.update_steps(steps)
            self._update_undo_redo_buttons()
            self._update_session_status()
            logger.info("Schritt wiederholt")
        else:
            messagebox.showinfo("Info", "Keine Schritte zum Wiederholen verfügbar.")
    
    def _update_undo_redo_buttons(self):
        """Aktualisiert den Status der Undo/Redo-Buttons"""
        if self.session_manager:
            self.undo_button.config(state=tk.NORMAL if self.session_manager.can_undo() else tk.DISABLED)
            self.redo_button.config(state=tk.NORMAL if self.session_manager.can_redo() else tk.DISABLED)
    
    def _delete_step_from_session(self, index: int):
        """
        Löscht einen Schritt aus der Session
        
        Args:
            index: Index des zu löschenden Schritts
        """
        if not self.session_manager:
            return
        
        steps = self.session_manager.get_steps()
        if index >= len(steps):
            return
        
        # Speichere History für Undo
        self.session_manager._save_history_state()
        
        # Lösche Schritt
        with self.session_manager.lock:
            if index < len(self.session_manager.steps):
                del self.session_manager.steps[index]
                # Aktualisiere Schritt-Nummern
                for i, step in enumerate(self.session_manager.steps[index:], start=index):
                    step['step_number'] = i + 1
        
        # Aktualisiere UI
        steps = self.session_manager.get_steps()
        self.preview_panel.update_steps(steps)
        self._update_undo_redo_buttons()
        self._update_session_status()
        
        logger.info(f"Schritt {index + 1} gelöscht")
    
    def _show_recovery_dialog(self):
        """Zeigt Dialog zur Session-Wiederherstellung"""
        if self.session_active:
            if not messagebox.askyesno(
                "Session beenden",
                "Es läuft bereits eine Session.\n"
                "Möchten Sie diese beenden und zur Wiederherstellung wechseln?"
            ):
                return
            self._stop_session()
        
        dialog = SessionRecoveryDialog(self.root)
        self.root.wait_window(dialog.dialog)
        
        # Wenn Session wiederhergestellt wurde, aktualisiere UI
        if hasattr(dialog, 'restored_session') and dialog.restored_session:
            session_manager = dialog.restored_session
            self.session_manager = session_manager
            self.session_active = True
            self.current_profile = session_manager.prompt_profile
            
            # Aktualisiere UI
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.NORMAL if not session_manager.paused else tk.DISABLED)
            self._update_status("Session wiederhergestellt", "green")
            
            # Lade Schritte
            steps = session_manager.get_steps()
            self.preview_panel.update_steps(steps)
            self._update_undo_redo_buttons()
            self._update_session_status()
            
            logger.info(f"Session UI aktualisiert: {session_manager.session_id}")
    
    def _run_manual_cleanup(self):
        """Führt manuelle Bereinigung aus"""
        if not messagebox.askyesno(
            "Bereinigung ausführen",
            "Möchten Sie die manuelle Bereinigung ausführen?\n"
            "Alte Screenshots und Sessions werden gelöscht."
        ):
            return
        
        try:
            from src.utils.cleanup_manager import CleanupManager
            import yaml
            
            # Lade Cleanup-Konfiguration
            cleanup_config_path = Path("config") / "cleanup_config.yml"
            retention_days_screenshots = 30
            retention_days_sessions = 90
            
            if cleanup_config_path.exists():
                try:
                    with open(cleanup_config_path, 'r', encoding='utf-8') as f:
                        cleanup_config = yaml.safe_load(f)
                        if cleanup_config:
                            retention_days_screenshots = cleanup_config.get('retention_days_screenshots', 30)
                            retention_days_sessions = cleanup_config.get('retention_days_sessions', 90)
                except Exception:
                    pass
            
            cleanup_manager = CleanupManager(
                retention_days_screenshots=retention_days_screenshots,
                retention_days_sessions=retention_days_sessions
            )
            
            stats = cleanup_manager.cleanup_all(dry_run=False)
            
            screenshots_stats = stats.get('screenshots', {})
            sessions_stats = stats.get('sessions', {})
            
            total_deleted = screenshots_stats.get('deleted_count', 0) + sessions_stats.get('deleted_count', 0)
            
            messagebox.showinfo(
                "Bereinigung abgeschlossen",
                f"Bereinigung erfolgreich durchgeführt:\n\n"
                f"Screenshots gelöscht: {screenshots_stats.get('deleted_count', 0)}\n"
                f"Sessions gelöscht: {sessions_stats.get('deleted_count', 0)}\n"
                f"Gesamt gelöscht: {total_deleted}"
            )
            
            logger.info(f"Manuelle Bereinigung abgeschlossen: {total_deleted} Dateien gelöscht")
        
        except Exception as e:
            logger.error(f"Fehler bei manueller Bereinigung: {e}", exc_info=True)
            messagebox.showerror("Fehler", f"Fehler bei der Bereinigung:\n{str(e)}")
    
    def _open_settings(self):
        """Öffnet den Einstellungsdialog"""
        dialog = SettingsDialog(self.root, self)
        self.root.wait_window(dialog.dialog)
    
    def _update_status(self, text: str, color: str = "black"):
        """
        Aktualisiert die Status-Anzeige
        
        Args:
            text: Status-Text
            color: Textfarbe
        """
        self.status_label.config(text=text, foreground=color)
    
    def set_prompt_profile(self, profile_name: str):
        """
        Setzt das aktuelle Prompt-Profil
        
        Args:
            profile_name: Name des Profils
        """
        self.current_profile = profile_name
        self.info_label.config(
            text=f"Aktuelles Profil: {profile_name}",
            foreground="gray"
        )
    
    def set_document_template(self, template_name: str):
        """
        Setzt die aktuelle Dokumentvorlage
        
        Args:
            template_name: Name der Vorlage
        """
        self.current_template = template_name
        self.info_label.config(
            text=f"Aktuelles Profil: {self.current_profile}, Vorlage: {template_name}",
            foreground="gray"
        )

