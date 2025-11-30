"""
Gap Analyzer - Identifies missing steps in documentation.
Part of Feature 3: Predictive Documentation Assistant
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum

from src.utils.logger import get_logger

logger = get_logger(__name__)


class GapSeverity(Enum):
    """Severity of documentation gap."""
    CRITICAL = "critical"  # Must be fixed
    WARNING = "warning"    # Should be addressed
    INFO = "info"          # Nice to have


@dataclass
class DocumentationGap:
    """Identified documentation gap."""
    gap_type: str
    description: str
    severity: GapSeverity
    suggestion: str
    affected_steps: List[str]
    metadata: Dict[str, Any]


class GapAnalyzer:
    """
    Analyzes documentation for completeness and identifies gaps.
    """
    
    # Standard documentation elements
    REQUIRED_ELEMENTS = {
        "prerequisites": "Voraussetzungen / Prerequisites",
        "expected_result": "Erwartetes Ergebnis / Expected Result",
        "error_handling": "Fehlerbehandlung / Error Handling"
    }
    
    # Step quality indicators
    QUALITY_CHECKS = [
        ("has_screenshot", "Step should have a screenshot"),
        ("has_description", "Step should have a description"),
        ("has_action", "Step should describe an action"),
    ]
    
    def __init__(self, ai_client: Optional[Any] = None):
        """
        Initialize gap analyzer.
        
        Args:
            ai_client: Optional OpenAI client for AI-powered analysis
        """
        self.ai_client = ai_client
        
        logger.info("GapAnalyzer initialized")
    
    def analyze_session(
        self,
        session_data: Dict[str, Any],
        check_completeness: bool = True,
        check_quality: bool = True,
        check_flow: bool = True
    ) -> List[DocumentationGap]:
        """
        Analyze a session for documentation gaps.
        
        Args:
            session_data: Session data to analyze
            check_completeness: Check for missing elements
            check_quality: Check step quality
            check_flow: Check logical flow
            
        Returns:
            List of identified gaps
        """
        gaps = []
        steps = session_data.get("steps", [])
        
        if check_completeness:
            gaps.extend(self._check_completeness(session_data))
        
        if check_quality:
            gaps.extend(self._check_step_quality(steps))
        
        if check_flow:
            gaps.extend(self._check_flow(steps))
        
        # Sort by severity
        severity_order = {GapSeverity.CRITICAL: 0, GapSeverity.WARNING: 1, GapSeverity.INFO: 2}
        gaps.sort(key=lambda g: severity_order[g.severity])
        
        logger.info(f"Analyzed session: {len(gaps)} gaps found")
        return gaps
    
    def analyze_steps(
        self,
        steps: List[Dict[str, Any]],
        context: Optional[str] = None
    ) -> List[DocumentationGap]:
        """
        Analyze steps for gaps.
        
        Args:
            steps: List of documentation steps
            context: Optional workflow context
            
        Returns:
            List of gaps
        """
        gaps = []
        
        gaps.extend(self._check_step_quality(steps))
        gaps.extend(self._check_flow(steps))
        
        if context and self.ai_client:
            gaps.extend(self._ai_analyze_context(steps, context))
        
        return gaps
    
    def suggest_improvements(
        self,
        gaps: List[DocumentationGap]
    ) -> Dict[str, List[str]]:
        """
        Generate improvement suggestions for identified gaps.
        
        Args:
            gaps: List of gaps to address
            
        Returns:
            Dictionary of category -> suggestions
        """
        suggestions = {
            "critical": [],
            "quality": [],
            "flow": [],
            "enhancement": []
        }
        
        for gap in gaps:
            if gap.severity == GapSeverity.CRITICAL:
                suggestions["critical"].append(gap.suggestion)
            elif gap.gap_type in ["missing_screenshot", "missing_description"]:
                suggestions["quality"].append(gap.suggestion)
            elif gap.gap_type in ["logical_jump", "missing_transition"]:
                suggestions["flow"].append(gap.suggestion)
            else:
                suggestions["enhancement"].append(gap.suggestion)
        
        return suggestions
    
    def get_completeness_score(
        self,
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate completeness score for a session.
        
        Args:
            session_data: Session data
            
        Returns:
            Completeness metrics
        """
        steps = session_data.get("steps", [])
        
        # Count elements
        total_steps = len(steps)
        steps_with_screenshots = sum(1 for s in steps if s.get("screenshot"))
        steps_with_descriptions = sum(1 for s in steps if s.get("description"))
        steps_with_actions = sum(1 for s in steps if s.get("action_type"))
        
        # Calculate scores
        screenshot_score = steps_with_screenshots / total_steps if total_steps else 0
        description_score = steps_with_descriptions / total_steps if total_steps else 0
        action_score = steps_with_actions / total_steps if total_steps else 0
        
        # Overall score
        overall = (screenshot_score + description_score + action_score) / 3
        
        return {
            "overall_score": round(overall * 100, 1),
            "screenshot_coverage": round(screenshot_score * 100, 1),
            "description_coverage": round(description_score * 100, 1),
            "action_coverage": round(action_score * 100, 1),
            "total_steps": total_steps,
            "quality_level": self._get_quality_level(overall)
        }
    
    def _check_completeness(
        self,
        session_data: Dict[str, Any]
    ) -> List[DocumentationGap]:
        """Check for missing required elements."""
        gaps = []
        steps = session_data.get("steps", [])
        
        # Check for empty session
        if not steps:
            gaps.append(DocumentationGap(
                gap_type="empty_session",
                description="Session has no steps",
                severity=GapSeverity.CRITICAL,
                suggestion="Add documentation steps to the session",
                affected_steps=[],
                metadata={}
            ))
            return gaps
        
        # Check first step (usually should have context)
        first_step = steps[0] if steps else {}
        if not first_step.get("description") or len(first_step.get("description", "")) < 20:
            gaps.append(DocumentationGap(
                gap_type="missing_introduction",
                description="First step lacks sufficient introduction/context",
                severity=GapSeverity.WARNING,
                suggestion="Add an introduction describing the workflow purpose",
                affected_steps=[first_step.get("id", "step_1")],
                metadata={}
            ))
        
        # Check last step (should have conclusion/result)
        last_step = steps[-1] if steps else {}
        if not self._has_conclusion_keywords(last_step.get("description", "")):
            gaps.append(DocumentationGap(
                gap_type="missing_conclusion",
                description="Last step lacks clear conclusion/expected result",
                severity=GapSeverity.WARNING,
                suggestion="Add a conclusion describing the expected outcome",
                affected_steps=[last_step.get("id", f"step_{len(steps)}")],
                metadata={}
            ))
        
        return gaps
    
    def _check_step_quality(
        self,
        steps: List[Dict[str, Any]]
    ) -> List[DocumentationGap]:
        """Check quality of individual steps."""
        gaps = []
        
        for i, step in enumerate(steps):
            step_id = step.get("id", f"step_{i+1}")
            
            # Check for screenshot
            if not step.get("screenshot"):
                gaps.append(DocumentationGap(
                    gap_type="missing_screenshot",
                    description=f"Step {i+1} has no screenshot",
                    severity=GapSeverity.WARNING,
                    suggestion=f"Add a screenshot to step {i+1}",
                    affected_steps=[step_id],
                    metadata={"step_index": i}
                ))
            
            # Check for description
            desc = step.get("description", "")
            if not desc or len(desc) < 10:
                gaps.append(DocumentationGap(
                    gap_type="missing_description",
                    description=f"Step {i+1} has no or minimal description",
                    severity=GapSeverity.WARNING,
                    suggestion=f"Add a detailed description to step {i+1}",
                    affected_steps=[step_id],
                    metadata={"step_index": i}
                ))
            
            # Check for action verb
            if desc and not self._has_action_verb(desc):
                gaps.append(DocumentationGap(
                    gap_type="passive_description",
                    description=f"Step {i+1} description lacks clear action",
                    severity=GapSeverity.INFO,
                    suggestion=f"Use action verbs (Click, Enter, Select) in step {i+1}",
                    affected_steps=[step_id],
                    metadata={"step_index": i}
                ))
        
        return gaps
    
    def _check_flow(
        self,
        steps: List[Dict[str, Any]]
    ) -> List[DocumentationGap]:
        """Check logical flow between steps."""
        gaps = []
        
        for i in range(1, len(steps)):
            prev_step = steps[i-1]
            curr_step = steps[i]
            
            # Check for large time gaps
            prev_time = prev_step.get("timestamp")
            curr_time = curr_step.get("timestamp")
            
            if prev_time and curr_time:
                try:
                    # Simple time gap check (if timestamps are comparable)
                    pass  # Would need proper datetime parsing
                except:
                    pass
            
            # Check for window context jumps
            prev_window = prev_step.get("window_title", "")
            curr_window = curr_step.get("window_title", "")
            
            if prev_window and curr_window and prev_window != curr_window:
                # Check if transition is explained
                desc = curr_step.get("description", "")
                if not self._mentions_navigation(desc):
                    gaps.append(DocumentationGap(
                        gap_type="unexplained_context_switch",
                        description=f"Unexplained switch from '{prev_window}' to '{curr_window}'",
                        severity=GapSeverity.INFO,
                        suggestion=f"Add navigation explanation between steps {i} and {i+1}",
                        affected_steps=[
                            prev_step.get("id", f"step_{i}"),
                            curr_step.get("id", f"step_{i+1}")
                        ],
                        metadata={"from": prev_window, "to": curr_window}
                    ))
        
        return gaps
    
    def _ai_analyze_context(
        self,
        steps: List[Dict[str, Any]],
        context: str
    ) -> List[DocumentationGap]:
        """Use AI to analyze context-specific gaps."""
        if not self.ai_client:
            return []
        
        gaps = []
        
        # Build step summary
        step_summary = "\n".join([
            f"{i+1}. {s.get('description', 'No description')}"
            for i, s in enumerate(steps)
        ])
        
        prompt = f"""Analysiere die folgende Dokumentation auf Vollständigkeit und Lücken.

Kontext: {context}

Schritte:
{step_summary}

Identifiziere fehlende oder unklare Schritte. Antworte im JSON-Format:
[{{"gap": "Beschreibung", "severity": "critical/warning/info", "suggestion": "Vorschlag"}}]"""
        
        try:
            response = self.ai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            for item in result:
                gaps.append(DocumentationGap(
                    gap_type="ai_identified",
                    description=item.get("gap", ""),
                    severity=GapSeverity[item.get("severity", "info").upper()],
                    suggestion=item.get("suggestion", ""),
                    affected_steps=[],
                    metadata={"source": "ai_analysis"}
                ))
        
        except Exception as e:
            logger.warning(f"AI analysis failed: {e}")
        
        return gaps
    
    def _has_conclusion_keywords(self, text: str) -> bool:
        """Check if text contains conclusion keywords."""
        keywords = [
            "complete", "done", "finish", "success", "confirm", "result",
            "abgeschlossen", "fertig", "erfolgreich", "bestätigt", "ergebnis"
        ]
        text_lower = text.lower()
        return any(kw in text_lower for kw in keywords)
    
    def _has_action_verb(self, text: str) -> bool:
        """Check if text contains action verbs."""
        action_verbs = [
            "click", "enter", "select", "choose", "type", "press", "open", "close",
            "klicken", "eingeben", "auswählen", "wählen", "tippen", "drücken", "öffnen", "schließen"
        ]
        text_lower = text.lower()
        return any(verb in text_lower for verb in action_verbs)
    
    def _mentions_navigation(self, text: str) -> bool:
        """Check if text mentions navigation."""
        nav_words = [
            "navigate", "go to", "switch", "open", "move",
            "navigieren", "wechseln", "öffnen", "gehen"
        ]
        text_lower = text.lower()
        return any(word in text_lower for word in nav_words)
    
    def _get_quality_level(self, score: float) -> str:
        """Get quality level from score."""
        if score >= 0.9:
            return "excellent"
        elif score >= 0.7:
            return "good"
        elif score >= 0.5:
            return "acceptable"
        else:
            return "needs_improvement"

