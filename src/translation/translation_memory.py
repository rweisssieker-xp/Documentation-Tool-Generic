"""
Translation Memory - Stores and retrieves previous translations.
Part of Feature: Intelligent Translation Hub (v2.0)
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TranslationUnit:
    """A translation unit (source + target)."""
    source_text: str
    target_text: str
    source_language: str
    target_language: str
    context: Optional[str] = None
    quality_score: float = 1.0  # 0-1
    usage_count: int = 1
    created_at: Optional[datetime] = None
    last_used: Optional[datetime] = None


class TranslationMemory:
    """
    Translation Memory (TM) for storing and reusing translations.
    Improves consistency and reduces translation costs.
    """
    
    def __init__(self, storage_dir: Path = Path("data/translation/memory")):
        """
        Initialize translation memory.
        
        Args:
            storage_dir: Directory for storing TM
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.memory_file = self.storage_dir / "tm.json"
        self._memory: Dict[str, TranslationUnit] = {}  # hash -> TranslationUnit
        self._load_memory()
    
    def _load_memory(self):
        """Load translation memory from storage."""
        if self.memory_file.exists():
            try:
                data = json.loads(self.memory_file.read_text(encoding='utf-8'))
                for unit_data in data.get('units', []):
                    unit = TranslationUnit(**unit_data)
                    # Convert datetime strings
                    if isinstance(unit.created_at, str):
                        unit.created_at = datetime.fromisoformat(unit.created_at)
                    if isinstance(unit.last_used, str):
                        unit.last_used = datetime.fromisoformat(unit.last_used)
                    
                    key = self._hash_text(unit.source_text, unit.source_language, unit.target_language)
                    self._memory[key] = unit
                logger.info(f"Loaded {len(self._memory)} translation units")
            except Exception as e:
                logger.warning(f"Could not load translation memory: {e}")
    
    def _save_memory(self):
        """Save translation memory to storage."""
        try:
            units_data = []
            for unit in self._memory.values():
                unit_dict = asdict(unit)
                if unit_dict.get('created_at'):
                    unit_dict['created_at'] = unit.created_at.isoformat() if isinstance(unit.created_at, datetime) else unit_dict['created_at']
                if unit_dict.get('last_used'):
                    unit_dict['last_used'] = unit.last_used.isoformat() if isinstance(unit.last_used, datetime) else unit_dict['last_used']
                units_data.append(unit_dict)
            
            self.memory_file.write_text(
                json.dumps({'units': units_data}, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
        except Exception as e:
            logger.error(f"Error saving translation memory: {e}")
    
    def _hash_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """Generate hash for text."""
        content = f"{source_lang}:{target_lang}:{text.lower().strip()}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def add_translation(
        self,
        source_text: str,
        target_text: str,
        source_language: str,
        target_language: str,
        context: Optional[str] = None,
        quality_score: float = 1.0
    ):
        """
        Add translation to memory.
        
        Args:
            source_text: Source text
            target_text: Translated text
            source_language: Source language code
            target_language: Target language code
            context: Optional context
            quality_score: Quality score (0-1)
        """
        key = self._hash_text(source_text, source_language, target_language)
        
        if key in self._memory:
            # Update existing
            unit = self._memory[key]
            unit.target_text = target_text  # Update translation
            unit.usage_count += 1
            unit.last_used = datetime.now()
            if context:
                unit.context = context
            unit.quality_score = max(unit.quality_score, quality_score)
        else:
            # Create new
            unit = TranslationUnit(
                source_text=source_text,
                target_text=target_text,
                source_language=source_language,
                target_language=target_language,
                context=context,
                quality_score=quality_score,
                created_at=datetime.now(),
                last_used=datetime.now()
            )
            self._memory[key] = unit
        
        self._save_memory()
        logger.debug(f"Added translation to TM: {source_text[:50]}...")
    
    def find_translation(
        self,
        source_text: str,
        source_language: str,
        target_language: str,
        min_quality: float = 0.7
    ) -> Optional[TranslationUnit]:
        """
        Find translation in memory.
        
        Args:
            source_text: Source text
            source_language: Source language
            target_language: Target language
            min_quality: Minimum quality score
            
        Returns:
            TranslationUnit or None
        """
        key = self._hash_text(source_text, source_language, target_language)
        
        unit = self._memory.get(key)
        if unit and unit.quality_score >= min_quality:
            unit.last_used = datetime.now()
            unit.usage_count += 1
            self._save_memory()
            return unit
        
        return None
    
    def find_fuzzy_match(
        self,
        source_text: str,
        source_language: str,
        target_language: str,
        similarity_threshold: float = 0.8
    ) -> List[Tuple[TranslationUnit, float]]:
        """
        Find fuzzy matches in translation memory.
        
        Args:
            source_text: Source text
            source_language: Source language
            target_language: Target language
            similarity_threshold: Minimum similarity (0-1)
            
        Returns:
            List of (TranslationUnit, similarity) tuples
        """
        matches = []
        source_lower = source_text.lower().strip()
        
        for unit in self._memory.values():
            if unit.source_language == source_language and unit.target_language == target_language:
                similarity = self._calculate_similarity(source_lower, unit.source_text.lower())
                if similarity >= similarity_threshold:
                    matches.append((unit, similarity))
        
        # Sort by similarity
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity (simple word overlap)."""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get translation memory statistics."""
        total_units = len(self._memory)
        total_usage = sum(unit.usage_count for unit in self._memory.values())
        avg_quality = sum(unit.quality_score for unit in self._memory.values()) / total_units if total_units > 0 else 0
        
        return {
            'total_units': total_units,
            'total_usage': total_usage,
            'avg_quality': avg_quality,
            'avg_usage_per_unit': total_usage / total_units if total_units > 0 else 0
        }

