"""
WCAG Auditor - WCAG 2.2 compliance checking.
Part of Feature: Accessibility Compliance Engine (v2.0)
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

try:
    from axe_selenium_python import Axe
    AXE_AVAILABLE = True
except ImportError:
    AXE_AVAILABLE = False

from src.utils.logger import get_logger

logger = get_logger(__name__)


class WCAGLevel(Enum):
    """WCAG conformance levels."""
    A = "A"
    AA = "AA"
    AAA = "AAA"


@dataclass
class WCAGViolation:
    """A WCAG violation."""
    rule_id: str
    description: str
    impact: str  # "critical", "serious", "moderate", "minor"
    element: Optional[str] = None
    help_url: Optional[str] = None
    html: Optional[str] = None


@dataclass
class WCAGAuditResult:
    """Result of WCAG audit."""
    level: WCAGLevel
    violations: List[WCAGViolation]
    passes: int
    incomplete: int
    inapplicable: int
    score: float  # 0-100


class WCAGAuditor:
    """
    Audits documentation for WCAG 2.2 compliance.
    Checks accessibility standards and generates reports.
    """
    
    def __init__(self, level: WCAGLevel = WCAGLevel.AA):
        """
        Initialize WCAG auditor.
        
        Args:
            level: WCAG conformance level to check
        """
        self.level = level
        self.axe_available = AXE_AVAILABLE
    
    def audit_html(self, html_content: str) -> WCAGAuditResult:
        """
        Audit HTML content for WCAG compliance.
        
        Args:
            html_content: HTML content to audit
            
        Returns:
            WCAGAuditResult with violations and score
        """
        violations = []
        
        # Basic checks without axe-core
        violations.extend(self._check_images(html_content))
        violations.extend(self._check_headings(html_content))
        violations.extend(self._check_links(html_content))
        violations.extend(self._check_forms(html_content))
        violations.extend(self._check_color_contrast(html_content))
        
        # Calculate score
        total_checks = len(violations) + 10  # Assume some passes
        passes = total_checks - len(violations)
        score = (passes / total_checks * 100) if total_checks > 0 else 100
        
        return WCAGAuditResult(
            level=self.level,
            violations=violations,
            passes=passes,
            incomplete=0,
            inapplicable=0,
            score=score
        )
    
    def audit_file(self, file_path: Path) -> WCAGAuditResult:
        """
        Audit file for WCAG compliance.
        
        Args:
            file_path: Path to HTML file
            
        Returns:
            WCAGAuditResult
        """
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return WCAGAuditResult(
                level=self.level,
                violations=[],
                passes=0,
                incomplete=0,
                inapplicable=0,
                score=0
            )
        
        html_content = file_path.read_text(encoding='utf-8')
        return self.audit_html(html_content)
    
    def _check_images(self, html: str) -> List[WCAGViolation]:
        """Check for missing alt text on images."""
        violations = []
        
        # Simple regex check for img tags without alt
        import re
        img_pattern = r'<img[^>]+>'
        imgs = re.findall(img_pattern, html, re.IGNORECASE)
        
        for img in imgs:
            if 'alt=' not in img.lower() or 'alt=""' in img.lower():
                violations.append(WCAGViolation(
                    rule_id="image-alt",
                    description="Image missing alt text",
                    impact="serious",
                    element=img[:100],
                    help_url="https://www.w3.org/WAI/WCAG22/Understanding/non-text-content.html"
                ))
        
        return violations
    
    def _check_headings(self, html: str) -> List[WCAGViolation]:
        """Check heading hierarchy."""
        violations = []
        
        import re
        headings = re.findall(r'<h([1-6])[^>]*>', html, re.IGNORECASE)
        
        if headings:
            levels = [int(h) for h in headings]
            # Check for skipped levels (e.g., h1 -> h3)
            for i in range(len(levels) - 1):
                if levels[i+1] > levels[i] + 1:
                    violations.append(WCAGViolation(
                        rule_id="heading-order",
                        description=f"Heading level skipped: h{levels[i]} -> h{levels[i+1]}",
                        impact="moderate",
                        help_url="https://www.w3.org/WAI/WCAG22/Understanding/headings-and-labels.html"
                    ))
        
        return violations
    
    def _check_links(self, html: str) -> List[WCAGViolation]:
        """Check link accessibility."""
        violations = []
        
        import re
        links = re.findall(r'<a[^>]*>(.*?)</a>', html, re.IGNORECASE | re.DOTALL)
        
        for link_text in links:
            link_text = re.sub(r'<[^>]+>', '', link_text).strip()
            # Check for generic link text
            if link_text.lower() in ['click here', 'read more', 'here', 'link']:
                violations.append(WCAGViolation(
                    rule_id="link-purpose",
                    description=f"Generic link text: '{link_text}'",
                    impact="moderate",
                    help_url="https://www.w3.org/WAI/WCAG22/Understanding/link-purpose-in-context.html"
                ))
        
        return violations
    
    def _check_forms(self, html: str) -> List[WCAGViolation]:
        """Check form accessibility."""
        violations = []
        
        import re
        inputs = re.findall(r'<input[^>]+>', html, re.IGNORECASE)
        
        for inp in inputs:
            # Check for inputs without labels
            if 'id=' in inp.lower() and 'label' not in html.lower():
                input_id_match = re.search(r'id=["\']([^"\']+)["\']', inp, re.IGNORECASE)
                if input_id_match:
                    input_id = input_id_match.group(1)
                    label_pattern = f'<label[^>]*for=["\']{input_id}["\']'
                    if not re.search(label_pattern, html, re.IGNORECASE):
                        violations.append(WCAGViolation(
                            rule_id="label-in-name",
                            description=f"Input without associated label: {input_id}",
                            impact="serious",
                            help_url="https://www.w3.org/WAI/WCAG22/Understanding/label-in-name.html"
                        ))
        
        return violations
    
    def _check_color_contrast(self, html: str) -> List[WCAGViolation]:
        """Check color contrast (basic check)."""
        # This is a placeholder - real contrast checking requires CSS parsing
        # and color calculation
        violations = []
        
        # Check for inline styles with color
        import re
        style_pattern = r'style=["\']([^"\']*color[^"\']*)["\']'
        styles = re.findall(style_pattern, html, re.IGNORECASE)
        
        if styles:
            violations.append(WCAGViolation(
                rule_id="contrast-minimum",
                description="Color contrast should be verified (inline styles detected)",
                impact="moderate",
                help_url="https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html"
            ))
        
        return violations

