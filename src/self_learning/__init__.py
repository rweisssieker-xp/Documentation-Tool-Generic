"""
Self-Learning AI Engine - v4.0 P0
Kontinuierliches Lernen aus Nutzer-Interaktionen, Feedback und Dokumentations-Patterns
"""

from .learning_engine import SelfLearningEngine
from .feedback.collector import FeedbackCollector
from .feedback.integrator import FeedbackIntegrator
from .style.transfer import StyleTransfer
from .style.adapter import StyleAdapter
from .patterns.detector import PatternDetector
from .patterns.learner import PatternLearner
from .meta.optimizer import MetaOptimizer

__all__ = [
    'SelfLearningEngine',
    'FeedbackCollector',
    'FeedbackIntegrator',
    'StyleTransfer',
    'StyleAdapter',
    'PatternDetector',
    'PatternLearner',
    'MetaOptimizer',
]
