"""
Mistral LLM Integration
"""

from typing import Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)


class MistralLLM:
    """Mistral LLM Integration"""
    
    def __init__(self, model_path: Optional[str] = None, use_gpu: bool = True):
        """
        Initialize Mistral LLM.
        
        Args:
            model_path: Path to Mistral model
            use_gpu: Use GPU acceleration
        """
        self.model_path = model_path
        self.use_gpu = use_gpu
        self.model = None
        
        try:
            # Try to import transformers
            from transformers import AutoModelForCausalLM, AutoTokenizer
            self.transformers_available = True
            
            if model_path:
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    device_map="auto" if use_gpu else "cpu",
                )
            else:
                logger.warning("No model path provided for Mistral")
        except ImportError:
            logger.warning("transformers not available. Install with: pip install transformers")
            self.transformers_available = False
    
    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text"""
        if not self.model or not self.tokenizer:
            raise RuntimeError("Mistral model not loaded")
        
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt")
            outputs = self.model.generate(
                inputs.input_ids,
                max_length=inputs.input_ids.shape[1] + max_tokens,
                temperature=0.7,
                do_sample=True,
            )
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return generated_text[len(prompt):]
        except Exception as e:
            logger.error(f"Error generating text with Mistral: {e}")
            raise

