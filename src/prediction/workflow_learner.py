"""
Workflow Learner - Learns and recognizes workflow patterns.
Part of Feature 3: Predictive Documentation Assistant
"""

import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from pathlib import Path
import hashlib

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class WorkflowPattern:
    """A learned workflow pattern."""
    id: str
    name: str
    steps: List[str]  # Ordered list of step actions
    frequency: int
    applications: List[str]
    avg_duration: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowLearner:
    """
    Learns workflow patterns from completed sessions.
    Recognizes common patterns and suggests workflow templates.
    """
    
    def __init__(
        self,
        storage_dir: str = "data/workflow_patterns",
        min_pattern_frequency: int = 2
    ):
        """
        Initialize workflow learner.
        
        Args:
            storage_dir: Directory for storing patterns
            min_pattern_frequency: Minimum occurrences to consider a pattern
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.min_frequency = min_pattern_frequency
        
        # Pattern storage
        self._patterns: Dict[str, WorkflowPattern] = {}
        
        # Session history for pattern detection
        self._session_sequences: List[Tuple[List[str], str]] = []  # (steps, app)
        
        # Load existing patterns
        self._load_patterns()
        
        logger.info("WorkflowLearner initialized")
    
    def learn_from_session(
        self,
        session_data: Dict[str, Any]
    ) -> List[WorkflowPattern]:
        """
        Learn patterns from a completed session.
        
        Args:
            session_data: Session data
            
        Returns:
            List of newly identified patterns
        """
        steps = session_data.get("steps", [])
        application = session_data.get("application", "unknown")
        
        # Extract action sequence
        actions = self._extract_action_sequence(steps)
        
        if len(actions) < 3:
            return []
        
        # Store session sequence
        self._session_sequences.append((actions, application))
        
        # Detect new patterns
        new_patterns = self._detect_patterns()
        
        # Save patterns
        self._save_patterns()
        
        logger.info(f"Learned from session: {len(new_patterns)} new patterns")
        return new_patterns
    
    def recognize_workflow(
        self,
        current_steps: List[Dict[str, Any]],
        threshold: float = 0.6
    ) -> List[Tuple[WorkflowPattern, float]]:
        """
        Recognize which known workflow(s) match current steps.
        
        Args:
            current_steps: Current session steps
            threshold: Minimum similarity threshold
            
        Returns:
            List of (pattern, similarity) tuples
        """
        current_actions = self._extract_action_sequence(current_steps)
        
        if not current_actions:
            return []
        
        matches = []
        
        for pattern in self._patterns.values():
            similarity = self._calculate_similarity(current_actions, pattern.steps)
            
            if similarity >= threshold:
                matches.append((pattern, similarity))
        
        # Sort by similarity
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches
    
    def get_workflow_suggestions(
        self,
        partial_steps: List[Dict[str, Any]],
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Suggest workflow completions based on partial steps.
        
        Args:
            partial_steps: Partial workflow steps
            limit: Maximum suggestions
            
        Returns:
            List of workflow suggestions
        """
        matches = self.recognize_workflow(partial_steps, threshold=0.3)
        
        suggestions = []
        partial_actions = self._extract_action_sequence(partial_steps)
        partial_set = set(partial_actions)
        
        for pattern, similarity in matches[:limit]:
            # Find remaining steps
            remaining = [s for s in pattern.steps if s not in partial_set]
            
            suggestions.append({
                "pattern_name": pattern.name,
                "similarity": similarity,
                "completed_steps": len(partial_actions),
                "remaining_steps": remaining,
                "total_steps": len(pattern.steps),
                "applications": pattern.applications
            })
        
        return suggestions
    
    def create_template(
        self,
        name: str,
        steps: List[str],
        application: Optional[str] = None
    ) -> WorkflowPattern:
        """
        Manually create a workflow template.
        
        Args:
            name: Template name
            steps: Ordered list of step actions
            application: Associated application
            
        Returns:
            Created WorkflowPattern
        """
        pattern_id = self._generate_pattern_id(steps)
        
        pattern = WorkflowPattern(
            id=pattern_id,
            name=name,
            steps=steps,
            frequency=1,
            applications=[application] if application else [],
            avg_duration=0.0,
            metadata={"manual": True}
        )
        
        self._patterns[pattern_id] = pattern
        self._save_patterns()
        
        logger.info(f"Created template: {name}")
        return pattern
    
    def get_all_patterns(self) -> List[WorkflowPattern]:
        """Get all learned patterns."""
        return list(self._patterns.values())
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """Get statistics about learned patterns."""
        patterns = list(self._patterns.values())
        
        if not patterns:
            return {
                "total_patterns": 0,
                "total_sessions_analyzed": len(self._session_sequences),
                "applications": []
            }
        
        all_apps = set()
        for p in patterns:
            all_apps.update(p.applications)
        
        return {
            "total_patterns": len(patterns),
            "total_sessions_analyzed": len(self._session_sequences),
            "avg_pattern_length": sum(len(p.steps) for p in patterns) / len(patterns),
            "max_pattern_frequency": max(p.frequency for p in patterns),
            "applications": list(all_apps)
        }
    
    def _extract_action_sequence(
        self,
        steps: List[Dict[str, Any]]
    ) -> List[str]:
        """Extract normalized action sequence from steps."""
        actions = []
        
        for step in steps:
            # Use action type or derive from description
            action = step.get("action_type")
            
            if not action:
                # Try to derive from description
                desc = step.get("description", "").lower()
                if "click" in desc or "klick" in desc:
                    action = "click"
                elif "enter" in desc or "eingeb" in desc or "type" in desc:
                    action = "input"
                elif "select" in desc or "wähl" in desc:
                    action = "select"
                elif "open" in desc or "öffn" in desc:
                    action = "open"
                elif "save" in desc or "speicher" in desc:
                    action = "save"
                else:
                    action = "action"
            
            # Add window context if available
            window = step.get("window_title", "")
            if window:
                window_short = window[:20].replace(" ", "_")
                action = f"{action}_{window_short}"
            
            actions.append(action.lower())
        
        return actions
    
    def _detect_patterns(self) -> List[WorkflowPattern]:
        """Detect patterns from stored session sequences."""
        new_patterns = []
        
        # Find common subsequences
        all_subsequences = defaultdict(list)
        
        for actions, app in self._session_sequences:
            # Extract subsequences of length 3-10
            for length in range(3, min(11, len(actions) + 1)):
                for i in range(len(actions) - length + 1):
                    subseq = tuple(actions[i:i + length])
                    all_subsequences[subseq].append(app)
        
        # Find frequent patterns
        for subseq, apps in all_subsequences.items():
            if len(apps) >= self.min_frequency:
                pattern_id = self._generate_pattern_id(list(subseq))
                
                if pattern_id not in self._patterns:
                    # Create new pattern
                    pattern = WorkflowPattern(
                        id=pattern_id,
                        name=f"Pattern_{len(self._patterns) + 1}",
                        steps=list(subseq),
                        frequency=len(apps),
                        applications=list(set(apps)),
                        avg_duration=0.0
                    )
                    
                    self._patterns[pattern_id] = pattern
                    new_patterns.append(pattern)
                else:
                    # Update existing pattern
                    self._patterns[pattern_id].frequency = len(apps)
                    self._patterns[pattern_id].applications = list(
                        set(self._patterns[pattern_id].applications + apps)
                    )
        
        return new_patterns
    
    def _calculate_similarity(
        self,
        seq1: List[str],
        seq2: List[str]
    ) -> float:
        """Calculate similarity between two sequences using LCS."""
        if not seq1 or not seq2:
            return 0.0
        
        # Longest Common Subsequence
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i - 1] == seq2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
        
        lcs_length = dp[m][n]
        
        # Similarity as ratio of LCS to shorter sequence
        return lcs_length / min(m, n)
    
    def _generate_pattern_id(self, steps: List[str]) -> str:
        """Generate unique ID for a pattern."""
        content = "->".join(steps)
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _save_patterns(self) -> None:
        """Save patterns to disk."""
        data = {
            "patterns": {
                pid: {
                    "id": p.id,
                    "name": p.name,
                    "steps": p.steps,
                    "frequency": p.frequency,
                    "applications": p.applications,
                    "avg_duration": p.avg_duration,
                    "metadata": p.metadata
                }
                for pid, p in self._patterns.items()
            },
            "sessions_count": len(self._session_sequences)
        }
        
        filepath = self.storage_dir / "patterns.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_patterns(self) -> None:
        """Load patterns from disk."""
        filepath = self.storage_dir / "patterns.json"
        
        if not filepath.exists():
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for pid, pdata in data.get("patterns", {}).items():
                self._patterns[pid] = WorkflowPattern(
                    id=pdata["id"],
                    name=pdata["name"],
                    steps=pdata["steps"],
                    frequency=pdata["frequency"],
                    applications=pdata["applications"],
                    avg_duration=pdata.get("avg_duration", 0.0),
                    metadata=pdata.get("metadata", {})
                )
            
            logger.info(f"Loaded {len(self._patterns)} patterns")
        
        except Exception as e:
            logger.error(f"Failed to load patterns: {e}")

