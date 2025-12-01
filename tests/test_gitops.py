"""
Tests for GitOps Documentation Pipeline Module
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

try:
    import git
    GITPYTHON_AVAILABLE = True
except ImportError:
    GITPYTHON_AVAILABLE = False


@pytest.mark.skipif(not GITPYTHON_AVAILABLE, reason="gitpython not available")
class TestGitManager:
    """Tests for GitManager class."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create temporary Git repository."""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir)
        yield repo_path
        shutil.rmtree(temp_dir)
    
    def test_git_manager_initialization(self, temp_repo):
        """Test GitManager initialization."""
        from src.gitops.git_manager import GitManager, GitConfig
        
        config = GitConfig(
            repo_path=temp_repo,
            author_name="Test User",
            author_email="test@example.com"
        )
        
        manager = GitManager(config)
        
        assert manager.repo_path == temp_repo
        assert manager.config.author_name == "Test User"
    
    def test_git_status(self, temp_repo):
        """Test getting Git status."""
        from src.gitops.git_manager import GitManager, GitConfig
        
        config = GitConfig(repo_path=temp_repo)
        manager = GitManager(config)
        
        # Create a test file
        test_file = temp_repo / "test.txt"
        test_file.write_text("test content")
        
        status = manager.status()
        assert "untracked_files" in status
        assert "test.txt" in status["untracked_files"]
    
    def test_add_and_commit(self, temp_repo):
        """Test staging and committing files."""
        from src.gitops.git_manager import GitManager, GitConfig
        
        config = GitConfig(repo_path=temp_repo)
        manager = GitManager(config)
        
        # Create and stage file
        test_file = temp_repo / "test.txt"
        test_file.write_text("test content")
        
        assert manager.add(["test.txt"]) == True
        
        # Commit
        commit_hash = manager.commit("test: Add test file")
        assert commit_hash is not None
        
        # Verify commit
        commits = manager.get_commits(limit=1)
        assert len(commits) == 1
        assert "test: Add test file" in commits[0].message


class TestCommitGenerator:
    """Tests for CommitGenerator class."""
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'})
    @patch('src.gitops.commit_generator.OpenAI')
    def test_commit_generator_initialization(self, mock_openai):
        """Test CommitGenerator initialization."""
        from src.gitops.commit_generator import CommitGenerator
        
        generator = CommitGenerator()
        assert generator.model == "gpt-4o-mini"
        assert generator.language == "de"
    
    def test_generate_basic_message(self):
        """Test basic commit message generation without AI."""
        from src.gitops.commit_generator import CommitGenerator, CommitContext
        
        generator = CommitGenerator()
        generator.client = None  # Disable AI
        
        context = CommitContext(
            files_changed=["docs/manual.md"],
            diff_summary="Added new section"
        )
        
        message = generator.generate_commit_message(context)
        assert message is not None
        assert len(message) > 0
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'})
    @patch('src.gitops.commit_generator.OpenAI')
    def test_generate_ai_message(self, mock_openai_class):
        """Test AI-powered commit message generation."""
        from src.gitops.commit_generator import CommitGenerator, CommitContext
        
        # Mock OpenAI response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "docs(manual): Neues Kapitel hinzugefügt"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        generator = CommitGenerator()
        generator.client = mock_client
        
        context = CommitContext(
            files_changed=["docs/manual.md"],
            diff_summary="Added new section",
            session_title="User Registration",
            step_count=5
        )
        
        message = generator.generate_commit_message(context)
        assert message == "docs(manual): Neues Kapitel hinzugefügt"


class TestRepositorySync:
    """Tests for RepositorySync class."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create temporary Git repository."""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir)
        yield repo_path
        shutil.rmtree(temp_dir)
    
    @pytest.mark.skipif(not GITPYTHON_AVAILABLE, reason="gitpython not available")
    def test_repository_sync_initialization(self, temp_repo):
        """Test RepositorySync initialization."""
        from src.gitops.repository_sync import RepositorySync, SyncConfig
        from src.gitops.git_manager import GitManager, GitConfig
        
        git_config = GitConfig(repo_path=temp_repo)
        git_manager = GitManager(git_config)
        
        sync_config = SyncConfig(auto_sync=True)
        sync = RepositorySync(git_manager, sync_config)
        
        assert sync.git_manager == git_manager
        assert sync.sync_config.auto_sync == True
    
    @pytest.mark.skipif(not GITPYTHON_AVAILABLE, reason="gitpython not available")
    def test_sync_status(self, temp_repo):
        """Test getting sync status."""
        from src.gitops.repository_sync import RepositorySync, SyncConfig
        from src.gitops.git_manager import GitManager, GitConfig
        
        git_config = GitConfig(repo_path=temp_repo)
        git_manager = GitManager(git_config)
        
        sync = RepositorySync(git_manager)
        status = sync.get_sync_status()
        
        assert "last_sync" in status
        assert "pending_changes" in status
        assert "current_branch" in status


class TestConflictResolver:
    """Tests for ConflictResolver class."""
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'})
    @patch('src.gitops.conflict_resolver.OpenAI')
    def test_conflict_resolver_initialization(self, mock_openai):
        """Test ConflictResolver initialization."""
        from src.gitops.conflict_resolver import ConflictResolver
        
        resolver = ConflictResolver()
        assert resolver.model == "gpt-4o"
    
    def test_parse_conflicts(self):
        """Test conflict parsing."""
        from src.gitops.conflict_resolver import ConflictResolver
        
        resolver = ConflictResolver()
        resolver.client = None  # Disable AI
        
        diff = """diff --git a/test.md b/test.md
<<<<<<< HEAD
Our version
=======
Their version
>>>>>>> branch
"""
        conflicts = resolver._parse_conflicts(diff)
        assert len(conflicts) > 0


class TestPRAutomation:
    """Tests for PRAutomation class."""
    
    def test_pr_config_initialization(self):
        """Test PRConfig initialization."""
        from src.gitops.pr_automation import PRConfig, Platform
        
        config = PRConfig(
            platform=Platform.GITHUB,
            repository="owner/repo"
        )
        
        assert config.platform == Platform.GITHUB
        assert config.repository == "owner/repo"
        assert config.base_branch == "main"
    
    @patch.dict('os.environ', {}, clear=True)
    def test_pr_automation_no_token(self):
        """Test PRAutomation without token."""
        from src.gitops.pr_automation import PRAutomation, PRConfig, Platform
        
        config = PRConfig(
            platform=Platform.GITHUB,
            repository="owner/repo"
        )
        
        automation = PRAutomation(config)
        assert automation.client is None


class TestWebhookHandler:
    """Tests for WebhookHandler class."""
    
    def test_webhook_handler_initialization(self):
        """Test WebhookHandler initialization."""
        from src.gitops.webhook_handler import WebhookHandler
        
        handler = WebhookHandler(secret="test_secret")
        assert handler.secret == "test_secret"
    
    def test_register_handler(self):
        """Test registering webhook handlers."""
        from src.gitops.webhook_handler import WebhookHandler, WebhookEvent
        
        handler = WebhookHandler()
        
        def test_handler(payload):
            return {"success": True}
        
        handler.register_handler(WebhookEvent.PUSH, test_handler)
        assert WebhookEvent.PUSH in handler.handlers
    
    def test_parse_github_payload(self):
        """Test parsing GitHub webhook payload."""
        from src.gitops.webhook_handler import WebhookHandler, WebhookEvent
        
        handler = WebhookHandler()
        
        payload = {
            "repository": {"full_name": "owner/repo"},
            "ref": "refs/heads/main",
            "commits": [{"id": "abc123"}]
        }
        
        webhook = handler._parse_github_payload(payload)
        assert webhook.repository == "owner/repo"
        assert webhook.branch == "main"
        assert webhook.event == WebhookEvent.PUSH


class TestCIIntegration:
    """Tests for CIIntegration class."""
    
    def test_ci_config_initialization(self):
        """Test CIConfig initialization."""
        from src.gitops.ci_integration import CIConfig, CICDPlatform
        
        config = CIConfig(
            platform=CICDPlatform.GITHUB_ACTIONS,
            trigger_on_push=True
        )
        
        assert config.platform == CICDPlatform.GITHUB_ACTIONS
        assert config.trigger_on_push == True
    
    def test_ci_integration_initialization(self):
        """Test CIIntegration initialization."""
        from src.gitops.ci_integration import CIIntegration, CIConfig, CICDPlatform
        
        config = CIConfig(platform=CICDPlatform.GITHUB_ACTIONS)
        ci = CIIntegration(config)
        
        assert ci.config.platform == CICDPlatform.GITHUB_ACTIONS
    
    def test_generate_github_actions_workflow(self, tmp_path):
        """Test GitHub Actions workflow generation."""
        from src.gitops.ci_integration import CIIntegration, CIConfig, CICDPlatform
        
        config = CIConfig(
            platform=CICDPlatform.GITHUB_ACTIONS,
            trigger_on_push=True
        )
        ci = CIIntegration(config)
        
        result = ci.generate_workflow_file(tmp_path)
        assert result == True
        
        workflow_file = tmp_path / ".github" / "workflows" / "docs.yml"
        assert workflow_file.exists()
        assert "Documentation Deployment" in workflow_file.read_text()

