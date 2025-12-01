"""Question Engine - Interactive clarification for agent"""

import os
from typing import Optional, List

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from src.utils.logger import get_logger

logger = get_logger(__name__)


class QuestionEngine:
    """Generates clarifying questions when agent is uncertain."""
    
    def __init__(self, model: str = "gpt-4o"):
        """Initialize question engine."""
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
            else:
                self.client = None
        else:
            self.client = None
        
        self.model = model
    
    def generate_question(self, context: str, uncertainty: str) -> Optional[str]:
        """Generate clarifying question."""
        if not self.client:
            return None
        
        try:
            prompt = f"""Context: {context}
Uncertainty: {uncertainty}

Generate a clear, specific question to clarify this uncertainty.
Return only the question."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating question: {e}")
            return None

