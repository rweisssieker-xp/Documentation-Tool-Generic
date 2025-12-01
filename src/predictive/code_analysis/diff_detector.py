"""
Diff Detector - Erkennt Code-Änderungen
"""

from typing import List, Dict, Any
from pathlib import Path
import difflib

from src.utils.logger import get_logger

logger = get_logger(__name__)


class DiffDetector:
    """Diff Detector"""
    
    def detect_changes(self, session_id: str) -> List[Dict[str, Any]]:
        """Detect code changes that might affect documentation"""
        issues = []
        
        # Placeholder implementation
        # In production, this would compare current code with code at documentation time
        
        logger.info(f"Detecting code changes for session: {session_id}")
        
        return issues
    
    def compare_files(self, file1: str, file2: str) -> List[str]:
        """Compare two files"""
        try:
            with open(file1, 'r', encoding='utf-8') as f1:
                lines1 = f1.readlines()
            with open(file2, 'r', encoding='utf-8') as f2:
                lines2 = f2.readlines()
            
            diff = list(difflib.unified_diff(lines1, lines2, lineterm=''))
            return diff
        except Exception as e:
            logger.error(f"Error comparing files: {e}")
            return []

