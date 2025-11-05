"""
Multi-Sprach-Export: Übersetzt Dokumente in verschiedene Sprachen
"""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from src.ai.openai_client import OpenAIClient
from src.document.template_engine import TemplateEngine
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MultiLanguageExporter:
    """Exportiert Dokumente in verschiedenen Sprachen"""
    
    # Unterstützte Sprachen mit ISO 639-1 Codes
    SUPPORTED_LANGUAGES = {
        'de': 'Deutsch',
        'en': 'English',
        'fr': 'Français',
        'es': 'Español',
        'it': 'Italiano',
        'pt': 'Português',
        'nl': 'Nederlands',
        'pl': 'Polski',
        'ru': 'Русский',
        'zh': '中文',
        'ja': '日本語'
    }
    
    def __init__(self):
        """Initialisiert den Multi-Language Exporter"""
        self.openai_client = OpenAIClient()
    
    def export_multilang(
        self,
        steps: List[Dict],
        output_dir: Path,
        target_languages: List[str],
        session_id: str,
        title: str = "Handbuch"
    ) -> Dict[str, Path]:
        """
        Exportiert Dokumente in mehreren Sprachen
        
        Args:
            steps: Liste von Schritten
            output_dir: Ausgabeverzeichnis
            target_languages: Liste von Zielsprachen (ISO 639-1 Codes)
            session_id: Session-ID
            title: Dokumenttitel
            
        Returns:
            Dictionary mit Sprache -> Pfad-Mapping
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        exported_files = {}
        
        for lang_code in target_languages:
            if lang_code not in self.SUPPORTED_LANGUAGES:
                logger.warning(f"Unbekannte Sprache: {lang_code}")
                continue
            
            try:
                # Übersetze Schritte
                translated_steps = self._translate_steps(steps, lang_code)
                
                # Erstelle temporären Session-Manager für Export
                from src.monitor.session_manager import SessionManager
                
                # Erstelle temporäre Session für Export
                temp_session_id = f"{session_id}_{lang_code}"
                temp_session = SessionManager(
                    session_id=temp_session_id,
                    prompt_profile='sop'  # Standard-Profil
                )
                
                # Setze übersetzte Schritte
                temp_session.steps = translated_steps
                
                # Exportiere Dokument
                template_engine = TemplateEngine(temp_session, output_dir=output_dir)
                
                output_filename = f"handbuch_{session_id}_{lang_code}"
                output_path = output_dir / f"{output_filename}.docx"
                
                # Generiere Dokument (nur DOCX für Multi-Lang)
                template_engine.generate_document(
                    export_formats={'docx': True, 'pdf': False, 'markdown': False, 'html': False}
                )
                
                exported_files[lang_code] = output_path
                
                logger.info(f"Dokument in {lang_code} exportiert: {output_path}")
            
            except Exception as e:
                logger.error(f"Fehler beim Exportieren in {lang_code}: {e}", exc_info=True)
        
        return exported_files
    
    def _translate_steps(self, steps: List[Dict], target_language: str) -> List[Dict]:
        """
        Übersetzt Schritte in Zielsprache
        
        Args:
            steps: Liste von Schritten
            target_language: Zielsprache (ISO 639-1 Code)
            
        Returns:
            Übersetzte Schritte
        """
        lang_name = self.SUPPORTED_LANGUAGES.get(target_language, target_language)
        
        translated_steps = []
        
        for step in steps:
            translated_step = step.copy()
            
            # Übersetze Beschreibung
            description = step.get('description', '')
            if description:
                try:
                    translated_desc = self._translate_text(description, target_language)
                    translated_step['description'] = translated_desc
                except Exception as e:
                    logger.warning(f"Fehler beim Übersetzen der Beschreibung: {e}")
                    translated_step['description'] = description
            
            # Übersetze Fenster-Titel (optional)
            window_title = step.get('window_title', '')
            if window_title:
                try:
                    translated_title = self._translate_text(window_title, target_language)
                    translated_step['window_title'] = translated_title
                except Exception as e:
                    logger.warning(f"Fehler beim Übersetzen des Fenster-Titels: {e}")
            
            translated_steps.append(translated_step)
        
        return translated_steps
    
    def _translate_text(self, text: str, target_language: str) -> str:
        """
        Übersetzt Text in Zielsprache
        
        Args:
            text: Zu übersetzender Text
            target_language: Zielsprache (ISO 639-1 Code)
            
        Returns:
            Übersetzter Text
        """
        lang_name = self.SUPPORTED_LANGUAGES.get(target_language, target_language)
        
        prompt = f"""Übersetze den folgenden Text ins {lang_name}. 
Behalte die technische Präzision und den Stil bei.
Übersetze nur den Text, ändere keine Formatierung oder Struktur.

Text:
{text}

Übersetzung:"""
        
        translated = self.openai_client.generate_text(
            system_prompt=f"Du bist ein professioneller Übersetzer für technische Dokumentation. Übersetze präzise ins {lang_name}.",
            user_prompt=prompt,
            temperature=0.3,  # Niedrigere Temperatur für präzisere Übersetzung
            max_tokens=500
        )
        
        return translated.strip() if translated else text
    
    def translate_document_sections(
        self,
        introduction: Optional[str],
        conclusion: Optional[str],
        target_language: str
    ) -> Dict[str, str]:
        """
        Übersetzt Dokument-Sektionen
        
        Args:
            introduction: Einleitungstext
            conclusion: Fazit-Text
            target_language: Zielsprache
            
        Returns:
            Dictionary mit übersetzten Texten
        """
        result = {}
        
        if introduction:
            result['introduction'] = self._translate_text(introduction, target_language)
        
        if conclusion:
            result['conclusion'] = self._translate_text(conclusion, target_language)
        
        return result

