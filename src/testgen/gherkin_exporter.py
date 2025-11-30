"""
Gherkin Exporter - Exports tests to Gherkin/BDD format.
Part of Feature 6: Automated Test Case Generator
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import re

from src.utils.logger import get_logger

logger = get_logger(__name__)


class GherkinExporter:
    """
    Exports documentation to Gherkin BDD format.
    Generates .feature files and step definitions.
    """
    
    def __init__(self, language: str = "de"):
        """
        Initialize Gherkin exporter.
        
        Args:
            language: Output language (de, en)
        """
        self.language = language
        
        # Gherkin keywords by language
        self.keywords = {
            "de": {
                "feature": "Funktionalität",
                "scenario": "Szenario",
                "given": "Angenommen",
                "when": "Wenn",
                "then": "Dann",
                "and": "Und",
                "but": "Aber"
            },
            "en": {
                "feature": "Feature",
                "scenario": "Scenario",
                "given": "Given",
                "when": "When",
                "then": "Then",
                "and": "And",
                "but": "But"
            }
        }
        
        logger.info(f"GherkinExporter initialized: {language}")
    
    def export_session(
        self,
        session_data: Dict[str, Any],
        output_path: str,
        feature_name: Optional[str] = None
    ) -> str:
        """
        Export session to Gherkin feature file.
        
        Args:
            session_data: Session data
            output_path: Output file path
            feature_name: Feature name
            
        Returns:
            Generated Gherkin content
        """
        kw = self.keywords.get(self.language, self.keywords["en"])
        steps = session_data.get("steps", [])
        feature_name = feature_name or session_data.get("name", "Dokumentierter Workflow")
        
        lines = [
            f"# language: {self.language}",
            f"{kw['feature']}: {feature_name}",
            f"  Als Benutzer" if self.language == "de" else "  As a user",
            f"  möchte ich den dokumentierten Workflow ausführen" if self.language == "de" 
                else "  I want to execute the documented workflow",
            f"  um mein Ziel zu erreichen" if self.language == "de"
                else "  So that I can achieve my goal",
            "",
            f"  {kw['scenario']}: {feature_name}",
        ]
        
        # Generate Given (preconditions)
        if steps:
            first_window = steps[0].get("window_title", "Anwendung")
            given_text = f"ich bin auf \"{first_window}\"" if self.language == "de" \
                        else f'I am on "{first_window}"'
            lines.append(f"    {kw['given']} {given_text}")
        
        # Generate When/And steps
        for i, step in enumerate(steps):
            keyword = kw['when'] if i == 0 else kw['and']
            step_text = self._convert_step_to_gherkin(step)
            lines.append(f"    {keyword} {step_text}")
        
        # Generate Then (expected result)
        then_text = "die Aktion erfolgreich abgeschlossen ist" if self.language == "de" \
                   else "the action is completed successfully"
        lines.append(f"    {kw['then']} {then_text}")
        
        content = "\n".join(lines)
        
        Path(output_path).write_text(content, encoding='utf-8')
        logger.info(f"Exported Gherkin feature to: {output_path}")
        
        return content
    
    def export_step_definitions(
        self,
        session_data: Dict[str, Any],
        output_path: str
    ) -> str:
        """
        Generate step definition file for the feature.
        
        Args:
            session_data: Session data
            output_path: Output file path
            
        Returns:
            Generated step definitions
        """
        steps = session_data.get("steps", [])
        
        code = '''"""
Generated Step Definitions
"""

from behave import given, when, then


@given('ich bin auf "{page}"')
@given('I am on "{page}"')
def step_impl_given_page(context, page):
    """Navigate to initial page."""
    # TODO: Implement navigation
    pass

'''
        
        for i, step in enumerate(steps):
            desc = step.get("description", "").replace('"', '\\"')
            safe_desc = re.sub(r'[^a-zA-Z0-9_]', '_', desc[:30]).lower()
            
            code += f'''
@when('{self._convert_step_to_gherkin(step)}')
def step_impl_{safe_desc}(context):
    """Step {i + 1}: {desc[:50]}"""
    # TODO: Implement step
    pass

'''
        
        code += '''
@then('die Aktion erfolgreich abgeschlossen ist')
@then('the action is completed successfully')
def step_impl_success(context):
    """Verify successful completion."""
    # TODO: Add verification
    assert True
'''
        
        Path(output_path).write_text(code, encoding='utf-8')
        logger.info(f"Exported step definitions to: {output_path}")
        
        return code
    
    def _convert_step_to_gherkin(self, step: Dict[str, Any]) -> str:
        """Convert step to Gherkin statement."""
        desc = step.get("description", "")
        desc_lower = desc.lower()
        
        if self.language == "de":
            if "click" in desc_lower or "klick" in desc_lower:
                return f'ich klicke auf "{self._extract_target(desc)}"'
            elif "enter" in desc_lower or "eingeb" in desc_lower or "type" in desc_lower:
                return f'ich gebe "{step.get("input_value", "Wert")}" ein'
            elif "select" in desc_lower or "wähl" in desc_lower:
                return f'ich wähle "{step.get("selected_value", "Option")}"'
            elif "wait" in desc_lower or "wart" in desc_lower:
                return 'ich warte auf die Antwort'
            else:
                return f'ich führe Aktion aus: "{desc[:50]}"'
        else:
            if "click" in desc_lower:
                return f'I click on "{self._extract_target(desc)}"'
            elif "enter" in desc_lower or "type" in desc_lower:
                return f'I enter "{step.get("input_value", "value")}"'
            elif "select" in desc_lower:
                return f'I select "{step.get("selected_value", "option")}"'
            elif "wait" in desc_lower:
                return 'I wait for the response'
            else:
                return f'I perform action: "{desc[:50]}"'
    
    def _extract_target(self, description: str) -> str:
        """Extract target element from description."""
        # Simple extraction - could be enhanced with NLP
        words = description.split()
        
        # Look for quoted text
        import re
        quoted = re.findall(r'"([^"]*)"', description)
        if quoted:
            return quoted[0]
        
        # Look for button/link keywords
        for i, word in enumerate(words):
            if word.lower() in ["button", "link", "field", "feld", "schaltfläche"]:
                if i + 1 < len(words):
                    return words[i + 1]
        
        return "Element"

