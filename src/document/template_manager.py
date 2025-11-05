"""
Vorlagen-Verwaltung für Dokumente
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentTemplate:
    """Verwaltet Dokumentvorlagen"""
    
    def __init__(self, template_path: Path):
        """
        Initialisiert eine Dokumentvorlage
        
        Args:
            template_path: Pfad zur YAML-Vorlagendatei
        """
        self.template_path = Path(template_path)
        self.config = self._load_template()
    
    def _load_template(self) -> Dict:
        """
        Lädt die Vorlage aus YAML
        
        Returns:
            Dictionary mit Vorlagen-Konfiguration
        """
        if not self.template_path.exists():
            return self._get_default_template()
        
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"Fehler beim Laden der Vorlage: {e}", exc_info=True)
            return self._get_default_template()
    
    def _get_default_template(self) -> Dict:
        """Gibt die Standard-Vorlage zurück"""
        return {
            'name': 'Standard',
            'description': 'Standard-Dokumentvorlage',
            'metadata': {
                'author': 'Auto-generiert',
                'version': '1.0',
                'organization': 'Unbekannt',
                'department': 'Unbekannt',
                'project': 'Dokumentation',
                'document_id': ''
            },
            'structure': {
                'include_title_page': True,
                'include_table_of_contents': True,
                'include_introduction': True,
                'include_steps': True,
                'include_conclusion': True,
                'include_security_notes': True,
                'include_troubleshooting': False,
                'include_appendices': False,
                'include_glossary': False,
                'include_revision_history': False
            },
            'formatting': {
                'title_font_size': 24,
                'heading_font_size': 18,
                'subheading_font_size': 14,
                'body_font_size': 11,
                'font_family': 'Calibri',
                'heading_font_family': 'Calibri Bold',
                'margin_top': 1.0,
                'margin_bottom': 1.0,
                'margin_left': 1.0,
                'margin_right': 1.0,
                'line_spacing': 1.15,
                'paragraph_spacing_after': 6,
                'color_scheme': {
                    'primary': '2E74B5',
                    'secondary': '5B9BD5',
                    'accent': '70AD47',
                    'text': '000000',
                    'background': 'FFFFFF'
                }
            },
            'sections': {
                'title_page': {
                    'title': 'Dokumentation',
                    'subtitle': 'Automatisch generiertes Handbuch',
                    'include_logo': False,
                    'logo_path': '',
                    'include_date': True,
                    'include_author': True
                },
                'introduction': {
                    'title': 'Einleitung',
                    'level': 1,
                    'include_purpose': True,
                    'include_scope': True,
                    'include_prerequisites': False
                },
                'steps': {
                    'title': 'Schritt-für-Schritt Anleitung',
                    'include_step_numbering': True,
                    'include_window_title': True,
                    'include_timestamp': False,
                    'include_screenshot_caption': True,
                    'screenshot_alignment': 'center',
                    'screenshot_size': 'medium'  # small, medium, large, original
                },
                'conclusion': {
                    'title': 'Fazit',
                    'level': 1,
                    'include_summary': True,
                    'include_next_steps': True
                },
                'security_notes': {
                    'title': 'Sicherheitshinweise',
                    'level': 1,
                    'include_general_security': True,
                    'include_process_specific': True,
                    'include_best_practices': True
                },
                'troubleshooting': {
                    'title': 'Fehlerbehebung',
                    'level': 1,
                    'include_common_issues': True,
                    'include_solutions': True
                },
                'appendices': {
                    'title': 'Anhang',
                    'level': 1
                },
                'glossary': {
                    'title': 'Glossar',
                    'level': 1
                },
                'revision_history': {
                    'title': 'Änderungshistorie',
                    'level': 1,
                    'include_version': True,
                    'include_date': True,
                    'include_author': True,
                    'include_changes': True
                }
            },
            'export_options': {
                'include_latex': False,
                'include_pdf': True,
                'include_docx': True,
                'include_html': False,
                'include_markdown': False,
                'include_json_audit': True,
                'include_csv_audit': False
            }
        }
    
    def get_structure(self) -> Dict:
        """
        Gibt die Dokumentstruktur zurück
        
        Returns:
            Dictionary mit Struktur-Einstellungen
        """
        return self.config.get('structure', {})
    
    def get_formatting(self) -> Dict:
        """
        Gibt Formatierungs-Einstellungen zurück
        
        Returns:
            Dictionary mit Formatierungs-Einstellungen
        """
        return self.config.get('formatting', {})
    
    def get_sections(self) -> Dict:
        """
        Gibt Sektionen-Konfiguration zurück
        
        Returns:
            Dictionary mit Sektionen-Konfiguration
        """
        return self.config.get('sections', {})
    
    def save(self, output_path: Optional[Path] = None):
        """
        Speichert die Vorlage
        
        Args:
            output_path: Optionaler Ausgabepfad (sonst ursprünglicher Pfad)
        """
        path = output_path or self.template_path
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)


class TemplateManager:
    """Verwaltet Dokumentvorlagen"""
    
    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Initialisiert den Template Manager
        
        Args:
            templates_dir: Verzeichnis für Vorlagen
        """
        if templates_dir is None:
            templates_dir = Path("config") / "document_templates"
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        self.templates: Dict[str, DocumentTemplate] = {}
        self._load_templates()
    
    def _load_templates(self):
        """Lädt alle verfügbaren Vorlagen"""
        if not self.templates_dir.exists():
            return
        
        for template_file in self.templates_dir.glob("*.yml"):
            try:
                template = DocumentTemplate(template_file)
                template_name = template.config.get('name', template_file.stem)
                self.templates[template_name] = template
            except Exception as e:
                logger.warning(f"Fehler beim Laden der Vorlage {template_file}: {e}", exc_info=True)
    
    def list_templates(self) -> List[str]:
        """
        Listet alle verfügbaren Vorlagen auf
        
        Returns:
            Liste von Vorlagen-Namen
        """
        return list(self.templates.keys())
    
    def get_template(self, name: str) -> Optional[DocumentTemplate]:
        """
        Gibt eine Vorlage zurück
        
        Args:
            name: Vorlagen-Name
            
        Returns:
            DocumentTemplate oder None
        """
        return self.templates.get(name)
    
    def create_template(self, name: str, description: str = "") -> DocumentTemplate:
        """
        Erstellt eine neue Vorlage
        
        Args:
            name: Vorlagen-Name
            description: Beschreibung
            
        Returns:
            Neue DocumentTemplate-Instanz
        """
        template_path = self.templates_dir / f"{name.lower().replace(' ', '_')}.yml"
        
        template = DocumentTemplate(template_path)
        template.config['name'] = name
        template.config['description'] = description
        template.config['created_at'] = datetime.now().isoformat()
        
        template.save()
        self.templates[name] = template
        
        return template
    
    def delete_template(self, name: str) -> bool:
        """
        Löscht eine Vorlage
        
        Args:
            name: Vorlagen-Name
            
        Returns:
            True wenn erfolgreich gelöscht
        """
        if name not in self.templates:
            return False
        
        template = self.templates[name]
        try:
            if template.template_path.exists():
                template.template_path.unlink()
            del self.templates[name]
            return True
        except Exception as e:
            logger.error(f"Fehler beim Löschen der Vorlage: {e}", exc_info=True)
            return False
    
    def update_template(self, name: str, config: Dict) -> bool:
        """
        Aktualisiert eine Vorlage
        
        Args:
            name: Vorlagen-Name
            config: Neue Konfiguration
            
        Returns:
            True wenn erfolgreich aktualisiert
        """
        if name not in self.templates:
            return False
        
        template = self.templates[name]
        template.config.update(config)
        template.config['updated_at'] = datetime.now().isoformat()
        template.save()
        
        return True

