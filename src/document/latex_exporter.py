"""
LaTeX-Exporter für Handbücher
"""

from pathlib import Path
from typing import List, Dict
from datetime import datetime
import os
import re


class LaTeXExporter:
    """Exportiert Handbücher als LaTeX"""
    
    def __init__(self):
        """Initialisiert den LaTeX Exporter"""
        pass

    def _escape_latex(self, text: str) -> str:
        """Escapes special LaTeX characters in text"""
        if text is None:
            return ""
        # Replace special LaTeX characters
        replacements = [
            ('\\', '\\textbackslash{}'),
            ('&', '\\&'),
            ('%', '\\%'),
            ('$', '\\$'),
            ('#', '\\#'),
            ('_', '\\_'),
            ('{', '\\{'),
            ('}', '\\}'),
            ('~', '\\textasciitilde{}'),
            ('^', '\\textasciicircum{}'),
        ]
        result = str(text)
        for old, new in replacements:
            result = result.replace(old, new)
        return result

    def _clean_filename(self, path: str) -> str:
        """Convert file path to a valid LaTeX filename (removes spaces and special chars)"""
        # Replace spaces with underscores and remove special characters
        filename = Path(path).name
        # Keep only alphanumeric characters, dots, hyphens, and underscores
        clean_name = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        return clean_name

    def export(
        self,
        steps: List[Dict],
        output_path: Path,
        title: str = "Handbuch",
        author: str = None,
        introduction: str = None,
        conclusion: str = None,
        include_screenshots: bool = True,
        document_class: str = "article"
    ) -> Path:
        """
        Exportiert Handbuch als LaTeX
        
        Args:
            steps: Liste von Schritten
            output_path: Ausgabepfad
            title: Titel des Dokuments
            author: Autor
            introduction: Einleitungstext
            conclusion: Fazit-Text
            include_screenshots: Ob Screenshots eingefügt werden sollen
            document_class: LaTeX Dokumentenklasse (z.B. article, report, book)
            
        Returns:
            Pfad zur erstellten LaTeX-Datei
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Stelle sicher, dass Extension .tex ist
        if output_path.suffix != '.tex':
            output_path = output_path.with_suffix('.tex')
        
        latex_lines = []
        
        # LaTeX Dokumentkopf
        latex_lines.append("\\documentclass[12pt,a4paper]{%s}\n" % document_class)
        latex_lines.append("\\usepackage[utf8]{inputenc}\n")
        latex_lines.append("\\usepackage[ngerman]{babel}\n")  # Assuming German content
        latex_lines.append("\\usepackage{graphicx}\n")
        latex_lines.append("\\usepackage{hyperref}\n")
        latex_lines.append("\\usepackage{geometry}\n")
        latex_lines.append("\\usepackage{float}\n")
        latex_lines.append("\\geometry{margin=1in}\n")  # 1 inch margins
        latex_lines.append("\n\\title{%s}\n" % self._escape_latex(title))
        if author:
            latex_lines.append("\\author{%s}\n" % self._escape_latex(author))
        latex_lines.append("\\date{%s}\n" % self._escape_latex(datetime.now().strftime('%d. %B %Y')))
        latex_lines.append("\n\\begin{document}\n")
        latex_lines.append("\\maketitle\n")
        latex_lines.append("\\newpage\n")
        latex_lines.append("\\tableofcontents\n")
        latex_lines.append("\\newpage\n")
        latex_lines.append("\n")
        
        # Einleitung
        if introduction:
            latex_lines.append("\\section{Einleitung}\n")
            escaped_intro = self._escape_latex(introduction).replace('\n', '\\\\ ')
            latex_lines.append(escaped_intro + "\n\n")
            latex_lines.append("\\newpage\n\n")
        
        # Schritte
        for step in steps:
            step_number = step.get('step_number', 0)
            window_title = step.get('window_title', 'Unbekannt')
            description = step.get('description', '')
            
            # Überschrift
            latex_lines.append("\\section{Schritt %s: %s}\n" % (step_number, self._escape_latex(window_title)))
            
            # Screenshot
            if include_screenshots:
                screenshot_path = step.get('screenshot_path', '')
                if screenshot_path and Path(screenshot_path).exists():
                    # Clean the filename for LaTeX compatibility
                    clean_filename = self._clean_filename(screenshot_path)
                    # Copy the file to the output directory with a clean name
                    screenshot_dest = output_path.parent / clean_filename
                    if not screenshot_dest.exists():
                        import shutil
                        shutil.copy2(screenshot_path, screenshot_dest)
                    
                    latex_lines.append("\\begin{figure}[H]\n")
                    latex_lines.append("    \\centering\n")
                    latex_lines.append("    \\includegraphics[width=\\textwidth]{%s}\n" % clean_filename)
                    latex_lines.append("    \\caption{%s}\n" % self._escape_latex(window_title))
                    latex_lines.append("    \\label{fig:step%s}\n" % step_number)
                    latex_lines.append("\\end{figure}\n\n")
            
            # Beschreibung
            if description:
                escaped_desc = self._escape_latex(description).replace('\n', '\\\\ ')
                latex_lines.append(escaped_desc + "\n\n")
            
            # Metadaten (optional)
            timestamp = step.get('timestamp', '')
            if timestamp:
                latex_lines.append("\\textit{Zeitstempel: %s}\n\n" % self._escape_latex(timestamp))
        
        # Fazit
        if conclusion:
            latex_lines.append("\\section{Fazit}\n")
            escaped_conclusion = self._escape_latex(conclusion).replace('\n', '\\\\ ')
            latex_lines.append(escaped_conclusion + "\n\n")
        
        # End of document
        latex_lines.append("\\end{document}\n")
        
        # Schreibe LaTeX-Datei
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(''.join(latex_lines))
        
        return output_path