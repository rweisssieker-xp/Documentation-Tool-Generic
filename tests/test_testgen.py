"""
Tests for Automated Test Case Generator Module
"""

import pytest
from unittest.mock import Mock, patch


class TestTestGenerator:
    """Tests for TestGenerator class."""
    
    def test_test_generator_initialization(self):
        """Test TestGenerator initialization."""
        from src.testgen.test_generator import TestGenerator, TestFramework
        
        generator = TestGenerator()
        assert generator.default_framework == TestFramework.PLAYWRIGHT
    
    def test_generate_test_cases(self):
        """Test generating test cases."""
        from src.testgen.test_generator import TestGenerator
        
        generator = TestGenerator()
        
        session_data = {
            "session_id": "test_001",
            "name": "Login Test",
            "steps": [
                {"description": "Click login button", "selector": "#login"},
                {"description": "Enter username", "selector": "#username", "input_value": "testuser"},
                {"description": "Enter password", "selector": "#password"},
                {"description": "Click submit", "selector": "#submit"}
            ]
        }
        
        test_cases = generator.generate_test_cases(session_data)
        
        assert len(test_cases) >= 1
        assert test_cases[0].name == "Test_Login Test"
    
    def test_export_selenium(self, tmp_path):
        """Test Selenium export."""
        from src.testgen.test_generator import TestGenerator, TestFramework, TestCase, TestStep
        
        generator = TestGenerator()
        
        test_case = TestCase(
            id="TC_001",
            name="Test Login",
            description="Login test",
            steps=[
                TestStep(action="click", target="#login", value=None, wait_for=None, assertion=None),
                TestStep(action="fill", target="#username", value="test", wait_for=None, assertion=None)
            ],
            preconditions=["App is running"],
            expected_result="User logged in",
            tags=["login"]
        )
        
        output_path = str(tmp_path / "test_login.py")
        code = generator.export_test(test_case, TestFramework.SELENIUM, output_path)
        
        assert "class TestTestLogin" in code
        assert "pytest" in code
    
    def test_export_playwright(self, tmp_path):
        """Test Playwright export."""
        from src.testgen.test_generator import TestGenerator, TestFramework, TestCase, TestStep
        
        generator = TestGenerator()
        
        test_case = TestCase(
            id="TC_001",
            name="Test Login",
            description="Login test",
            steps=[
                TestStep(action="click", target="#login", value=None, wait_for=None, assertion=None)
            ],
            preconditions=[],
            expected_result="Success",
            tags=[]
        )
        
        code = generator.export_test(test_case, TestFramework.PLAYWRIGHT)
        
        assert "def test_tc_001" in code
        assert "playwright" in code
    
    def test_export_gherkin(self):
        """Test Gherkin export."""
        from src.testgen.test_generator import TestGenerator, TestFramework, TestCase, TestStep
        
        generator = TestGenerator()
        
        test_case = TestCase(
            id="TC_001",
            name="Login Feature",
            description="User can login",
            steps=[
                TestStep(action="click", target="login", value=None, wait_for=None, assertion=None),
                TestStep(action="fill", target="username", value="test", wait_for=None, assertion=None)
            ],
            preconditions=["User is on login page"],
            expected_result="User is logged in",
            tags=[]
        )
        
        code = generator.export_test(test_case, TestFramework.GHERKIN)
        
        assert "Feature:" in code
        assert "Scenario:" in code
        assert "Given" in code
        assert "Then" in code


class TestGherkinExporter:
    """Tests for GherkinExporter class."""
    
    def test_gherkin_exporter_initialization(self):
        """Test GherkinExporter initialization."""
        from src.testgen.gherkin_exporter import GherkinExporter
        
        exporter = GherkinExporter(language="de")
        assert exporter.language == "de"
    
    def test_export_session_german(self, tmp_path):
        """Test German Gherkin export."""
        from src.testgen.gherkin_exporter import GherkinExporter
        
        exporter = GherkinExporter(language="de")
        
        session_data = {
            "name": "Benutzer anlegen",
            "steps": [
                {"description": "Klicke auf Neu", "window_title": "Admin"},
                {"description": "Eingabe Benutzername", "input_value": "testuser"}
            ]
        }
        
        output_path = str(tmp_path / "test.feature")
        content = exporter.export_session(session_data, output_path)
        
        assert "# language: de" in content
        assert "Funktionalität:" in content
    
    def test_export_session_english(self, tmp_path):
        """Test English Gherkin export."""
        from src.testgen.gherkin_exporter import GherkinExporter
        
        exporter = GherkinExporter(language="en")
        
        session_data = {
            "name": "Create User",
            "steps": [
                {"description": "Click on New"},
                {"description": "Enter username"}
            ]
        }
        
        output_path = str(tmp_path / "test.feature")
        content = exporter.export_session(session_data, output_path)
        
        assert "# language: en" in content
        assert "Feature:" in content


class TestSelectorEngine:
    """Tests for SelectorEngine class."""
    
    def test_selector_engine_initialization(self):
        """Test SelectorEngine initialization."""
        from src.testgen.selector_engine import SelectorEngine, SelectorType
        
        engine = SelectorEngine(prefer_type=SelectorType.CSS)
        assert engine.prefer_type == SelectorType.CSS
    
    def test_generate_selector_with_id(self):
        """Test selector generation with ID."""
        from src.testgen.selector_engine import SelectorEngine, SelectorType
        
        engine = SelectorEngine()
        
        element_info = {
            "id": "submit-button",
            "tag": "button"
        }
        
        selector = engine.generate_selector(element_info)
        
        assert selector.selector_type == SelectorType.ID
        assert "#submit-button" in selector.value
        assert selector.confidence >= 0.9
    
    def test_generate_selector_with_text(self):
        """Test selector generation with text content."""
        from src.testgen.selector_engine import SelectorEngine, SelectorType
        
        engine = SelectorEngine()
        
        element_info = {
            "text": "Submit Form",
            "tag": "button"
        }
        
        selector = engine.generate_selector(element_info)
        
        # Should use text-based XPath
        assert selector is not None
    
    def test_selector_to_playwright(self):
        """Test converting selector to Playwright format."""
        from src.testgen.selector_engine import SelectorEngine, SelectorType, Selector
        
        engine = SelectorEngine()
        
        selector = Selector(
            selector_type=SelectorType.ID,
            value="#my-button",
            confidence=0.95,
            fallbacks=[]
        )
        
        pw_selector = engine.to_playwright(selector)
        assert "#my-button" in pw_selector
    
    def test_selector_to_selenium(self):
        """Test converting selector to Selenium format."""
        from src.testgen.selector_engine import SelectorEngine, SelectorType, Selector
        
        engine = SelectorEngine()
        
        selector = Selector(
            selector_type=SelectorType.ID,
            value="#my-button",
            confidence=0.95,
            fallbacks=[]
        )
        
        by_type, value = engine.to_selenium(selector)
        assert by_type == "By.ID"
        assert value == "my-button"

