"""
Variant Analyzer - Analyzes process variants.
Part of Feature 2: Process Mining Engine
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ProcessVariant:
    """A process variant."""
    id: str
    trace: List[str]
    frequency: int
    percentage: float
    avg_duration: float
    is_happy_path: bool
    deviations: List[str]


class VariantAnalyzer:
    """
    Analyzes process variants and identifies deviations.
    """
    
    def __init__(self):
        """Initialize variant analyzer."""
        logger.info("VariantAnalyzer initialized")
    
    def analyze_variants(
        self,
        traces: List[List[str]],
        durations: Optional[List[float]] = None
    ) -> List[ProcessVariant]:
        """
        Analyze all process variants.
        
        Args:
            traces: List of activity traces
            durations: Optional list of trace durations
            
        Returns:
            List of ProcessVariant objects
        """
        if not traces:
            return []
        
        # Group by variant
        variant_data = defaultdict(lambda: {"count": 0, "durations": []})
        
        for i, trace in enumerate(traces):
            key = tuple(trace)
            variant_data[key]["count"] += 1
            if durations and i < len(durations):
                variant_data[key]["durations"].append(durations[i])
        
        total = len(traces)
        
        # Find happy path (most common)
        happy_path = max(variant_data.keys(), key=lambda k: variant_data[k]["count"])
        
        # Create variant objects
        variants = []
        for i, (trace, data) in enumerate(sorted(
            variant_data.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )):
            avg_duration = (
                sum(data["durations"]) / len(data["durations"])
                if data["durations"] else 0.0
            )
            
            # Calculate deviations from happy path
            deviations = self._find_deviations(list(trace), list(happy_path))
            
            variants.append(ProcessVariant(
                id=f"var_{i+1:03d}",
                trace=list(trace),
                frequency=data["count"],
                percentage=data["count"] / total * 100,
                avg_duration=avg_duration,
                is_happy_path=(trace == happy_path),
                deviations=deviations
            ))
        
        logger.info(f"Analyzed {len(variants)} variants")
        return variants
    
    def compare_variants(
        self,
        variant1: ProcessVariant,
        variant2: ProcessVariant
    ) -> Dict[str, Any]:
        """
        Compare two variants.
        
        Args:
            variant1: First variant
            variant2: Second variant
            
        Returns:
            Comparison results
        """
        trace1 = variant1.trace
        trace2 = variant2.trace
        
        # Find common activities
        common = set(trace1) & set(trace2)
        
        # Find differences
        only_in_1 = set(trace1) - set(trace2)
        only_in_2 = set(trace2) - set(trace1)
        
        # Calculate similarity
        similarity = len(common) / len(set(trace1) | set(trace2)) if trace1 or trace2 else 1.0
        
        # Find structural differences
        lcs = self._longest_common_subsequence(trace1, trace2)
        
        return {
            "similarity": similarity,
            "common_activities": list(common),
            "only_in_variant1": list(only_in_1),
            "only_in_variant2": list(only_in_2),
            "lcs_length": len(lcs),
            "frequency_diff": variant1.frequency - variant2.frequency,
            "duration_diff": variant1.avg_duration - variant2.avg_duration
        }
    
    def cluster_variants(
        self,
        variants: List[ProcessVariant],
        similarity_threshold: float = 0.7
    ) -> List[List[ProcessVariant]]:
        """
        Cluster similar variants.
        
        Args:
            variants: List of variants
            similarity_threshold: Minimum similarity for clustering
            
        Returns:
            List of variant clusters
        """
        if not variants:
            return []
        
        clusters = []
        assigned = set()
        
        for i, var1 in enumerate(variants):
            if i in assigned:
                continue
            
            cluster = [var1]
            assigned.add(i)
            
            for j, var2 in enumerate(variants[i + 1:], i + 1):
                if j in assigned:
                    continue
                
                comparison = self.compare_variants(var1, var2)
                if comparison["similarity"] >= similarity_threshold:
                    cluster.append(var2)
                    assigned.add(j)
            
            clusters.append(cluster)
        
        return clusters
    
    def identify_anomalies(
        self,
        variants: List[ProcessVariant],
        threshold_percentage: float = 5.0
    ) -> List[ProcessVariant]:
        """
        Identify anomalous variants.
        
        Args:
            variants: List of variants
            threshold_percentage: Minimum percentage to not be anomaly
            
        Returns:
            List of anomalous variants
        """
        return [
            v for v in variants
            if v.percentage < threshold_percentage and not v.is_happy_path
        ]
    
    def _find_deviations(
        self,
        trace: List[str],
        reference: List[str]
    ) -> List[str]:
        """Find deviations from reference trace."""
        deviations = []
        
        # Activities in trace but not in reference
        extra = set(trace) - set(reference)
        for act in extra:
            deviations.append(f"Extra: {act}")
        
        # Activities in reference but not in trace
        missing = set(reference) - set(trace)
        for act in missing:
            deviations.append(f"Missing: {act}")
        
        # Order differences
        common = [a for a in trace if a in reference]
        ref_common = [a for a in reference if a in trace]
        
        if common != ref_common:
            deviations.append("Different order")
        
        return deviations
    
    def _longest_common_subsequence(
        self,
        seq1: List[str],
        seq2: List[str]
    ) -> List[str]:
        """Calculate longest common subsequence."""
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i - 1] == seq2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
        
        # Backtrack to get LCS
        lcs = []
        i, j = m, n
        while i > 0 and j > 0:
            if seq1[i - 1] == seq2[j - 1]:
                lcs.append(seq1[i - 1])
                i -= 1
                j -= 1
            elif dp[i - 1][j] > dp[i][j - 1]:
                i -= 1
            else:
                j -= 1
        
        return lcs[::-1]

