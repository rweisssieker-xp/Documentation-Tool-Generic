"""Feedback Collector - Sammelt Nutzer-Feedback"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class FeedbackCollector:
    """Sammelt Feedback von Nutzern"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("data/feedback")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.feedback_queue: List[Dict] = []
    
    def collect_feedback(self, feedback_type: str, data: Dict) -> bool:
        """Sammelt Feedback"""
        feedback = {
            'type': feedback_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        self.feedback_queue.append(feedback)
        logger.info(f"Collected feedback: {feedback_type}")
        return True
    
    def collect_correction(self, original: str, corrected: str, context: Dict) -> bool:
        """Sammelt Korrekturen"""
        return self.collect_feedback('correction', {
            'original': original,
            'corrected': corrected,
            'context': context
        })
    
    def collect_rating(self, rating: int, content_id: str, comment: Optional[str] = None) -> bool:
        """Sammelt Ratings"""
        return self.collect_feedback('rating', {
            'rating': rating,
            'content_id': content_id,
            'comment': comment
        })
    
    def get_pending_feedback(self) -> List[Dict]:
        """Gibt ausstehendes Feedback zurück"""
        return self.feedback_queue.copy()
    
    def clear_feedback(self) -> None:
        """Löscht Feedback-Queue"""
        self.feedback_queue.clear()
