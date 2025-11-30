"""
Playwright Exporter - Exports tests to Playwright format.
Part of Feature 6: Automated Test Case Generator
"""

from typing import Dict, List, Optional, Any
from pathlib import Path

from src.utils.logger import get_logger

logger = get_logger(__name__)


class PlaywrightExporter:
    """
    Exports documentation to Playwright test scripts.
    Supports Python and TypeScript output.
    """
    
    def __init__(self, language: str = "python"):
        """
        Initialize Playwright exporter.
        
        Args:
            language: Output language (python, typescript)
        """
        self.language = language
        logger.info(f"PlaywrightExporter initialized: {language}")
    
    def export_session(
        self,
        session_data: Dict[str, Any],
        output_path: str,
        test_name: Optional[str] = None
    ) -> str:
        """
        Export session to Playwright test.
        
        Args:
            session_data: Session data
            output_path: Output file path
            test_name: Test function name
            
        Returns:
            Generated code
        """
        if self.language == "python":
            code = self._generate_python(session_data, test_name)
        else:
            code = self._generate_typescript(session_data, test_name)
        
        Path(output_path).write_text(code, encoding='utf-8')
        logger.info(f"Exported Playwright test to: {output_path}")
        
        return code
    
    def _generate_python(
        self,
        session_data: Dict[str, Any],
        test_name: Optional[str]
    ) -> str:
        """Generate Python Playwright test."""
        test_name = test_name or "test_documented_workflow"
        steps = session_data.get("steps", [])
        
        code = f'''"""
Generated Playwright Test
Session: {session_data.get('name', 'Unknown')}
Generated from documentation
"""

import pytest
from playwright.sync_api import Page, expect


def {test_name}(page: Page):
    """
    Test the documented workflow.
    Steps: {len(steps)}
    """
'''
        
        for i, step in enumerate(steps):
            desc = step.get("description", "Step").replace('"', '\\"')
            window = step.get("window_title", "")
            
            code += f'''
    # Step {i + 1}: {desc[:60]}
'''
            
            desc_lower = desc.lower()
            if "click" in desc_lower:
                code += f'    # page.click("selector")  # TODO: Update selector\n'
            elif "enter" in desc_lower or "type" in desc_lower:
                code += f'    # page.fill("selector", "value")  # TODO: Update\n'
            elif "select" in desc_lower:
                code += f'    # page.select_option("selector", "option")  # TODO\n'
            elif "wait" in desc_lower:
                code += f'    # page.wait_for_selector("selector")\n'
        
        code += '''
    # Verify final state
    # expect(page.locator("success")).to_be_visible()
'''
        
        return code
    
    def _generate_typescript(
        self,
        session_data: Dict[str, Any],
        test_name: Optional[str]
    ) -> str:
        """Generate TypeScript Playwright test."""
        test_name = test_name or "documented workflow"
        steps = session_data.get("steps", [])
        
        code = f'''/**
 * Generated Playwright Test
 * Session: {session_data.get('name', 'Unknown')}
 */

import {{ test, expect }} from '@playwright/test';

test('{test_name}', async ({{ page }}) => {{
  // Total steps: {len(steps)}
'''
        
        for i, step in enumerate(steps):
            desc = step.get("description", "Step").replace("'", "\\'")
            
            code += f'''
  // Step {i + 1}: {desc[:60]}
'''
            
            desc_lower = desc.lower()
            if "click" in desc_lower:
                code += f"  // await page.click('selector');\n"
            elif "enter" in desc_lower or "type" in desc_lower:
                code += f"  // await page.fill('selector', 'value');\n"
        
        code += '''
  // Verify final state
  // await expect(page.locator('success')).toBeVisible();
}});
'''
        
        return code

