"""Model Aggregator"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class ModelAggregator:
    """Aggregiert Models von Teilnehmern"""
    
    def aggregate(self, models: List[Dict]) -> Dict:
        """Aggregiert Models"""
        return {'aggregated': True}
