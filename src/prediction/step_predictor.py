"""
Step Predictor - Predicts next documentation steps.
Part of Feature 3: Predictive Documentation Assistant
"""

import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict
from pathlib import Path

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class StepPrediction:
    """A predicted next step."""
    action: str
    description: str
    confidence: float
    based_on: str  # "pattern", "sequence", "ai"
    metadata: Dict[str, Any]


class StepPredictor:
    """
    Predicts next documentation steps based on learned patterns.
    Uses sequence analysis and optional AI enhancement.
    """
    
    def __init__(
        self,
        model_dir: str = "data/prediction_models",
        min_confidence: float = 0.3
    ):
        """
        Initialize step predictor.
        
        Args:
            model_dir: Directory for storing learned patterns
            min_confidence: Minimum confidence threshold
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.min_confidence = min_confidence
        
        # Learned patterns: sequence -> next_step -> count
        self._patterns: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # Application-specific patterns
        self._app_patterns: Dict[str, Dict[str, Dict[str, int]]] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(int))
        )
        
        # Common workflow templates
        self._workflow_templates = self._load_default_templates()
        
        # Load existing patterns
        self._load_patterns()
        
        logger.info("StepPredictor initialized")
    
    def predict_next(
        self,
        current_steps: List[Dict[str, Any]],
        application: Optional[str] = None,
        limit: int = 3
    ) -> List[StepPrediction]:
        """
        Predict next possible steps.
        
        Args:
            current_steps: List of current steps (most recent last)
            application: Current application name
            limit: Maximum number of predictions
            
        Returns:
            List of StepPrediction objects
        """
        predictions = []
        
        # Get recent step sequence
        recent_actions = self._extract_actions(current_steps[-5:])
        sequence_key = "->".join(recent_actions[-3:]) if recent_actions else ""
        
        # Check application-specific patterns
        if application and application in self._app_patterns:
            app_preds = self._predict_from_patterns(
                sequence_key,
                self._app_patterns[application],
                "app_pattern"
            )
            predictions.extend(app_preds)
        
        # Check global patterns
        global_preds = self._predict_from_patterns(
            sequence_key,
            self._patterns,
            "global_pattern"
        )
        predictions.extend(global_preds)
        
        # Check workflow templates
        template_preds = self._predict_from_templates(recent_actions, application)
        predictions.extend(template_preds)
        
        # Deduplicate and sort by confidence
        seen = set()
        unique_predictions = []
        for pred in sorted(predictions, key=lambda p: p.confidence, reverse=True):
            if pred.action not in seen:
                seen.add(pred.action)
                unique_predictions.append(pred)
        
        return unique_predictions[:limit]
    
    def learn_from_session(
        self,
        session_steps: List[Dict[str, Any]],
        application: Optional[str] = None
    ) -> int:
        """
        Learn patterns from a completed session.
        
        Args:
            session_steps: List of session steps
            application: Application name
            
        Returns:
            Number of patterns learned
        """
        patterns_learned = 0
        actions = self._extract_actions(session_steps)
        
        # Learn n-gram patterns (1-3 steps)
        for n in range(1, 4):
            for i in range(len(actions) - n):
                sequence = "->".join(actions[i:i+n])
                next_action = actions[i+n]
                
                # Global pattern
                self._patterns[sequence][next_action] += 1
                patterns_learned += 1
                
                # App-specific pattern
                if application:
                    self._app_patterns[application][sequence][next_action] += 1
                    patterns_learned += 1
        
        # Save updated patterns
        self._save_patterns()
        
        logger.info(f"Learned {patterns_learned} patterns from session")
        return patterns_learned
    
    def suggest_missing_steps(
        self,
        current_steps: List[Dict[str, Any]],
        workflow_type: str = "general"
    ) -> List[StepPrediction]:
        """
        Suggest steps that might be missing.
        
        Args:
            current_steps: Current steps
            workflow_type: Type of workflow
            
        Returns:
            List of suggested missing steps
        """
        suggestions = []
        current_actions = set(self._extract_actions(current_steps))
        
        # Check against workflow templates
        if workflow_type in self._workflow_templates:
            template = self._workflow_templates[workflow_type]
            expected = set(template.get("required_steps", []))
            missing = expected - current_actions
            
            for step in missing:
                suggestions.append(StepPrediction(
                    action=step,
                    description=template.get("step_descriptions", {}).get(step, f"Missing step: {step}"),
                    confidence=0.8,
                    based_on="template",
                    metadata={"template": workflow_type}
                ))
        
        return suggestions
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """Get statistics about learned patterns."""
        total_patterns = sum(len(nexts) for nexts in self._patterns.values())
        total_app_patterns = sum(
            sum(len(nexts) for nexts in app.values())
            for app in self._app_patterns.values()
        )
        
        return {
            "global_patterns": total_patterns,
            "app_specific_patterns": total_app_patterns,
            "applications": list(self._app_patterns.keys()),
            "workflow_templates": list(self._workflow_templates.keys())
        }
    
    def _extract_actions(self, steps: List[Dict[str, Any]]) -> List[str]:
        """Extract action identifiers from steps."""
        actions = []
        for step in steps:
            # Use window title or action type as identifier
            action = step.get("action_type", step.get("window_title", "unknown"))
            if isinstance(action, str):
                # Normalize action name
                action = action.lower().replace(" ", "_")[:50]
                actions.append(action)
        return actions
    
    def _predict_from_patterns(
        self,
        sequence: str,
        patterns: Dict[str, Dict[str, int]],
        source: str
    ) -> List[StepPrediction]:
        """Generate predictions from pattern dictionary."""
        predictions = []
        
        if sequence in patterns:
            next_steps = patterns[sequence]
            total = sum(next_steps.values())
            
            for action, count in next_steps.items():
                confidence = count / total
                if confidence >= self.min_confidence:
                    predictions.append(StepPrediction(
                        action=action,
                        description=f"Predicted: {action}",
                        confidence=confidence,
                        based_on=source,
                        metadata={"count": count, "total": total}
                    ))
        
        return predictions
    
    def _predict_from_templates(
        self,
        recent_actions: List[str],
        application: Optional[str]
    ) -> List[StepPrediction]:
        """Generate predictions from workflow templates."""
        predictions = []
        
        for template_name, template in self._workflow_templates.items():
            # Check if template matches current workflow
            required = template.get("required_steps", [])
            optional = template.get("optional_steps", [])
            
            current_set = set(recent_actions)
            required_set = set(required)
            
            # If we've done some required steps, suggest next
            overlap = current_set & required_set
            if overlap:
                # Find next required step not yet done
                for step in required:
                    if step not in current_set:
                        predictions.append(StepPrediction(
                            action=step,
                            description=template.get("step_descriptions", {}).get(step, step),
                            confidence=0.6,
                            based_on="template",
                            metadata={"template": template_name}
                        ))
                        break
        
        return predictions
    
    def _load_default_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load default workflow templates."""
        return {
            "form_submission": {
                "required_steps": ["open_form", "fill_fields", "validate", "submit", "confirm"],
                "optional_steps": ["upload_file", "preview"],
                "step_descriptions": {
                    "open_form": "Open the form or dialog",
                    "fill_fields": "Fill in required fields",
                    "validate": "Validate input data",
                    "submit": "Submit the form",
                    "confirm": "Confirm submission"
                }
            },
            "data_entry": {
                "required_steps": ["navigate", "open_record", "edit", "save"],
                "optional_steps": ["search", "filter", "export"],
                "step_descriptions": {
                    "navigate": "Navigate to the data section",
                    "open_record": "Open the record for editing",
                    "edit": "Edit the data fields",
                    "save": "Save the changes"
                }
            },
            "report_generation": {
                "required_steps": ["select_report", "configure", "generate", "export"],
                "optional_steps": ["filter_data", "customize_format", "schedule"],
                "step_descriptions": {
                    "select_report": "Select the report type",
                    "configure": "Configure report parameters",
                    "generate": "Generate the report",
                    "export": "Export or print the report"
                }
            }
        }
    
    def _save_patterns(self) -> None:
        """Save learned patterns to disk."""
        data = {
            "patterns": dict(self._patterns),
            "app_patterns": {k: dict(v) for k, v in self._app_patterns.items()}
        }
        
        filepath = self.model_dir / "patterns.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=dict)
    
    def _load_patterns(self) -> None:
        """Load patterns from disk."""
        filepath = self.model_dir / "patterns.json"
        if not filepath.exists():
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for seq, nexts in data.get("patterns", {}).items():
                for action, count in nexts.items():
                    self._patterns[seq][action] = count
            
            for app, patterns in data.get("app_patterns", {}).items():
                for seq, nexts in patterns.items():
                    for action, count in nexts.items():
                        self._app_patterns[app][seq][action] = count
            
            logger.info(f"Loaded patterns from {filepath}")
        
        except Exception as e:
            logger.error(f"Failed to load patterns: {e}")

