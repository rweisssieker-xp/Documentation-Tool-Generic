"""
PR Automation - Automated Pull Request creation and management.
Part of Feature: GitOps Documentation Pipeline (v2.0)
"""

import os
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

try:
    from github import Github
    from gitlab import Gitlab
    GITHUB_AVAILABLE = True
    GITLAB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False
    GITLAB_AVAILABLE = False

from src.utils.logger import get_logger

logger = get_logger(__name__)


class Platform(Enum):
    """Git platform types."""
    GITHUB = "github"
    GITLAB = "gitlab"
    UNKNOWN = "unknown"


@dataclass
class PRConfig:
    """Pull Request configuration."""
    platform: Platform
    repository: str  # owner/repo format
    base_branch: str = "main"
    title_template: str = "docs: {title}"
    body_template: str = "Documentation update: {description}"
    auto_assign: bool = False
    assignees: List[str] = None
    labels: List[str] = None
    
    def __post_init__(self):
        if self.assignees is None:
            self.assignees = []
        if self.labels is None:
            self.labels = ["documentation"]


class PRAutomation:
    """
    Automates Pull Request creation and management.
    Supports GitHub and GitLab.
    """
    
    def __init__(self, config: PRConfig):
        """
        Initialize PR automation.
        
        Args:
            config: PR configuration
        """
        self.config = config
        self.client = None
        
        if config.platform == Platform.GITHUB:
            self._init_github()
        elif config.platform == Platform.GITLAB:
            self._init_gitlab()
    
    def _init_github(self):
        """Initialize GitHub client."""
        if not GITHUB_AVAILABLE:
            logger.warning("PyGithub not available. Install with: pip install PyGithub")
            return
        
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            logger.warning("GITHUB_TOKEN not set, PR automation disabled")
            return
        
        try:
            self.client = Github(token)
            logger.info("GitHub client initialized")
        except Exception as e:
            logger.error(f"Error initializing GitHub client: {e}")
    
    def _init_gitlab(self):
        """Initialize GitLab client."""
        if not GITLAB_AVAILABLE:
            logger.warning("python-gitlab not available. Install with: pip install python-gitlab")
            return
        
        token = os.getenv("GITLAB_TOKEN")
        url = os.getenv("GITLAB_URL", "https://gitlab.com")
        
        if not token:
            logger.warning("GITLAB_TOKEN not set, PR automation disabled")
            return
        
        try:
            self.client = Gitlab(url, private_token=token)
            self.client.auth()
            logger.info("GitLab client initialized")
        except Exception as e:
            logger.error(f"Error initializing GitLab client: {e}")
    
    def create_pr(
        self,
        branch: str,
        title: str,
        description: str,
        files_changed: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a Pull Request.
        
        Args:
            branch: Source branch
            title: PR title
            description: PR description
            files_changed: Optional list of changed files
            
        Returns:
            PR information dictionary or None
        """
        if not self.client:
            logger.warning("PR client not initialized, cannot create PR")
            return None
        
        try:
            if self.config.platform == Platform.GITHUB:
                return self._create_github_pr(branch, title, description, files_changed)
            elif self.config.platform == Platform.GITLAB:
                return self._create_gitlab_mr(branch, title, description, files_changed)
        except Exception as e:
            logger.error(f"Error creating PR: {e}")
            return None
    
    def _create_github_pr(
        self,
        branch: str,
        title: str,
        description: str,
        files_changed: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Create GitHub Pull Request."""
        repo = self.client.get_repo(self.config.repository)
        
        # Format title and body
        pr_title = self.config.title_template.format(title=title)
        pr_body = self._format_pr_body(description, files_changed)
        
        # Create PR
        pr = repo.create_pull(
            title=pr_title,
            body=pr_body,
            head=branch,
            base=self.config.base_branch
        )
        
        # Add labels
        if self.config.labels:
            pr.add_to_labels(*self.config.labels)
        
        # Assign reviewers
        if self.config.auto_assign and self.config.assignees:
            pr.add_to_assignees(*self.config.assignees)
        
        logger.info(f"Created GitHub PR: {pr.html_url}")
        
        return {
            "number": pr.number,
            "url": pr.html_url,
            "title": pr.title,
            "state": pr.state
        }
    
    def _create_gitlab_mr(
        self,
        branch: str,
        title: str,
        description: str,
        files_changed: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Create GitLab Merge Request."""
        # Parse repository (owner/repo)
        parts = self.config.repository.split('/')
        if len(parts) != 2:
            raise ValueError(f"Invalid repository format: {self.config.repository}")
        
        project = self.client.projects.get(f"{parts[0]}/{parts[1]}")
        
        # Format title and body
        mr_title = self.config.title_template.format(title=title)
        mr_body = self._format_pr_body(description, files_changed)
        
        # Create MR
        mr = project.mergerequests.create({
            'source_branch': branch,
            'target_branch': self.config.base_branch,
            'title': mr_title,
            'description': mr_body,
            'labels': ','.join(self.config.labels) if self.config.labels else None
        })
        
        logger.info(f"Created GitLab MR: {mr.web_url}")
        
        return {
            "id": mr.id,
            "url": mr.web_url,
            "title": mr.title,
            "state": mr.state
        }
    
    def _format_pr_body(self, description: str, files_changed: Optional[List[str]]) -> str:
        """Format PR body with template."""
        body = self.config.body_template.format(description=description)
        
        if files_changed:
            body += "\n\n### Files Changed\n"
            for file in files_changed[:20]:  # Limit to first 20
                body += f"- {file}\n"
            if len(files_changed) > 20:
                body += f"\n*... and {len(files_changed) - 20} more files*\n"
        
        return body

