"""
Auto Remediation - Automatically fixes accessibility issues.
Part of Feature: Accessibility Compliance Engine (v2.0)
"""

import re
from typing import List, Dict, Any
from pathlib import Path

from src.accessibility.wcag_auditor import WCAGViolation
from src.accessibility.alt_text_generator import AltTextGenerator
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AutoRemediation:
    """
    Automatically fixes accessibility issues in HTML documents.
    Applies fixes for common WCAG violations.
    """
    
    def __init__(self):
        """Initialize auto remediation."""
        self.alt_generator = AltTextGenerator()
    
    def remediate_html(
        self,
        html_content: str,
        violations: List[WCAGViolation],
        image_paths: Dict[str, Path] = None
    ) -> str:
        """
        Remediate HTML content based on violations.
        
        Args:
            html_content: Original HTML
            violations: List of WCAG violations
            image_paths: Mapping of image src to file paths
            
        Returns:
            Remediated HTML
        """
        remediated = html_content
        image_paths = image_paths or {}
        
        for violation in violations:
            if violation.rule_id == "image-alt":
                remediated = self._fix_missing_alt_text(remediated, violation, image_paths)
            elif violation.rule_id == "heading-order":
                remediated = self._fix_heading_order(remediated, violation)
            elif violation.rule_id == "link-purpose":
                remediated = self._fix_link_text(remediated, violation)
            elif violation.rule_id == "label-in-name":
                remediated = self._fix_missing_label(remediated, violation)
        
        return remediated
    
    def _fix_missing_alt_text(
        self,
        html: str,
        violation: WCAGViolation,
        image_paths: Dict[str, Path]
    ) -> str:
        """Fix missing alt text on images."""
        # Find the img tag
        img_match = re.search(r'<img[^>]+>', html, re.IGNORECASE)
        if not img_match:
            return html
        
        img_tag = img_match.group(0)
        
        # Extract src
        src_match = re.search(r'src=["\']([^"\']+)["\']', img_tag, re.IGNORECASE)
        if not src_match:
            return html
        
        src = src_match.group(1)
        
        # Generate alt text
        image_path = image_paths.get(src)
        if image_path and image_path.exists():
            alt_text = self.alt_generator.generate_alt_text(image_path)
        else:
            alt_text = "Documentation image"
        
        # Add or update alt attribute
        if 'alt=' in img_tag.lower():
            # Replace existing alt
            img_tag_fixed = re.sub(
                r'alt=["\'][^"\']*["\']',
                f'alt="{alt_text}"',
                img_tag,
                flags=re.IGNORECASE
            )
        else:
            # Insert alt before closing >
            img_tag_fixed = img_tag[:-1] + f' alt="{alt_text}">'
        
        return html.replace(img_tag, img_tag_fixed)
    
    def _fix_heading_order(self, html: str, violation: WCAGViolation) -> str:
        """Fix heading order issues."""
        # This would require more sophisticated parsing
        # For now, just log the issue
        logger.info(f"Heading order issue detected: {violation.description}")
        return html
    
    def _fix_link_text(self, html: str, violation: WCAGViolation) -> str:
        """Fix generic link text."""
        # Find generic link texts and suggest improvements
        generic_texts = ['click here', 'read more', 'here', 'link']
        
        for generic in generic_texts:
            pattern = f'<a[^>]*>{re.escape(generic)}</a>'
            matches = re.finditer(pattern, html, re.IGNORECASE)
            
            for match in matches:
                # Extract href for context
                link_tag = match.group(0)
                href_match = re.search(r'href=["\']([^"\']+)["\']', link_tag, re.IGNORECASE)
                if href_match:
                    href = href_match.group(1)
                    # Suggest better text based on href
                    better_text = href.split('/')[-1].replace('-', ' ').replace('_', ' ')
                    better_text = better_text.title() if better_text else "Learn more"
                    
                    fixed_link = link_tag.replace(generic, better_text)
                    html = html.replace(link_tag, fixed_link)
        
        return html
    
    def _fix_missing_label(self, html: str, violation: WCAGViolation) -> str:
        """Fix missing labels for form inputs."""
        # Find inputs without labels
        input_pattern = r'<input([^>]+)>'
        
        def add_label(match):
            input_tag = match.group(0)
            input_attrs = match.group(1)
            
            # Extract id
            id_match = re.search(r'id=["\']([^"\']+)["\']', input_attrs, re.IGNORECASE)
            if not id_match:
                return input_tag
            
            input_id = id_match.group(1)
            
            # Check if label already exists
            label_pattern = f'<label[^>]*for=["\']{re.escape(input_id)}["\']'
            if re.search(label_pattern, html, re.IGNORECASE):
                return input_tag
            
            # Extract placeholder or name for label text
            placeholder_match = re.search(r'placeholder=["\']([^"\']+)["\']', input_attrs, re.IGNORECASE)
            name_match = re.search(r'name=["\']([^"\']+)["\']', input_attrs, re.IGNORECASE)
            
            label_text = placeholder_match.group(1) if placeholder_match else (
                name_match.group(1).replace('_', ' ').title() if name_match else "Input"
            )
            
            label = f'<label for="{input_id}">{label_text}</label>\n'
            return label + input_tag
        
        return re.sub(input_pattern, add_label, html, flags=re.IGNORECASE)

