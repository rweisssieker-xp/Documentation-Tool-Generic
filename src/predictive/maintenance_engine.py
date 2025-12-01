"""
Predictive Maintenance Engine - Zentrale Maintenance Engine
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from .code_analysis.ast_parser import ASTParser
from .code_analysis.diff_detector import DiffDetector
from .ui_analysis.screenshot_diff import ScreenshotDiff
from .ml_models.drift_detector import DriftDetector
from .notifications.alert_system import AlertSystem
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PredictiveMaintenanceEngine:
    """Predictive Maintenance Engine"""
    
    def __init__(self):
        """Initialize Predictive Maintenance Engine"""
        self.ast_parser = ASTParser()
        self.diff_detector = DiffDetector()
        self.screenshot_diff = ScreenshotDiff()
        self.drift_detector = DriftDetector()
        self.alert_system = AlertSystem()
    
    def analyze_documentation(self, session_id: str) -> List[Dict[str, Any]]:
        """Analyze documentation for outdated content"""
        issues = []
        
        try:
            # Analyze code changes
            code_issues = self.diff_detector.detect_changes(session_id)
            issues.extend(code_issues)
            
            # Analyze UI changes
            ui_issues = self.screenshot_diff.detect_drift(session_id)
            issues.extend(ui_issues)
            
            # ML-based drift detection
            ml_issues = self.drift_detector.detect_drift(session_id)
            issues.extend(ml_issues)
            
            # Score and prioritize issues
            prioritized_issues = self._prioritize_issues(issues)
            
            return prioritized_issues
        except Exception as e:
            logger.error(f"Error analyzing documentation: {e}")
            return []
    
    def _prioritize_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize issues by severity"""
        # Simple prioritization based on type and confidence
        for issue in issues:
            priority = 0
            
            if issue.get('type') == 'code_change':
                priority += 10
            elif issue.get('type') == 'ui_change':
                priority += 5
            
            priority += issue.get('confidence', 0) * 0.1
            issue['priority'] = priority
        
        return sorted(issues, key=lambda x: x.get('priority', 0), reverse=True)
    
    def send_alerts(self, issues: List[Dict[str, Any]]):
        """Send alerts for high-priority issues"""
        high_priority = [i for i in issues if i.get('priority', 0) > 5]
        
        if high_priority:
            self.alert_system.send_alerts(high_priority)

