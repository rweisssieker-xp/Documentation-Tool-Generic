"""
Template-Engine für konfigurierbare Dokumentstruktur
"""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import os
import hashlib

from src.document.docx_builder import DOCXBuilder
from src.document.pdf_exporter import PDFExporter
from src.document.markdown_exporter import MarkdownExporter
from src.document.html_exporter import HTMLExporter
from src.document.template_manager import TemplateManager, DocumentTemplate
from src.ai.text_generator import TextGenerator
from src.audit.audit_logger import AuditLogger
from pathlib import Path
import yaml
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TemplateEngine:
    """Generiert Dokumente basierend auf Template-Konfiguration"""
    
    def __init__(self, session_manager, output_dir: Optional[Path] = None, template_name: Optional[str] = None):
        """
        Initialisiert die Template Engine
        
        Args:
            session_manager: SessionManager-Instanz
            output_dir: Ausgabeverzeichnis
            template_name: Name der Dokumentvorlage (optional)
        """
        self.session_manager = session_manager
        self.session_info = session_manager.get_session_info()
        
        if output_dir is None:
            output_dir = Path("data") / "output"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Lade Dokumentvorlage
        template_manager = TemplateManager()
        if template_name and template_name in template_manager.list_templates():
            self.document_template = template_manager.get_template(template_name)
        else:
            # Verwende Standard-Vorlage
            self.document_template = None
        
        # Initialisiere Komponenten
        self.text_generator = TextGenerator(self.session_info['prompt_profile'])
        self.pdf_exporter = PDFExporter()
    
    def generate_document(
        self,
        include_introduction: bool = True,
        include_conclusion: bool = True,
        include_security_notes: bool = True,
        include_troubleshooting: bool = False,
        include_screenshots: bool = True,
        export_formats: Optional[Dict[str, bool]] = None
    ) -> Path:
        """
        Generiert das vollständige Dokument
        
        Args:
            include_introduction: Ob Einleitung eingefügt werden soll
            include_conclusion: Ob Fazit eingefügt werden soll
            include_security_notes: Ob Sicherheitshinweise eingefügt werden sollen
            include_troubleshooting: Ob Troubleshooting eingefügt werden soll
            include_screenshots: Ob Screenshots eingefügt werden sollen
            export_formats: Dictionary mit Export-Format-Optionen (docx, pdf, markdown, html, json, csv)
            
        Returns:
            Pfad zur erstellten DOCX-Datei
        """
        # Hole alle Schritte
        steps = self.session_manager.get_steps()
        
        if not steps:
            raise ValueError("Keine Schritte zum Dokumentieren vorhanden!")
        
        # Generiere Beschreibungen für alle Schritte
        logger.info("Generiere Beschreibungen für alle Schritte...")
        steps_with_descriptions = self.text_generator.generate_all_step_descriptions(steps)
        
        # Verwende Vorlagen-Struktur falls verfügbar
        if self.document_template:
            structure = self.document_template.get_structure()
            include_introduction = structure.get('include_introduction', include_introduction)
            include_conclusion = structure.get('include_conclusion', include_conclusion)
            include_security_notes = structure.get('include_security_notes', include_security_notes)
            include_troubleshooting = structure.get('include_troubleshooting', include_troubleshooting)
        
        # Lade erweiterte Metadaten
        metadata_config_path = Path("config") / "document_metadata.yml"
        document_metadata = {}
        if metadata_config_path.exists():
            try:
                with open(metadata_config_path, 'r', encoding='utf-8') as f:
                    document_metadata = yaml.safe_load(f) or {}
            except Exception:
                pass
        
        # Erstelle DOCX-Builder
        title = f"Handbuch - {self.session_info['session_id']}"
        docx_builder = DOCXBuilder(
            title=title,
            author=os.getenv('USERNAME', 'Unbekannt'),
            version="1.0",
            metadata=document_metadata
        )
        
        # Wende Formatierung aus Vorlage an falls verfügbar
        if self.document_template:
            formatting = self.document_template.get_formatting()
            # Formatierung kann hier auf docx_builder angewendet werden
        
        # Titelblatt
        if not self.document_template or self.document_template.get_structure().get('include_title_page', True):
            docx_builder.add_title_page(
                title=title,
                subtitle=f"Erstellt am {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
            )
        
        # Inhaltsverzeichnis
        if not self.document_template or self.document_template.get_structure().get('include_table_of_contents', True):
            docx_builder.add_table_of_contents()
        
        # Einleitung
        if include_introduction:
            logger.info("Generiere Einleitung...")
            introduction = self.text_generator.generate_introduction(steps_with_descriptions)
            docx_builder.add_introduction(introduction)
        
        # Schritte
        logger.info("Füge Schritte zum Dokument hinzu...")
        docx_builder.add_steps(steps_with_descriptions, include_screenshots)
        
        # Fazit
        if include_conclusion:
            logger.info("Generiere Fazit...")
            conclusion = self.text_generator.generate_conclusion(steps_with_descriptions)
            docx_builder.add_conclusion(conclusion)
        
        # Sicherheitshinweise
        if include_security_notes:
            logger.info("Generiere Sicherheitshinweise...")
            security_notes = self.text_generator.generate_security_notes(steps_with_descriptions)
            if security_notes:
                docx_builder.add_security_notes(security_notes)
        
        # Troubleshooting (optional)
        if include_troubleshooting:
            logger.info("Generiere Troubleshooting...")
            troubleshooting_items = self.text_generator.generate_troubleshooting(steps_with_descriptions)
            if troubleshooting_items:
                docx_builder.add_troubleshooting(troubleshooting_items)
        
        # Standard-Export-Formate falls nicht angegeben
        if export_formats is None:
            export_formats = {
                'docx': True,
                'pdf': True,
                'markdown': False,
                'html': False
            }
        
        # Speichere DOCX
        output_filename = f"handbuch_{self.session_info['session_id']}"
        docx_path = None
        
        if export_formats.get('docx', True):
            docx_filename = f"{output_filename}.docx"
            docx_path = self.output_dir / docx_filename
            
            logger.info(f"Speichere Dokument: {docx_path}")
            docx_builder.save(docx_path)
        
        # Exportiere als PDF falls gewünscht
        pdf_path = None
        if export_formats.get('pdf', True) and self.pdf_exporter.is_available() and docx_path:
            try:
                logger.info("Exportiere als PDF...")
                pdf_filename = f"{output_filename}.pdf"
                pdf_path = self.output_dir / pdf_filename
                self.pdf_exporter.export(docx_path, pdf_path)
                logger.info(f"PDF erstellt: {pdf_path}")
            except Exception as e:
                logger.warning(f"PDF-Export fehlgeschlagen: {e}", exc_info=True)
        
        # Exportiere als Markdown falls gewünscht
        if export_formats.get('markdown', False):
            try:
                logger.info("Exportiere als Markdown...")
                markdown_exporter = MarkdownExporter()
                markdown_filename = f"{output_filename}.md"
                markdown_path = self.output_dir / markdown_filename
                
                markdown_exporter.export(
                    steps=steps_with_descriptions,
                    output_path=markdown_path,
                    title=title,
                    author=os.getenv('USERNAME', 'Unbekannt'),
                    introduction=introduction if include_introduction else None,
                    conclusion=conclusion if include_conclusion else None,
                    include_screenshots=include_screenshots
                )
                logger.info(f"Markdown erstellt: {markdown_path}")
            except Exception as e:
                logger.warning(f"Markdown-Export fehlgeschlagen: {e}", exc_info=True)
        
        # Exportiere als HTML falls gewünscht
        if export_formats.get('html', False):
            try:
                logger.info("Exportiere als HTML...")
                html_exporter = HTMLExporter()
                html_filename = f"{output_filename}.html"
                html_path = self.output_dir / html_filename
                
                html_exporter.export(
                    steps=steps_with_descriptions,
                    output_path=html_path,
                    title=title,
                    author=os.getenv('USERNAME', 'Unbekannt'),
                    introduction=introduction if include_introduction else None,
                    conclusion=conclusion if include_conclusion else None,
                    include_screenshots=include_screenshots
                )
                logger.info(f"HTML erstellt: {html_path}")
            except Exception as e:
                logger.warning(f"HTML-Export fehlgeschlagen: {e}", exc_info=True)
        
        # Exportiere Audit-Trail
        audit_logger = self.session_manager.get_audit_logger()
        
        try:
            logger.info("Exportiere Audit-Trail...")
            if export_formats.get('json', True):
                audit_json_path = audit_logger.export_json()
                logger.info(f"Audit-Trail (JSON) erstellt: {audit_json_path}")
            
            if export_formats.get('csv', False):
                audit_csv_path = audit_logger.export_csv()
                logger.info(f"Audit-Trail (CSV) erstellt: {audit_csv_path}")
        except Exception as e:
            logger.warning(f"Audit-Trail-Export fehlgeschlagen: {e}", exc_info=True)
        
        # Validiere Export
        validation_result = self.validate_export(
            docx_path=docx_path,
            pdf_path=pdf_path,
            steps=steps_with_descriptions,
            export_formats=export_formats
        )
        
        if not validation_result['valid']:
            logger.warning(f"Export-Validierung gefunden Fehler: {validation_result['errors']}")
            # Werfe keine Exception, aber logge Warnung
        
        return docx_path or pdf_path or self.output_dir / f"{output_filename}.docx"
    
    def validate_export(
        self,
        docx_path: Optional[Path],
        pdf_path: Optional[Path],
        steps: List[Dict],
        export_formats: Dict[str, bool]
    ) -> Dict:
        """
        Validiert die generierten Export-Dateien
        
        Args:
            docx_path: Pfad zur DOCX-Datei
            pdf_path: Pfad zur PDF-Datei
            steps: Liste der Schritte mit Beschreibungen
            export_formats: Dictionary mit Export-Format-Optionen
            
        Returns:
            Dictionary mit Validierungs-Ergebnissen
        """
        errors = []
        warnings = []
        
        # Prüfe DOCX falls erstellt
        if export_formats.get('docx', True) and docx_path:
            if not docx_path.exists():
                errors.append(f"DOCX-Datei nicht gefunden: {docx_path}")
            else:
                # Prüfe Dateigröße
                file_size = docx_path.stat().st_size
                if file_size == 0:
                    errors.append(f"DOCX-Datei ist leer: {docx_path}")
                elif file_size < 1024:  # Weniger als 1KB
                    warnings.append(f"DOCX-Datei ist sehr klein ({file_size} Bytes): {docx_path}")
                
                # Prüfe Datei-Integrität (SHA-256)
                try:
                    with open(docx_path, 'rb') as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                    logger.debug(f"DOCX SHA-256: {file_hash}")
                except Exception as e:
                    warnings.append(f"Konnte SHA-256 von DOCX nicht berechnen: {e}")
        
        # Prüfe PDF falls erstellt
        if export_formats.get('pdf', True) and pdf_path:
            if not pdf_path.exists():
                errors.append(f"PDF-Datei nicht gefunden: {pdf_path}")
            else:
                # Prüfe Dateigröße
                file_size = pdf_path.stat().st_size
                if file_size == 0:
                    errors.append(f"PDF-Datei ist leer: {pdf_path}")
                elif file_size < 1024:  # Weniger als 1KB
                    warnings.append(f"PDF-Datei ist sehr klein ({file_size} Bytes): {pdf_path}")
        
        # Prüfe fehlende Screenshots
        missing_screenshots = []
        for step in steps:
            screenshot_path = step.get('screenshot_path')
            if screenshot_path:
                screenshot_file = Path(screenshot_path)
                if not screenshot_file.exists():
                    missing_screenshots.append(f"Schritt {step.get('step_number', '?')}: {screenshot_path}")
        
        if missing_screenshots:
            warnings.append(f"{len(missing_screenshots)} fehlende Screenshots gefunden")
            for missing in missing_screenshots[:5]:  # Zeige nur erste 5
                warnings.append(f"  - {missing}")
            if len(missing_screenshots) > 5:
                warnings.append(f"  ... und {len(missing_screenshots) - 5} weitere")
        
        # Prüfe ob Schritte Beschreibungen haben
        steps_without_description = [
            step.get('step_number', '?')
            for step in steps
            if not step.get('description') or step.get('description', '').strip() == ''
        ]
        
        if steps_without_description:
            warnings.append(f"{len(steps_without_description)} Schritte ohne Beschreibung: {', '.join(map(str, steps_without_description[:5]))}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'error_count': len(errors),
            'warning_count': len(warnings)
        }

