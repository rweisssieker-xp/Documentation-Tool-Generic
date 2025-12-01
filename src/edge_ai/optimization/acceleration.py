"""
GPU/TPU Acceleration - Hardware acceleration for inference
"""

from typing import Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GPUAccelerator:
    """GPU/TPU Accelerator"""
    
    def __init__(self):
        """Initialize GPU Accelerator"""
        self.has_gpu = self._check_gpu()
        logger.info(f"GPU Accelerator initialized (GPU: {self.has_gpu})")
    
    def _check_gpu(self) -> bool:
        """Check if GPU is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def accelerate(self, model, use_gpu: bool = True):
        """Move model to GPU if available"""
        if use_gpu and self.has_gpu:
            try:
                import torch
                return model.cuda()
            except Exception as e:
                logger.warning(f"GPU acceleration failed: {e}")
        return model
