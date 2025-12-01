"""
Webhook Handler - Handles incoming webhooks from Git platforms.
Part of Feature: GitOps Documentation Pipeline (v2.0)
"""

import json
import hmac
import hashlib
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from src.utils.logger import get_logger

logger = get_logger(__name__)


class WebhookEvent(Enum):
    """Webhook event types."""
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    MERGE_REQUEST = "merge_request"
    PING = "ping"
    UNKNOWN = "unknown"


@dataclass
class WebhookPayload:
    """Parsed webhook payload."""
    event: WebhookEvent
    repository: str
    branch: str
    commits: list
    action: Optional[str] = None
    raw_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.raw_data is None:
            self.raw_data = {}


class WebhookHandler:
    """
    Handles incoming webhooks from Git platforms.
    Supports GitHub and GitLab webhooks.
    """
    
    def __init__(self, secret: Optional[str] = None):
        """
        Initialize webhook handler.
        
        Args:
            secret: Webhook secret for verification
        """
        self.secret = secret
        self.handlers: Dict[WebhookEvent, Callable] = {}
    
    def register_handler(self, event: WebhookEvent, handler: Callable):
        """
        Register handler for webhook event.
        
        Args:
            event: Webhook event type
            handler: Handler function
        """
        self.handlers[event] = handler
        logger.debug(f"Registered handler for {event.value}")
    
    def handle_webhook(
        self,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        platform: str = "github"
    ) -> Dict[str, Any]:
        """
        Handle incoming webhook.
        
        Args:
            payload: Webhook payload
            headers: HTTP headers
            platform: Platform type ("github" or "gitlab")
            
        Returns:
            Response dictionary
        """
        try:
            # Verify webhook signature
            if self.secret and not self._verify_signature(payload, headers, platform):
                logger.warning("Webhook signature verification failed")
                return {"error": "Invalid signature", "status": 401}
            
            # Parse payload
            webhook_payload = self._parse_payload(payload, platform)
            
            # Execute handler
            if webhook_payload.event in self.handlers:
                handler = self.handlers[webhook_payload.event]
                result = handler(webhook_payload)
                logger.info(f"Handled {webhook_payload.event.value} event")
                return {"success": True, "result": result}
            else:
                logger.warning(f"No handler registered for {webhook_payload.event.value}")
                return {"success": False, "message": "No handler registered"}
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return {"error": str(e), "status": 500}
    
    def _verify_signature(
        self,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        platform: str
    ) -> bool:
        """Verify webhook signature."""
        if not self.secret:
            return True  # No verification if no secret set
        
        try:
            if platform == "github":
                signature = headers.get("X-Hub-Signature-256", "")
                if not signature.startswith("sha256="):
                    return False
                
                expected = hmac.new(
                    self.secret.encode(),
                    json.dumps(payload).encode(),
                    hashlib.sha256
                ).hexdigest()
                
                return hmac.compare_digest(f"sha256={expected}", signature)
            elif platform == "gitlab":
                token = headers.get("X-Gitlab-Token", "")
                return token == self.secret
            else:
                return False
        except Exception as e:
            logger.error(f"Error verifying signature: {e}")
            return False
    
    def _parse_payload(self, payload: Dict[str, Any], platform: str) -> WebhookPayload:
        """Parse webhook payload."""
        if platform == "github":
            return self._parse_github_payload(payload)
        elif platform == "gitlab":
            return self._parse_gitlab_payload(payload)
        else:
            return WebhookPayload(
                event=WebhookEvent.UNKNOWN,
                repository="unknown",
                branch="unknown",
                commits=[],
                raw_data=payload
            )
    
    def _parse_github_payload(self, payload: Dict[str, Any]) -> WebhookPayload:
        """Parse GitHub webhook payload."""
        event_type = payload.get("action") or payload.get("zen")  # zen for ping
        
        if event_type == "ping":
            event = WebhookEvent.PING
        elif "pull_request" in payload:
            event = WebhookEvent.PULL_REQUEST
            action = payload.get("action")
        elif "commits" in payload:
            event = WebhookEvent.PUSH
            action = None
        else:
            event = WebhookEvent.UNKNOWN
            action = None
        
        repository = payload.get("repository", {}).get("full_name", "unknown")
        branch = payload.get("ref", "").replace("refs/heads/", "")
        commits = payload.get("commits", [])
        
        return WebhookPayload(
            event=event,
            repository=repository,
            branch=branch,
            commits=commits,
            action=action,
            raw_data=payload
        )
    
    def _parse_gitlab_payload(self, payload: Dict[str, Any]) -> WebhookPayload:
        """Parse GitLab webhook payload."""
        event_type = payload.get("event_type", "")
        
        if event_type == "push":
            event = WebhookEvent.PUSH
        elif event_type == "merge_request":
            event = WebhookEvent.MERGE_REQUEST
        else:
            event = WebhookEvent.UNKNOWN
        
        repository = payload.get("project", {}).get("path_with_namespace", "unknown")
        branch = payload.get("ref", "").replace("refs/heads/", "")
        commits = payload.get("commits", [])
        
        return WebhookPayload(
            event=event,
            repository=repository,
            branch=branch,
            commits=commits,
            raw_data=payload
        )

