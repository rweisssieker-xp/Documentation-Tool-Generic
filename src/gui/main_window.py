"""
Hauptfenster der GUI-Anwendung
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import os
from datetime import datetime
from typing import Dict, List
import threading

from src.gui.settings_dialog import SettingsDialog
from src.gui.preview_panel import PreviewPanel
from src.gui.recovery_dialog import SessionRecoveryDialog
from src.gui.batch_dialog import BatchDialog
from src.gui.export_filter_dialog import ExportFilterDialog
from src.gui.stats_dashboard import StatisticsDashboard
from src.gui.multilang_export_dialog import MultiLangExportDialog
from src.gui.cloud_upload_dialog import CloudUploadDialog
from src.gui.quickref_export_dialog import QuickRefExportDialog
from src.gui.video_export_dialog import VideoExportDialog
from src.gui.consolidation_dialog import ConsolidationDialog
from src.gui.session_compare_dialog import SessionCompareDialog
from src.gui.test_checklist_dialog import TestChecklistDialog
from src.gui.app_selector_dialog import AppSelectorDialog
from src.gui.exploration_progress_dialog import ExplorationProgressDialog
from src.gui.progress_dialog import ProgressDialog
from src.gui.platform_export_dialog import PlatformExportDialog
from src.gui.gitops_dialog import GitOpsDialog
from src.gui.accessibility_dialog import AccessibilityDialog
from src.gui.roi_dashboard import ROIDashboard
from src.gui.video_synthesis_dialog import VideoSynthesisDialog
from src.gui.translation_dialog import TranslationDialog
from src.gui.collaboration_dialog import CollaborationDialog
from src.gui.agent_dialog import AgentDialog
from src.gui.api_dialog import APIDialog
from src.gui.plugin_dialog import PluginDialog
from src.gui.edge_ai_dialog import EdgeAIDialog
from src.gui.blockchain_dialog import BlockchainDialog
from src.gui.predictive_dialog import PredictiveDialog
from src.gui.multimodal_dialog import MultiModalDialog
from src.gui.ar_dialog import ARDialog
from src.gui.self_learning_dialog import SelfLearningDialog
from src.gui.agentic_dialog import AgenticDialog
from src.gui.hyperautomation_dialog import HyperautomationDialog
from src.gui.localization_dialog import LocalizationDialog
from src.gui.compliance_dialog import ComplianceDialog
from src.gui.adaptive_ux_dialog import AdaptiveUXDialog
from src.gui.predictive_workflow_dialog import PredictiveWorkflowDialog
from src.gui.data_hub_dialog import DataHubDialog
from src.gui.intelligent_assistant_dialog import IntelligentAssistantDialog
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
        
        # Export-Menü
        export_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Export", menu=export_menu)
        export_menu.add_command(label="Multi-Sprach-Export...", command=self._show_multilang_export)
        export_menu.add_command(label="Cloud-Upload...", command=self._show_cloud_upload)
        export_menu.add_command(label="Quick-Reference...", command=self._show_quickref_export)
        export_menu.add_command(label="Video-Export...", command=self._show_video_export)
        export_menu.add_command(label="Platform-Export...", command=self._show_platform_export)
        export_menu.add_separator()
        export_menu.add_command(label="Export-Filter...", command=self._show_export_filter_dialog)
        
        # Hilfe-Menü
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Hilfe", menu=help_menu)
        help_menu.add_command(label="Tastenkürzel...", command=self._show_shortcuts)
        help_menu.add_command(label="Über...", command=self._show_about)
        
        # Tools-Menü
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Bereinigung ausführen...", command=self._run_manual_cleanup)
        tools_menu.add_separator()
        tools_menu.add_command(label="Batch-Verarbeitung...", command=self._show_batch_dialog)
        tools_menu.add_command(label="Statistiken...", command=self._show_stats_dashboard)
        tools_menu.add_separator()
        tools_menu.add_command(label="Schritt-Konsolidierung...", command=self._show_consolidation_dialog)
        tools_menu.add_command(label="Session-Vergleich...", command=self._show_session_compare)
        tools_menu.add_command(label="Test-Checkliste generieren...", command=self._show_test_checklist)
        tools_menu.add_command(label="Qualitätsprüfung...", command=self._show_quality_check)
        tools_menu.add_separator()
        tools_menu.add_command(label="Export-Filter...", command=self._show_export_filter_dialog)
        
        # Automatisierung-Menü
        automation_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Automatisierung", menu=automation_menu)
        automation_menu.add_command(label="App erkunden...", command=self._start_automated_exploration)
        
        # Innovation-Menü (Neue Features)
        innovation_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🚀 Innovation", menu=innovation_menu)
        innovation_menu.add_command(label="🎤 Sprachsteuerung...", command=self._show_voice_control)
        innovation_menu.add_command(label="🔍 Wissenssuche...", command=self._show_knowledge_search)
        innovation_menu.add_separator()
        innovation_menu.add_command(label="🧪 Test-Export...", command=self._show_test_export)
        innovation_menu.add_command(label="📚 Tutorial-Export...", command=self._show_tutorial_export)
        innovation_menu.add_separator()
        innovation_menu.add_command(label="🔎 Process Mining...", command=self._show_process_mining)
        innovation_menu.add_separator()
        innovation_menu.add_command(label="🔧 GitOps Pipeline...", command=self._show_gitops_dialog, accelerator="Ctrl+Alt+G")
        innovation_menu.add_command(label="♿ Accessibility Check...", command=self._show_accessibility_dialog, accelerator="Ctrl+Alt+A")
        innovation_menu.add_command(label="📊 ROI Dashboard...", command=self._show_roi_dashboard, accelerator="Ctrl+Alt+R")
        innovation_menu.add_command(label="🎬 Video Tutorial Generator...", command=self._show_video_synthesis)
        innovation_menu.add_separator()
        innovation_menu.add_command(label="🌐 Translation Hub...", command=self._show_translation_dialog, accelerator="Ctrl+Alt+T")
        innovation_menu.add_command(label="👥 Collaboration Hub...", command=self._show_collaboration_dialog, accelerator="Ctrl+Alt+C")
        innovation_menu.add_command(label="🤖 Autonomous Agent...", command=self._show_agent_dialog, accelerator="Ctrl+Alt+B")
        innovation_menu.add_separator()
        innovation_menu.add_command(label="🔌 API Gateway...", command=self._show_api_dialog, accelerator="Ctrl+Alt+Shift+A")
        innovation_menu.add_command(label="🔌 Plugin System...", command=self._show_plugin_dialog, accelerator="Ctrl+Alt+Shift+P")
        innovation_menu.add_command(label="⚡ Edge AI Engine...", command=self._show_edge_ai_dialog, accelerator="Ctrl+Alt+Shift+E")
        innovation_menu.add_command(label="🔗 Blockchain Audit...", command=self._show_blockchain_dialog, accelerator="Ctrl+Alt+Shift+B")
        innovation_menu.add_command(label="🔮 Predictive Maintenance...", command=self._show_predictive_dialog, accelerator="Ctrl+Alt+Shift+M")
        innovation_menu.add_command(label="🎥 Multi-Modal Capture...", command=self._show_multimodal_dialog, accelerator="Ctrl+Alt+Shift+U")
        innovation_menu.add_command(label="🥽 AR Documentation...", command=self._show_ar_dialog, accelerator="Ctrl+Alt+Shift+R")
        innovation_menu.add_separator()
        innovation_menu.add_command(label="🧠 Self-Learning AI...", command=self._show_self_learning_dialog, accelerator="Ctrl+Alt+Shift+L")
        innovation_menu.add_command(label="🤖 Agentic Automation...", command=self._show_agentic_dialog, accelerator="Ctrl+Alt+Shift+O")
        innovation_menu.add_command(label="🔗 Federated Learning...", command=self._show_federated_dialog, accelerator="Ctrl+Alt+Shift+F")
        innovation_menu.add_separator()
        innovation_menu.add_command(label="⚙️ Hyperautomation...", command=self._show_hyperautomation_dialog, accelerator="Ctrl+Alt+Shift+H")
        innovation_menu.add_command(label="🌍 AI Localization...", command=self._show_localization_dialog, accelerator="Ctrl+Alt+Shift+I")
        innovation_menu.add_command(label="✅ Compliance Automation...", command=self._show_compliance_dialog, accelerator="Ctrl+Alt+Shift+N")
        innovation_menu.add_separator()
        innovation_menu.add_command(label="🎨 Adaptive UX...", command=self._show_adaptive_ux_dialog, accelerator="Ctrl+Alt+Shift+X")
        innovation_menu.add_command(label="🔮 Predictive Workflow...", command=self._show_predictive_workflow_dialog, accelerator="Ctrl+Alt+Shift+W")
        innovation_menu.add_command(label="🔌 Universal Data Hub...", command=self._show_data_hub_dialog, accelerator="Ctrl+Alt+Shift+D")
        innovation_menu.add_command(label="💬 Intelligent Assistant...", command=self._show_intelligent_assistant_dialog, accelerator="Ctrl+Alt+Shift+S")
    
    def _show_shortcuts(self):
        """Zeigt Dialog mit Tastenkürzeln"""
        shortcuts_text = """
Tastenkürzel (Hotkeys)

Session-Steuerung:
  Ctrl+S              - Session starten
  Ctrl+Shift+S        - Session beenden
  Ctrl+P              - Pause/Fortsetzen
  ESC                 - Session beenden (wenn aktiv)
  Space               - Pause/Fortsetzen (je nach Zustand)
  Enter               - Bestätigen/Starten (je nach Zustand)

Bearbeitung:
  Ctrl+Z              - Rückgängig (Undo)
  Ctrl+Y              - Wiederholen (Redo)
  Ctrl+Shift+Z        - Wiederholen (Redo, alternativ)
  Ctrl+R              - Schritt-Konsolidierung
  Ctrl+E              - Export-Filter öffnen

Navigation:
  Ctrl+M              - Statistiken öffnen
  Ctrl+T              - Qualitätsprüfung öffnen
  Ctrl+O              - Session wiederherstellen
  F2                  - Batch-Verarbeitung öffnen
  F3                  - Session-Vergleich öffnen
  F4                  - Test-Checkliste öffnen
  F5                  - Vorschau aktualisieren
  Ctrl+H              - Diese Hilfe öffnen

Funktionen:
  Ctrl+D              - Bereinigung ausführen
  Ctrl+Q              - Anwendung beenden
  Ctrl+Shift+P        - Vorschau-Sichtbarkeit umschalten

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
        
        # Weitere Tastenkürzel für häufige Aktionen
        # Ctrl+O: Session wiederherstellen
        self.root.bind('<Control-o>', lambda e: self._show_recovery_dialog())
        
        # Ctrl+M: Statistiken öffnen
        self.root.bind('<Control-m>', lambda e: self._show_stats_dashboard())
        
        # Ctrl+Alt+G: GitOps Dialog
        self.root.bind('<Control-Alt-g>', lambda e: self._show_gitops_dialog())
        
        # Ctrl+Alt+A: Accessibility Dialog
        self.root.bind('<Control-Alt-a>', lambda e: self._show_accessibility_dialog())
        
        # Ctrl+Alt+R: ROI Dashboard
        self.root.bind('<Control-Alt-r>', lambda e: self._show_roi_dashboard())
        
        # Ctrl+Alt+T: Translation Hub
        self.root.bind('<Control-Alt-t>', lambda e: self._show_translation_dialog())
        
        # Ctrl+Alt+C: Collaboration Hub
        self.root.bind('<Control-Alt-c>', lambda e: self._show_collaboration_dialog())
        
        # Ctrl+Alt+B: Autonomous Agent
        self.root.bind('<Control-Alt-b>', lambda e: self._show_agent_dialog())
        
        # Ctrl+Alt+Shift+A: API Gateway
        self.root.bind('<Control-Alt-Shift-a>', lambda e: self._show_api_dialog())
        
        # Ctrl+Alt+Shift+P: Plugin System
        self.root.bind('<Control-Alt-Shift-p>', lambda e: self._show_plugin_dialog())
        
        # Ctrl+Alt+Shift+E: Edge AI
        self.root.bind('<Control-Alt-Shift-e>', lambda e: self._show_edge_ai_dialog())
        
        # Ctrl+Alt+Shift+B: Blockchain
        self.root.bind('<Control-Alt-Shift-b>', lambda e: self._show_blockchain_dialog())
        
        # Ctrl+Alt+Shift+M: Predictive Maintenance
        self.root.bind('<Control-Alt-Shift-m>', lambda e: self._show_predictive_dialog())
        
        # Ctrl+Alt+Shift+U: Multi-Modal Capture
        self.root.bind('<Control-Alt-Shift-u>', lambda e: self._show_multimodal_dialog())
        
        # Ctrl+Alt+Shift+R: AR Documentation
        self.root.bind('<Control-Alt-Shift-r>', lambda e: self._show_ar_dialog())
        
        # Ctrl+T: Qualitätsprüfung öffnen
        self.root.bind('<Control-t>', lambda e: self._show_quality_check())
        
        # Ctrl+E: Export-Filter öffnen
        self.root.bind('<Control-e>', lambda e: self._show_export_filter_dialog())
        
        # F2: Batch-Verarbeitung öffnen
        self.root.bind('<F2>', lambda e: self._show_batch_dialog())
        
        # F3: Session-Vergleich öffnen
        self.root.bind('<F3>', lambda e: self._show_session_compare())
        
        # F4: Test-Checkliste öffnen
        self.root.bind('<F4>', lambda e: self._show_test_checklist())
        
        # F5: Aktualisierung/Neuladen der Vorschau
        self.root.bind('<F5>', lambda e: self._refresh_preview())
        
        # Ctrl+D: Bereinigung ausführen
        self.root.bind('<Control-d>', lambda e: self._run_manual_cleanup())
        
        # Ctrl+H: Hilfe öffnen (Tastenkürzel-Ansicht)
        self.root.bind('<Control-h>', lambda e: self._show_shortcuts())
        
        # Ctrl+R: Schritt-Konsolidierung öffnen
        self.root.bind('<Control-r>', lambda e: self._show_consolidation_dialog())
        
        # Ctrl+Q: Anwendung beenden
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        
        # Enter: Bestätigen/OK in aktueller Situation
        self.root.bind('<Return>', lambda e: self._handle_enter_key())
        
        # Space: Pause/Weiter je nach aktuellem Zustand
        self.root.bind('<space>', lambda e: self._handle_space_key())
        
        # Strg+Shift+P: Screenshot-Preview umschalten (falls implementiert)
        self.root.bind('<Control-Shift-P>', lambda e: self._toggle_preview())
    
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
        self.preview_panel.main_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
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
            
            # Setze Callbacks für Preview-Panel
            self.preview_panel.set_delete_callback(self._delete_step_from_session)
            self.preview_panel.set_reorder_callback(self._reorder_steps)
            
        except Exception as e:
            logger.error(f"Fehler beim Starten der Session: {str(e)}", exc_info=True)
            messagebox.showerror(
                "Fehler", 
                f"Fehler beim Starten der Session:\n\n{str(e)}\n\nDetails finden Sie in der Logdatei unter 'logs/ahg.log'."
            )
    
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
                
                # Frage nach Filter VOR dem Thread (im Hauptthread)
                steps = self.session_manager.get_steps()
                filtered_steps = steps
                apply_filter = False
                
                if steps:
                    apply_filter = messagebox.askyesno(
                        "Export-Filter",
                        "Möchten Sie einen Export-Filter anwenden?\n\n"
                        "Sie können Schritte nach Datum, Fenster-Titel oder Schritt-Indizes filtern."
                    )
                    
                    if apply_filter:
                        filter_dialog = ExportFilterDialog(self.root, steps)
                        self.root.wait_window(filter_dialog.dialog)
                        filtered_steps = filter_dialog.get_filtered_steps()
                
                # Generiere Dokumente (in separatem Thread)
                threading.Thread(
                    target=self._generate_documents,
                    args=(filtered_steps, apply_filter),
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
            logger.error(f"Fehler beim Beenden der Session: {str(e)}", exc_info=True)
            messagebox.showerror(
                "Fehler", 
                f"Fehler beim Beenden der Session:\n\n{str(e)}\n\nDetails finden Sie in der Logdatei unter 'logs/ahg.log'."
            )
    
    def _generate_documents(self, filtered_steps: List[Dict] = None, applied_filter: bool = False):
        """Generiert die Dokumente nach Session-Ende"""
        try:
            if not self.session_manager:
                self.root.after(0, lambda: messagebox.showerror(
                    "Fehler",
                    "Keine Session vorhanden."
                ))
                return
            
            steps = filtered_steps if filtered_steps else self.session_manager.get_steps()
            
            if not steps:
                self.root.after(0, lambda: messagebox.showwarning(
                    "Keine Schritte",
                    "Es sind keine Schritte vorhanden. Dokument kann nicht generiert werden."
                ))
                return
            
            # Temporär gefilterte Schritte setzen
            original_steps = None
            if applied_filter and filtered_steps != self.session_manager.get_steps():
                original_steps = self.session_manager.steps.copy()
                with self.session_manager.lock:
                    self.session_manager.steps = filtered_steps.copy()
            
            # Erstelle Fortschrittsdialog
            progress_dialog = ProgressDialog(
                self.root,
                title="Dokumente werden generiert...",
                max_value=100,
                show_percentage=True,
                cancellable=True
            )
            
            # Callback für Abbruch
            def cancel_callback():
                logger.info("Dokumentgenerierung wurde abgebrochen")
                # Hier könnte man eine Abbruchvariable setzen
            
            progress_dialog.set_cancel_callback(cancel_callback)
            
            # Starte Generierung in separatem Thread mit Fortschrittsanzeige
            def generate_with_progress():
                try:
                    # Simuliere Fortschritt für verschiedene Phasen
                    total_phases = 4  # 1. Initialisierung, 2. Textgenerierung, 3. Export, 4. Abschluss
                    phase_progress = 100 / total_phases
                    
                    # Phase 1: Initialisierung
                    progress_dialog.update_progress(0, "Initialisiere Dokumentenerstellung...")
                    from src.document.template_engine import TemplateEngine
                    
                    template_engine = TemplateEngine(
                        self.session_manager,
                        template_name=self.current_template
                    )
                    
                    if progress_dialog.is_cancelled():
                        return
                    
                    # Phase 2: Lade Export-Formate
                    progress_dialog.update_progress(
                        phase_progress, 
                        "Lade Export-Konfiguration..."
                    )
                    from pathlib import Path
                    import yaml
                    export_config_path = Path("config") / "export_formats.yml"
                    export_formats = {
                        'docx': True,
                        'pdf': True,
                        'markdown': False,
                        'html': False,
                        'json': True,
                        'csv': False,
                        'latex': False  # Hinzugefügt für LaTeX-Export
                    }
                    
                    if export_config_path.exists():
                        try:
                            with open(export_config_path, 'r', encoding='utf-8') as f:
                                export_config = yaml.safe_load(f)
                                export_formats.update(export_config or {})
                        except Exception:
                            pass
                    
                    if progress_dialog.is_cancelled():
                        return
                    
                    # Phase 3: Generiere Dokumente
                    progress_dialog.update_progress(
                        phase_progress * 2, 
                        "Generiere Dokumente (dies kann einige Minuten dauern)..."
                    )
                    output_path = template_engine.generate_document(export_formats=export_formats)
                    
                    if progress_dialog.is_cancelled():
                        return
                    
                    # Phase 4: Qualitätsprüfung und Abschluss
                    progress_dialog.update_progress(
                        phase_progress * 3, 
                        "Führe Qualitätsprüfung durch..."
                    )
                    
                    # Stelle originale Schritte wieder her
                    if original_steps is not None:
                        with self.session_manager.lock:
                            self.session_manager.steps = original_steps
                    
                    # Optionale Qualitätsprüfung
                    from src.document.quality_checker import QualityChecker
                    quality_checker = QualityChecker()
                    quality_metrics = quality_checker.check_quality(steps)
                    
                    logger.info(f"Dokument erfolgreich generiert: {output_path}")
                    
                    # Update UI
                    self.root.after(0, lambda: progress_dialog.close())
                    self.root.after(0, lambda: self._on_documents_generated(output_path, quality_metrics))
                
                except Exception as e:
                    import traceback
                    error_msg = f"Fehler bei der Dokumentgenerierung:\n{str(e)}\n\n{traceback.format_exc()}"
                    logger.error(error_msg, exc_info=True)
                    
                    # Schließe Dialog und zeige Fehlermeldung
                    self.root.after(0, lambda: progress_dialog.close())
                    self.root.after(0, lambda err=e: messagebox.showerror(
                        "Fehler",
                        f"Fehler bei der Dokumentgenerierung:\n{str(err)}\n\nÜberprüfen Sie die Logs für Details."
                    ))
            
            # Starte Thread für Generierung
            generation_thread = threading.Thread(target=generate_with_progress, daemon=True)
            generation_thread.start()
        
        except ValueError as e:
            # Spezifische Behandlung für ValueError (z.B. keine Schritte)
            error_msg = str(e)
            logger.warning(f"Dokumentgenerierung abgebrochen: {error_msg}")
            messagebox.showwarning(
                "Keine Schritte",
                f"{error_msg}\n\nBitte starten Sie eine Session und erfassen Sie mindestens einen Schritt."
            )
        except Exception as e:
            import traceback
            error_msg = f"Fehler bei der Dokumentgenerierung:\n{str(e)}\n\n{traceback.format_exc()}"
            logger.error(error_msg, exc_info=True)
            messagebox.showerror(
                "Fehler",
                f"Fehler bei der Dokumentgenerierung:\n{str(e)}\n\nÜberprüfen Sie die Logs für Details."
            )
    
    def _on_documents_generated(self, output_path: Path, quality_metrics: Dict = None):
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
            
            # Füge Qualitäts-Score hinzu falls verfügbar
            if quality_metrics:
                score = quality_metrics.get('overall_score', 0.0)
                stats_text += f"\n\nQualitäts-Score: {score:.1%}"
                if score < 0.7:
                    stats_text += "\n⚠️ Empfehlung: Qualitätsprüfung ausführen für Verbesserungsvorschläge"
            
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
    
    def _reorder_steps(self, from_index: int, to_index: int):
        """
        Ändert die Reihenfolge von Schritten
        
        Args:
            from_index: Ursprünglicher Index
            to_index: Neuer Index
        """
        if not self.session_manager:
            return
        
        steps = self.session_manager.get_steps()
        if from_index >= len(steps) or to_index >= len(steps):
            return
        
        # Speichere History für Undo
        self.session_manager._save_history_state()
        
        # Verschiebe Schritt
        with self.session_manager.lock:
            step = self.session_manager.steps.pop(from_index)
            self.session_manager.steps.insert(to_index, step)
            
            # Aktualisiere Schritt-Nummern
            for i, s in enumerate(self.session_manager.steps, start=1):
                s['step_number'] = i
        
        # Aktualisiere UI
        steps = self.session_manager.get_steps()
        self.preview_panel.update_steps(steps)
        self._update_undo_redo_buttons()
        self._update_session_status()
        
        logger.info(f"Schritt {from_index + 1} nach Position {to_index + 1} verschoben")
    
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
            
            # Setze Callbacks für Preview-Panel
            self.preview_panel.set_delete_callback(self._delete_step_from_session)
            self.preview_panel.set_reorder_callback(self._reorder_steps)
            
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
            messagebox.showerror(
                "Fehler", 
                f"Fehler bei der Bereinigung:\n\n{str(e)}\n\nDetails finden Sie in der Logdatei unter 'logs/ahg.log'."
            )
    
    def _show_batch_dialog(self):
        """Zeigt Dialog zur Batch-Verarbeitung"""
        dialog = BatchDialog(self.root)
        self.root.wait_window(dialog.dialog)
    
    def _show_stats_dashboard(self):
        """Zeigt Statistiken-Dashboard"""
        dashboard = StatisticsDashboard(self.root)
        # Aktualisiere Qualitäts-Metriken wenn Session aktiv
        if self.session_manager and self.session_active:
            steps = self.session_manager.get_steps()
            dashboard.update_quality_metrics(steps)
        self.root.wait_window(dashboard.dialog)
    
    def _show_export_filter_dialog(self):
        """Zeigt Export-Filter-Dialog"""
        if not self.session_manager or not self.session_active:
            messagebox.showinfo(
                "Keine Session",
                "Bitte starten Sie zuerst eine Session oder stellen Sie eine wieder her."
            )
            return
        
        steps = self.session_manager.get_steps()
        if not steps:
            messagebox.showinfo(
                "Keine Schritte",
                "Es sind noch keine Schritte vorhanden."
            )
            return
        
        dialog = ExportFilterDialog(self.root, steps)
        self.root.wait_window(dialog.dialog)
    
    def _show_multilang_export(self):
        """Zeigt Multi-Sprach-Export Dialog"""
        if not self.session_manager:
            messagebox.showwarning("Keine Session", "Bitte starten Sie zuerst eine Session.")
            return
        
        steps = self.session_manager.get_steps()
        if not steps:
            messagebox.showwarning("Keine Schritte", "Es sind keine Schritte vorhanden.")
            return
        
        session_id = self.session_manager.session_id if self.session_manager else "unknown"
        dialog = MultiLangExportDialog(self.root, steps, session_id)
        self.root.wait_window(dialog.dialog)
    
    def _show_cloud_upload(self):
        """Zeigt Cloud-Upload Dialog"""
        # Frage nach Dateien zum Hochladen
        from tkinter import filedialog
        
        file_paths = filedialog.askopenfilenames(
            title="Dateien für Cloud-Upload auswählen",
            filetypes=[
                ("Alle Dokumente", "*.docx;*.pdf;*.md;*.html"),
                ("Word-Dokumente", "*.docx"),
                ("PDF-Dateien", "*.pdf"),
                ("Markdown-Dateien", "*.md"),
                ("HTML-Dateien", "*.html"),
                ("Alle Dateien", "*.*")
            ]
        )
        
        if not file_paths:
            return
        
        file_paths = [Path(f) for f in file_paths]
        dialog = CloudUploadDialog(self.root, file_paths)
        self.root.wait_window(dialog.dialog)
    
    def _show_quickref_export(self):
        """Zeigt Quick-Reference Export Dialog"""
        if not self.session_manager:
            messagebox.showwarning("Keine Session", "Bitte starten Sie zuerst eine Session.")
            return
        
        steps = self.session_manager.get_steps()
        if not steps:
            messagebox.showwarning("Keine Schritte", "Es sind keine Schritte vorhanden.")
            return
        
        dialog = QuickRefExportDialog(self.root, steps)
        self.root.wait_window(dialog.dialog)
    
    def _show_video_export(self):
        """Zeigt Video-Export Dialog"""
        if not self.session_manager:
            messagebox.showwarning("Keine Session", "Bitte starten Sie zuerst eine Session.")
            return
        
        steps = self.session_manager.get_steps()
        if not steps:
            messagebox.showwarning("Keine Schritte", "Es sind keine Schritte vorhanden.")
            return
        
        dialog = VideoExportDialog(self.root, steps)
        self.root.wait_window(dialog.dialog)
    
    def _show_platform_export(self):
        """Zeigt Platform-Export Dialog"""
        if not self.session_manager:
            messagebox.showwarning("Keine Session", "Bitte starten Sie zuerst eine Session.")
            return
        
        steps = self.session_manager.get_steps()
        if not steps:
            messagebox.showwarning("Keine Schritte", "Es sind keine Schritte vorhanden.")
            return
        
        dialog = PlatformExportDialog(self.root, steps)
        self.root.wait_window(dialog.dialog)
    
    def _show_consolidation_dialog(self):
        """Zeigt Schritt-Konsolidierung Dialog"""
        if not self.session_manager:
            messagebox.showwarning("Keine Session", "Bitte starten Sie zuerst eine Session.")
            return
        
        steps = self.session_manager.get_steps()
        if not steps:
            messagebox.showwarning("Keine Schritte", "Es sind keine Schritte vorhanden.")
            return
        
        if len(steps) < 2:
            messagebox.showinfo("Info", "Mindestens 2 Schritte erforderlich für Konsolidierung.")
            return
        
        dialog = ConsolidationDialog(self.root, steps, self.session_manager)
        self.root.wait_window(dialog.dialog)
        
        # Aktualisiere UI nach Konsolidierung
        if self.session_manager:
            updated_steps = self.session_manager.get_steps()
            self.preview_panel.update_steps(updated_steps)
            self._update_session_status()
    
    def _show_session_compare(self):
        """Zeigt Session-Vergleich Dialog"""
        dialog = SessionCompareDialog(self.root)
        self.root.wait_window(dialog.dialog)
    
    def _show_test_checklist(self):
        """Zeigt Test-Checkliste Generator Dialog"""
        if not self.session_manager:
            messagebox.showwarning("Keine Session", "Bitte starten Sie zuerst eine Session.")
            return
        
        steps = self.session_manager.get_steps()
        if not steps:
            messagebox.showwarning("Keine Schritte", "Es sind keine Schritte vorhanden.")
            return
        
        dialog = TestChecklistDialog(self.root, steps)
        self.root.wait_window(dialog.dialog)
    
    def _show_quality_check(self):
        """Zeigt Qualitätsprüfung Dialog"""
        if not self.session_manager:
            messagebox.showwarning("Keine Session", "Bitte starten Sie zuerst eine Session.")
            return
        
        steps = self.session_manager.get_steps()
        if not steps:
            messagebox.showwarning("Keine Schritte", "Es sind keine Schritte vorhanden.")
            return
        
        from src.document.quality_checker import QualityChecker
        
        quality_checker = QualityChecker()
        metrics = quality_checker.check_quality(steps)
        
        # Zeige Qualitätsbericht
        report = quality_checker.get_quality_report(steps)
        
        # Öffne Dialog mit Bericht
        dialog = tk.Toplevel(self.root)
        dialog.title("Qualitätsprüfung")
        dialog.geometry("700x600")
        dialog.transient(self.root)
        
        # Zentriere Dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Score-Anzeige
        score_frame = ttk.LabelFrame(main_frame, text="Gesamt-Qualitäts-Score", padding="10")
        score_frame.pack(fill=tk.X, pady=(0, 10))
        
        score = metrics.get('overall_score', 0.0)
        score_label = ttk.Label(
            score_frame,
            text=f"{score:.1%}",
            font=("Arial", 24, "bold"),
            foreground="green" if score >= 0.8 else "orange" if score >= 0.6 else "red"
        )
        score_label.pack()
        
        # Bericht
        report_frame = ttk.LabelFrame(main_frame, text="Qualitätsbericht", padding="10")
        report_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(report_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        report_text = tk.Text(
            report_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            yscrollcommand=scrollbar.set
        )
        report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=report_text.yview)
        
        report_text.config(state=tk.NORMAL)
        report_text.insert(1.0, report)
        report_text.config(state=tk.DISABLED)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="Schließen",
            command=dialog.destroy
        ).pack(side=tk.RIGHT)
    
    def _start_automated_exploration(self):
        """Startet automatische App-Erkundung"""
        # Öffne App-Selector Dialog
        app_dialog = AppSelectorDialog(self.root)
        self.root.wait_window(app_dialog.dialog)
        
        selected_window = app_dialog.get_selected_window()
        
        if not selected_window:
            return
        
        # Bestätigung
        if not messagebox.askyesno(
            "Automatische Erkundung",
            f"Automatische Erkundung für '{selected_window.get('title', 'Unbekannt')}' starten?\n\n"
            "Die App wird automatisch durchklickt und dokumentiert.\n"
            "Dies kann einige Zeit dauern."
        ):
            return
        
        # Starte Session falls nicht aktiv
        if not self.session_active:
            self._start_session()
            if not self.session_active:
                return
        
        # Lade Exploration Config
        import yaml
        config_path = Path("config") / "exploration_config.yml"
        config = {}
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
            except Exception as e:
                logger.error(f"Fehler beim Laden der Exploration Config: {e}")
        
        # Starte Exploration Session
        try:
            from src.automation.exploration_session import ExplorationSession
            
            exploration_session = ExplorationSession(
                window_info=selected_window,
                session_manager=self.session_manager,
                config=config
            )
            
            # Zeige Progress Dialog
            progress_dialog = ExplorationProgressDialog(self.root, exploration_session)
            
            # Starte in separatem Thread
            def start_exploration():
                try:
                    exploration_session.start()
                except Exception as err:
                    logger.error(f"Fehler bei Erkundung: {err}", exc_info=True)
                    self.root.after(0, lambda err=err: messagebox.showerror(
                        "Fehler",
                        f"Fehler bei Erkundung:\n\n{str(err)}\n\nDetails finden Sie in der Logdatei unter 'logs/ahg.log'."
                    ))
                    self.root.after(0, progress_dialog.dialog.destroy)
            
            threading.Thread(target=start_exploration, daemon=True).start()
            
            # Warte auf Dialog-Schließung
            self.root.wait_window(progress_dialog.dialog)
            
            logger.info(f"Automatische Erkundung für Fenster {selected_window.get('hwnd')} gestartet")
        
        except Exception as e:
            logger.error(f"Fehler beim Starten der Erkundung: {e}", exc_info=True)
            messagebox.showerror(
                "Fehler",
                f"Fehler beim Starten der automatischen Erkundung:\n\n{str(e)}\n\nDetails finden Sie in der Logdatei unter 'logs/ahg.log'."
            )
    
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
    
    def _refresh_preview(self):
        """Aktualisiert die Vorschau"""
        if self.session_manager:
            steps = self.session_manager.get_steps()
            self.preview_panel.update_steps(steps)
            self._update_session_status()
    
    def _handle_enter_key(self):
        """Behandelt Enter-Taste je nach Kontext"""
        # In Abhängigkeit vom aktuellen Fokus und Zustand
        # Aktuell: Führt Standardaktion aus, z.B. Starten einer Session wenn bereit
        if not self.session_active:
            self._start_session()
    
    def _handle_space_key(self):
        """Behandelt Space-Taste je nach Kontext"""
        # Pausiert/Fortsetzt die Session je nach aktuellem Zustand
        if self.session_active and self.session_manager:
            if self.session_manager.paused:
                self._pause_session()  # Fortsetzen
            else:
                self._pause_session()  # Pausieren
    
    def _toggle_preview(self):
        """Schaltet die Vorschau-Ansicht um"""
        # Aktiviert/Deaktiviert die Vorschau je nach aktuellem Zustand
        self.preview_panel.toggle_preview_visibility()
    
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
    
    # ============================================
    # Innovation Features (Neue Module)
    # ============================================
    
    def _show_voice_control(self):
        """Zeigt Sprachsteuerungs-Panel"""
        try:
            from src.gui.voice_panel import VoiceControlPanel
            
            # Create voice control window
            voice_window = tk.Toplevel(self.root)
            voice_window.title("🎤 Sprachsteuerung")
            voice_window.geometry("400x350")
            voice_window.transient(self.root)
            
            def on_transcription(text):
                # Add transcription as comment to current step
                if self.session_manager and text:
                    logger.info(f"Voice transcription: {text}")
                    # Could add to step comments or annotations
            
            panel = VoiceControlPanel(voice_window, on_transcription=on_transcription)
            panel.pack(fill=tk.BOTH, expand=True)
            
        except ImportError as e:
            messagebox.showwarning(
                "Nicht verfügbar",
                f"Sprachsteuerung nicht verfügbar.\nFehlende Abhängigkeit: {e}\n\n"
                "Installieren Sie: pip install sounddevice openai"
            )
        except Exception as e:
            logger.error(f"Voice control error: {e}")
            messagebox.showerror("Fehler", f"Sprachsteuerung konnte nicht geöffnet werden:\n{e}")
    
    def _show_knowledge_search(self):
        """Zeigt Wissenssuche-Dialog"""
        try:
            from src.gui.knowledge_search_dialog import KnowledgeSearchDialog
            from src.knowledge import KnowledgeBase
            
            # Initialize or get knowledge base
            kb = KnowledgeBase(storage_dir="data/knowledge_base")
            
            # Try to initialize RAG if API key available
            rag = None
            if os.getenv("OPENAI_API_KEY"):
                try:
                    from src.knowledge import EmbeddingEngine, SemanticSearch, RAGEngine
                    embedding = EmbeddingEngine(storage_dir="data/embeddings")
                    search = SemanticSearch(kb, embedding)
                    rag = RAGEngine(search, language="de")
                except Exception as e:
                    logger.warning(f"RAG initialization failed: {e}")
            
            dialog = KnowledgeSearchDialog(self.root, knowledge_base=kb, rag_engine=rag)
            
        except ImportError as e:
            messagebox.showwarning(
                "Nicht verfügbar",
                f"Wissenssuche nicht verfügbar.\nFehlende Abhängigkeit: {e}\n\n"
                "Installieren Sie: pip install chromadb openai"
            )
        except Exception as e:
            logger.error(f"Knowledge search error: {e}")
            messagebox.showerror("Fehler", f"Wissenssuche konnte nicht geöffnet werden:\n{e}")
    
    def _show_test_export(self):
        """Zeigt Test-Export Dialog"""
        if not self.session_manager:
            messagebox.showwarning("Keine Session", "Bitte starten Sie zuerst eine Session.")
            return
        
        steps = self.session_manager.get_steps()
        if not steps:
            messagebox.showwarning("Keine Schritte", "Es sind keine Schritte vorhanden.")
            return
        
        try:
            from src.gui.test_export_dialog import TestExportDialog
            
            session_data = {
                "session_id": getattr(self.session_manager, 'session_id', 'unknown'),
                "name": getattr(self.session_manager, 'session_name', 'Dokumentation'),
                "steps": steps
            }
            
            dialog = TestExportDialog(self.root, session_data)
            
        except ImportError as e:
            messagebox.showwarning(
                "Nicht verfügbar",
                f"Test-Export nicht verfügbar.\nFehlende Abhängigkeit: {e}"
            )
        except Exception as e:
            logger.error(f"Test export error: {e}")
            messagebox.showerror("Fehler", f"Test-Export konnte nicht geöffnet werden:\n{e}")
    
    def _show_tutorial_export(self):
        """Zeigt Tutorial-Export Dialog"""
        if not self.session_manager:
            messagebox.showwarning("Keine Session", "Bitte starten Sie zuerst eine Session.")
            return
        
        steps = self.session_manager.get_steps()
        if not steps:
            messagebox.showwarning("Keine Schritte", "Es sind keine Schritte vorhanden.")
            return
        
        try:
            from src.gui.tutorial_export_dialog import TutorialExportDialog
            
            session_data = {
                "session_id": getattr(self.session_manager, 'session_id', 'unknown'),
                "name": getattr(self.session_manager, 'session_name', 'Tutorial'),
                "description": "Interaktives Tutorial aus Dokumentation",
                "steps": steps
            }
            
            dialog = TutorialExportDialog(self.root, session_data)
            
        except ImportError as e:
            messagebox.showwarning(
                "Nicht verfügbar",
                f"Tutorial-Export nicht verfügbar.\nFehlende Abhängigkeit: {e}"
            )
        except Exception as e:
            logger.error(f"Tutorial export error: {e}")
            messagebox.showerror("Fehler", f"Tutorial-Export konnte nicht geöffnet werden:\n{e}")
    
    def _show_process_mining(self):
        """Zeigt Process Mining Dialog"""
        try:
            from src.gui.process_mining_dialog import ProcessMiningDialog
            
            # Collect session data (current and from knowledge base if available)
            sessions = []
            
            # Add current session if available
            if self.session_manager:
                steps = self.session_manager.get_steps()
                if steps:
                    sessions.append({
                        "session_id": getattr(self.session_manager, 'session_id', 'current'),
                        "name": getattr(self.session_manager, 'session_name', 'Aktuelle Session'),
                        "steps": steps
                    })
            
            # Try to load sessions from data directory
            data_dir = Path("data/sessions")
            if data_dir.exists():
                import json
                for session_file in data_dir.glob("*.json"):
                    try:
                        with open(session_file, 'r', encoding='utf-8') as f:
                            session_data = json.load(f)
                            if session_data.get("steps"):
                                sessions.append(session_data)
                    except Exception as e:
                        logger.warning(f"Could not load session {session_file}: {e}")
            
            if not sessions:
                messagebox.showwarning(
                    "Keine Daten",
                    "Keine Sessions für Process Mining gefunden.\n\n"
                    "Starten Sie eine Session oder laden Sie Session-Daten in data/sessions/"
                )
                return
            
            dialog = ProcessMiningDialog(self.root, sessions)
            
        except ImportError as e:
            messagebox.showwarning(
                "Nicht verfügbar",
                f"Process Mining nicht verfügbar.\nFehlende Abhängigkeit: {e}\n\n"
                "Installieren Sie: pip install pm4py networkx"
            )
        except Exception as e:
            logger.error(f"Process mining error: {e}")
            messagebox.showerror("Fehler", f"Process Mining konnte nicht geöffnet werden:\n{e}")
    
    def _show_gitops_dialog(self):
        """Zeigt GitOps Configuration Dialog"""
        try:
            dialog = GitOpsDialog(self.root)
            config = dialog.show()
            
            if config:
                logger.info("GitOps Konfiguration gespeichert")
                # TODO: Save config to settings
                messagebox.showinfo("Erfolg", "GitOps-Konfiguration gespeichert!")
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des GitOps-Dialogs: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des GitOps-Dialogs:\n{e}")
    
    def _show_accessibility_dialog(self):
        """Zeigt Accessibility Compliance Dialog"""
        try:
            dialog = AccessibilityDialog(self.root)
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des Accessibility-Dialogs: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des Accessibility-Dialogs:\n{e}")
    
    def _show_roi_dashboard(self):
        """Zeigt ROI Dashboard"""
        try:
            dashboard = ROIDashboard(self.root)
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des ROI-Dashboards: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des ROI-Dashboards:\n{e}")
    
    def _show_video_synthesis(self):
        """Zeigt Video Synthesis Dialog"""
        try:
            session_data = {}
            screenshot_paths = []
            
            if self.session_manager:
                steps = self.session_manager.get_steps()
                session_data = {"steps": steps}
                # Get screenshot paths from steps
                screenshot_paths = [Path(s.get('screenshot_path', '')) for s in steps if s.get('screenshot_path')]
            
            dialog = VideoSynthesisDialog(self.root, session_data, screenshot_paths)
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des Video-Dialogs: {e}")
            messagebox.showerror("Fehler", f"Fehler: {e}")
    
    def _show_translation_dialog(self):
        """Zeigt Translation Hub Dialog"""
        try:
            dialog = TranslationDialog(self.root)
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des Translation-Dialogs: {e}")
            messagebox.showerror("Fehler", f"Fehler: {e}")
    
    def _show_collaboration_dialog(self):
        """Zeigt Collaboration Hub Dialog"""
        try:
            dialog = CollaborationDialog(self.root)
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des Collaboration-Dialogs: {e}")
            messagebox.showerror("Fehler", f"Fehler: {e}")
    
    def _show_agent_dialog(self):
        """Zeigt Autonomous Agent Dialog"""
        try:
            dialog = AgentDialog(self.root)
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des Agent-Dialogs: {e}")
            messagebox.showerror("Fehler", f"Fehler: {e}")
    
    def _show_api_dialog(self):
        """Zeigt API Gateway Dialog"""
        try:
            dialog = APIDialog(self.root)
            self.root.wait_window(dialog.dialog)
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des API-Dialogs: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des API-Dialogs:\n{e}")
    
    def _show_plugin_dialog(self):
        """Zeigt Plugin System Dialog"""
        try:
            dialog = PluginDialog(self.root)
            self.root.wait_window(dialog.dialog)
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des Plugin-Dialogs: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des Plugin-Dialogs:\n{e}")
    
    def _show_edge_ai_dialog(self):
        """Zeigt Edge AI Engine Dialog"""
        try:
            dialog = EdgeAIDialog(self.root)
            self.root.wait_window(dialog.dialog)
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des Edge AI-Dialogs: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des Edge AI-Dialogs:\n{e}")
    
    def _show_blockchain_dialog(self):
        """Zeigt Blockchain Audit Trail Dialog"""
        try:
            dialog = BlockchainDialog(self.root)
            self.root.wait_window(dialog.dialog)
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des Blockchain-Dialogs: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des Blockchain-Dialogs:\n{e}")
    
    def _show_predictive_dialog(self):
        """Zeigt Predictive Maintenance Dialog"""
        try:
            dialog = PredictiveDialog(self.root)
            self.root.wait_window(dialog.dialog)
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des Predictive-Dialogs: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des Predictive-Dialogs:\n{e}")
    
    def _show_multimodal_dialog(self):
        """Zeigt Multi-Modal Capture Dialog"""
        try:
            dialog = MultiModalDialog(self.root)
            self.root.wait_window(dialog.dialog)
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des Multi-Modal-Dialogs: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des Multi-Modal-Dialogs:\n{e}")
    
    def _show_ar_dialog(self):
        """Zeigt AR Documentation Dialog"""
        try:
            dialog = ARDialog(self.root)
            self.root.wait_window(dialog.dialog)
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des AR-Dialogs: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des AR-Dialogs:\n{e}")
    
    def _show_self_learning_dialog(self):
        """Zeigt Self-Learning AI Dialog"""
        try:
            dialog = SelfLearningDialog(self.root)
            self.root.wait_window(dialog.dialog)
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des Self-Learning-Dialogs: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des Self-Learning-Dialogs:\n{e}")
    
    def _show_agentic_dialog(self):
        """Zeigt Agentic Automation Dialog"""
        try:
            dialog = AgenticDialog(self.root)
            self.root.wait_window(dialog.dialog)
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des Agentic-Dialogs: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des Agentic-Dialogs:\n{e}")
    
    def _show_federated_dialog(self):
        """Zeigt Federated Learning Dialog"""
        try:
            messagebox.showinfo("Federated Learning", "Federated Learning Network - Coming Soon")
        except Exception as e:
            logger.error(f"Fehler: {e}")
    
    def _show_hyperautomation_dialog(self):
        """Zeigt Hyperautomation Dialog"""
        try:
            dialog = HyperautomationDialog(self.root)
            self.root.wait_window(dialog.dialog)
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des Hyperautomation-Dialogs: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des Hyperautomation-Dialogs:\n{e}")
    
    def _show_localization_dialog(self):
        """Zeigt AI Localization Dialog"""
        try:
            dialog = LocalizationDialog(self.root)
            self.root.wait_window(dialog.dialog)
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des Localization-Dialogs: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des Localization-Dialogs:\n{e}")
    
    def _show_compliance_dialog(self):
        """Zeigt Compliance Automation Dialog"""
        try:
            dialog = ComplianceDialog(self.root)
            self.root.wait_window(dialog.dialog)
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des Compliance-Dialogs: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des Compliance-Dialogs:\n{e}")
    
    def _show_adaptive_ux_dialog(self):
        """Zeigt Adaptive UX Dialog"""
        try:
            dialog = AdaptiveUXDialog(self.root)
            self.root.wait_window(dialog.dialog)
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des Adaptive-UX-Dialogs: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des Adaptive-UX-Dialogs:\n{e}")
    
    def _show_predictive_workflow_dialog(self):
        """Zeigt Predictive Workflow Dialog"""
        try:
            dialog = PredictiveWorkflowDialog(self.root)
            self.root.wait_window(dialog.dialog)
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des Predictive-Workflow-Dialogs: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des Predictive-Workflow-Dialogs:\n{e}")
    
    def _show_data_hub_dialog(self):
        """Zeigt Universal Data Hub Dialog"""
        try:
            dialog = DataHubDialog(self.root)
            self.root.wait_window(dialog.dialog)
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des Data-Hub-Dialogs: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des Data-Hub-Dialogs:\n{e}")
    
    def _show_intelligent_assistant_dialog(self):
        """Zeigt Intelligent Assistant Dialog"""
        try:
            dialog = IntelligentAssistantDialog(self.root)
            self.root.wait_window(dialog.dialog)
        except Exception as e:
            logger.error(f"Fehler beim Öffnen des Intelligent-Assistant-Dialogs: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des Intelligent-Assistant-Dialogs:\n{e}")

