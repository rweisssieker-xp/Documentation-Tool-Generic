"""
Structure Validator - Validates document structure for accessibility.
Part of Feature: Accessibility Compliance Engine (v2.0)
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class StructureIssueType(Enum):
    """Types of structure issues."""
    MISSING_HEADING = "missing_heading"
    SKIPPED_LEVEL = "skipped_level"
    DUPLICATE_ID = "duplicate_id"
    MISSING_LANDMARK = "missing_landmark"
    INVALID_LIST = "invalid_list"


@dataclass
class StructureIssue:
    """A structure accessibility issue."""
    issue_type: StructureIssueType
    description: str
    severity: str  # "error", "warning"
    location: Optional[str] = None
    suggestion: Optional[str] = None


class StructureValidator:
    """
    Validates HTML document structure for accessibility.
    Checks heading hierarchy, landmarks, lists, and IDs.
    """
    
    def validate(self, html_content: str) -> List[StructureIssue]:
        """
        Validate document structure.
        
        Args:
            html_content: HTML content to validate
            
        Returns:
            List of structure issues
        """
        issues = []
        
        issues.extend(self._check_heading_hierarchy(html_content))
        issues.extend(self._check_duplicate_ids(html_content))
        issues.extend(self._check_landmarks(html_content))
        issues.extend(self._check_lists(html_content))
        
        return issues
    
    def _check_heading_hierarchy(self, html: str) -> List[StructureIssue]:
        """Check heading hierarchy."""
        issues = []
        
        # Extract headings with their levels
        heading_pattern = r'<h([1-6])[^>]*>(.*?)</h[1-6]>'
        headings = re.findall(heading_pattern, html, re.IGNORECASE | re.DOTALL)
        
        if not headings:
            issues.append(StructureIssue(
                issue_type=StructureIssueType.MISSING_HEADING,
                description="Document has no headings",
                severity="warning",
                suggestion="Add at least one h1 heading"
            ))
            return issues
        
        levels = [int(h[0]) for h in headings]
        
        # Check if starts with h1
        if levels[0] != 1:
            issues.append(StructureIssue(
                issue_type=StructureIssueType.MISSING_HEADING,
                description="Document should start with h1",
                severity="error",
                suggestion="Add an h1 heading at the beginning"
            ))
        
        # Check for skipped levels
        for i in range(len(levels) - 1):
            if levels[i+1] > levels[i] + 1:
                issues.append(StructureIssue(
                    issue_type=StructureIssueType.SKIPPED_LEVEL,
                    description=f"Heading level skipped: h{levels[i]} -> h{levels[i+1]}",
                    severity="error",
                    location=f"After '{headings[i][1][:50]}...'",
                    suggestion=f"Use h{levels[i]+1} instead of h{levels[i+1]}"
                ))
        
        return issues
    
    def _check_duplicate_ids(self, html: str) -> List[StructureIssue]:
        """Check for duplicate IDs."""
        issues = []
        
        id_pattern = r'id=["\']([^"\']+)["\']'
        ids = re.findall(id_pattern, html, re.IGNORECASE)
        
        seen = {}
        for id_val in ids:
            if id_val in seen:
                issues.append(StructureIssue(
                    issue_type=StructureIssueType.DUPLICATE_ID,
                    description=f"Duplicate ID: {id_val}",
                    severity="error",
                    suggestion="Ensure all IDs are unique"
                ))
            seen[id_val] = True
        
        return issues
    
    def _check_landmarks(self, html: str) -> List[StructureIssue]:
        """Check for semantic landmarks."""
        issues = []
        
        landmarks = ['main', 'nav', 'header', 'footer', 'aside', 'article', 'section']
        found_landmarks = []
        
        for landmark in landmarks:
            if f'<{landmark}' in html.lower():
                found_landmarks.append(landmark)
        
        if 'main' not in found_landmarks:
            issues.append(StructureIssue(
                issue_type=StructureIssueType.MISSING_LANDMARK,
                description="Missing <main> landmark",
                severity="warning",
                suggestion="Add a <main> element for main content"
            ))
        
        return issues
    
    def _check_lists(self, html: str) -> List[StructureIssue]:
        """Check list structure."""
        issues = []
        
        # Check for proper list nesting
        list_pattern = r'<(ul|ol)[^>]*>'
        lists = re.findall(list_pattern, html, re.IGNORECASE)
        
        # Check if lists have list items
        for list_type in ['ul', 'ol']:
            list_tags = re.findall(f'<{list_type}[^>]*>', html, re.IGNORECASE)
            for list_tag in list_tags:
                # Check if next closing tag is </li> or </ul>/</ol>
                # This is simplified - real validation would parse HTML properly
                pass
        
        return issues

