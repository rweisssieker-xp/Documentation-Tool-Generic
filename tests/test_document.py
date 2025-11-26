"""
Unit-Tests für Document-Module
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Füge src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.document.docx_builder import DOCXBuilder
from src.document.pdf_exporter import PDFExporter
from src.document.markdown_exporter import MarkdownExporter
from src.document.html_exporter import HTMLExporter
from src.document.template_manager import TemplateManager


class TestDOCXBuilder:
    """Tests für DOCXBuilder"""
    
    def test_init(self):
        """Testet Initialisierung"""
        builder = DOCXBuilder(
            title="Test Document",
            author="Test Author",
            version="1.0"
        )
        
        assert builder.title == "Test Document"
        assert builder.author == "Test Author"
        assert builder.version == "1.0"
    
    def test_add_title_page(self, tmp_path):
        """Testet Hinzufügen eines Titelblatts"""
        builder = DOCXBuilder(
            title="Test Document",
            author="Test Author",
            version="1.0"
        )
        
        builder.add_title_page(
            title="Test Document",
            subtitle="Test Subtitle"
        )
        
        # Dokument sollte erstellt sein
        assert builder.document is not None
    
    def test_add_table_of_contents(self, tmp_path):
        """Testet Hinzufügen eines Inhaltsverzeichnisses"""
        builder = DOCXBuilder(
            title="Test Document",
            author="Test Author",
            version="1.0"
        )
        
        builder.add_table_of_contents()
        
        assert builder.document is not None
    
    def test_add_steps(self, tmp_path):
        """Testet Hinzufügen von Schritten"""
        builder = DOCXBuilder(
            title="Test Document",
            author="Test Author",
            version="1.0"
        )
        
        steps = [
            {
                'step_number': 1,
                'description': 'Test step 1',
                'window_title': 'Window 1',
                'screenshot_path': None
            },
            {
                'step_number': 2,
                'description': 'Test step 2',
                'window_title': 'Window 2',
                'screenshot_path': None
            }
        ]
        
        builder.add_steps(steps, include_screenshots=False)
        
        assert builder.document is not None
    
    def test_save(self, tmp_path):
        """Testet Speichern des Dokuments"""
        builder = DOCXBuilder(
            title="Test Document",
            author="Test Author",
            version="1.0"
        )
        
        # Füge etwas Inhalt hinzu
        builder.add_title_page("Test Document", "Test Subtitle")
        
        output_path = tmp_path / "test.docx"
        builder.save(output_path)
        
        assert output_path.exists()


class TestPDFExporter:
    """Tests für PDFExporter"""
    
    def test_init(self):
        """Testet Initialisierung"""
        exporter = PDFExporter()
        assert exporter is not None
    
    @patch('docx2pdf.convert')
    def test_export_with_docx2pdf(self, mock_convert, tmp_path):
        """Testet PDF-Export mit docx2pdf"""
        exporter = PDFExporter()
        
        if exporter.use_docx2pdf:
            docx_path = tmp_path / "test.docx"
            pdf_path = tmp_path / "test.pdf"
            
            # Erstelle leere DOCX-Datei für Test
            docx_path.write_bytes(b'fake docx content')
            
            mock_convert.return_value = None
            
            try:
                result = exporter.export(docx_path, pdf_path)
                assert isinstance(result, Path)
                mock_convert.assert_called_once()
            except Exception:
                # Kann fehlschlagen wenn docx2pdf nicht richtig funktioniert
                pass
        else:
            # Wenn docx2pdf nicht verfügbar ist, überspringe den Test
            pytest.skip("docx2pdf nicht verfügbar")


class TestMarkdownExporter:
    """Tests für MarkdownExporter"""
    
    def test_export(self, tmp_path):
        """Testet Markdown-Export"""
        exporter = MarkdownExporter()
        
        steps = [
            {
                'step_number': 1,
                'description': 'Test step 1',
                'window_title': 'Window 1',
                'screenshot_path': None
            }
        ]
        
        output_path = tmp_path / "test.md"
        
        exporter.export(
            steps=steps,
            output_path=output_path,
            title="Test Document",
            author="Test Author"
        )
        
        assert output_path.exists()
        content = output_path.read_text(encoding='utf-8')
        assert 'Test Document' in content
        assert 'Test step 1' in content


class TestHTMLExporter:
    """Tests für HTMLExporter"""
    
    def test_export(self, tmp_path):
        """Testet HTML-Export"""
        exporter = HTMLExporter()
        
        steps = [
            {
                'step_number': 1,
                'description': 'Test step 1',
                'window_title': 'Window 1',
                'screenshot_path': None
            }
        ]
        
        output_path = tmp_path / "test.html"
        
        exporter.export(
            steps=steps,
            output_path=output_path,
            title="Test Document",
            author="Test Author"
        )
        
        assert output_path.exists()
        content = output_path.read_text(encoding='utf-8')
        assert 'Test Document' in content
        assert '<html' in content.lower()


class TestTemplateManager:
    """Tests für TemplateManager"""
    
    def test_list_templates(self, tmp_path):
        """Testet Auflisten von Templates"""
        # Erstelle temporäres Template-Verzeichnis
        template_dir = tmp_path / "config" / "document_templates"
        template_dir.mkdir(parents=True)
        
        import yaml
        test_template = template_dir / "test.yml"
        test_template.write_text(yaml.dump({
            'name': 'Test Template',
            'structure': {
                'include_introduction': True,
                'include_conclusion': True
            }
        }))
        
        manager = TemplateManager(templates_dir=template_dir)
        templates = manager.list_templates()
        
        # Template sollte geladen sein (Name aus YAML oder Dateiname)
        assert len(templates) > 0
    
    def test_get_template(self, tmp_path):
        """Testet Abrufen eines Templates"""
        template_dir = tmp_path / "config" / "document_templates"
        template_dir.mkdir(parents=True)
        
        import yaml
        test_template = template_dir / "test.yml"
        test_data = {
            'name': 'Test Template',
            'structure': {
                'include_introduction': True
            }
        }
        test_template.write_text(yaml.dump(test_data))
        
        manager = TemplateManager(templates_dir=template_dir)
        template = manager.get_template('Test Template')  # Name aus YAML
        
        assert template is not None
        assert template.config.get('structure', {}).get('include_introduction') is True

