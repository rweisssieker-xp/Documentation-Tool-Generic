"""
Qualitätsprüfung & Suggestions: Prüft Dokumentationsqualität und gibt Verbesserungsvorschläge
"""

from typing import List, Dict, Optional
from pathlib import Path
from PIL import Image
import os

from src.utils.logger import get_logger

logger = get_logger(__name__)


class QualityChecker:
    """Prüft Qualität von Dokumentation und gibt Vorschläge"""
    
    def __init__(self):
        """Initialisiert den Quality Checker"""
        pass
    
    def check_quality(self, steps: List[Dict]) -> Dict:
        """
        Prüft Qualität der Dokumentation
        
        Args:
            steps: Liste von Schritten
            
        Returns:
            Dictionary mit Qualitäts-Metriken und Vorschlägen
        """
        metrics = {
            'overall_score': 0.0,
            'screenshot_quality': [],
            'text_quality': [],
            'consistency_issues': [],
            'suggestions': [],
            'warnings': [],
            'errors': []
        }
        
        if not steps:
            metrics['errors'].append("Keine Schritte vorhanden")
            return metrics
        
        # Prüfe Screenshot-Qualität
        screenshot_metrics = self._check_screenshot_quality(steps)
        metrics['screenshot_quality'] = screenshot_metrics
        
        # Prüfe Text-Qualität
        text_metrics = self._check_text_quality(steps)
        metrics['text_quality'] = text_metrics
        
        # Prüfe Konsistenz
        consistency_issues = self._check_consistency(steps)
        metrics['consistency_issues'] = consistency_issues
        
        # Generiere Vorschläge
        suggestions = self._generate_suggestions(steps, metrics)
        metrics['suggestions'] = suggestions
        
        # Berechne Gesamt-Score
        metrics['overall_score'] = self._calculate_overall_score(metrics)
        
        return metrics
    
    def _check_screenshot_quality(self, steps: List[Dict]) -> List[Dict]:
        """Prüft Screenshot-Qualität"""
        issues = []
        
        for step in steps:
            screenshot_path = Path(step.get('screenshot_path', ''))
            
            if not screenshot_path.exists():
                issues.append({
                    'step_number': step.get('step_number', '?'),
                    'type': 'missing_screenshot',
                    'severity': 'error',
                    'message': 'Screenshot fehlt'
                })
                continue
            
            try:
                img = Image.open(screenshot_path)
                width, height = img.size
                
                # Prüfe Auflösung
                if width < 800 or height < 600:
                    issues.append({
                        'step_number': step.get('step_number', '?'),
                        'type': 'low_resolution',
                        'severity': 'warning',
                        'message': f'Niedrige Auflösung: {width}x{height}'
                    })
                
                # Prüfe Bildschärfe (vereinfacht)
                # In vollständiger Implementierung würde man hier Edge-Detection verwenden
                img_gray = img.convert('L')
                # Berechne Varianz als Maß für Schärfe
                import numpy as np
                img_array = np.array(img_gray)
                variance = np.var(img_array)
                
                if variance < 500:  # Niedrige Varianz = möglicherweise unscharf
                    issues.append({
                        'step_number': step.get('step_number', '?'),
                        'type': 'blurry',
                        'severity': 'warning',
                        'message': 'Möglicherweise unscharf'
                    })
            
            except Exception as e:
                issues.append({
                    'step_number': step.get('step_number', '?'),
                    'type': 'invalid_image',
                    'severity': 'error',
                    'message': f'Fehler beim Laden: {str(e)}'
                })
        
        return issues
    
    def _check_text_quality(self, steps: List[Dict]) -> List[Dict]:
        """Prüft Text-Qualität"""
        issues = []
        
        for step in steps:
            description = step.get('description', '')
            step_number = step.get('step_number', '?')
            
            # Prüfe ob Beschreibung vorhanden
            if not description or description.strip() == '':
                issues.append({
                    'step_number': step_number,
                    'type': 'missing_description',
                    'severity': 'error',
                    'message': 'Beschreibung fehlt'
                })
                continue
            
            # Prüfe Mindestlänge
            if len(description) < 20:
                issues.append({
                    'step_number': step_number,
                    'type': 'too_short',
                    'severity': 'warning',
                    'message': f'Beschreibung zu kurz ({len(description)} Zeichen)'
                })
            
            # Prüfe maximale Länge
            if len(description) > 1000:
                issues.append({
                    'step_number': step_number,
                    'type': 'too_long',
                    'severity': 'warning',
                    'message': f'Beschreibung sehr lang ({len(description)} Zeichen)'
                })
            
            # Prüfe auf häufige Probleme
            if description.lower().startswith('schritt'):
                issues.append({
                    'step_number': step_number,
                    'type': 'redundant_prefix',
                    'severity': 'info',
                    'message': 'Beschreibung beginnt mit "Schritt" (redundant)'
                })
        
        return issues
    
    def _check_consistency(self, steps: List[Dict]) -> List[Dict]:
        """Prüft Konsistenz zwischen Schritten"""
        issues = []
        
        if len(steps) < 2:
            return issues
        
        # Prüfe Schritt-Nummerierung
        expected_number = 1
        for step in steps:
            step_number = step.get('step_number', 0)
            if step_number != expected_number:
                issues.append({
                    'type': 'numbering_inconsistency',
                    'severity': 'warning',
                    'message': f'Schritt-Nummerierung inkonsistent: erwartet {expected_number}, gefunden {step_number}'
                })
            expected_number += 1
        
        # Prüfe Fenster-Titel-Konsistenz
        window_titles = {}
        for step in steps:
            title = step.get('window_title', '')
            if title:
                window_titles[title] = window_titles.get(title, 0) + 1
        
        # Prüfe ob zu viele verschiedene Fenster
        unique_windows = len(window_titles)
        if unique_windows > len(steps) * 0.8:
            issues.append({
                'type': 'too_many_windows',
                'severity': 'info',
                'message': f'Viele verschiedene Fenster ({unique_windows} von {len(steps)} Schritten)'
            })
        
        return issues
    
    def _generate_suggestions(self, steps: List[Dict], metrics: Dict) -> List[Dict]:
        """Generiert Verbesserungsvorschläge"""
        suggestions = []
        
        # Screenshot-Vorschläge
        screenshot_issues = [i for i in metrics['screenshot_quality'] if i['severity'] in ['error', 'warning']]
        if screenshot_issues:
            suggestions.append({
                'type': 'screenshot_quality',
                'priority': 'high' if any(i['severity'] == 'error' for i in screenshot_issues) else 'medium',
                'message': f'{len(screenshot_issues)} Screenshot-Qualitätsprobleme gefunden',
                'action': 'Überprüfen Sie die Screenshots und stellen Sie sicher, dass sie klar und scharf sind'
            })
        
        # Text-Vorschläge
        text_issues = [i for i in metrics['text_quality'] if i['severity'] in ['error', 'warning']]
        if text_issues:
            suggestions.append({
                'type': 'text_quality',
                'priority': 'high' if any(i['severity'] == 'error' for i in text_issues) else 'medium',
                'message': f'{len(text_issues)} Text-Qualitätsprobleme gefunden',
                'action': 'Überprüfen Sie die Beschreibungen und stellen Sie sicher, dass sie vollständig und klar sind'
            })
        
        # Konsistenz-Vorschläge
        consistency_issues = metrics['consistency_issues']
        if consistency_issues:
            suggestions.append({
                'type': 'consistency',
                'priority': 'medium',
                'message': f'{len(consistency_issues)} Konsistenzprobleme gefunden',
                'action': 'Überprüfen Sie die Konsistenz zwischen den Schritten'
            })
        
        # Allgemeine Vorschläge
        if len(steps) < 3:
            suggestions.append({
                'type': 'too_few_steps',
                'priority': 'low',
                'message': 'Nur wenige Schritte vorhanden',
                'action': 'Erwägen Sie zusätzliche Schritte für vollständigere Dokumentation'
            })
        
        return suggestions
    
    def _calculate_overall_score(self, metrics: Dict) -> float:
        """Berechnet Gesamt-Qualitäts-Score (0.0-1.0)"""
        score = 1.0
        
        # Abzüge für Fehler
        error_count = len([i for i in metrics['screenshot_quality'] if i['severity'] == 'error'])
        error_count += len([i for i in metrics['text_quality'] if i['severity'] == 'error'])
        error_count += len(metrics['errors'])
        
        score -= error_count * 0.2
        
        # Abzüge für Warnungen
        warning_count = len([i for i in metrics['screenshot_quality'] if i['severity'] == 'warning'])
        warning_count += len([i for i in metrics['text_quality'] if i['severity'] == 'warning'])
        warning_count += len(metrics['warnings'])
        
        score -= warning_count * 0.05
        
        # Begrenze auf 0.0-1.0
        score = max(0.0, min(1.0, score))
        
        return score
    
    def get_quality_report(self, steps: List[Dict]) -> str:
        """
        Generiert lesbaren Qualitätsbericht
        
        Args:
            steps: Liste von Schritten
            
        Returns:
            Formatierter Bericht als String
        """
        metrics = self.check_quality(steps)
        
        report_lines = [
            "=" * 60,
            "QUALITÄTSBERICHT",
            "=" * 60,
            f"Gesamt-Score: {metrics['overall_score']:.2%}",
            "",
            f"Schritte geprüft: {len(steps)}",
            "",
        ]
        
        # Screenshot-Qualität
        screenshot_issues = metrics['screenshot_quality']
        if screenshot_issues:
            report_lines.append("Screenshot-Qualität:")
            for issue in screenshot_issues:
                report_lines.append(f"  [{issue['severity'].upper()}] Schritt {issue['step_number']}: {issue['message']}")
            report_lines.append("")
        
        # Text-Qualität
        text_issues = metrics['text_quality']
        if text_issues:
            report_lines.append("Text-Qualität:")
            for issue in text_issues:
                report_lines.append(f"  [{issue['severity'].upper()}] Schritt {issue['step_number']}: {issue['message']}")
            report_lines.append("")
        
        # Vorschläge
        suggestions = metrics['suggestions']
        if suggestions:
            report_lines.append("Verbesserungsvorschläge:")
            for suggestion in suggestions:
                report_lines.append(f"  [{suggestion['priority'].upper()}] {suggestion['message']}")
                report_lines.append(f"    → {suggestion['action']}")
            report_lines.append("")
        
        return "\n".join(report_lines)

