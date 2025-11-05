"""
DOCX-Generator für Handbücher
"""

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import os
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DOCXBuilder:
    """Erstellt DOCX-Dokumente aus Handbuch-Daten"""
    
    def __init__(self, title: str = "Handbuch", author: str = None, version: str = "1.0", metadata: Optional[Dict] = None):
        """
        Initialisiert den DOCX Builder
        
        Args:
            title: Titel des Dokuments
            author: Autor
            version: Version
            metadata: Erweiterte Metadaten (Abteilung, Projekt, Kontakt, etc.)
        """
        self.document = Document()
        self.title = title
        self.author = author or os.getenv('USERNAME', 'Unbekannt')
        self.version = version
        self.metadata = metadata or {}
        
        self._setup_document()
    
    def _setup_document(self):
        """Konfiguriert Dokument-Grundlagen"""
        # Seitenränder
        sections = self.document.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)
    
    def add_title_page(self, title: str = None, subtitle: str = None):
        """
        Fügt Titelblatt hinzu
        
        Args:
            title: Titel
            subtitle: Untertitel
        """
        title = title or self.title
        
        # Titel
        title_paragraph = self.document.add_paragraph()
        title_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = title_paragraph.add_run(title)
        title_run.font.size = Pt(24)
        title_run.font.bold = True
        
        self.document.add_paragraph()
        
        # Untertitel
        if subtitle:
            subtitle_paragraph = self.document.add_paragraph()
            subtitle_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            subtitle_run = subtitle_paragraph.add_run(subtitle)
            subtitle_run.font.size = Pt(14)
        
        # Metadaten
        self.document.add_paragraph()
        self.document.add_paragraph()
        
        meta_paragraph = self.document.add_paragraph()
        meta_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        meta_text = f"Autor: {self.author}\n"
        meta_text += f"Erstellungsdatum: {datetime.now().strftime('%d.%m.%Y')}\n"
        meta_text += f"Version: {self.version}\n"
        
        # Erweiterte Metadaten
        if self.metadata.get('department'):
            meta_text += f"Abteilung: {self.metadata['department']}\n"
        if self.metadata.get('project'):
            meta_text += f"Projekt: {self.metadata['project']}\n"
        if self.metadata.get('contact'):
            meta_text += f"Kontakt: {self.metadata['contact']}\n"
        if self.metadata.get('document_id'):
            meta_text += f"Dokument-ID: {self.metadata['document_id']}\n"
        
        meta_run = meta_paragraph.add_run(meta_text)
        meta_run.font.size = Pt(10)
        
        # Seitenumbruch
        self.document.add_page_break()
    
    def add_table_of_contents(self):
        """Fügt Inhaltsverzeichnis hinzu"""
        toc_paragraph = self.document.add_paragraph()
        toc_run = toc_paragraph.add_run("Inhaltsverzeichnis")
        toc_run.font.size = Pt(18)
        toc_run.font.bold = True
        
        self.document.add_paragraph()
        
        # Erstelle manuelles Inhaltsverzeichnis
        # Word generiert automatisch ein TOC-Feld, aber python-docx unterstützt das nicht direkt
        # Wir erstellen daher ein manuelles TOC basierend auf den Überschriften
        
        # Sammle alle Überschriften während des Dokumentaufbaus
        # Diese Methode wird nach dem Hinzufügen aller Inhalte aufgerufen
        # Für jetzt: Platzhalter, wird später durch echte TOC-Generierung ersetzt
        self.document.add_paragraph("Inhaltsverzeichnis wird automatisch generiert...")
        self.document.add_page_break()
    
    def update_table_of_contents(self):
        """
        Aktualisiert das Inhaltsverzeichnis mit allen Überschriften
        Diese Methode sollte nach dem Hinzufügen aller Inhalte aufgerufen werden
        """
        # Suche nach dem TOC-Platzhalter
        # Erstelle neues TOC basierend auf Überschriften-Level
        headings = []
        for paragraph in self.document.paragraphs:
            if paragraph.style.name.startswith('Heading'):
                level = 1
                if paragraph.style.name == 'Heading 1':
                    level = 1
                elif paragraph.style.name == 'Heading 2':
                    level = 2
                elif paragraph.style.name == 'Heading 3':
                    level = 3
                
                text = paragraph.text.strip()
                if text:
                    headings.append({'level': level, 'text': text})
        
        # Erstelle TOC-Einträge
        # Finde TOC-Paragraph und ersetze ihn
        for i, paragraph in enumerate(self.document.paragraphs):
            if "Inhaltsverzeichnis wird automatisch generiert" in paragraph.text:
                # Ersetze durch echtes TOC
                paragraph.clear()
                for heading in headings:
                    indent = "  " * (heading['level'] - 1)
                    run = paragraph.add_run(f"{indent}{heading['text']}\n")
                    run.font.size = Pt(11)
                break
    
    def add_introduction(self, text: str):
        """
        Fügt Einleitung hinzu
        
        Args:
            text: Einleitungstext
        """
        heading = self.document.add_heading('Einleitung', level=1)
        
        paragraph = self.document.add_paragraph(text)
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    def add_step(self, step: Dict, include_screenshot: bool = True):
        """
        Fügt einen Schritt hinzu
        
        Args:
            step: Schritt-Dictionary
            include_screenshot: Ob Screenshot eingefügt werden soll
        """
        step_number = step.get('step_number', 0)
        window_title = step.get('window_title', 'Unbekannt')
        description = step.get('description', '')
        
        # Überschrift
        heading_text = f"Schritt {step_number}: {window_title}"
        heading = self.document.add_heading(heading_text, level=2)
        
        # Screenshot
        if include_screenshot:
            screenshot_path = Path(step.get('screenshot_path', ''))
            if screenshot_path.exists():
                try:
                    paragraph = self.document.add_paragraph()
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    
                    run = paragraph.add_run()
                    run.add_picture(str(screenshot_path), width=Inches(6))
                    
                    # Bildunterschrift
                    caption_paragraph = self.document.add_paragraph()
                    caption_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    caption_run = caption_paragraph.add_run(f"Abbildung {step_number}: {window_title}")
                    caption_run.font.size = Pt(9)
                    caption_run.italic = True
                    
                    self.document.add_paragraph()
                
                except Exception as e:
                    logger.warning(f"Fehler beim Einfügen des Screenshots: {e}", exc_info=True)
        
        # Beschreibung
        if description:
            paragraph = self.document.add_paragraph(description)
            paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        # Metadaten (optional, klein)
        meta_text = f"Zeitstempel: {step.get('timestamp', 'N/A')}"
        meta_paragraph = self.document.add_paragraph()
        meta_run = meta_paragraph.add_run(meta_text)
        meta_run.font.size = Pt(8)
        meta_run.font.color.rgb = RGBColor(128, 128, 128)
    
    def add_steps(self, steps: List[Dict], include_screenshots: bool = True):
        """
        Fügt mehrere Schritte hinzu
        
        Args:
            steps: Liste von Schritt-Dictionaries
            include_screenshots: Ob Screenshots eingefügt werden sollen
        """
        for step in steps:
            self.add_step(step, include_screenshots)
    
    def add_conclusion(self, text: str):
        """
        Fügt Fazit hinzu
        
        Args:
            text: Fazit-Text
        """
        heading = self.document.add_heading('Fazit', level=1)
        
        paragraph = self.document.add_paragraph(text)
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    def add_security_notes(self, text: str):
        """
        Fügt Sicherheitshinweise hinzu
        
        Args:
            text: Sicherheitshinweise-Text
        """
        heading = self.document.add_heading('Sicherheitshinweise', level=1)
        
        paragraph = self.document.add_paragraph(text)
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    def add_troubleshooting(self, items: List[Dict[str, str]]):
        """
        Fügt Troubleshooting-Sektion hinzu
        
        Args:
            items: Liste von Problem-Lösung-Paaren
        """
        heading = self.document.add_heading('Fehlerbehebung', level=1)
        
        for item in items:
            problem = item.get('problem', '')
            solution = item.get('solution', '')
            
            problem_paragraph = self.document.add_paragraph(f"Problem: {problem}", style='List Bullet')
            solution_paragraph = self.document.add_paragraph(f"Lösung: {solution}")
            solution_paragraph.style = 'List Bullet 2'
    
    def save(self, output_path: Path) -> Path:
        """
        Speichert das Dokument
        
        Args:
            output_path: Ausgabepfad
            
        Returns:
            Pfad zur gespeicherten Datei
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Stelle sicher, dass Extension .docx ist
        if output_path.suffix != '.docx':
            output_path = output_path.with_suffix('.docx')
        
        # Aktualisiere Inhaltsverzeichnis vor dem Speichern
        self.update_table_of_contents()
        
        self.document.save(str(output_path))
        return output_path


