"""
Review Workflow - Translation review and approval workflow.
Part of Feature: Intelligent Translation Hub (v2.0)
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class ReviewStatus(Enum):
    """Review status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


@dataclass
class TranslationReview:
    """A translation review."""
    translation_id: str
    source_text: str
    translated_text: str
    reviewer: str
    status: ReviewStatus
    comments: Optional[str] = None
    reviewed_at: Optional[datetime] = None


class ReviewWorkflow:
    """
    Manages translation review and approval workflow.
    Tracks reviewer feedback and ensures quality.
    """
    
    def __init__(self):
        """Initialize review workflow."""
        self.reviews: Dict[str, TranslationReview] = {}
    
    def submit_for_review(
        self,
        translation_id: str,
        source_text: str,
        translated_text: str
    ) -> str:
        """
        Submit translation for review.
        
        Args:
            translation_id: Unique translation ID
            source_text: Source text
            translated_text: Translated text
            
        Returns:
            Review ID
        """
        review = TranslationReview(
            translation_id=translation_id,
            source_text=source_text,
            translated_text=translated_text,
            reviewer="",
            status=ReviewStatus.PENDING
        )
        
        self.reviews[translation_id] = review
        return translation_id
    
    def review_translation(
        self,
        translation_id: str,
        reviewer: str,
        status: ReviewStatus,
        comments: Optional[str] = None
    ) -> bool:
        """
        Review a translation.
        
        Args:
            translation_id: Translation ID
            reviewer: Reviewer name
            status: Review status
            comments: Optional comments
            
        Returns:
            True if successful
        """
        if translation_id not in self.reviews:
            return False
        
        review = self.reviews[translation_id]
        review.reviewer = reviewer
        review.status = status
        review.comments = comments
        review.reviewed_at = datetime.now()
        
        return True
    
    def get_pending_reviews(self) -> List[TranslationReview]:
        """Get all pending reviews."""
        return [r for r in self.reviews.values() if r.status == ReviewStatus.PENDING]
    
    def get_review(self, translation_id: str) -> Optional[TranslationReview]:
        """Get review by ID."""
        return self.reviews.get(translation_id)

