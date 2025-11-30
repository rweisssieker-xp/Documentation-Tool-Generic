"""
Selenium Exporter - Exports tests to Selenium format.
Part of Feature 6: Automated Test Case Generator
"""

from typing import Dict, List, Optional, Any
from pathlib import Path

from src.utils.logger import get_logger

logger = get_logger(__name__)


class SeleniumExporter:
    """
    Exports documentation to Selenium test scripts.
    Supports Python and Java output.
    """
    
    def __init__(self, language: str = "python"):
        """
        Initialize Selenium exporter.
        
        Args:
            language: Output language (python, java)
        """
        self.language = language
        logger.info(f"SeleniumExporter initialized: {language}")
    
    def export_session(
        self,
        session_data: Dict[str, Any],
        output_path: str,
        class_name: Optional[str] = None
    ) -> str:
        """
        Export session to Selenium test.
        
        Args:
            session_data: Session data
            output_path: Output file path
            class_name: Test class name
            
        Returns:
            Generated code
        """
        if self.language == "python":
            code = self._generate_python(session_data, class_name)
        else:
            code = self._generate_java(session_data, class_name)
        
        Path(output_path).write_text(code, encoding='utf-8')
        logger.info(f"Exported Selenium test to: {output_path}")
        
        return code
    
    def _generate_python(
        self,
        session_data: Dict[str, Any],
        class_name: Optional[str]
    ) -> str:
        """Generate Python Selenium test."""
        class_name = class_name or "TestDocumentation"
        steps = session_data.get("steps", [])
        
        code = f'''"""
Generated Selenium Test
Session: {session_data.get('name', 'Unknown')}
Generated from documentation
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class {class_name}:
    """
    Automated test generated from documentation session.
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 20)
        yield
        self.driver.quit()
    
    def test_documented_workflow(self):
        """
        Test the documented workflow.
        Steps: {len(steps)}
        """
'''
        
        for i, step in enumerate(steps):
            desc = step.get("description", "Step").replace('"', '\\"')
            window = step.get("window_title", "")
            
            code += f'''
        # Step {i + 1}: {desc[:50]}
        # Window: {window}
'''
            
            # Generate action based on description
            desc_lower = desc.lower()
            if "click" in desc_lower:
                code += f'        # TODO: Update selector\n'
                code += f'        # self.driver.find_element(By.XPATH, "//button").click()\n'
            elif "enter" in desc_lower or "type" in desc_lower:
                code += f'        # TODO: Update selector and value\n'
                code += f'        # self.driver.find_element(By.XPATH, "//input").send_keys("value")\n'
            elif "wait" in desc_lower:
                code += f'        # self.wait.until(EC.presence_of_element_located((By.XPATH, "//element")))\n'
        
        code += '''
        # Verify final state
        # assert self.driver.find_element(By.XPATH, "//success").is_displayed()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''
        
        return code
    
    def _generate_java(
        self,
        session_data: Dict[str, Any],
        class_name: Optional[str]
    ) -> str:
        """Generate Java Selenium test."""
        class_name = class_name or "TestDocumentation"
        steps = session_data.get("steps", [])
        
        code = f'''/**
 * Generated Selenium Test
 * Session: {session_data.get('name', 'Unknown')}
 */

import org.junit.jupiter.api.*;
import org.openqa.selenium.*;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.openqa.selenium.support.ui.ExpectedConditions;
import java.time.Duration;

public class {class_name} {{
    
    private WebDriver driver;
    private WebDriverWait wait;
    
    @BeforeEach
    public void setUp() {{
        driver = new ChromeDriver();
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));
        wait = new WebDriverWait(driver, Duration.ofSeconds(20));
    }}
    
    @AfterEach
    public void tearDown() {{
        if (driver != null) {{
            driver.quit();
        }}
    }}
    
    @Test
    public void testDocumentedWorkflow() {{
        // Total steps: {len(steps)}
'''
        
        for i, step in enumerate(steps):
            desc = step.get("description", "Step").replace('"', '\\"')
            code += f'''
        // Step {i + 1}: {desc[:50]}
        // TODO: Implement step
'''
        
        code += '''
    }
}
'''
        
        return code

