"""
Alt Text Generator - AI-powered alt text generation for images.
Part of Feature: Accessibility Compliance Engine (v2.0)
"""

import os
from typing import Optional, List
from pathlib import Path
from PIL import Image

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from src.utils.logger import get_logger

logger = get_logger(__name__)


class AltTextGenerator:
    """
    Generates descriptive alt text for images using AI.
    Ensures WCAG compliance for image accessibility.
    """
    
    def __init__(self, model: str = "gpt-4o"):
        """
        Initialize alt text generator.
        
        Args:
            model: OpenAI model to use
        """
        if not OPENAI_AVAILABLE:
            logger.warning("OpenAI not available, alt text generation disabled")
            self.client = None
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
            else:
                logger.warning("OPENAI_API_KEY not set, alt text generation disabled")
                self.client = None
        
        self.model = model
    
    def generate_alt_text(
        self,
        image_path: Path,
        context: Optional[str] = None,
        max_length: int = 125
    ) -> str:
        """
        Generate alt text for an image.
        
        Args:
            image_path: Path to image file
            context: Optional context about the image
            max_length: Maximum length of alt text
            
        Returns:
            Generated alt text
        """
        if not self.client:
            return self._generate_basic_alt_text(image_path)
        
        try:
            # Read image
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            
            # Prepare prompt
            prompt = "Describe this image in detail for use as alt text. "
            prompt += "Be specific about what is shown, including text, UI elements, and actions. "
            prompt += f"Keep it under {max_length} characters. "
            
            if context:
                prompt += f"Context: {context}. "
            
            prompt += "Focus on what a visually impaired user needs to know."
            
            # Call Vision API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{self._encode_image(image_data)}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=150
            )
            
            alt_text = response.choices[0].message.content.strip()
            
            # Truncate if too long
            if len(alt_text) > max_length:
                alt_text = alt_text[:max_length-3] + "..."
            
            logger.debug(f"Generated alt text for {image_path.name}: {alt_text[:50]}...")
            return alt_text
        except Exception as e:
            logger.error(f"Error generating alt text: {e}")
            return self._generate_basic_alt_text(image_path)
    
    def generate_alt_texts_batch(
        self,
        image_paths: List[Path],
        contexts: Optional[List[str]] = None
    ) -> List[str]:
        """
        Generate alt texts for multiple images.
        
        Args:
            image_paths: List of image paths
            contexts: Optional list of contexts
            
        Returns:
            List of alt texts
        """
        results = []
        contexts = contexts or [None] * len(image_paths)
        
        for image_path, context in zip(image_paths, contexts):
            alt_text = self.generate_alt_text(image_path, context)
            results.append(alt_text)
        
        return results
    
    def _encode_image(self, image_data: bytes) -> str:
        """Encode image to base64."""
        import base64
        return base64.b64encode(image_data).decode('utf-8')
    
    def _generate_basic_alt_text(self, image_path: Path) -> str:
        """Generate basic alt text without AI."""
        # Try to extract text from filename or use generic description
        name = image_path.stem
        
        # Common patterns
        if "screenshot" in name.lower():
            return f"Screenshot: {name.replace('_', ' ').replace('-', ' ')}"
        elif "step" in name.lower():
            step_num = ''.join(filter(str.isdigit, name))
            return f"Step {step_num} screenshot" if step_num else "Documentation step screenshot"
        else:
            return f"Image: {name.replace('_', ' ').replace('-', ' ')}"

