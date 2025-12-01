"""
Compliance Report - Generates WCAG compliance reports.
Part of Feature: Accessibility Compliance Engine (v2.0)
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import json

from src.accessibility.wcag_auditor import WCAGAuditResult, WCAGViolation
from src.accessibility.structure_validator import StructureIssue
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ComplianceReport:
    """WCAG compliance report."""
    timestamp: datetime
    file_path: Optional[str]
    level: str
    score: float
    violations: List[Dict[str, Any]]
    structure_issues: List[Dict[str, Any]]
    recommendations: List[str]
    compliant: bool


class ComplianceReportGenerator:
    """
    Generates WCAG compliance reports in various formats.
    """
    
    def generate_report(
        self,
        audit_result: WCAGAuditResult,
        structure_issues: List[StructureIssue],
        file_path: Optional[str] = None
    ) -> ComplianceReport:
        """
        Generate compliance report.
        
        Args:
            audit_result: WCAG audit result
            structure_issues: Structure validation issues
            file_path: Optional file path
            
        Returns:
            ComplianceReport
        """
        # Determine compliance
        compliant = (
            len(audit_result.violations) == 0 and
            len([i for i in structure_issues if i.severity == "error"]) == 0
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(audit_result, structure_issues)
        
        return ComplianceReport(
            timestamp=datetime.now(),
            file_path=file_path,
            level=audit_result.level.value,
            score=audit_result.score,
            violations=[self._violation_to_dict(v) for v in audit_result.violations],
            structure_issues=[self._issue_to_dict(i) for i in structure_issues],
            recommendations=recommendations,
            compliant=compliant
        )
    
    def export_json(self, report: ComplianceReport, output_path: Path) -> bool:
        """Export report as JSON."""
        try:
            data = asdict(report)
            data['timestamp'] = report.timestamp.isoformat()
            
            output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
            return True
        except Exception as e:
            logger.error(f"Error exporting JSON report: {e}")
            return False
    
    def export_html(self, report: ComplianceReport, output_path: Path) -> bool:
        """Export report as HTML."""
        try:
            html = self._generate_html_report(report)
            output_path.write_text(html, encoding='utf-8')
            return True
        except Exception as e:
            logger.error(f"Error exporting HTML report: {e}")
            return False
    
    def _violation_to_dict(self, violation: WCAGViolation) -> Dict[str, Any]:
        """Convert violation to dictionary."""
        return {
            "rule_id": violation.rule_id,
            "description": violation.description,
            "impact": violation.impact,
            "element": violation.element,
            "help_url": violation.help_url
        }
    
    def _issue_to_dict(self, issue: StructureIssue) -> Dict[str, Any]:
        """Convert structure issue to dictionary."""
        return {
            "type": issue.issue_type.value,
            "description": issue.description,
            "severity": issue.severity,
            "location": issue.location,
            "suggestion": issue.suggestion
        }
    
    def _generate_recommendations(
        self,
        audit_result: WCAGAuditResult,
        structure_issues: List[StructureIssue]
    ) -> List[str]:
        """Generate recommendations based on violations."""
        recommendations = []
        
        # Count violations by type
        violation_types = {}
        for v in audit_result.violations:
            violation_types[v.rule_id] = violation_types.get(v.rule_id, 0) + 1
        
        if "image-alt" in violation_types:
            recommendations.append(
                f"Add alt text to {violation_types['image-alt']} image(s) for screen reader accessibility"
            )
        
        if "link-purpose" in violation_types:
            recommendations.append(
                f"Replace generic link text in {violation_types['link-purpose']} link(s) with descriptive text"
            )
        
        if "label-in-name" in violation_types:
            recommendations.append(
                f"Add labels to {violation_types['label-in-name']} form input(s)"
            )
        
        error_issues = [i for i in structure_issues if i.severity == "error"]
        if error_issues:
            recommendations.append(
                f"Fix {len(error_issues)} critical structure issue(s) (heading hierarchy, duplicate IDs)"
            )
        
        if audit_result.score < 80:
            recommendations.append(
                f"Overall accessibility score is {audit_result.score:.1f}%. "
                "Aim for 90%+ for WCAG AA compliance."
            )
        
        return recommendations
    
    def _generate_html_report(self, report: ComplianceReport) -> str:
        """Generate HTML report."""
        status_color = "#28a745" if report.compliant else "#dc3545"
        status_text = "COMPLIANT" if report.compliant else "NON-COMPLIANT"
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WCAG Compliance Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
        .status {{ color: {status_color}; font-weight: bold; font-size: 1.2em; }}
        .score {{ font-size: 2em; font-weight: bold; color: {status_color}; }}
        .section {{ margin: 20px 0; }}
        .violation {{ background: #fff3cd; padding: 10px; margin: 5px 0; border-left: 4px solid #ffc107; }}
        .error {{ background: #f8d7da; border-left-color: #dc3545; }}
        .recommendation {{ background: #d1ecf1; padding: 10px; margin: 5px 0; border-left: 4px solid #17a2b8; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>WCAG {report.level} Compliance Report</h1>
        <div class="status">Status: {status_text}</div>
        <div class="score">Score: {report.score:.1f}%</div>
        <p>Generated: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
        {f'<p>File: {report.file_path}</p>' if report.file_path else ''}
    </div>
    
    <div class="section">
        <h2>Violations ({len(report.violations)})</h2>
"""
        
        for violation in report.violations:
            html += f"""
        <div class="violation {'error' if violation['impact'] in ['critical', 'serious'] else ''}">
            <strong>{violation['rule_id']}</strong>: {violation['description']}<br>
            Impact: {violation['impact']}
            {f"<br><a href='{violation['help_url']}'>Learn more</a>" if violation.get('help_url') else ''}
        </div>
"""
        
        html += """
    </div>
    
    <div class="section">
        <h2>Structure Issues ({len(report.structure_issues)})</h2>
"""
        
        for issue in report.structure_issues:
            html += f"""
        <div class="violation {'error' if issue['severity'] == 'error' else ''}">
            <strong>{issue['type']}</strong>: {issue['description']}<br>
            {f"Suggestion: {issue['suggestion']}" if issue.get('suggestion') else ''}
        </div>
"""
        
        html += f"""
    </div>
    
    <div class="section">
        <h2>Recommendations</h2>
"""
        
        for rec in report.recommendations:
            html += f'        <div class="recommendation">{rec}</div>\n'
        
        html += """
    </div>
</body>
</html>
"""
        
        return html

