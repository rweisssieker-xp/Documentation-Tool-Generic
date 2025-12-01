"""
Commit Generator - AI-powered commit message generation.
Part of Feature: GitOps Documentation Pipeline (v2.0)
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CommitContext:
    """Context for commit message generation."""
    files_changed: List[str]
    diff_summary: str
    session_title: Optional[str] = None
    step_count: Optional[int] = None
    documentation_type: Optional[str] = None  # "sop", "tutorial", "manual"


class CommitGenerator:
    """
    Generates semantic commit messages using AI.
    Follows conventional commits format when possible.
    """
    
    def __init__(self, model: str = "gpt-4o-mini", language: str = "de"):
        """
        Initialize commit generator.
        
        Args:
            model: OpenAI model to use
            language: Language for commit messages (de/en)
        """
        if not OPENAI_AVAILABLE:
            logger.warning("OpenAI not available, commit messages will be basic")
            self.client = None
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
            else:
                logger.warning("OPENAI_API_KEY not set, commit messages will be basic")
                self.client = None
        
        self.model = model
        self.language = language
    
    def generate_commit_message(
        self,
        context: CommitContext,
        style: str = "conventional"
    ) -> str:
        """
        Generate commit message from context.
        
        Args:
            context: Commit context with changes
            style: Commit style ("conventional", "semantic", "simple")
            
        Returns:
            Generated commit message
        """
        if not self.client:
            return self._generate_basic_message(context)
        
        try:
            prompt = self._build_prompt(context, style)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt(style)},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=150
            )
            
            message = response.choices[0].message.content.strip()
            logger.debug(f"Generated commit message: {message[:50]}...")
            return message
        except Exception as e:
            logger.error(f"Error generating commit message: {e}")
            return self._generate_basic_message(context)
    
    def _get_system_prompt(self, style: str) -> str:
        """Get system prompt for commit message generation."""
        if self.language == "de":
            if style == "conventional":
                return """Du bist ein Git-Experte. Generiere präzise Commit-Messages im Conventional Commits Format:
- Format: <type>(<scope>): <subject>
- Types: docs, feat, fix, refactor, style, test
- Scope: Optional, z.B. "manual", "tutorial", "sop"
- Subject: Kurz, präzise, im Imperativ
- Maximal 50 Zeichen für Subject
- Beispiele:
  - docs(manual): Benutzer-Registrierung dokumentiert
  - feat(tutorial): Neues Login-Tutorial hinzugefügt
  - fix(sop): Screenshot-Reihenfolge korrigiert"""
            else:
                return """Du bist ein Git-Experte. Generiere präzise, semantische Commit-Messages auf Deutsch.
Die Message sollte kurz, präzise und im Imperativ sein."""
        else:
            if style == "conventional":
                return """You are a Git expert. Generate precise commit messages in Conventional Commits format:
- Format: <type>(<scope>): <subject>
- Types: docs, feat, fix, refactor, style, test
- Scope: Optional, e.g., "manual", "tutorial", "sop"
- Subject: Short, precise, imperative mood
- Maximum 50 characters for subject"""
            else:
                return """You are a Git expert. Generate precise, semantic commit messages in English.
The message should be short, precise, and in imperative mood."""
    
    def _build_prompt(self, context: CommitContext, style: str) -> str:
        """Build user prompt for commit generation."""
        parts = []
        
        if context.session_title:
            parts.append(f"Session: {context.session_title}")
        
        if context.step_count:
            parts.append(f"Steps: {context.step_count}")
        
        if context.documentation_type:
            parts.append(f"Type: {context.documentation_type}")
        
        parts.append(f"\nFiles changed ({len(context.files_changed)}):")
        for file in context.files_changed[:10]:  # Limit to first 10
            parts.append(f"  - {file}")
        
        if context.diff_summary:
            parts.append(f"\nSummary of changes:\n{context.diff_summary[:500]}")
        
        return "\n".join(parts)
    
    def _generate_basic_message(self, context: CommitContext) -> str:
        """Generate basic commit message without AI."""
        if context.session_title:
            prefix = context.session_title[:30]
        elif context.documentation_type:
            prefix = f"docs({context.documentation_type})"
        else:
            prefix = "docs"
        
        file_count = len(context.files_changed)
        if file_count == 1:
            suffix = f": {context.files_changed[0]}"
        else:
            suffix = f": {file_count} files updated"
        
        return f"{prefix}{suffix}"

