"""
Tests for Accessibility Compliance Engine Module
"""

import pytest
from pathlib import Path
import tempfile

from src.accessibility.wcag_auditor import WCAGAuditor, WCAGLevel
from src.accessibility.contrast_analyzer import ContrastAnalyzer
from src.accessibility.structure_validator import StructureValidator, StructureIssueType
from src.accessibility.auto_remediation import AutoRemediation
from src.accessibility.compliance_report import ComplianceReportGenerator


class TestWCAGAuditor:
    """Tests for WCAGAuditor class."""
    
    def test_wcag_auditor_initialization(self):
        """Test WCAGAuditor initialization."""
        auditor = WCAGAuditor(level=WCAGLevel.AA)
        assert auditor.level == WCAGLevel.AA
    
    def test_audit_html_missing_alt(self):
        """Test auditing HTML with missing alt text."""
        auditor = WCAGAuditor()
        
        html = '<img src="test.png">'
        result = auditor.audit_html(html)
        
        assert len(result.violations) > 0
        assert any(v.rule_id == "image-alt" for v in result.violations)
    
    def test_audit_html_heading_hierarchy(self):
        """Test heading hierarchy check."""
        auditor = WCAGAuditor()
        
        html = '<h1>Title</h1><h3>Subtitle</h3>'  # Skipped h2
        result = auditor.audit_html(html)
        
        assert len(result.violations) > 0
    
    def test_audit_file(self, tmp_path):
        """Test auditing a file."""
        auditor = WCAGAuditor()
        
        html_file = tmp_path / "test.html"
        html_file.write_text('<img src="test.png">', encoding='utf-8')
        
        result = auditor.audit_file(html_file)
        assert result is not None
        assert isinstance(result.score, float)


class TestContrastAnalyzer:
    """Tests for ContrastAnalyzer class."""
    
    def test_contrast_analyzer_initialization(self):
        """Test ContrastAnalyzer initialization."""
        analyzer = ContrastAnalyzer()
        assert analyzer is not None
    
    def test_calculate_contrast_ratio(self):
        """Test contrast ratio calculation."""
        analyzer = ContrastAnalyzer()
        
        # Black on white should have high contrast
        ratio = analyzer.calculate_contrast_ratio((0, 0, 0), (255, 255, 255))
        assert ratio >= 20.0
        
        # White on white should have low contrast
        ratio = analyzer.calculate_contrast_ratio((255, 255, 255), (255, 255, 255))
        assert ratio == 1.0
    
    def test_analyze_contrast(self):
        """Test contrast analysis."""
        analyzer = ContrastAnalyzer()
        
        result = analyzer.analyze_contrast("#000000", "#FFFFFF")
        assert result.ratio >= 20.0
        assert result.level_aa == True
        assert result.level_aaa == True


class TestStructureValidator:
    """Tests for StructureValidator class."""
    
    def test_structure_validator_initialization(self):
        """Test StructureValidator initialization."""
        validator = StructureValidator()
        assert validator is not None
    
    def test_validate_missing_headings(self):
        """Test validation with missing headings."""
        validator = StructureValidator()
        
        html = "<p>No headings</p>"
        issues = validator.validate(html)
        
        assert len(issues) > 0
        assert any(i.issue_type == StructureIssueType.MISSING_HEADING for i in issues)
    
    def test_validate_heading_hierarchy(self):
        """Test heading hierarchy validation."""
        validator = StructureValidator()
        
        html = "<h1>Title</h1><h3>Subtitle</h3>"
        issues = validator.validate(html)
        
        assert any(i.issue_type == StructureIssueType.SKIPPED_LEVEL for i in issues)
    
    def test_validate_duplicate_ids(self):
        """Test duplicate ID detection."""
        validator = StructureValidator()
        
        html = '<div id="test"></div><div id="test"></div>'
        issues = validator.validate(html)
        
        assert any(i.issue_type == StructureIssueType.DUPLICATE_ID for i in issues)


class TestAutoRemediation:
    """Tests for AutoRemediation class."""
    
    def test_auto_remediation_initialization(self):
        """Test AutoRemediation initialization."""
        remediation = AutoRemediation()
        assert remediation is not None
    
    def test_fix_missing_alt_text(self):
        """Test fixing missing alt text."""
        remediation = AutoRemediation()
        
        html = '<img src="test.png">'
        violations = [
            type('Violation', (), {
                'rule_id': 'image-alt',
                'description': 'Missing alt',
                'element': '<img src="test.png">'
            })()
        ]
        
        fixed = remediation.remediate_html(html, violations)
        assert 'alt=' in fixed.lower()


class TestComplianceReport:
    """Tests for ComplianceReportGenerator class."""
    
    def test_generate_report(self):
        """Test report generation."""
        generator = ComplianceReportGenerator()
        
        from src.accessibility.wcag_auditor import WCAGAuditResult, WCAGViolation
        
        audit_result = WCAGAuditResult(
            level=WCAGLevel.AA,
            violations=[],
            passes=10,
            incomplete=0,
            inapplicable=0,
            score=100.0
        )
        
        report = generator.generate_report(audit_result, [])
        assert report.compliant == True
        assert report.score == 100.0
    
    def test_export_json(self, tmp_path):
        """Test JSON export."""
        generator = ComplianceReportGenerator()
        
        from src.accessibility.wcag_auditor import WCAGAuditResult
        
        audit_result = WCAGAuditResult(
            level=WCAGLevel.AA,
            violations=[],
            passes=10,
            incomplete=0,
            inapplicable=0,
            score=100.0
        )
        
        report = generator.generate_report(audit_result, [])
        output_path = tmp_path / "report.json"
        
        result = generator.export_json(report, output_path)
        assert result == True
        assert output_path.exists()
    
    def test_export_html(self, tmp_path):
        """Test HTML export."""
        generator = ComplianceReportGenerator()
        
        from src.accessibility.wcag_auditor import WCAGAuditResult
        
        audit_result = WCAGAuditResult(
            level=WCAGLevel.AA,
            violations=[],
            passes=10,
            incomplete=0,
            inapplicable=0,
            score=100.0
        )
        
        report = generator.generate_report(audit_result, [])
        output_path = tmp_path / "report.html"
        
        result = generator.export_html(report, output_path)
        assert result == True
        assert output_path.exists()
        assert "WCAG" in output_path.read_text()

