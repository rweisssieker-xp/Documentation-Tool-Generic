"""
Edge AI Engine - On-Device AI ohne Cloud
"""

from .engine import EdgeAIEngine, ModelType
from .llm.llama import LlamaLLM
from .llm.mistral import MistralLLM
from .llm.phi import PhiLLM
from .whisper.local_whisper import LocalWhisper
from .embeddings.local_embeddings import LocalEmbeddings
from .models.manager import ModelManager
from .models.downloader import ModelDownloader
from .optimization.quantization import ModelQuantizer
from .optimization.acceleration import GPUAccelerator
from .hybrid.fallback import CloudFallback

__all__ = [
    'EdgeAIEngine',
    'ModelType',
    'LlamaLLM',
    'MistralLLM',
    'PhiLLM',
    'LocalWhisper',
    'LocalEmbeddings',
    'ModelManager',
    'ModelDownloader',
    'ModelQuantizer',
    'GPUAccelerator',
    'CloudFallback',
]

