"""
Selector Engine - Generates robust element selectors.
Part of Feature 6: Automated Test Case Generator
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from src.utils.logger import get_logger

logger = get_logger(__name__)


class SelectorType(Enum):
    """Types of selectors."""
    ID = "id"
    NAME = "name"
    CLASS = "class"
    XPATH = "xpath"
    CSS = "css"
    TEXT = "text"
    ROLE = "role"


@dataclass
class Selector:
    """A generated selector."""
    selector_type: SelectorType
    value: str
    confidence: float
    fallbacks: List['Selector']


class SelectorEngine:
    """
    Generates robust element selectors from UI information.
    Uses multiple strategies to create reliable locators.
    """
    
    def __init__(self, prefer_type: SelectorType = SelectorType.CSS):
        """
        Initialize selector engine.
        
        Args:
            prefer_type: Preferred selector type
        """
        self.prefer_type = prefer_type
        logger.info(f"SelectorEngine initialized: prefer {prefer_type.value}")
    
    def generate_selector(
        self,
        element_info: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Selector:
        """
        Generate a robust selector for an element.
        
        Args:
            element_info: Element information
            context: Page context
            
        Returns:
            Selector object with fallbacks
        """
        selectors = []
        
        # Try ID
        if element_info.get("id"):
            selectors.append(Selector(
                selector_type=SelectorType.ID,
                value=f"#{element_info['id']}",
                confidence=0.95,
                fallbacks=[]
            ))
        
        # Try data-testid
        if element_info.get("data-testid"):
            selectors.append(Selector(
                selector_type=SelectorType.CSS,
                value=f'[data-testid="{element_info["data-testid"]}"]',
                confidence=0.9,
                fallbacks=[]
            ))
        
        # Try name attribute
        if element_info.get("name"):
            selectors.append(Selector(
                selector_type=SelectorType.NAME,
                value=f'[name="{element_info["name"]}"]',
                confidence=0.85,
                fallbacks=[]
            ))
        
        # Try text content
        if element_info.get("text"):
            text = element_info["text"][:50]
            selectors.append(Selector(
                selector_type=SelectorType.XPATH,
                value=f'//*[contains(text(), "{text}")]',
                confidence=0.7,
                fallbacks=[]
            ))
        
        # Try role + label
        if element_info.get("role") and element_info.get("label"):
            selectors.append(Selector(
                selector_type=SelectorType.ROLE,
                value=f'{element_info["role"]}:"{element_info["label"]}"',
                confidence=0.8,
                fallbacks=[]
            ))
        
        # Try class combination
        if element_info.get("classes"):
            classes = ".".join(element_info["classes"][:3])
            tag = element_info.get("tag", "*")
            selectors.append(Selector(
                selector_type=SelectorType.CSS,
                value=f"{tag}.{classes}",
                confidence=0.6,
                fallbacks=[]
            ))
        
        # Generate XPath from hierarchy
        if element_info.get("hierarchy"):
            xpath = self._generate_xpath_from_hierarchy(element_info["hierarchy"])
            selectors.append(Selector(
                selector_type=SelectorType.XPATH,
                value=xpath,
                confidence=0.5,
                fallbacks=[]
            ))
        
        if not selectors:
            # Fallback to generic position-based
            selectors.append(Selector(
                selector_type=SelectorType.XPATH,
                value=f'//{element_info.get("tag", "*")}[1]',
                confidence=0.2,
                fallbacks=[]
            ))
        
        # Sort by confidence and return best with fallbacks
        selectors.sort(key=lambda s: s.confidence, reverse=True)
        
        best = selectors[0]
        best.fallbacks = selectors[1:4]  # Keep top 3 as fallbacks
        
        logger.debug(f"Generated selector: {best.value} (confidence: {best.confidence})")
        return best
    
    def generate_from_screenshot(
        self,
        screenshot_path: str,
        click_position: Tuple[int, int],
        ocr_text: Optional[str] = None
    ) -> Selector:
        """
        Generate selector from screenshot and click position.
        
        Args:
            screenshot_path: Path to screenshot
            click_position: (x, y) click position
            ocr_text: OCR text at position
            
        Returns:
            Selector object
        """
        # This would integrate with UI element detection
        # For now, generate a position-based selector
        
        element_info = {
            "position": click_position,
            "text": ocr_text
        }
        
        if ocr_text:
            return Selector(
                selector_type=SelectorType.XPATH,
                value=f'//*[contains(text(), "{ocr_text[:30]}")]',
                confidence=0.6,
                fallbacks=[]
            )
        
        # Position-based fallback
        x, y = click_position
        return Selector(
            selector_type=SelectorType.XPATH,
            value=f'//body',  # Would need element detection
            confidence=0.2,
            fallbacks=[]
        )
    
    def validate_selector(
        self,
        selector: Selector,
        page_source: str
    ) -> bool:
        """
        Validate if selector matches in page source.
        
        Args:
            selector: Selector to validate
            page_source: HTML page source
            
        Returns:
            True if selector would match
        """
        # Simple validation - would need proper DOM parsing
        if selector.selector_type == SelectorType.ID:
            element_id = selector.value.lstrip("#")
            return f'id="{element_id}"' in page_source
        
        elif selector.selector_type == SelectorType.CSS:
            # Very basic CSS check
            if selector.value.startswith("["):
                attr = selector.value.strip("[]").split("=")[0]
                return attr in page_source
        
        return True  # Assume valid if can't check
    
    def _generate_xpath_from_hierarchy(
        self,
        hierarchy: List[Dict[str, Any]]
    ) -> str:
        """Generate XPath from element hierarchy."""
        parts = []
        
        for element in hierarchy:
            tag = element.get("tag", "*")
            index = element.get("index", 1)
            
            if element.get("id"):
                parts.append(f'{tag}[@id="{element["id"]}"]')
            elif element.get("class"):
                parts.append(f'{tag}[contains(@class, "{element["class"]}")]')
            else:
                parts.append(f'{tag}[{index}]')
        
        return "//" + "/".join(parts)
    
    def to_playwright(self, selector: Selector) -> str:
        """Convert selector to Playwright format."""
        if selector.selector_type == SelectorType.ID:
            return selector.value  # CSS format works
        elif selector.selector_type == SelectorType.ROLE:
            role, label = selector.value.split(":", 1)
            stripped_label = label.strip('"')
            return f'role={role}[name="{stripped_label}"]'
        elif selector.selector_type == SelectorType.TEXT:
            return f'text={selector.value}'
        elif selector.selector_type == SelectorType.XPATH:
            return f'xpath={selector.value}'
        else:
            return selector.value
    
    def to_selenium(self, selector: Selector) -> Tuple[str, str]:
        """Convert selector to Selenium By format."""
        type_map = {
            SelectorType.ID: "By.ID",
            SelectorType.NAME: "By.NAME",
            SelectorType.CLASS: "By.CLASS_NAME",
            SelectorType.XPATH: "By.XPATH",
            SelectorType.CSS: "By.CSS_SELECTOR",
        }
        
        by_type = type_map.get(selector.selector_type, "By.CSS_SELECTOR")
        value = selector.value
        
        # Clean up value for specific types
        if selector.selector_type == SelectorType.ID:
            value = value.lstrip("#")
        elif selector.selector_type == SelectorType.NAME:
            value = value.split('"')[1] if '"' in value else value
        
        return (by_type, value)

