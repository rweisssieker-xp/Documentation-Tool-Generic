"""
Git Manager - Core Git operations for Documentation-as-Code.
Part of Feature: GitOps Documentation Pipeline (v2.0)
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import subprocess

try:
    import git
    from git import Repo, GitCommandError
    GITPYTHON_AVAILABLE = True
except ImportError:
    GITPYTHON_AVAILABLE = False

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class GitConfig:
    """Git repository configuration."""
    repo_path: Path
    remote_url: Optional[str] = None
    branch: str = "main"
    author_name: str = "AHG Documentation Tool"
    author_email: str = "ahg@example.com"
    auto_push: bool = True
    auto_pull: bool = True


@dataclass
class CommitInfo:
    """Information about a Git commit."""
    hash: str
    message: str
    author: str
    date: datetime
    files_changed: List[str]


class GitManager:
    """
    Manages Git operations for documentation repositories.
    Provides high-level interface for Git operations.
    """
    
    def __init__(self, config: GitConfig):
        """
        Initialize Git Manager.
        
        Args:
            config: Git configuration
        """
        if not GITPYTHON_AVAILABLE:
            raise ImportError(
                "gitpython is required for GitOps features. "
                "Install with: pip install gitpython"
            )
        
        self.config = config
        self.repo_path = Path(config.repo_path)
        
        # Initialize or open repository
        if self.repo_path.exists() and (self.repo_path / ".git").exists():
            self.repo = Repo(str(self.repo_path))
            logger.info(f"Opened existing Git repository: {self.repo_path}")
        else:
            self.repo_path.mkdir(parents=True, exist_ok=True)
            self.repo = Repo.init(str(self.repo_path))
            logger.info(f"Initialized new Git repository: {self.repo_path}")
        
        # Configure Git user
        self.repo.config_writer().set_value("user", "name", config.author_name).release()
        self.repo.config_writer().set_value("user", "email", config.author_email).release()
        
        # Set up remote if provided
        if config.remote_url:
            self._setup_remote(config.remote_url)
    
    def _setup_remote(self, remote_url: str):
        """Set up Git remote."""
        try:
            if "origin" in self.repo.remotes:
                origin = self.repo.remotes.origin
                origin.set_url(remote_url)
            else:
                self.repo.create_remote("origin", remote_url)
            logger.info(f"Configured remote: {remote_url}")
        except Exception as e:
            logger.warning(f"Could not set up remote: {e}")
    
    def status(self) -> Dict[str, Any]:
        """
        Get repository status.
        
        Returns:
            Status dictionary with changes, untracked files, etc.
        """
        try:
            has_commits = self.repo.head.is_valid()
            
            result = {
                "is_dirty": self.repo.is_dirty() if has_commits else False,
                "untracked_files": list(self.repo.untracked_files),
                "modified_files": [],
                "staged_files": [],
                "current_branch": self.repo.active_branch.name if has_commits else self.config.branch,
                "last_commit": self.repo.head.commit.hexsha[:8] if has_commits else None
            }
            
            if has_commits:
                result["modified_files"] = [item.a_path for item in self.repo.index.diff(None)]
                result["staged_files"] = [item.a_path for item in self.repo.index.diff("HEAD")]
            
            return result
        except Exception as e:
            logger.error(f"Error getting Git status: {e}")
            return {"error": str(e)}
    
    def add(self, paths: List[str]) -> bool:
        """
        Stage files for commit.
        
        Args:
            paths: List of file paths to stage
            
        Returns:
            True if successful
        """
        try:
            for path in paths:
                file_path = self.repo_path / path
                if file_path.exists():
                    self.repo.index.add([path])
                    logger.debug(f"Staged: {path}")
            return True
        except Exception as e:
            logger.error(f"Error staging files: {e}")
            return False
    
    def commit(
        self,
        message: str,
        author_name: Optional[str] = None,
        author_email: Optional[str] = None
    ) -> Optional[str]:
        """
        Commit staged changes.
        
        Args:
            message: Commit message
            author_name: Optional author name override
            author_email: Optional author email override
            
        Returns:
            Commit hash if successful, None otherwise
        """
        try:
            if not self.repo.is_dirty() and not self.repo.untracked_files:
                logger.warning("No changes to commit")
                return None
            
            # Stage all changes if nothing staged
            has_commits = self.repo.head.is_valid()
            if has_commits:
                if not self.repo.index.diff("HEAD"):
                    self.repo.git.add(A=True)
            else:
                # First commit - stage everything
                self.repo.git.add(A=True)
            
            # Create commit
            commit = self.repo.index.commit(
                message,
                author=git.Actor(
                    author_name or self.config.author_name,
                    author_email or self.config.author_email
                )
            )
            
            logger.info(f"Committed: {commit.hexsha[:8]} - {message[:50]}")
            return commit.hexsha
        except GitCommandError as e:
            logger.error(f"Git commit error: {e}")
            return None
    
    def push(self, branch: Optional[str] = None, force: bool = False) -> bool:
        """
        Push commits to remote.
        
        Args:
            branch: Branch to push (defaults to current branch)
            force: Force push
            
        Returns:
            True if successful
        """
        try:
            branch = branch or self.config.branch
            
            if "origin" not in self.repo.remotes:
                logger.warning("No remote configured, skipping push")
                return False
            
            origin = self.repo.remotes.origin
            
            if force:
                origin.push(branch, force=True)
            else:
                origin.push(branch)
            
            logger.info(f"Pushed to origin/{branch}")
            return True
        except GitCommandError as e:
            logger.error(f"Git push error: {e}")
            return False
    
    def pull(self, branch: Optional[str] = None) -> bool:
        """
        Pull latest changes from remote.
        
        Args:
            branch: Branch to pull (defaults to current branch)
            
        Returns:
            True if successful
        """
        try:
            branch = branch or self.config.branch
            
            if "origin" not in self.repo.remotes:
                logger.warning("No remote configured, skipping pull")
                return False
            
            origin = self.repo.remotes.origin
            origin.pull(branch)
            
            logger.info(f"Pulled from origin/{branch}")
            return True
        except GitCommandError as e:
            logger.error(f"Git pull error: {e}")
            return False
    
    def create_branch(self, branch_name: str, checkout: bool = True) -> bool:
        """
        Create a new branch.
        
        Args:
            branch_name: Name of new branch
            checkout: Whether to checkout the new branch
            
        Returns:
            True if successful
        """
        try:
            if checkout:
                self.repo.git.checkout("-b", branch_name)
            else:
                self.repo.create_head(branch_name)
            
            logger.info(f"Created branch: {branch_name}")
            return True
        except GitCommandError as e:
            logger.error(f"Error creating branch: {e}")
            return False
    
    def get_commits(self, limit: int = 10) -> List[CommitInfo]:
        """
        Get recent commits.
        
        Args:
            limit: Maximum number of commits
            
        Returns:
            List of CommitInfo objects
        """
        try:
            commits = []
            for commit in self.repo.iter_commits(max_count=limit):
                commits.append(CommitInfo(
                    hash=commit.hexsha,
                    message=commit.message.strip(),
                    author=f"{commit.author.name} <{commit.author.email}>",
                    date=datetime.fromtimestamp(commit.committed_date),
                    files_changed=list(commit.stats.files.keys())
                ))
            return commits
        except Exception as e:
            logger.error(f"Error getting commits: {e}")
            return []
    
    def get_diff(self, commit_hash: Optional[str] = None) -> str:
        """
        Get diff for changes.
        
        Args:
            commit_hash: Optional commit hash to diff against
            
        Returns:
            Diff string
        """
        try:
            if commit_hash:
                return self.repo.git.diff(commit_hash)
            else:
                return self.repo.git.diff()
        except Exception as e:
            logger.error(f"Error getting diff: {e}")
            return ""

