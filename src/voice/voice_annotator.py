"""
Voice Annotator - Links voice transcriptions to documentation steps.
Part of Feature 7: Voice-First Documentation
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class VoiceAnnotation:
    """A voice annotation linked to a documentation step."""
    id: str
    step_id: str
    text: str
    audio_file: Optional[str]
    timestamp: datetime
    duration: float
    language: str
    annotation_type: str = "narration"  # narration, note, warning, tip
    processed: bool = False
    ai_enhanced_text: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class VoiceAnnotator:
    """
    Manages voice annotations for documentation steps.
    Links transcribed audio to specific steps and enhances text with AI.
    """
    
    def __init__(self, session_id: str, storage_dir: Optional[str] = None):
        """
        Initialize voice annotator.
        
        Args:
            session_id: Current documentation session ID
            storage_dir: Directory for storing annotation data
        """
        self.session_id = session_id
        self.storage_dir = Path(storage_dir) if storage_dir else Path("data/voice_annotations")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self._annotations: Dict[str, VoiceAnnotation] = {}
        self._step_annotations: Dict[str, List[str]] = {}  # step_id -> [annotation_ids]
        self._current_step_id: Optional[str] = None
        
        # Load existing annotations for session
        self._load_annotations()
        
        logger.info(f"VoiceAnnotator initialized for session: {session_id}")
    
    def set_current_step(self, step_id: str) -> None:
        """
        Set the current active step for annotations.
        
        Args:
            step_id: ID of the current step
        """
        self._current_step_id = step_id
        if step_id not in self._step_annotations:
            self._step_annotations[step_id] = []
        logger.debug(f"Current step set to: {step_id}")
    
    def add_annotation(
        self,
        text: str,
        audio_file: Optional[str] = None,
        duration: float = 0.0,
        language: str = "de",
        annotation_type: str = "narration",
        step_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> VoiceAnnotation:
        """
        Add a voice annotation.
        
        Args:
            text: Transcribed text
            audio_file: Path to audio file
            duration: Duration of audio in seconds
            language: Language code
            annotation_type: Type of annotation
            step_id: Step ID (uses current step if not provided)
            metadata: Additional metadata
            
        Returns:
            Created VoiceAnnotation
        """
        step_id = step_id or self._current_step_id
        if not step_id:
            raise ValueError("No step ID provided and no current step set")
        
        annotation_id = f"{self.session_id}_{step_id}_{datetime.now().strftime('%H%M%S%f')}"
        
        annotation = VoiceAnnotation(
            id=annotation_id,
            step_id=step_id,
            text=text,
            audio_file=audio_file,
            timestamp=datetime.now(),
            duration=duration,
            language=language,
            annotation_type=annotation_type,
            metadata=metadata or {}
        )
        
        self._annotations[annotation_id] = annotation
        
        if step_id not in self._step_annotations:
            self._step_annotations[step_id] = []
        self._step_annotations[step_id].append(annotation_id)
        
        logger.info(f"Added voice annotation: {annotation_id} to step {step_id}")
        return annotation
    
    def get_annotations_for_step(self, step_id: str) -> List[VoiceAnnotation]:
        """
        Get all annotations for a specific step.
        
        Args:
            step_id: Step ID
            
        Returns:
            List of VoiceAnnotation objects
        """
        annotation_ids = self._step_annotations.get(step_id, [])
        return [self._annotations[aid] for aid in annotation_ids if aid in self._annotations]
    
    def get_combined_text_for_step(self, step_id: str, use_ai_enhanced: bool = True) -> str:
        """
        Get combined text from all annotations for a step.
        
        Args:
            step_id: Step ID
            use_ai_enhanced: Use AI-enhanced text if available
            
        Returns:
            Combined text string
        """
        annotations = self.get_annotations_for_step(step_id)
        texts = []
        
        for ann in sorted(annotations, key=lambda a: a.timestamp):
            if use_ai_enhanced and ann.ai_enhanced_text:
                texts.append(ann.ai_enhanced_text)
            else:
                texts.append(ann.text)
        
        return " ".join(texts)
    
    def enhance_annotation_with_ai(
        self,
        annotation_id: str,
        ai_client: Any,
        context: Optional[str] = None
    ) -> Optional[str]:
        """
        Enhance annotation text with AI.
        
        Args:
            annotation_id: Annotation ID
            ai_client: OpenAI client instance
            context: Additional context for enhancement
            
        Returns:
            Enhanced text or None if failed
        """
        annotation = self._annotations.get(annotation_id)
        if not annotation:
            logger.warning(f"Annotation not found: {annotation_id}")
            return None
        
        if annotation.processed:
            return annotation.ai_enhanced_text
        
        prompt = f"""Verbessere den folgenden gesprochenen Text für die technische Dokumentation.
Korrigiere Grammatik, entferne Füllwörter und formatiere professionell.
Behalte alle technischen Details und Fachbegriffe bei.

Original: {annotation.text}

{f'Kontext: {context}' if context else ''}

Verbesserter Text:"""
        
        try:
            response = ai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Du bist ein technischer Dokumentationsexperte."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            enhanced_text = response.choices[0].message.content.strip()
            annotation.ai_enhanced_text = enhanced_text
            annotation.processed = True
            
            logger.info(f"Enhanced annotation: {annotation_id}")
            return enhanced_text
        
        except Exception as e:
            logger.error(f"AI enhancement failed: {e}")
            return None
    
    def export_annotations(self, format: str = "json") -> str:
        """
        Export all annotations.
        
        Args:
            format: Export format ('json' or 'markdown')
            
        Returns:
            Exported data as string
        """
        if format == "json":
            data = {
                "session_id": self.session_id,
                "annotations": [
                    {
                        "id": a.id,
                        "step_id": a.step_id,
                        "text": a.text,
                        "ai_enhanced_text": a.ai_enhanced_text,
                        "timestamp": a.timestamp.isoformat(),
                        "duration": a.duration,
                        "language": a.language,
                        "annotation_type": a.annotation_type,
                        "audio_file": a.audio_file
                    }
                    for a in self._annotations.values()
                ]
            }
            return json.dumps(data, indent=2, ensure_ascii=False)
        
        elif format == "markdown":
            lines = [f"# Voice Annotations - Session {self.session_id}\n"]
            
            for step_id in sorted(self._step_annotations.keys()):
                lines.append(f"\n## Step: {step_id}\n")
                for ann in self.get_annotations_for_step(step_id):
                    text = ann.ai_enhanced_text or ann.text
                    lines.append(f"- **{ann.annotation_type}** ({ann.timestamp.strftime('%H:%M:%S')}): {text}")
            
            return "\n".join(lines)
        
        raise ValueError(f"Unsupported format: {format}")
    
    def save(self) -> None:
        """Save annotations to disk."""
        filepath = self.storage_dir / f"{self.session_id}_annotations.json"
        
        data = {
            "session_id": self.session_id,
            "annotations": {
                aid: {
                    "id": a.id,
                    "step_id": a.step_id,
                    "text": a.text,
                    "ai_enhanced_text": a.ai_enhanced_text,
                    "audio_file": a.audio_file,
                    "timestamp": a.timestamp.isoformat(),
                    "duration": a.duration,
                    "language": a.language,
                    "annotation_type": a.annotation_type,
                    "processed": a.processed,
                    "metadata": a.metadata
                }
                for aid, a in self._annotations.items()
            },
            "step_annotations": self._step_annotations
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved annotations to: {filepath}")
    
    def _load_annotations(self) -> None:
        """Load annotations from disk."""
        filepath = self.storage_dir / f"{self.session_id}_annotations.json"
        
        if not filepath.exists():
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._step_annotations = data.get("step_annotations", {})
            
            for aid, adata in data.get("annotations", {}).items():
                self._annotations[aid] = VoiceAnnotation(
                    id=adata["id"],
                    step_id=adata["step_id"],
                    text=adata["text"],
                    ai_enhanced_text=adata.get("ai_enhanced_text"),
                    audio_file=adata.get("audio_file"),
                    timestamp=datetime.fromisoformat(adata["timestamp"]),
                    duration=adata.get("duration", 0.0),
                    language=adata.get("language", "de"),
                    annotation_type=adata.get("annotation_type", "narration"),
                    processed=adata.get("processed", False),
                    metadata=adata.get("metadata", {})
                )
            
            logger.info(f"Loaded {len(self._annotations)} annotations from: {filepath}")
        
        except Exception as e:
            logger.error(f"Failed to load annotations: {e}")

