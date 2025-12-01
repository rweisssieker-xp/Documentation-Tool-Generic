"""
GitOps Configuration Dialog
GUI for configuring GitOps Documentation Pipeline
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import Optional, Dict, Any

from src.gitops.git_manager import GitConfig
from src.gitops.repository_sync import SyncConfig
from src.gitops.pr_automation import PRConfig, Platform
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GitOpsDialog:
    """Dialog for configuring GitOps settings."""
    
    def __init__(self, parent, initial_config: Optional[Dict[str, Any]] = None):
        """
        Initialize GitOps dialog.
        
        Args:
            parent: Parent window
            initial_config: Optional initial configuration
        """
        self.parent = parent
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("GitOps Documentation Pipeline - Konfiguration")
        self.dialog.geometry("600x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.config = initial_config or {}
        
        self._create_widgets()
        self._load_config()
    
    def _create_widgets(self):
        """Create dialog widgets."""
        # Notebook for tabs
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Git Configuration Tab
        git_frame = ttk.Frame(notebook)
        notebook.add(git_frame, text="Git Repository")
        self._create_git_tab(git_frame)
        
        # Sync Configuration Tab
        sync_frame = ttk.Frame(notebook)
        notebook.add(sync_frame, text="Synchronisation")
        self._create_sync_tab(sync_frame)
        
        # PR Automation Tab
        pr_frame = ttk.Frame(notebook)
        notebook.add(pr_frame, text="Pull Requests")
        self._create_pr_tab(pr_frame)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Abbrechen", command=self._cancel).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Speichern", command=self._save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Testen", command=self._test_connection).pack(side=tk.LEFT, padx=5)
    
    def _create_git_tab(self, parent):
        """Create Git configuration tab."""
        # Repository Path
        ttk.Label(parent, text="Repository-Pfad:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.repo_path_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.repo_path_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(parent, text="Durchsuchen...", command=self._browse_repo_path).grid(row=0, column=2, padx=5)
        
        # Remote URL
        ttk.Label(parent, text="Remote URL:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.remote_url_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.remote_url_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        
        # Branch
        ttk.Label(parent, text="Branch:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.branch_var = tk.StringVar(value="main")
        ttk.Entry(parent, textvariable=self.branch_var, width=20).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Author Name
        ttk.Label(parent, text="Autor Name:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.author_name_var = tk.StringVar(value="AHG Documentation Tool")
        ttk.Entry(parent, textvariable=self.author_name_var, width=30).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Author Email
        ttk.Label(parent, text="Autor E-Mail:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.author_email_var = tk.StringVar(value="ahg@example.com")
        ttk.Entry(parent, textvariable=self.author_email_var, width=30).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Initialize Repository Button
        ttk.Button(parent, text="Repository initialisieren", command=self._init_repo).grid(row=5, column=1, sticky=tk.W, padx=5, pady=10)
    
    def _create_sync_tab(self, parent):
        """Create synchronization configuration tab."""
        # Auto Sync
        self.auto_sync_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, text="Automatische Synchronisation aktivieren", variable=self.auto_sync_var).grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Sync Interval
        ttk.Label(parent, text="Sync-Intervall (Sekunden):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.sync_interval_var = tk.IntVar(value=300)
        ttk.Spinbox(parent, from_=60, to=3600, textvariable=self.sync_interval_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Conflict Strategy
        ttk.Label(parent, text="Konflikt-Strategie:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.conflict_strategy_var = tk.StringVar(value="merge")
        strategy_combo = ttk.Combobox(parent, textvariable=self.conflict_strategy_var, values=["merge", "ours", "theirs", "manual"], state="readonly", width=15)
        strategy_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Sync Triggers
        ttk.Label(parent, text="Sync-Trigger:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        trigger_frame = ttk.Frame(parent)
        trigger_frame.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.sync_on_session_end_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(trigger_frame, text="Bei Session-Ende", variable=self.sync_on_session_end_var).pack(anchor=tk.W)
        
        self.sync_on_export_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(trigger_frame, text="Bei Export", variable=self.sync_on_export_var).pack(anchor=tk.W)
    
    def _create_pr_tab(self, parent):
        """Create PR automation tab."""
        # Platform
        ttk.Label(parent, text="Platform:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.platform_var = tk.StringVar(value="github")
        platform_combo = ttk.Combobox(parent, textvariable=self.platform_var, values=["github", "gitlab"], state="readonly", width=15)
        platform_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Repository (owner/repo)
        ttk.Label(parent, text="Repository (owner/repo):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.pr_repo_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.pr_repo_var, width=30).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Base Branch
        ttk.Label(parent, text="Base Branch:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.pr_base_branch_var = tk.StringVar(value="main")
        ttk.Entry(parent, textvariable=self.pr_base_branch_var, width=20).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Auto Assign
        self.auto_assign_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(parent, text="Automatisch zuweisen", variable=self.auto_assign_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Labels
        ttk.Label(parent, text="Labels (kommasepariert):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.pr_labels_var = tk.StringVar(value="documentation")
        ttk.Entry(parent, textvariable=self.pr_labels_var, width=30).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Token Info
        info_label = ttk.Label(parent, text="Hinweis: Setzen Sie GITHUB_TOKEN oder GITLAB_TOKEN als Umgebungsvariable", foreground="gray")
        info_label.grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=5, pady=10)
    
    def _browse_repo_path(self):
        """Browse for repository path."""
        path = filedialog.askdirectory(title="Repository-Pfad wählen")
        if path:
            self.repo_path_var.set(path)
    
    def _init_repo(self):
        """Initialize Git repository."""
        repo_path = self.repo_path_var.get()
        if not repo_path:
            messagebox.showwarning("Warnung", "Bitte geben Sie einen Repository-Pfad an")
            return
        
        try:
            from src.gitops.git_manager import GitManager, GitConfig
            
            config = GitConfig(
                repo_path=Path(repo_path),
                remote_url=self.remote_url_var.get() or None,
                branch=self.branch_var.get(),
                author_name=self.author_name_var.get(),
                author_email=self.author_email_var.get()
            )
            
            manager = GitManager(config)
            messagebox.showinfo("Erfolg", f"Repository erfolgreich initialisiert:\n{repo_path}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Initialisieren:\n{e}")
    
    def _test_connection(self):
        """Test Git connection."""
        repo_path = self.repo_path_var.get()
        if not repo_path:
            messagebox.showwarning("Warnung", "Bitte geben Sie einen Repository-Pfad an")
            return
        
        try:
            from src.gitops.git_manager import GitManager, GitConfig
            
            config = GitConfig(
                repo_path=Path(repo_path),
                remote_url=self.remote_url_var.get() or None,
                branch=self.branch_var.get()
            )
            
            manager = GitManager(config)
            status = manager.status()
            
            info = f"Repository Status:\n"
            info += f"Branch: {status.get('current_branch', 'N/A')}\n"
            info += f"Letzter Commit: {status.get('last_commit', 'Keine Commits')}\n"
            info += f"Änderungen: {len(status.get('modified_files', []))} modifiziert, {len(status.get('untracked_files', []))} neu"
            
            messagebox.showinfo("Verbindung erfolgreich", info)
        except Exception as e:
            messagebox.showerror("Fehler", f"Verbindungstest fehlgeschlagen:\n{e}")
    
    def _load_config(self):
        """Load configuration into widgets."""
        if "repo_path" in self.config:
            self.repo_path_var.set(self.config["repo_path"])
        if "remote_url" in self.config:
            self.remote_url_var.set(self.config["remote_url"])
        if "branch" in self.config:
            self.branch_var.set(self.config["branch"])
    
    def _save(self):
        """Save configuration."""
        self.result = {
            "repo_path": self.repo_path_var.get(),
            "remote_url": self.remote_url_var.get() or None,
            "branch": self.branch_var.get(),
            "author_name": self.author_name_var.get(),
            "author_email": self.author_email_var.get(),
            "auto_sync": self.auto_sync_var.get(),
            "sync_interval": self.sync_interval_var.get(),
            "conflict_strategy": self.conflict_strategy_var.get(),
            "sync_on_session_end": self.sync_on_session_end_var.get(),
            "sync_on_export": self.sync_on_export_var.get(),
            "platform": self.platform_var.get(),
            "pr_repository": self.pr_repo_var.get(),
            "pr_base_branch": self.pr_base_branch_var.get(),
            "auto_assign": self.auto_assign_var.get(),
            "pr_labels": [l.strip() for l in self.pr_labels_var.get().split(",") if l.strip()]
        }
        self.dialog.destroy()
    
    def _cancel(self):
        """Cancel dialog."""
        self.result = None
        self.dialog.destroy()
    
    def show(self) -> Optional[Dict[str, Any]]:
        """Show dialog and return result."""
        self.dialog.wait_window()
        return self.result

