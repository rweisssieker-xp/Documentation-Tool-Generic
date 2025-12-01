"""
Model Optimization - Quantization and Acceleration
"""

from .quantization import ModelQuantizer
from .acceleration import GPUAccelerator

__all__ = ['ModelQuantizer', 'GPUAccelerator']
