"""Adaptive UX Engine - v4.2 P0"""

from .ux_engine import AdaptiveUXEngine
from .behavioral.analyzer import BehavioralAnalyzer
from .adaptation.ui_adapter import UIAdapter

__all__ = [
    'AdaptiveUXEngine',
    'BehavioralAnalyzer',
    'UIAdapter',
]
