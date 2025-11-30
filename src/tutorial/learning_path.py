"""
Learning Path Optimizer - Optimizes tutorial learning paths.
Part of Feature 5: Interactive Tutorial Generator
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from src.utils.logger import get_logger

logger = get_logger(__name__)


class LearnerLevel(Enum):
    """Learner experience levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class LearningNode:
    """A node in the learning path."""
    id: str
    content: str
    difficulty: float  # 0-1
    prerequisites: List[str]
    estimated_time: int  # seconds
    importance: float  # 0-1


class LearningPathOptimizer:
    """
    Optimizes learning paths based on learner profile.
    Adapts content order and difficulty.
    """
    
    def __init__(self):
        """Initialize learning path optimizer."""
        logger.info("LearningPathOptimizer initialized")
    
    def optimize_path(
        self,
        nodes: List[LearningNode],
        learner_level: LearnerLevel = LearnerLevel.INTERMEDIATE,
        available_time: Optional[int] = None
    ) -> List[LearningNode]:
        """
        Optimize learning path for learner.
        
        Args:
            nodes: Available learning nodes
            learner_level: Learner experience level
            available_time: Available time in seconds
            
        Returns:
            Optimized list of nodes
        """
        # Filter by prerequisites
        valid_nodes = self._filter_by_prerequisites(nodes)
        
        # Adjust for learner level
        adjusted_nodes = self._adjust_for_level(valid_nodes, learner_level)
        
        # Optimize for time if specified
        if available_time:
            adjusted_nodes = self._fit_to_time(adjusted_nodes, available_time)
        
        # Sort by optimal order
        optimized = self._sort_optimal(adjusted_nodes)
        
        logger.info(f"Optimized path: {len(optimized)} nodes for {learner_level.value}")
        return optimized
    
    def create_adaptive_path(
        self,
        nodes: List[LearningNode],
        performance_history: List[Dict[str, Any]]
    ) -> List[LearningNode]:
        """
        Create adaptive path based on learner performance.
        
        Args:
            nodes: Available learning nodes
            performance_history: Previous performance data
            
        Returns:
            Adapted learning path
        """
        # Analyze performance
        avg_score = self._calculate_avg_performance(performance_history)
        weak_areas = self._identify_weak_areas(performance_history)
        
        # Determine effective level
        if avg_score >= 0.8:
            level = LearnerLevel.ADVANCED
        elif avg_score >= 0.5:
            level = LearnerLevel.INTERMEDIATE
        else:
            level = LearnerLevel.BEGINNER
        
        # Get base path
        path = self.optimize_path(nodes, level)
        
        # Add reinforcement for weak areas
        reinforcement = self._create_reinforcement(nodes, weak_areas)
        
        # Interleave reinforcement
        return self._interleave_content(path, reinforcement)
    
    def suggest_next(
        self,
        completed_nodes: List[str],
        all_nodes: List[LearningNode],
        performance: float
    ) -> Optional[LearningNode]:
        """
        Suggest next learning node.
        
        Args:
            completed_nodes: IDs of completed nodes
            all_nodes: All available nodes
            performance: Performance on last node (0-1)
            
        Returns:
            Suggested next node
        """
        completed_set = set(completed_nodes)
        
        # Find eligible nodes (prerequisites met)
        eligible = [
            n for n in all_nodes
            if n.id not in completed_set
            and all(p in completed_set for p in n.prerequisites)
        ]
        
        if not eligible:
            return None
        
        # Adjust difficulty based on performance
        target_difficulty = self._calculate_target_difficulty(performance)
        
        # Find closest match
        best_match = min(
            eligible,
            key=lambda n: abs(n.difficulty - target_difficulty)
        )
        
        return best_match
    
    def _filter_by_prerequisites(
        self,
        nodes: List[LearningNode]
    ) -> List[LearningNode]:
        """Filter nodes with satisfied prerequisites."""
        available_ids = {n.id for n in nodes}
        
        return [
            n for n in nodes
            if all(p in available_ids or p == "" for p in n.prerequisites)
        ]
    
    def _adjust_for_level(
        self,
        nodes: List[LearningNode],
        level: LearnerLevel
    ) -> List[LearningNode]:
        """Adjust nodes for learner level."""
        level_weights = {
            LearnerLevel.BEGINNER: (0.0, 0.4),
            LearnerLevel.INTERMEDIATE: (0.2, 0.7),
            LearnerLevel.ADVANCED: (0.5, 1.0)
        }
        
        min_diff, max_diff = level_weights.get(level, (0.0, 1.0))
        
        # Include all but prioritize level-appropriate
        adjusted = []
        for node in nodes:
            # Adjust importance based on difficulty match
            if min_diff <= node.difficulty <= max_diff:
                adjusted.append(node)
            elif node.importance > 0.7:  # Important nodes always included
                adjusted.append(node)
        
        return adjusted
    
    def _fit_to_time(
        self,
        nodes: List[LearningNode],
        available_time: int
    ) -> List[LearningNode]:
        """Select nodes that fit available time."""
        # Sort by importance/time ratio
        sorted_nodes = sorted(
            nodes,
            key=lambda n: n.importance / max(n.estimated_time, 1),
            reverse=True
        )
        
        selected = []
        total_time = 0
        
        for node in sorted_nodes:
            if total_time + node.estimated_time <= available_time:
                selected.append(node)
                total_time += node.estimated_time
        
        return selected
    
    def _sort_optimal(
        self,
        nodes: List[LearningNode]
    ) -> List[LearningNode]:
        """Sort nodes in optimal learning order."""
        # Topological sort with difficulty consideration
        sorted_nodes = []
        remaining = list(nodes)
        completed = set()
        
        while remaining:
            # Find nodes with met prerequisites
            ready = [
                n for n in remaining
                if all(p in completed or p == "" for p in n.prerequisites)
            ]
            
            if not ready:
                # Handle circular dependencies
                ready = remaining[:1]
            
            # Select easiest ready node
            next_node = min(ready, key=lambda n: n.difficulty)
            sorted_nodes.append(next_node)
            completed.add(next_node.id)
            remaining.remove(next_node)
        
        return sorted_nodes
    
    def _calculate_avg_performance(
        self,
        history: List[Dict[str, Any]]
    ) -> float:
        """Calculate average performance from history."""
        if not history:
            return 0.5
        
        scores = [h.get("score", 0.5) for h in history]
        return sum(scores) / len(scores)
    
    def _identify_weak_areas(
        self,
        history: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify weak areas from performance history."""
        weak = []
        
        for entry in history:
            if entry.get("score", 1.0) < 0.6:
                topic = entry.get("topic")
                if topic and topic not in weak:
                    weak.append(topic)
        
        return weak
    
    def _create_reinforcement(
        self,
        nodes: List[LearningNode],
        weak_areas: List[str]
    ) -> List[LearningNode]:
        """Create reinforcement nodes for weak areas."""
        reinforcement = []
        
        for node in nodes:
            if any(area in node.content.lower() for area in weak_areas):
                # Create simplified version for reinforcement
                reinforcement.append(node)
        
        return reinforcement
    
    def _interleave_content(
        self,
        main_path: List[LearningNode],
        reinforcement: List[LearningNode]
    ) -> List[LearningNode]:
        """Interleave reinforcement into main path."""
        result = []
        reinforcement_index = 0
        
        for i, node in enumerate(main_path):
            result.append(node)
            
            # Add reinforcement after every 3 nodes
            if (i + 1) % 3 == 0 and reinforcement_index < len(reinforcement):
                result.append(reinforcement[reinforcement_index])
                reinforcement_index += 1
        
        return result
    
    def _calculate_target_difficulty(self, performance: float) -> float:
        """Calculate target difficulty based on performance."""
        # Good performance -> increase difficulty
        # Poor performance -> decrease difficulty
        if performance >= 0.8:
            return min(1.0, performance + 0.1)
        elif performance >= 0.5:
            return performance
        else:
            return max(0.0, performance - 0.1)

