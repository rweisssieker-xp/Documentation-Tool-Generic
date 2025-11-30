"""
Intent Analyzer - Analyzes user intent from context.
Part of Feature 1: Smart Context Capture
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from src.utils.logger import get_logger

logger = get_logger(__name__)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class IntentCategory(Enum):
    """Categories of user intent."""
    DATA_ENTRY = "data_entry"
    NAVIGATION = "navigation"
    CONFIGURATION = "configuration"
    ANALYSIS = "analysis"
    COMMUNICATION = "communication"
    FILE_OPERATION = "file_operation"
    SEARCH = "search"
    UNKNOWN = "unknown"


@dataclass
class IntentAnalysis:
    """Result of intent analysis."""
    category: IntentCategory
    action: str
    confidence: float
    description: str
    suggested_next: List[str]


class IntentAnalyzer:
    """
    Analyzes user intent from collected context.
    Uses AI to understand the purpose behind actions.
    """
    
    # Pattern-based intent detection
    INTENT_PATTERNS = {
        IntentCategory.DATA_ENTRY: [
            "enter", "type", "input", "fill", "eingeben", "ausfüllen"
        ],
        IntentCategory.NAVIGATION: [
            "click", "open", "go to", "navigate", "switch", "klicken", "öffnen", "wechseln"
        ],
        IntentCategory.CONFIGURATION: [
            "settings", "configure", "option", "preference", "einstellung", "konfigur"
        ],
        IntentCategory.ANALYSIS: [
            "report", "analyze", "view", "check", "bericht", "analyse", "anzeigen"
        ],
        IntentCategory.COMMUNICATION: [
            "email", "send", "message", "reply", "nachricht", "senden", "antworten"
        ],
        IntentCategory.FILE_OPERATION: [
            "save", "open file", "export", "import", "download", "speichern", "exportieren"
        ],
        IntentCategory.SEARCH: [
            "search", "find", "filter", "suchen", "finden", "filtern"
        ]
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        use_ai: bool = True
    ):
        """
        Initialize intent analyzer.
        
        Args:
            api_key: OpenAI API key
            use_ai: Whether to use AI for analysis
        """
        self.use_ai = use_ai and OPENAI_AVAILABLE
        
        if self.use_ai:
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            if self.api_key:
                self.client = OpenAI(api_key=self.api_key)
            else:
                self.use_ai = False
        
        logger.info(f"IntentAnalyzer initialized (AI: {self.use_ai})")
    
    def analyze(
        self,
        context: Dict[str, Any],
        previous_intents: Optional[List[IntentAnalysis]] = None
    ) -> IntentAnalysis:
        """
        Analyze user intent from context.
        
        Args:
            context: Context data
            previous_intents: Previous intent analyses for continuity
            
        Returns:
            IntentAnalysis result
        """
        # Extract relevant context
        window_title = context.get("window", {}).get("title", "")
        clipboard = context.get("clipboard", "")
        history = context.get("history", [])
        
        # Pattern-based analysis
        pattern_intent = self._pattern_analysis(window_title, history)
        
        # AI-enhanced analysis if available
        if self.use_ai and pattern_intent.confidence < 0.7:
            ai_intent = self._ai_analysis(context, previous_intents)
            
            # Use AI result if more confident
            if ai_intent.confidence > pattern_intent.confidence:
                return ai_intent
        
        return pattern_intent
    
    def analyze_sequence(
        self,
        contexts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze a sequence of contexts to understand overall intent.
        
        Args:
            contexts: List of context data
            
        Returns:
            Analysis of the complete sequence
        """
        intents = []
        
        for i, ctx in enumerate(contexts):
            prev = intents[-3:] if intents else None
            intent = self.analyze(ctx, prev)
            intents.append(intent)
        
        # Determine dominant intent
        intent_counts = {}
        for intent in intents:
            cat = intent.category.value
            intent_counts[cat] = intent_counts.get(cat, 0) + 1
        
        dominant = max(intent_counts.items(), key=lambda x: x[1]) if intent_counts else ("unknown", 0)
        
        return {
            "dominant_intent": dominant[0],
            "intent_distribution": intent_counts,
            "total_steps": len(intents),
            "workflow_description": self._describe_workflow(intents)
        }
    
    def suggest_documentation_style(
        self,
        intent: IntentAnalysis
    ) -> str:
        """
        Suggest documentation style based on intent.
        
        Args:
            intent: Analyzed intent
            
        Returns:
            Suggested documentation style
        """
        style_map = {
            IntentCategory.DATA_ENTRY: "step_by_step",
            IntentCategory.NAVIGATION: "overview",
            IntentCategory.CONFIGURATION: "reference",
            IntentCategory.ANALYSIS: "explanatory",
            IntentCategory.COMMUNICATION: "procedural",
            IntentCategory.FILE_OPERATION: "quick_reference",
            IntentCategory.SEARCH: "tips",
            IntentCategory.UNKNOWN: "standard"
        }
        
        return style_map.get(intent.category, "standard")
    
    def _pattern_analysis(
        self,
        window_title: str,
        history: List[str]
    ) -> IntentAnalysis:
        """Pattern-based intent detection."""
        combined = f"{window_title} {' '.join(history)}".lower()
        
        best_match = IntentCategory.UNKNOWN
        best_count = 0
        
        for category, patterns in self.INTENT_PATTERNS.items():
            count = sum(1 for p in patterns if p in combined)
            if count > best_count:
                best_count = count
                best_match = category
        
        confidence = min(best_count * 0.2, 0.8) if best_count > 0 else 0.1
        
        return IntentAnalysis(
            category=best_match,
            action=history[-1] if history else "unknown",
            confidence=confidence,
            description=f"Pattern-detected: {best_match.value}",
            suggested_next=self._get_suggested_next(best_match)
        )
    
    def _ai_analysis(
        self,
        context: Dict[str, Any],
        previous_intents: Optional[List[IntentAnalysis]]
    ) -> IntentAnalysis:
        """AI-based intent analysis."""
        # Build context summary
        summary = f"""Window: {context.get('window', {}).get('title', 'Unknown')}
Recent actions: {', '.join(context.get('history', [])[-5:])}
Clipboard: {context.get('clipboard', '')[:100] if context.get('clipboard') else 'Empty'}"""
        
        if previous_intents:
            summary += f"\nPrevious intents: {', '.join(p.category.value for p in previous_intents[-3:])}"
        
        prompt = f"""Analysiere die Benutzerabsicht basierend auf dem Kontext:

{summary}

Kategorien: data_entry, navigation, configuration, analysis, communication, file_operation, search

Antworte im Format:
CATEGORY: [Kategorie]
ACTION: [Beschreibung der Aktion]
CONFIDENCE: [0.0-1.0]"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.3
            )
            
            text = response.choices[0].message.content
            
            # Parse response
            category = IntentCategory.UNKNOWN
            action = "unknown"
            confidence = 0.5
            
            for line in text.split("\n"):
                if line.startswith("CATEGORY:"):
                    cat_str = line.split(":", 1)[1].strip().lower()
                    try:
                        category = IntentCategory(cat_str)
                    except:
                        pass
                elif line.startswith("ACTION:"):
                    action = line.split(":", 1)[1].strip()
                elif line.startswith("CONFIDENCE:"):
                    try:
                        confidence = float(line.split(":", 1)[1].strip())
                    except:
                        pass
            
            return IntentAnalysis(
                category=category,
                action=action,
                confidence=confidence,
                description=f"AI-analyzed: {action}",
                suggested_next=self._get_suggested_next(category)
            )
        
        except Exception as e:
            logger.warning(f"AI analysis failed: {e}")
            return IntentAnalysis(
                category=IntentCategory.UNKNOWN,
                action="unknown",
                confidence=0.1,
                description="AI analysis failed",
                suggested_next=[]
            )
    
    def _get_suggested_next(self, category: IntentCategory) -> List[str]:
        """Get suggested next actions based on intent category."""
        suggestions = {
            IntentCategory.DATA_ENTRY: ["Save", "Submit", "Review", "Next field"],
            IntentCategory.NAVIGATION: ["Open", "Select", "Back", "Home"],
            IntentCategory.CONFIGURATION: ["Apply", "Save", "Cancel", "Reset"],
            IntentCategory.ANALYSIS: ["Export", "Print", "Filter", "Compare"],
            IntentCategory.COMMUNICATION: ["Send", "Reply", "Attach", "Cancel"],
            IntentCategory.FILE_OPERATION: ["Save", "Close", "Open", "Export"],
            IntentCategory.SEARCH: ["Filter", "Sort", "Clear", "Select"],
            IntentCategory.UNKNOWN: []
        }
        return suggestions.get(category, [])
    
    def _describe_workflow(self, intents: List[IntentAnalysis]) -> str:
        """Generate workflow description from intent sequence."""
        if not intents:
            return "No workflow detected"
        
        categories = [i.category.value for i in intents]
        unique = []
        for c in categories:
            if not unique or unique[-1] != c:
                unique.append(c)
        
        if len(unique) == 1:
            return f"Single-purpose workflow: {unique[0]}"
        else:
            return f"Multi-step workflow: {' → '.join(unique)}"

