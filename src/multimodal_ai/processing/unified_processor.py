"""Unified processor for multimodal content."""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class UnifiedProcessor:
    """Processes multimodal content into unified documentation."""
    
    def process(
        self,
        encoded_content: Dict[str, Any],
        relationships: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process encoded content and relationships into unified documentation.
        
        Args:
            encoded_content: Encoded content from all modalities
            relationships: Cross-modal relationships
            
        Returns:
            Unified documentation dictionary
        """
        try:
            unified_doc = {
                'title': self._extract_title(encoded_content),
                'sections': [],
                'modalities': list(encoded_content.keys()),
                'relationships': relationships,
                'metadata': {}
            }
            
            # Process each modality into sections
            if 'text' in encoded_content:
                unified_doc['sections'].append({
                    'type': 'text',
                    'content': encoded_content['text'].get('content', '')
                })
            
            if 'video' in encoded_content:
                unified_doc['sections'].append({
                    'type': 'video',
                    'path': encoded_content['video'].get('path', ''),
                    'transcript': encoded_content['video'].get('transcript', '')
                })
            
            if 'audio' in encoded_content:
                unified_doc['sections'].append({
                    'type': 'audio',
                    'path': encoded_content['audio'].get('path', ''),
                    'transcript': encoded_content['audio'].get('transcript', '')
                })
            
            if 'code' in encoded_content:
                unified_doc['sections'].append({
                    'type': 'code',
                    'content': encoded_content['code'].get('content', ''),
                    'language': encoded_content['code'].get('language', '')
                })
            
            if 'images' in encoded_content:
                unified_doc['sections'].extend([
                    {
                        'type': 'image',
                        'path': img.get('path', ''),
                        'ocr_text': img.get('ocr_text', '')
                    }
                    for img in encoded_content['images']
                ])
            
            return unified_doc
        except Exception as e:
            logger.error(f"Error in unified processing: {e}")
            return {'error': str(e)}
    
    def _extract_title(self, content: Dict[str, Any]) -> str:
        """Extract title from content."""
        if 'text' in content:
            text = content['text'].get('content', '')
            # Simple title extraction - first line or first sentence
            lines = text.split('\n')
            if lines:
                return lines[0][:100]  # First 100 chars
        return 'Untitled Documentation'
