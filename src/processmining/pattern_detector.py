"""
Pattern Detector - Detects patterns in process data.
Part of Feature 2: Process Mining Engine
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Pattern:
    """A detected process pattern."""
    id: str
    name: str
    sequence: List[str]
    support: float
    confidence: float
    occurrences: int
    pattern_type: str  # "sequential", "parallel", "loop", "choice"


class PatternDetector:
    """
    Detects patterns in process data.
    Identifies sequential, parallel, loop, and choice patterns.
    """
    
    def __init__(
        self,
        min_support: float = 0.1,
        min_confidence: float = 0.5
    ):
        """
        Initialize pattern detector.
        
        Args:
            min_support: Minimum support threshold
            min_confidence: Minimum confidence threshold
        """
        self.min_support = min_support
        self.min_confidence = min_confidence
        
        logger.info("PatternDetector initialized")
    
    def detect_patterns(
        self,
        traces: List[List[str]],
        max_length: int = 5
    ) -> List[Pattern]:
        """
        Detect patterns in traces.
        
        Args:
            traces: List of activity traces
            max_length: Maximum pattern length
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # Detect sequential patterns
        seq_patterns = self._detect_sequential(traces, max_length)
        patterns.extend(seq_patterns)
        
        # Detect loop patterns
        loop_patterns = self._detect_loops(traces)
        patterns.extend(loop_patterns)
        
        # Detect choice patterns
        choice_patterns = self._detect_choices(traces)
        patterns.extend(choice_patterns)
        
        # Sort by support
        patterns.sort(key=lambda p: p.support, reverse=True)
        
        logger.info(f"Detected {len(patterns)} patterns")
        return patterns
    
    def find_common_subsequences(
        self,
        traces: List[List[str]],
        min_length: int = 2
    ) -> List[Tuple[List[str], int]]:
        """
        Find common subsequences across traces.
        
        Args:
            traces: List of traces
            min_length: Minimum subsequence length
            
        Returns:
            List of (subsequence, count) tuples
        """
        subsequence_counts = defaultdict(int)
        
        for trace in traces:
            # Generate all subsequences
            for length in range(min_length, len(trace) + 1):
                for i in range(len(trace) - length + 1):
                    subseq = tuple(trace[i:i + length])
                    subsequence_counts[subseq] += 1
        
        # Filter by minimum support
        min_count = max(1, int(len(traces) * self.min_support))
        
        common = [
            (list(seq), count)
            for seq, count in subsequence_counts.items()
            if count >= min_count
        ]
        
        # Sort by count and length
        common.sort(key=lambda x: (x[1], len(x[0])), reverse=True)
        
        return common
    
    def _detect_sequential(
        self,
        traces: List[List[str]],
        max_length: int
    ) -> List[Pattern]:
        """Detect sequential patterns."""
        patterns = []
        total = len(traces)
        
        # Count n-grams
        for n in range(2, max_length + 1):
            ngram_counts = defaultdict(int)
            
            for trace in traces:
                for i in range(len(trace) - n + 1):
                    ngram = tuple(trace[i:i + n])
                    ngram_counts[ngram] += 1
            
            # Create patterns
            for ngram, count in ngram_counts.items():
                support = count / total
                if support >= self.min_support:
                    patterns.append(Pattern(
                        id=f"seq_{hash(ngram) % 10000:04d}",
                        name=f"Sequence: {' → '.join(ngram)}",
                        sequence=list(ngram),
                        support=support,
                        confidence=self._calculate_confidence(ngram, traces),
                        occurrences=count,
                        pattern_type="sequential"
                    ))
        
        return patterns
    
    def _detect_loops(self, traces: List[List[str]]) -> List[Pattern]:
        """Detect loop patterns."""
        patterns = []
        total = len(traces)
        
        loop_counts = defaultdict(int)
        
        for trace in traces:
            # Find repeated activities
            for i in range(len(trace)):
                activity = trace[i]
                # Check if activity repeats
                for j in range(i + 1, len(trace)):
                    if trace[j] == activity:
                        loop_seq = tuple(trace[i:j + 1])
                        loop_counts[loop_seq] += 1
                        break
        
        for loop_seq, count in loop_counts.items():
            support = count / total
            if support >= self.min_support and len(loop_seq) >= 2:
                patterns.append(Pattern(
                    id=f"loop_{hash(loop_seq) % 10000:04d}",
                    name=f"Loop: {' → '.join(loop_seq)}",
                    sequence=list(loop_seq),
                    support=support,
                    confidence=1.0,
                    occurrences=count,
                    pattern_type="loop"
                ))
        
        return patterns
    
    def _detect_choices(self, traces: List[List[str]]) -> List[Pattern]:
        """Detect choice/XOR patterns."""
        patterns = []
        total = len(traces)
        
        # Find activities that follow the same activity
        followers = defaultdict(lambda: defaultdict(int))
        
        for trace in traces:
            for i in range(len(trace) - 1):
                followers[trace[i]][trace[i + 1]] += 1
        
        # Activities with multiple followers = choice
        for activity, next_acts in followers.items():
            if len(next_acts) > 1:
                total_follows = sum(next_acts.values())
                
                for next_act, count in next_acts.items():
                    confidence = count / total_follows
                    if confidence >= 0.1:  # Lower threshold for choices
                        patterns.append(Pattern(
                            id=f"choice_{hash((activity, next_act)) % 10000:04d}",
                            name=f"Choice: {activity} → {next_act}",
                            sequence=[activity, next_act],
                            support=count / total,
                            confidence=confidence,
                            occurrences=count,
                            pattern_type="choice"
                        ))
        
        return patterns
    
    def _calculate_confidence(
        self,
        ngram: Tuple[str, ...],
        traces: List[List[str]]
    ) -> float:
        """Calculate confidence for a pattern."""
        if len(ngram) < 2:
            return 1.0
        
        antecedent = ngram[:-1]
        consequent = ngram[-1]
        
        antecedent_count = 0
        full_count = 0
        
        for trace in traces:
            for i in range(len(trace) - len(antecedent)):
                if tuple(trace[i:i + len(antecedent)]) == antecedent:
                    antecedent_count += 1
                    if i + len(antecedent) < len(trace) and trace[i + len(antecedent)] == consequent:
                        full_count += 1
        
        return full_count / antecedent_count if antecedent_count > 0 else 0.0

