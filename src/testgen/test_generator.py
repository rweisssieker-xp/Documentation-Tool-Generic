"""
Test Generator - Generates automated test cases from documentation.
Part of Feature 6: Automated Test Case Generator
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from src.utils.logger import get_logger

logger = get_logger(__name__)


class TestFramework(Enum):
    """Supported test frameworks."""
    SELENIUM = "selenium"
    PLAYWRIGHT = "playwright"
    CYPRESS = "cypress"
    ROBOT = "robot"
    GHERKIN = "gherkin"


@dataclass
class TestStep:
    """A test step."""
    action: str
    target: str
    value: Optional[str]
    wait_for: Optional[str]
    assertion: Optional[str]


@dataclass
class TestCase:
    """A generated test case."""
    id: str
    name: str
    description: str
    steps: List[TestStep]
    preconditions: List[str]
    expected_result: str
    tags: List[str]


class TestGenerator:
    """
    Generates automated test cases from documentation sessions.
    Supports multiple test frameworks.
    """
    
    def __init__(
        self,
        selector_engine: Optional[Any] = None,
        default_framework: TestFramework = TestFramework.PLAYWRIGHT
    ):
        """
        Initialize test generator.
        
        Args:
            selector_engine: SelectorEngine for element location
            default_framework: Default test framework
        """
        self.selector_engine = selector_engine
        self.default_framework = default_framework
        
        logger.info(f"TestGenerator initialized: {default_framework.value}")
    
    def generate_test_cases(
        self,
        session_data: Dict[str, Any],
        framework: Optional[TestFramework] = None
    ) -> List[TestCase]:
        """
        Generate test cases from a session.
        
        Args:
            session_data: Session data
            framework: Target framework
            
        Returns:
            List of TestCase objects
        """
        framework = framework or self.default_framework
        steps = session_data.get("steps", [])
        
        if not steps:
            return []
        
        test_cases = []
        
        # Generate main test case
        main_test = self._create_test_case(
            session_data,
            f"Test_{session_data.get('name', 'Session')}",
            steps
        )
        test_cases.append(main_test)
        
        # Generate edge case tests
        edge_cases = self._generate_edge_cases(steps)
        test_cases.extend(edge_cases)
        
        logger.info(f"Generated {len(test_cases)} test cases")
        return test_cases
    
    def export_test(
        self,
        test_case: TestCase,
        framework: TestFramework,
        output_path: Optional[str] = None
    ) -> str:
        """
        Export test case to framework-specific code.
        
        Args:
            test_case: Test case to export
            framework: Target framework
            output_path: Output file path
            
        Returns:
            Generated code string
        """
        exporters = {
            TestFramework.SELENIUM: self._export_selenium,
            TestFramework.PLAYWRIGHT: self._export_playwright,
            TestFramework.GHERKIN: self._export_gherkin,
        }
        
        exporter = exporters.get(framework)
        if not exporter:
            raise ValueError(f"Unsupported framework: {framework}")
        
        code = exporter(test_case)
        
        if output_path:
            Path(output_path).write_text(code, encoding='utf-8')
            logger.info(f"Exported test to: {output_path}")
        
        return code
    
    def _create_test_case(
        self,
        session_data: Dict[str, Any],
        name: str,
        steps: List[Dict[str, Any]]
    ) -> TestCase:
        """Create a test case from steps."""
        test_steps = []
        
        for step in steps:
            test_step = self._convert_step(step)
            if test_step:
                test_steps.append(test_step)
        
        return TestCase(
            id=f"TC_{session_data.get('session_id', 'unknown')[:8]}",
            name=name,
            description=session_data.get("description", "Generated from documentation"),
            steps=test_steps,
            preconditions=self._extract_preconditions(steps),
            expected_result=self._extract_expected_result(steps),
            tags=["automated", "generated"]
        )
    
    def _convert_step(self, step: Dict[str, Any]) -> Optional[TestStep]:
        """Convert documentation step to test step."""
        description = step.get("description", "").lower()
        
        # Detect action type
        action = "click"
        target = ""
        value = None
        
        if "click" in description or "klick" in description:
            action = "click"
        elif "enter" in description or "type" in description or "eingeb" in description:
            action = "fill"
            value = step.get("input_value", "test_value")
        elif "select" in description or "wähl" in description:
            action = "select"
        elif "wait" in description or "wart" in description:
            action = "wait"
        
        # Get selector from screenshot analysis or OCR
        target = step.get("selector", step.get("window_title", ""))
        
        return TestStep(
            action=action,
            target=target,
            value=value,
            wait_for=step.get("wait_for"),
            assertion=step.get("assertion")
        )
    
    def _generate_edge_cases(
        self,
        steps: List[Dict[str, Any]]
    ) -> List[TestCase]:
        """Generate edge case test cases."""
        edge_cases = []
        
        # Empty input test
        input_steps = [s for s in steps if "enter" in s.get("description", "").lower()]
        if input_steps:
            edge_cases.append(TestCase(
                id="TC_empty_input",
                name="Test_Empty_Input",
                description="Test with empty input values",
                steps=[TestStep(action="fill", target=s.get("selector", ""), value="", wait_for=None, assertion=None) 
                       for s in input_steps[:3]],
                preconditions=["Application is running"],
                expected_result="Validation error displayed",
                tags=["edge_case", "negative"]
            ))
        
        return edge_cases
    
    def _extract_preconditions(self, steps: List[Dict[str, Any]]) -> List[str]:
        """Extract preconditions from steps."""
        preconditions = ["Application is accessible"]
        
        if steps and steps[0].get("window_title"):
            preconditions.append(f"User is on: {steps[0]['window_title']}")
        
        return preconditions
    
    def _extract_expected_result(self, steps: List[Dict[str, Any]]) -> str:
        """Extract expected result from final step."""
        if not steps:
            return "Workflow completed successfully"
        
        last_step = steps[-1]
        return last_step.get("expected_result", "Final state achieved as documented")
    
    def _export_selenium(self, test_case: TestCase) -> str:
        """Export to Selenium Python code."""
        lines = [
            "import pytest",
            "from selenium import webdriver",
            "from selenium.webdriver.common.by import By",
            "from selenium.webdriver.support.ui import WebDriverWait",
            "from selenium.webdriver.support import expected_conditions as EC",
            "",
            "",
            f"class Test{test_case.name.replace(' ', '')}:",
            f'    """',
            f'    {test_case.description}',
            f'    """',
            "",
            "    @pytest.fixture(autouse=True)",
            "    def setup(self):",
            "        self.driver = webdriver.Chrome()",
            "        yield",
            "        self.driver.quit()",
            "",
            f"    def test_{test_case.id.lower()}(self):",
            f'        """Test: {test_case.name}"""',
        ]
        
        for i, step in enumerate(test_case.steps):
            comment = f"        # Step {i+1}: {step.action}"
            lines.append(comment)
            
            if step.action == "click":
                lines.append(f'        self.driver.find_element(By.XPATH, "{step.target}").click()')
            elif step.action == "fill":
                lines.append(f'        self.driver.find_element(By.XPATH, "{step.target}").send_keys("{step.value}")')
            elif step.action == "wait":
                lines.append(f'        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "{step.target}")))')
        
        lines.append("")
        lines.append(f'        # Expected: {test_case.expected_result}')
        
        return "\n".join(lines)
    
    def _export_playwright(self, test_case: TestCase) -> str:
        """Export to Playwright Python code."""
        lines = [
            "import pytest",
            "from playwright.sync_api import Page, expect",
            "",
            "",
            f"def test_{test_case.id.lower()}(page: Page):",
            f'    """',
            f'    {test_case.description}',
            f'    """',
        ]
        
        for i, step in enumerate(test_case.steps):
            comment = f"    # Step {i+1}: {step.action}"
            lines.append(comment)
            
            if step.action == "click":
                lines.append(f'    page.click("{step.target}")')
            elif step.action == "fill":
                lines.append(f'    page.fill("{step.target}", "{step.value}")')
            elif step.action == "wait":
                lines.append(f'    page.wait_for_selector("{step.target}")')
            elif step.action == "select":
                lines.append(f'    page.select_option("{step.target}", "{step.value}")')
        
        lines.append("")
        lines.append(f'    # Expected: {test_case.expected_result}')
        
        return "\n".join(lines)
    
    def _export_gherkin(self, test_case: TestCase) -> str:
        """Export to Gherkin BDD format."""
        lines = [
            f"Feature: {test_case.name}",
            f"  {test_case.description}",
            "",
            f"  Scenario: {test_case.name}",
        ]
        
        # Preconditions as Given
        for pre in test_case.preconditions:
            lines.append(f"    Given {pre}")
        
        # Steps as When/And
        for i, step in enumerate(test_case.steps):
            keyword = "When" if i == 0 else "And"
            
            if step.action == "click":
                lines.append(f'    {keyword} I click on "{step.target}"')
            elif step.action == "fill":
                lines.append(f'    {keyword} I enter "{step.value}" in "{step.target}"')
            elif step.action == "select":
                lines.append(f'    {keyword} I select "{step.value}" from "{step.target}"')
            elif step.action == "wait":
                lines.append(f'    {keyword} I wait for "{step.target}" to be visible')
        
        # Expected result as Then
        lines.append(f"    Then {test_case.expected_result}")
        
        return "\n".join(lines)

