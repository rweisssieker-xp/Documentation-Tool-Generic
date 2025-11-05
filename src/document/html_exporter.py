"""
HTML-Exporter für Handbücher
"""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import os
import base64


class HTMLExporter:
    """Exportiert Handbücher als HTML"""
    
    def __init__(self, style: str = "default"):
        """
        Initialisiert den HTML Exporter
        
        Args:
            style: Stil-Template ('default', 'modern', 'minimal')
        """
        self.style = style
    
    def export(
        self,
        steps: List[Dict],
        output_path: Path,
        title: str = "Handbuch",
        author: str = None,
        introduction: str = None,
        conclusion: str = None,
        include_screenshots: bool = True,
        embed_images: bool = False
    ) -> Path:
        """
        Exportiert Handbuch als HTML
        
        Args:
            steps: Liste von Schritten
            output_path: Ausgabepfad
            title: Titel des Dokuments
            author: Autor
            introduction: Einleitungstext
            conclusion: Fazit-Text
            include_screenshots: Ob Screenshots eingefügt werden sollen
            embed_images: Ob Bilder als Base64 eingebettet werden sollen
            
        Returns:
            Pfad zur erstellten HTML-Datei
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Stelle sicher, dass Extension .html ist
        if output_path.suffix != '.html':
            output_path = output_path.with_suffix('.html')
        
        html_parts = []
        
        # HTML-Header
        html_parts.append(self._get_html_header(title))
        
        # Body-Start
        html_parts.append('<body>\n')
        html_parts.append('<div class="container">\n')
        
        # Titel
        html_parts.append(f'<h1>{title}</h1>\n')
        
        # Metadaten
        html_parts.append('<div class="metadata">\n')
        if author:
            html_parts.append(f'<p><strong>Autor:</strong> {author}</p>\n')
        html_parts.append(f'<p><strong>Erstellungsdatum:</strong> {datetime.now().strftime("%d.%m.%Y")}</p>\n')
        html_parts.append('</div>\n')
        html_parts.append('<hr>\n')
        
        # Inhaltsverzeichnis
        html_parts.append('<div class="toc">\n')
        html_parts.append('<h2>Inhaltsverzeichnis</h2>\n')
        html_parts.append('<ul>\n')
        for i, step in enumerate(steps, 1):
            window_title = step.get('window_title', 'Unbekannt')
            html_parts.append(f'<li><a href="#step-{i}">Schritt {i}: {window_title}</a></li>\n')
        html_parts.append('</ul>\n')
        html_parts.append('</div>\n')
        html_parts.append('<hr>\n')
        
        # Einleitung
        if introduction:
            html_parts.append('<div class="introduction">\n')
            html_parts.append('<h2>Einleitung</h2>\n')
            html_parts.append(f'<p>{introduction.replace(chr(10), "<br>")}</p>\n')
            html_parts.append('</div>\n')
            html_parts.append('<hr>\n')
        
        # Schritte
        for step in steps:
            step_number = step.get('step_number', 0)
            window_title = step.get('window_title', 'Unbekannt')
            description = step.get('description', '')
            
            html_parts.append(f'<div class="step" id="step-{step_number}">\n')
            html_parts.append(f'<h2>Schritt {step_number}: {window_title}</h2>\n')
            
            # Screenshot
            if include_screenshots:
                screenshot_path = step.get('screenshot_path', '')
                if screenshot_path and Path(screenshot_path).exists():
                    if embed_images:
                        img_data = self._embed_image(screenshot_path)
                        html_parts.append(f'<img src="data:image/png;base64,{img_data}" alt="Abbildung {step_number}" class="screenshot">\n')
                    else:
                        rel_path = Path(screenshot_path).relative_to(output_path.parent)
                        html_parts.append(f'<img src="{rel_path}" alt="Abbildung {step_number}" class="screenshot">\n')
                    html_parts.append(f'<p class="caption"><em>Abbildung {step_number}: {window_title}</em></p>\n')
            
            # Beschreibung
            if description:
                formatted_desc = description.replace(chr(10), "<br>")
                html_parts.append(f'<div class="description">{formatted_desc}</div>\n')
            
            # Metadaten
            timestamp = step.get('timestamp', '')
            if timestamp:
                html_parts.append(f'<p class="metadata-small"><em>Zeitstempel: {timestamp}</em></p>\n')
            
            html_parts.append('</div>\n')
            html_parts.append('<hr>\n')
        
        # Fazit
        if conclusion:
            html_parts.append('<div class="conclusion">\n')
            html_parts.append('<h2>Fazit</h2>\n')
            html_parts.append(f'<p>{conclusion.replace(chr(10), "<br>")}</p>\n')
            html_parts.append('</div>\n')
        
        # Body-End
        html_parts.append('</div>\n')
        html_parts.append('</body>\n')
        html_parts.append('</html>\n')
        
        # Schreibe HTML-Datei
        html_content = '\n'.join(html_parts)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def _get_html_header(self, title: str) -> str:
        """
        Gibt HTML-Header zurück
        
        Args:
            title: Dokument-Titel
            
        Returns:
            HTML-Header-String
        """
        css = self._get_css()
        
        return f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
{css}
    </style>
</head>
"""
    
    def _get_css(self) -> str:
        """Gibt CSS-Styles zurück"""
        if self.style == "modern":
            return """
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 40px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
        }
        .metadata {
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .screenshot {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin: 20px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .caption {
            text-align: center;
            color: #7f8c8d;
            font-style: italic;
        }
        .step {
            margin: 40px 0;
        }
        .description {
            margin: 20px 0;
            line-height: 1.8;
        }
        .metadata-small {
            color: #95a5a6;
            font-size: 0.9em;
        }
        hr {
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 30px 0;
        }
        .toc {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .toc ul {
            list-style-type: none;
            padding-left: 0;
        }
        .toc li {
            margin: 10px 0;
        }
        .toc a {
            color: #3498db;
            text-decoration: none;
        }
        .toc a:hover {
            text-decoration: underline;
        }
"""
        else:  # default
            return """
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #2c3e50;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
        }
        .metadata {
            margin: 20px 0;
        }
        .screenshot {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            margin: 20px 0;
        }
        .caption {
            text-align: center;
            color: #666;
            font-style: italic;
        }
        .step {
            margin: 30px 0;
        }
        .description {
            margin: 15px 0;
        }
        .metadata-small {
            color: #999;
            font-size: 0.9em;
        }
        hr {
            margin: 20px 0;
        }
        .toc {
            margin: 20px 0;
        }
        .toc ul {
            list-style-type: none;
            padding-left: 0;
        }
        .toc li {
            margin: 8px 0;
        }
        .toc a {
            color: #0066cc;
            text-decoration: none;
        }
        .toc a:hover {
            text-decoration: underline;
        }
"""
    
    def _embed_image(self, image_path: Path) -> str:
        """
        Konvertiert Bild zu Base64
        
        Args:
            image_path: Pfad zum Bild
            
        Returns:
            Base64-String
        """
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

