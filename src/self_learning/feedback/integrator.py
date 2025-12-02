"""Feedback Integrator - Integriert Feedback in Learning"""

import logging
from typing import Dict, List
from .collector import FeedbackCollector

logger = logging.getLogger(__name__)


class FeedbackIntegrator:
    """Integriert Feedback in Learning-Engine"""
    
    def __init__(self, learning_engine):
        self.learning_engine = learning_engine
        self.feedback_collector = FeedbackCollector()
    
    def integrate_feedback(self, feedback: Dict) -> bool:
        """Integriert Feedback"""
        try:
            feedback_type = feedback.get('type')
            if feedback_type == 'correction':
                return self.learning_engine.learn_from_feedback(feedback)
            elif feedback_type == 'rating':
                return self.learning_engine.learn_from_feedback(feedback)
            return False
        except Exception as e:
            logger.error(f"Error integrating feedback: {e}")
            return False
    
    def integrate_all_pending(self) -> int:
        """Integriert alle ausstehenden Feedbacks"""
        pending = self.feedback_collector.get_pending_feedback()
        integrated = 0
        for feedback in pending:
            if self.integrate_feedback(feedback):
                integrated += 1
        self.feedback_collector.clear_feedback()
        return integrated
