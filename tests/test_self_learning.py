"""Tests für Self-Learning AI Engine"""

import pytest
from src.self_learning import SelfLearningEngine, FeedbackCollector


def test_learning_engine_init():
    """Test Learning Engine Initialisierung"""
    engine = SelfLearningEngine()
    assert engine is not None
    assert engine.learning_rate == 0.001


def test_learn_from_interaction():
    """Test Lernen aus Interaktion"""
    engine = SelfLearningEngine()
    interaction = {'type': 'documentation', 'sequence': ['step1', 'step2']}
    result = engine.learn_from_interaction(interaction)
    assert result is True


def test_feedback_collector():
    """Test Feedback Collector"""
    collector = FeedbackCollector()
    result = collector.collect_feedback('correction', {'data': 'test'})
    assert result is True
    assert len(collector.feedback_queue) == 1
