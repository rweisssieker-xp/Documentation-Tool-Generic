"""
Quick-Reference Export: Generiert kompakte Checklisten und Cheat-Sheets
"""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import os

from src.document.pdf_exporter import PDFExporter
from src.utils.logger import get_logger

logger = get_logger(__name__)


class QuickReferenceExporter:
    """Exportiert Quick-Reference-Dokumente (Checklisten, Cheat-Sheets)"""
    
    def __init__(self):
        """Initialisiert den Quick-Reference Exporter"""
        self.pdf_exporter = PDFExporter()
    
    def export_checklist(
        self,
        steps: List[Dict],
        output_path: Path,
        title: str = "Checkliste",
        include_screenshots: bool = False
    ) -> Path:
        """
        Exportiert Checkliste als Markdown
        
        Args:
            steps: Liste von Schritten
            output_path: Ausgabepfad
            title: Titel der Checkliste
            include_screenshots: Ob Screenshots eingefügt werden sollen
            
        Returns:
            Pfad zur erstellten Datei
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        lines = [
            f"# {title}",
            "",
            f"*Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M')}*",
            "",
            "---",
            ""
        ]
        
        for step in steps:
            step_num = step.get('step_number', '?')
            window_title = step.get('window_title', 'Unbekannt')
            description = step.get('description', '')
            
            # Extrahiere kurze Beschreibung
            short_desc = self._extract_short_description(description, window_title)
            
            lines.append(f"- [ ] **Schritt {step_num}**: {short_desc}")
            
            if include_screenshots:
                screenshot_path = step.get('screenshot_path')
                if screenshot_path and Path(screenshot_path).exists():
                    rel_path = os.path.relpath(screenshot_path, output_path.parent)
                    lines.append(f"  ![Schritt {step_num}]({rel_path})")
            
            lines.append("")
        
        # Speichere Markdown
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        logger.info(f"Checkliste exportiert: {output_path}")
        return output_path
    
    def export_cheat_sheet(
        self,
        steps: List[Dict],
        output_path: Path,
        title: str = "Quick Reference"
    ) -> Path:
        """
        Exportiert Cheat-Sheet als kompaktes PDF (1-Seite)
        
        Args:
            steps: Liste von Schritten
            output_path: Ausgabepfad
            title: Titel des Cheat-Sheets
            
        Returns:
            Pfad zur erstellten PDF-Datei
        """
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import cm
            from reportlab.pdfgen import canvas
            from reportlab.lib import colors
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Erstelle PDF
            c = canvas.Canvas(str(output_path), pagesize=A4)
            width, height = A4
            
            # Titel
            c.setFont("Helvetica-Bold", 16)
            c.drawString(2*cm, height - 2*cm, title)
            
            # Datum
            c.setFont("Helvetica", 10)
            date_str = datetime.now().strftime('%d.%m.%Y')
            c.drawString(width - 5*cm, height - 2*cm, date_str)
            
            # Schritte (kompakt)
            y_pos = height - 4*cm
            line_height = 0.6*cm
            max_lines = int((height - 4*cm) / line_height)
            
            c.setFont("Helvetica", 9)
            
            for i, step in enumerate(steps[:max_lines]):
                step_num = step.get('step_number', '?')
                window_title = step.get('window_title', 'Unbekannt')
                description = step.get('description', '')
                
                short_desc = self._extract_short_description(description, window_title)
                
                # Zeichne Schritt
                text = f"{step_num}. {short_desc[:60]}"
                c.drawString(1*cm, y_pos - i*line_height, text)
            
            # Speichere PDF
            c.save()
            
            logger.info(f"Cheat-Sheet exportiert: {output_path}")
            return output_path
        
        except ImportError:
            logger.warning("reportlab nicht verfügbar, verwende Markdown-Export")
            # Fallback zu Markdown
            md_path = output_path.with_suffix('.md')
            return self.export_checklist(steps, md_path, title, include_screenshots=False)
    
    def export_one_pager(
        self,
        steps: List[Dict],
        output_path: Path,
        title: str = "Quick Reference"
    ) -> Path:
        """
        Exportiert One-Pager (1 Seite, alle Schritte)
        
        Args:
            steps: Liste von Schritten
            output_path: Ausgabepfad
            title: Titel
            
        Returns:
            Pfad zur erstellten Datei
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        lines = [
            f"# {title}",
            "",
            f"*Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M')}*",
            "",
            "---",
            ""
        ]
        
        # Kompakte Schritt-Liste
        for step in steps:
            step_num = step.get('step_number', '?')
            window_title = step.get('window_title', 'Unbekannt')
            description = step.get('description', '')
            
            short_desc = self._extract_short_description(description, window_title, max_length=80)
            
            lines.append(f"**{step_num}.** {short_desc}")
            lines.append("")
        
        # Speichere
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        logger.info(f"One-Pager exportiert: {output_path}")
        return output_path
    
    def _extract_short_description(self, description: str, window_title: str, max_length: int = 100) -> str:
        """
        Extrahiert kurze Beschreibung
        
        Args:
            description: Vollständige Beschreibung
            window_title: Fenster-Titel
            max_length: Maximale Länge
            
        Returns:
            Kurze Beschreibung
        """
        if description:
            # Entferne Präfixe wie "Schritt X:"
            desc = description.strip()
            if ':' in desc:
                parts = desc.split(':', 1)
                if len(parts) > 1:
                    desc = parts[1].strip()
            
            # Kürze auf max_length
            if len(desc) > max_length:
                desc = desc[:max_length - 3] + "..."
            
            return desc
        
        # Fallback zu Fenster-Titel
        return window_title

