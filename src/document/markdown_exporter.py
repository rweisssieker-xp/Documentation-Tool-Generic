"""
Markdown-Exporter für Handbücher
"""

from pathlib import Path
from typing import List, Dict
from datetime import datetime
import os


class MarkdownExporter:
    """Exportiert Handbücher als Markdown"""
    
    def __init__(self):
        """Initialisiert den Markdown Exporter"""
        pass
    
    def export(
        self,
        steps: List[Dict],
        output_path: Path,
        title: str = "Handbuch",
        author: str = None,
        introduction: str = None,
        conclusion: str = None,
        include_screenshots: bool = True
    ) -> Path:
        """
        Exportiert Handbuch als Markdown
        
        Args:
            steps: Liste von Schritten
            output_path: Ausgabepfad
            title: Titel des Dokuments
            author: Autor
            introduction: Einleitungstext
            conclusion: Fazit-Text
            include_screenshots: Ob Screenshot-Links eingefügt werden sollen
            
        Returns:
            Pfad zur erstellten Markdown-Datei
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Stelle sicher, dass Extension .md ist
        if output_path.suffix != '.md':
            output_path = output_path.with_suffix('.md')
        
        markdown_lines = []
        
        # Titel
        markdown_lines.append(f"# {title}\n")
        
        # Metadaten
        if author:
            markdown_lines.append(f"**Autor:** {author}  \n")
        markdown_lines.append(f"**Erstellungsdatum:** {datetime.now().strftime('%d.%m.%Y')}  \n")
        markdown_lines.append("\n---\n\n")
        
        # Inhaltsverzeichnis
        markdown_lines.append("## Inhaltsverzeichnis\n\n")
        for i, step in enumerate(steps, 1):
            window_title = step.get('window_title', 'Unbekannt')
            markdown_lines.append(f"{i}. [Schritt {i}: {window_title}](#schritt-{i})\n")
        markdown_lines.append("\n---\n\n")
        
        # Einleitung
        if introduction:
            markdown_lines.append("## Einleitung\n\n")
            markdown_lines.append(f"{introduction}\n\n")
            markdown_lines.append("---\n\n")
        
        # Schritte
        for step in steps:
            step_number = step.get('step_number', 0)
            window_title = step.get('window_title', 'Unbekannt')
            description = step.get('description', '')
            
            # Überschrift
            markdown_lines.append(f"## Schritt {step_number}: {window_title}\n\n")
            
            # Screenshot
            if include_screenshots:
                screenshot_path = step.get('screenshot_path', '')
                if screenshot_path and Path(screenshot_path).exists():
                    # Relativer Pfad für Markdown
                    rel_path = Path(screenshot_path).relative_to(output_path.parent)
                    markdown_lines.append(f"![Abbildung {step_number}]({rel_path})\n\n")
                    markdown_lines.append(f"*Abbildung {step_number}: {window_title}*\n\n")
            
            # Beschreibung
            if description:
                markdown_lines.append(f"{description}\n\n")
            
            # Metadaten (optional, klein)
            timestamp = step.get('timestamp', '')
            if timestamp:
                markdown_lines.append(f"*Zeitstempel: {timestamp}*\n\n")
            
            markdown_lines.append("---\n\n")
        
        # Fazit
        if conclusion:
            markdown_lines.append("## Fazit\n\n")
            markdown_lines.append(f"{conclusion}\n\n")
        
        # Schreibe Markdown-Datei
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown_lines))
        
        return output_path

