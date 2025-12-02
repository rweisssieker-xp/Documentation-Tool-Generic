"""Pattern Learner - Lernt aus Patterns"""

import logging
from typing import Dict, List
from .detector import PatternDetector

logger = logging.getLogger(__name__)


class PatternLearner:
    """Lernt aus erkannten Patterns"""
    
    def __init__(self):
        self.pattern_detector = PatternDetector()
        self.learned_patterns: Dict[str, Dict] = {}
    
    def learn_from_patterns(self, patterns: List[Dict]) -> bool:
        """Lernt aus Patterns"""
        try:
            for pattern in patterns:
                pattern_type = pattern.get('type', 'default')
                if pattern_type not in self.learned_patterns:
                    self.learned_patterns[pattern_type] = {
                        'count': 0,
                        'examples': []
                    }
                self.learned_patterns[pattern_type]['count'] += 1
                self.learned_patterns[pattern_type]['examples'].append(pattern)
            return True
        except Exception as e:
            logger.error(f"Error learning from patterns: {e}")
            return False
