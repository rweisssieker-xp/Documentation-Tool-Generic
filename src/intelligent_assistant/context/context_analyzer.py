"""Context Analyzer"""

import logging

logger = logging.getLogger(__name__)


class ContextAnalyzer:
    """Analysiert Kontext für Assistant"""
    
    def analyze(self, context: Dict) -> Dict:
        """Analysiert Kontext"""
        return {'intent': 'help'}
