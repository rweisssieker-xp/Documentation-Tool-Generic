"""
Metrics Collector - Collects documentation metrics.
Part of Feature: Documentation ROI Dashboard (v2.0)
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DocumentationMetrics:
    """Documentation metrics."""
    timestamp: datetime
    session_id: str
    steps_count: int
    screenshots_count: int
    duration_seconds: float
    manual_time_estimate: float  # Estimated manual documentation time
    ai_time_saved: float  # Time saved by using AI
    quality_score: float  # 0-100
    completeness_score: float  # 0-100


@dataclass
class UsageMetrics:
    """Usage metrics."""
    views: int
    downloads: int
    searches: int
    last_accessed: Optional[datetime]


class MetricsCollector:
    """
    Collects metrics about documentation creation and usage.
    Tracks efficiency, quality, and ROI indicators.
    """
    
    def __init__(self, storage_dir: Path = Path("data/analytics")):
        """
        Initialize metrics collector.
        
        Args:
            storage_dir: Directory for storing metrics
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics_file = self.storage_dir / "metrics.json"
        self._metrics: List[Dict[str, Any]] = []
        self._load_metrics()
    
    def _load_metrics(self):
        """Load metrics from storage."""
        if self.metrics_file.exists():
            try:
                self._metrics = json.loads(self.metrics_file.read_text(encoding='utf-8'))
            except Exception as e:
                logger.warning(f"Could not load metrics: {e}")
                self._metrics = []
    
    def _save_metrics(self):
        """Save metrics to storage."""
        try:
            self.metrics_file.write_text(
                json.dumps(self._metrics, indent=2, default=str, ensure_ascii=False),
                encoding='utf-8'
            )
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
    
    def record_session_metrics(self, metrics: DocumentationMetrics):
        """
        Record metrics for a documentation session.
        
        Args:
            metrics: Documentation metrics
        """
        data = asdict(metrics)
        data['timestamp'] = metrics.timestamp.isoformat()
        self._metrics.append(data)
        self._save_metrics()
        logger.debug(f"Recorded metrics for session {metrics.session_id}")
    
    def calculate_time_saved(self, session_id: str) -> float:
        """
        Calculate time saved for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Time saved in hours
        """
        for metric in self._metrics:
            if metric.get('session_id') == session_id:
                return metric.get('ai_time_saved', 0) / 3600  # Convert to hours
        return 0.0
    
    def get_total_time_saved(self, days: Optional[int] = None) -> Dict[str, float]:
        """
        Get total time saved across all sessions.
        
        Args:
            days: Optional number of days to look back
            
        Returns:
            Dictionary with time saved metrics
        """
        cutoff = None
        if days:
            cutoff = datetime.now() - timedelta(days=days)
        
        total_saved = 0.0
        total_manual = 0.0
        session_count = 0
        
        for metric in self._metrics:
            if cutoff:
                metric_time = datetime.fromisoformat(metric['timestamp']) if isinstance(metric['timestamp'], str) else metric['timestamp']
                if metric_time < cutoff:
                    continue
            
            total_saved += metric.get('ai_time_saved', 0)
            total_manual += metric.get('manual_time_estimate', 0)
            session_count += 1
        
        return {
            'total_time_saved_hours': total_saved / 3600,
            'total_manual_hours': total_manual / 3600,
            'session_count': session_count,
            'avg_time_saved_per_session': (total_saved / session_count / 3600) if session_count > 0 else 0
        }
    
    def get_quality_trends(self, days: int = 30) -> Dict[str, List[float]]:
        """
        Get quality score trends.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with quality trends
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        quality_scores = []
        completeness_scores = []
        
        for metric in self._metrics:
            metric_time = datetime.fromisoformat(metric['timestamp']) if isinstance(metric['timestamp'], str) else metric['timestamp']
            if metric_time >= cutoff:
                quality_scores.append(metric.get('quality_score', 0))
                completeness_scores.append(metric.get('completeness_score', 0))
        
        return {
            'quality_scores': quality_scores,
            'completeness_scores': completeness_scores,
            'avg_quality': sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            'avg_completeness': sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0
        }
    
    def get_efficiency_metrics(self) -> Dict[str, Any]:
        """
        Get efficiency metrics.
        
        Returns:
            Dictionary with efficiency metrics
        """
        if not self._metrics:
            return {
                'total_sessions': 0,
                'total_steps': 0,
                'total_screenshots': 0,
                'avg_steps_per_session': 0,
                'avg_duration_per_session': 0
            }
        
        total_sessions = len(self._metrics)
        total_steps = sum(m.get('steps_count', 0) for m in self._metrics)
        total_screenshots = sum(m.get('screenshots_count', 0) for m in self._metrics)
        total_duration = sum(m.get('duration_seconds', 0) for m in self._metrics)
        
        return {
            'total_sessions': total_sessions,
            'total_steps': total_steps,
            'total_screenshots': total_screenshots,
            'avg_steps_per_session': total_steps / total_sessions if total_sessions > 0 else 0,
            'avg_duration_per_session': total_duration / total_sessions if total_sessions > 0 else 0,
            'avg_screenshots_per_session': total_screenshots / total_sessions if total_sessions > 0 else 0
        }

