"""
Contrast Analyzer - Color contrast checking for WCAG compliance.
Part of Feature: Accessibility Compliance Engine (v2.0)
"""

from typing import Tuple, List, Dict, Any
from dataclasses import dataclass
import colorsys


@dataclass
class ContrastResult:
    """Result of contrast analysis."""
    foreground: str
    background: str
    ratio: float
    level_aa: bool
    level_aaa: bool
    level_aa_large: bool
    level_aaa_large: bool


class ContrastAnalyzer:
    """
    Analyzes color contrast ratios for WCAG compliance.
    WCAG 2.2 requires:
    - Level AA: 4.5:1 for normal text, 3:1 for large text
    - Level AAA: 7:1 for normal text, 4.5:1 for large text
    """
    
    @staticmethod
    def calculate_contrast_ratio(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
        """
        Calculate contrast ratio between two colors.
        
        Args:
            color1: RGB tuple (0-255)
            color2: RGB tuple (0-255)
            
        Returns:
            Contrast ratio (1-21)
        """
        def get_luminance(rgb: Tuple[int, int, int]) -> float:
            """Calculate relative luminance."""
            r, g, b = [c / 255.0 for c in rgb]
            
            def adjust(c: float) -> float:
                if c <= 0.03928:
                    return c / 12.92
                return ((c + 0.055) / 1.055) ** 2.4
            
            r = adjust(r)
            g = adjust(g)
            b = adjust(b)
            
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        l1 = get_luminance(color1)
        l2 = get_luminance(color2)
        
        lighter = max(l1, l2)
        darker = min(l1, l2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def analyze_contrast(
        self,
        foreground: str,
        background: str
    ) -> ContrastResult:
        """
        Analyze contrast between foreground and background colors.
        
        Args:
            foreground: Hex color code (e.g., "#000000")
            background: Hex color code (e.g., "#FFFFFF")
            
        Returns:
            ContrastResult
        """
        fg_rgb = self.hex_to_rgb(foreground)
        bg_rgb = self.hex_to_rgb(background)
        
        ratio = self.calculate_contrast_ratio(fg_rgb, bg_rgb)
        
        return ContrastResult(
            foreground=foreground,
            background=background,
            ratio=ratio,
            level_aa=ratio >= 4.5,
            level_aaa=ratio >= 7.0,
            level_aa_large=ratio >= 3.0,
            level_aaa_large=ratio >= 4.5
        )
    
    def find_accessible_color(
        self,
        base_color: str,
        background: str,
        target_ratio: float = 4.5
    ) -> str:
        """
        Find an accessible color variant that meets contrast requirements.
        
        Args:
            base_color: Base hex color
            background: Background hex color
            target_ratio: Target contrast ratio
            
        Returns:
            Accessible hex color
        """
        base_rgb = self.hex_to_rgb(base_color)
        bg_rgb = self.hex_to_rgb(background)
        
        # Get background luminance
        def get_luminance(rgb):
            r, g, b = [c / 255.0 for c in rgb]
            def adjust(c):
                return (c / 12.92) if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
            return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)
        
        bg_lum = get_luminance(bg_rgb)
        
        # If background is light, darken foreground; if dark, lighten
        target_lum = bg_lum - (target_ratio - 1) / (target_ratio + 1) if bg_lum > 0.5 else bg_lum + (target_ratio - 1) / (target_ratio + 1)
        target_lum = max(0, min(1, target_lum))
        
        # Convert to RGB
        if bg_lum > 0.5:
            # Darken
            return "#000000"  # Simplest: use black
        else:
            # Lighten
            return "#FFFFFF"  # Simplest: use white

