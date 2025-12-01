"""
Edge AI Engine - On-Device AI ohne Cloud
"""

from .engine import EdgeAIEngine
from .llm.llama import LlamaLLM
from .llm.mistral import MistralLLM
from .whisper.local_whisper import LocalWhisper
from .embeddings.local_embeddings import LocalEmbeddings
from .models.manager import ModelManager

__all__ = [
    'EdgeAIEngine',
    'LlamaLLM',
    'MistralLLM',
    'LocalWhisper',
    'LocalEmbeddings',
    'ModelManager',
]

