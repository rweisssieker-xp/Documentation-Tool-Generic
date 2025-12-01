"""
Conflict Resolver - AI-powered conflict resolution for Git merges.
Part of Feature: GitOps Documentation Pipeline (v2.0)
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from src.gitops.git_manager import GitManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ConflictResolver:
    """
    Resolves Git merge conflicts using AI.
    Analyzes conflicts and suggests resolutions.
    """
    
    def __init__(self, model: str = "gpt-4o"):
        """
        Initialize conflict resolver.
        
        Args:
            model: OpenAI model to use
        """
        if not OPENAI_AVAILABLE:
            logger.warning("OpenAI not available, conflict resolution will be manual")
            self.client = None
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
            else:
                logger.warning("OPENAI_API_KEY not set, conflict resolution will be manual")
                self.client = None
        
        self.model = model
    
    def resolve_conflicts(self, git_manager: GitManager) -> List[str]:
        """
        Resolve conflicts in Git repository.
        
        Args:
            git_manager: GitManager instance
            
        Returns:
            List of files that still have conflicts
        """
        if not self.client:
            logger.info("AI conflict resolution not available, returning conflicts for manual resolution")
            status = git_manager.status()
            return status.get("modified_files", [])
        
        unresolved = []
        
        try:
            # Get diff to find conflicts
            diff = git_manager.get_diff()
            if not diff or "<<<<<<<" not in diff:
                logger.info("No conflicts detected")
                return []
            
            # Parse conflicts
            conflicts = self._parse_conflicts(diff)
            
            for conflict_file, conflict_content in conflicts.items():
                resolution = self._resolve_single_conflict(conflict_file, conflict_content)
                
                if resolution:
                    # Write resolved content
                    file_path = git_manager.repo_path / conflict_file
                    if file_path.exists():
                        file_path.write_text(resolution, encoding='utf-8')
                        logger.info(f"Resolved conflict in: {conflict_file}")
                    else:
                        unresolved.append(conflict_file)
                else:
                    unresolved.append(conflict_file)
            
            return unresolved
        except Exception as e:
            logger.error(f"Error resolving conflicts: {e}")
            return unresolved
    
    def _parse_conflicts(self, diff: str) -> Dict[str, str]:
        """Parse conflict markers from diff."""
        conflicts = {}
        current_file = None
        current_conflict = []
        
        for line in diff.split('\n'):
            if line.startswith('diff --git'):
                # Save previous conflict
                if current_file and current_conflict:
                    conflicts[current_file] = '\n'.join(current_conflict)
                
                # Extract filename
                parts = line.split()
                if len(parts) >= 3:
                    current_file = parts[2].replace('a/', '')
                    current_conflict = []
            elif current_file and ('<<<<<<<' in line or '=======' in line or '>>>>>>>' in line):
                current_conflict.append(line)
        
        # Save last conflict
        if current_file and current_conflict:
            conflicts[current_file] = '\n'.join(current_conflict)
        
        return conflicts
    
    def _resolve_single_conflict(self, file_path: str, conflict_content: str) -> Optional[str]:
        """
        Resolve a single conflict using AI.
        
        Args:
            file_path: Path to conflicted file
            conflict_content: Conflict content with markers
            
        Returns:
            Resolved content or None
        """
        try:
            prompt = f"""Resolve this Git merge conflict in a documentation file.

File: {file_path}

Conflict:
{conflict_content}

Instructions:
1. Analyze both versions (ours and theirs)
2. Merge them intelligently, preserving all important information
3. Remove conflict markers (<<<<<<<, =======, >>>>>>>)
4. Ensure the result is coherent and complete
5. If both versions have unique valuable content, combine them
6. If versions are identical or one is clearly better, use the better one

Return only the resolved content, no explanations."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Git expert specializing in documentation merge conflicts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            resolved = response.choices[0].message.content.strip()
            
            # Remove any remaining conflict markers as safety check
            if "<<<<<<<" in resolved or ">>>>>>>" in resolved:
                logger.warning(f"Conflict markers still present in resolution for {file_path}")
                return None
            
            return resolved
        except Exception as e:
            logger.error(f"Error resolving conflict for {file_path}: {e}")
            return None

