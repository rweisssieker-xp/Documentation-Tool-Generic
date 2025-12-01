"""
Repository Sync - Bidirectional synchronization between AHG and Git.
Part of Feature: GitOps Documentation Pipeline (v2.0)
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, asdict

from src.gitops.git_manager import GitManager, GitConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SyncConfig:
    """Synchronization configuration."""
    auto_sync: bool = True
    sync_interval: int = 300  # seconds
    conflict_strategy: str = "merge"  # "merge", "ours", "theirs", "manual"
    sync_on_session_end: bool = True
    sync_on_export: bool = True


@dataclass
class SyncStatus:
    """Status of synchronization."""
    last_sync: Optional[datetime] = None
    last_pull: Optional[datetime] = None
    last_push: Optional[datetime] = None
    conflicts: List[str] = None
    pending_changes: int = 0
    
    def __post_init__(self):
        if self.conflicts is None:
            self.conflicts = []


class RepositorySync:
    """
    Manages bidirectional synchronization between AHG and Git repositories.
    Handles conflicts and ensures consistency.
    """
    
    def __init__(
        self,
        git_manager: GitManager,
        sync_config: Optional[SyncConfig] = None
    ):
        """
        Initialize repository sync.
        
        Args:
            git_manager: GitManager instance
            sync_config: Synchronization configuration
        """
        self.git_manager = git_manager
        self.sync_config = sync_config or SyncConfig()
        self.status = SyncStatus()
        
        # State file for tracking sync
        self.state_file = self.git_manager.repo_path / ".ahg_sync_state.json"
        self._load_state()
    
    def _load_state(self):
        """Load sync state from file."""
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text())
                self.status.last_sync = datetime.fromisoformat(data.get("last_sync")) if data.get("last_sync") else None
                self.status.last_pull = datetime.fromisoformat(data.get("last_pull")) if data.get("last_pull") else None
                self.status.last_push = datetime.fromisoformat(data.get("last_push")) if data.get("last_push") else None
            except Exception as e:
                logger.warning(f"Could not load sync state: {e}")
    
    def _save_state(self):
        """Save sync state to file."""
        try:
            data = {
                "last_sync": self.status.last_sync.isoformat() if self.status.last_sync else None,
                "last_pull": self.status.last_pull.isoformat() if self.status.last_pull else None,
                "last_push": self.status.last_push.isoformat() if self.status.last_push else None,
            }
            self.state_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.warning(f"Could not save sync state: {e}")
    
    def sync_to_git(
        self,
        files: List[str],
        commit_message: Optional[str] = None,
        auto_push: bool = True
    ) -> bool:
        """
        Sync local changes to Git repository.
        
        Args:
            files: List of files to sync
            commit_message: Optional commit message
            auto_push: Whether to push after commit
            
        Returns:
            True if successful
        """
        try:
            # Stage files
            if not self.git_manager.add(files):
                return False
            
            # Generate commit message if not provided
            if not commit_message:
                from src.gitops.commit_generator import CommitGenerator, CommitContext
                generator = CommitGenerator()
                context = CommitContext(
                    files_changed=files,
                    diff_summary=self.git_manager.get_diff()
                )
                commit_message = generator.generate_commit_message(context)
            
            # Commit
            commit_hash = self.git_manager.commit(commit_message)
            if not commit_hash:
                return False
            
            # Push if configured
            if auto_push and self.sync_config.auto_sync:
                if self.git_manager.push():
                    self.status.last_push = datetime.now()
                    self._save_state()
                    logger.info(f"Synced {len(files)} files to Git")
                    return True
            
            self.status.last_sync = datetime.now()
            self._save_state()
            return True
        except Exception as e:
            logger.error(f"Error syncing to Git: {e}")
            return False
    
    def sync_from_git(self, auto_merge: bool = True) -> Dict[str, Any]:
        """
        Sync changes from Git repository.
        
        Args:
            auto_merge: Whether to auto-merge conflicts
            
        Returns:
            Sync result dictionary
        """
        try:
            # Check for conflicts before pull
            status = self.git_manager.status()
            if status.get("is_dirty"):
                logger.warning("Local changes detected, handling conflicts...")
                conflicts = self._handle_conflicts(auto_merge)
                if conflicts:
                    return {
                        "success": False,
                        "conflicts": conflicts,
                        "message": "Conflicts detected, manual resolution required"
                    }
            
            # Pull latest changes
            if self.git_manager.pull():
                self.status.last_pull = datetime.now()
                self.status.last_sync = datetime.now()
                self._save_state()
                
                return {
                    "success": True,
                    "message": "Successfully synced from Git",
                    "files_updated": status.get("modified_files", [])
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to pull from Git"
                }
        except Exception as e:
            logger.error(f"Error syncing from Git: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _handle_conflicts(self, auto_merge: bool) -> List[str]:
        """
        Handle merge conflicts.
        
        Args:
            auto_merge: Whether to auto-merge
            
        Returns:
            List of conflicted files
        """
        conflicts = []
        
        if self.sync_config.conflict_strategy == "manual":
            # Return conflicts for manual resolution
            status = self.git_manager.status()
            conflicts = status.get("modified_files", [])
        elif auto_merge:
            # Try to auto-merge using conflict resolver
            from src.gitops.conflict_resolver import ConflictResolver
            resolver = ConflictResolver()
            conflicts = resolver.resolve_conflicts(self.git_manager)
        
        self.status.conflicts = conflicts
        return conflicts
    
    def get_sync_status(self) -> Dict[str, Any]:
        """
        Get current synchronization status.
        
        Returns:
            Status dictionary
        """
        git_status = self.git_manager.status()
        
        return {
            "last_sync": self.status.last_sync.isoformat() if self.status.last_sync else None,
            "last_pull": self.status.last_pull.isoformat() if self.status.last_pull else None,
            "last_push": self.status.last_push.isoformat() if self.status.last_push else None,
            "pending_changes": len(git_status.get("modified_files", [])) + len(git_status.get("untracked_files", [])),
            "conflicts": self.status.conflicts,
            "is_dirty": git_status.get("is_dirty", False),
            "current_branch": git_status.get("current_branch")
        }

