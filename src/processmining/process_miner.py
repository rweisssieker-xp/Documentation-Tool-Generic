"""
Process Miner - Extracts process models from documentation sessions.
Part of Feature 2: Process Mining Engine
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime
import hashlib

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ProcessActivity:
    """An activity in the process."""
    id: str
    name: str
    activity_type: str
    timestamp: Optional[datetime] = None
    duration: float = 0.0
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessCase:
    """A case (trace) in the process."""
    case_id: str
    activities: List[ProcessActivity]
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessModel:
    """A discovered process model."""
    id: str
    name: str
    activities: List[str]
    transitions: Dict[str, List[str]]
    start_activities: List[str]
    end_activities: List[str]
    frequency: Dict[str, int]
    variants: List[List[str]]


class ProcessMiner:
    """
    Mines process models from documentation sessions.
    Discovers workflows, patterns, and variants.
    """
    
    def __init__(self, min_support: float = 0.1):
        """
        Initialize process miner.
        
        Args:
            min_support: Minimum support threshold for patterns
        """
        self.min_support = min_support
        self._cases: List[ProcessCase] = []
        
        logger.info("ProcessMiner initialized")
    
    def add_session(self, session_data: Dict[str, Any]) -> ProcessCase:
        """
        Add a session as a process case.
        
        Args:
            session_data: Session data
            
        Returns:
            Created ProcessCase
        """
        steps = session_data.get("steps", [])
        session_id = session_data.get("session_id", hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8])
        
        activities = []
        for i, step in enumerate(steps):
            activity = ProcessActivity(
                id=f"{session_id}_act_{i}",
                name=self._normalize_activity_name(step),
                activity_type=step.get("action_type", "action"),
                timestamp=self._parse_timestamp(step.get("timestamp")),
                attributes={
                    "window": step.get("window_title"),
                    "description": step.get("description")
                }
            )
            activities.append(activity)
        
        case = ProcessCase(
            case_id=session_id,
            activities=activities,
            start_time=activities[0].timestamp if activities else None,
            end_time=activities[-1].timestamp if activities else None,
            attributes={
                "application": session_data.get("application"),
                "name": session_data.get("name")
            }
        )
        
        self._cases.append(case)
        logger.info(f"Added process case: {session_id} ({len(activities)} activities)")
        
        return case
    
    def discover_process(self, name: str = "Discovered Process") -> ProcessModel:
        """
        Discover process model from all cases.
        
        Args:
            name: Name for the discovered process
            
        Returns:
            ProcessModel object
        """
        if not self._cases:
            return ProcessModel(
                id="empty",
                name=name,
                activities=[],
                transitions={},
                start_activities=[],
                end_activities=[],
                frequency={},
                variants=[]
            )
        
        # Extract all activity names
        all_activities = set()
        for case in self._cases:
            for act in case.activities:
                all_activities.add(act.name)
        
        # Count transitions
        transitions = defaultdict(lambda: defaultdict(int))
        start_activities = defaultdict(int)
        end_activities = defaultdict(int)
        
        for case in self._cases:
            if case.activities:
                start_activities[case.activities[0].name] += 1
                end_activities[case.activities[-1].name] += 1
                
                for i in range(len(case.activities) - 1):
                    from_act = case.activities[i].name
                    to_act = case.activities[i + 1].name
                    transitions[from_act][to_act] += 1
        
        # Convert to process model
        transition_dict = {}
        for from_act, to_acts in transitions.items():
            transition_dict[from_act] = list(to_acts.keys())
        
        # Activity frequency
        frequency = defaultdict(int)
        for case in self._cases:
            for act in case.activities:
                frequency[act.name] += 1
        
        # Extract variants
        variants = self._extract_variants()
        
        model = ProcessModel(
            id=hashlib.md5(name.encode()).hexdigest()[:8],
            name=name,
            activities=list(all_activities),
            transitions=transition_dict,
            start_activities=list(start_activities.keys()),
            end_activities=list(end_activities.keys()),
            frequency=dict(frequency),
            variants=variants
        )
        
        logger.info(f"Discovered process: {len(model.activities)} activities, {len(model.variants)} variants")
        return model
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get mining statistics."""
        if not self._cases:
            return {"total_cases": 0}
        
        total_activities = sum(len(c.activities) for c in self._cases)
        
        return {
            "total_cases": len(self._cases),
            "total_activities": total_activities,
            "avg_activities_per_case": total_activities / len(self._cases),
            "unique_activities": len(set(
                act.name for case in self._cases for act in case.activities
            )),
            "variants_count": len(self._extract_variants())
        }
    
    def get_conformance(
        self,
        case: ProcessCase,
        model: ProcessModel
    ) -> Dict[str, Any]:
        """
        Check conformance of a case against a model.
        
        Args:
            case: Process case to check
            model: Reference process model
            
        Returns:
            Conformance metrics
        """
        trace = [act.name for act in case.activities]
        
        # Check if trace follows valid transitions
        violations = []
        for i in range(len(trace) - 1):
            from_act = trace[i]
            to_act = trace[i + 1]
            
            valid_next = model.transitions.get(from_act, [])
            if to_act not in valid_next and valid_next:
                violations.append({
                    "position": i,
                    "from": from_act,
                    "to": to_act,
                    "expected": valid_next
                })
        
        # Calculate fitness
        fitness = 1.0 - (len(violations) / max(len(trace) - 1, 1))
        
        return {
            "fitness": fitness,
            "violations": violations,
            "trace_length": len(trace),
            "is_conformant": len(violations) == 0
        }
    
    def _normalize_activity_name(self, step: Dict[str, Any]) -> str:
        """Normalize step to activity name."""
        # Use action type if available
        if step.get("action_type"):
            return step["action_type"]
        
        # Extract from description
        desc = step.get("description", "").lower()
        
        if any(w in desc for w in ["click", "klick"]):
            return "click"
        elif any(w in desc for w in ["enter", "type", "eingeb"]):
            return "input"
        elif any(w in desc for w in ["select", "wähl"]):
            return "select"
        elif any(w in desc for w in ["open", "öffn"]):
            return "open"
        elif any(w in desc for w in ["save", "speicher"]):
            return "save"
        elif any(w in desc for w in ["close", "schließ"]):
            return "close"
        else:
            return "action"
    
    def _parse_timestamp(self, ts: Any) -> Optional[datetime]:
        """Parse timestamp from various formats."""
        if ts is None:
            return None
        if isinstance(ts, datetime):
            return ts
        try:
            return datetime.fromisoformat(str(ts))
        except:
            return None
    
    def _extract_variants(self) -> List[List[str]]:
        """Extract unique process variants."""
        variant_counts = defaultdict(int)
        
        for case in self._cases:
            trace = tuple(act.name for act in case.activities)
            variant_counts[trace] += 1
        
        # Sort by frequency
        sorted_variants = sorted(
            variant_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [list(v[0]) for v in sorted_variants]

