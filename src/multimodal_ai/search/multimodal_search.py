"""Multimodal search across all content types."""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class MultimodalSearch:
    """Search across all modalities."""
    
    def search(
        self,
        query: str,
        content_index: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search across all modalities.
        
        Args:
            query: Search query
            content_index: Optional pre-built content index
            
        Returns:
            List of search results
        """
        try:
            results = []
            
            if not content_index:
                return results
            
            # Simple text-based search across all modalities
            query_lower = query.lower()
            
            for modality, content in content_index.items():
                if isinstance(content, dict):
                    # Search in text fields
                    for key, value in content.items():
                        if isinstance(value, str) and query_lower in value.lower():
                            results.append({
                                'modality': modality,
                                'field': key,
                                'match': value[:200],  # First 200 chars
                                'relevance': 0.8
                            })
            
            # Sort by relevance
            results.sort(key=lambda x: x.get('relevance', 0), reverse=True)
            
            return results
        except Exception as e:
            logger.error(f"Error in multimodal search: {e}")
            return []
