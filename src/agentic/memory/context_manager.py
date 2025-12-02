"""Context Manager - Verwaltet Agent-Kontext"""

import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ContextManager:
    """Verwaltet Kontext für Agents"""
    
    def __init__(self):
        self.contexts: Dict[str, Dict] = {}
    
    def store_context(self, agent_id: str, context: Dict) -> bool:
        """Speichert Kontext"""
        self.contexts[agent_id] = {
            'data': context,
            'timestamp': datetime.now().isoformat()
        }
        return True
    
    def get_context(self, agent_id: str) -> Optional[Dict]:
        """Gibt Kontext zurück"""
        return self.contexts.get(agent_id, {}).get('data')
