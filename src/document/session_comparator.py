"""
Session-Vergleich: Vergleicht zwei Sessions und erstellt Diff-Dokument
"""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import difflib
import os

from src.document.docx_builder import DOCXBuilder
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SessionComparator:
    """Vergleicht zwei Sessions und erstellt Diff-Dokument"""
    
    def __init__(self):
        """Initialisiert den Session Comparator"""
        pass
    
    def compare_sessions(
        self,
        session1_steps: List[Dict],
        session2_steps: List[Dict],
        session1_id: str,
        session2_id: str
    ) -> Dict:
        """
        Vergleicht zwei Sessions
        
        Args:
            session1_steps: Schritte der ersten Session
            session2_steps: Schritte der zweiten Session
            session1_id: ID der ersten Session
            session2_id: ID der zweiten Session
            
        Returns:
            Dictionary mit Vergleichs-Ergebnissen
        """
        comparison = {
            'session1_id': session1_id,
            'session2_id': session2_id,
            'session1_step_count': len(session1_steps),
            'session2_step_count': len(session2_steps),
            'differences': [],
            'similarities': [],
            'added_steps': [],
            'removed_steps': [],
            'modified_steps': []
        }
        
        # Vergleiche Schritt-Anzahl
        if len(session1_steps) != len(session2_steps):
            comparison['differences'].append({
                'type': 'step_count',
                'session1': len(session1_steps),
                'session2': len(session2_steps),
                'message': f'Unterschiedliche Anzahl von Schritten: {len(session1_steps)} vs {len(session2_steps)}'
            })
        
        # Vergleiche Schritte paarweise
        max_steps = max(len(session1_steps), len(session2_steps))
        
        for i in range(max_steps):
            step1 = session1_steps[i] if i < len(session1_steps) else None
            step2 = session2_steps[i] if i < len(session2_steps) else None
            
            if step1 is None:
                comparison['added_steps'].append({
                    'step_number': i + 1,
                    'session': 'session2',
                    'step': step2
                })
                continue
            
            if step2 is None:
                comparison['removed_steps'].append({
                    'step_number': i + 1,
                    'session': 'session1',
                    'step': step1
                })
                continue
            
            # Vergleiche Schritt-Inhalte
            step_diff = self._compare_steps(step1, step2, i + 1)
            
            if step_diff['different']:
                comparison['modified_steps'].append(step_diff)
            else:
                comparison['similarities'].append({
                    'step_number': i + 1,
                    'step': step1
                })
        
        return comparison
    
    def _compare_steps(self, step1: Dict, step2: Dict, step_number: int) -> Dict:
        """Vergleicht zwei Schritte"""
        differences = []
        
        # Vergleiche Fenster-Titel
        title1 = step1.get('window_title', '')
        title2 = step2.get('window_title', '')
        if title1 != title2:
            differences.append({
                'field': 'window_title',
                'value1': title1,
                'value2': title2
            })
        
        # Vergleiche Beschreibungen
        desc1 = step1.get('description', '')
        desc2 = step2.get('description', '')
        
        if desc1 != desc2:
            # Berechne Ähnlichkeit
            similarity = self._text_similarity(desc1, desc2)
            
            differences.append({
                'field': 'description',
                'value1': desc1,
                'value2': desc2,
                'similarity': similarity
            })
        
        # Vergleiche Screenshots (Hash)
        screenshot1 = step1.get('screenshot_path', '')
        screenshot2 = step2.get('screenshot_path', '')
        
        if screenshot1 and screenshot2:
            hash1 = self._calculate_file_hash(screenshot1)
            hash2 = self._calculate_file_hash(screenshot2)
            
            if hash1 != hash2:
                differences.append({
                    'field': 'screenshot',
                    'screenshot1': screenshot1,
                    'screenshot2': screenshot2,
                    'hash1': hash1,
                    'hash2': hash2
                })
        
        return {
            'step_number': step_number,
            'different': len(differences) > 0,
            'differences': differences
        }
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Berechnet Text-Ähnlichkeit (0.0-1.0)"""
        if not text1 or not text2:
            return 0.0
        
        # Verwende SequenceMatcher für Ähnlichkeit
        similarity = difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        return similarity
    
    def _calculate_file_hash(self, file_path: str) -> Optional[str]:
        """Berechnet SHA-256 Hash einer Datei"""
        try:
            import hashlib
            
            file = Path(file_path)
            if not file.exists():
                return None
            
            with open(file, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            return file_hash
        
        except Exception as e:
            logger.warning(f"Fehler beim Berechnen des File-Hash: {e}")
            return None
    
    def generate_diff_document(
        self,
        comparison: Dict,
        output_path: Path,
        session1_steps: List[Dict],
        session2_steps: List[Dict]
    ) -> Path:
        """
        Generiert Diff-Dokument
        
        Args:
            comparison: Vergleichs-Ergebnisse
            output_path: Ausgabepfad
            session1_steps: Schritte der ersten Session
            session2_steps: Schritte der zweiten Session
            
        Returns:
            Pfad zur erstellten Diff-Datei
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        title = f"Session-Vergleich: {comparison['session1_id']} vs {comparison['session2_id']}"
        
        docx_builder = DOCXBuilder(
            title=title,
            author=os.getenv('USERNAME', 'Unbekannt'),
            version="1.0"
        )
        
        # Titelblatt
        docx_builder.add_title_page(
            title=title,
            subtitle=f"Erstellt am {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
        )
        
        # Vergleichs-Übersicht
        docx_builder.document.add_heading('Vergleichs-Übersicht', level=1)
        
        overview_text = f"""
Session 1: {comparison['session1_id']} ({comparison['session1_step_count']} Schritte)
Session 2: {comparison['session2_id']} ({comparison['session2_step_count']} Schritte)

Unterschiede gefunden: {len(comparison['differences']) + len(comparison['modified_steps'])}
Hinzugefügte Schritte: {len(comparison['added_steps'])}
Entfernte Schritte: {len(comparison['removed_steps'])}
Geänderte Schritte: {len(comparison['modified_steps'])}
"""
        
        docx_builder.document.add_paragraph(overview_text)
        
        # Unterschiede
        if comparison['modified_steps']:
            docx_builder.document.add_heading('Geänderte Schritte', level=1)
            
            for mod_step in comparison['modified_steps']:
                step_num = mod_step['step_number']
                docx_builder.document.add_heading(f'Schritt {step_num}', level=2)
                
                for diff in mod_step['differences']:
                    field = diff['field']
                    docx_builder.document.add_paragraph(f"Unterschied in {field}:", style='Heading 3')
                    
                    if field == 'description':
                        docx_builder.document.add_paragraph(f"Session 1: {diff['value1'][:200]}...")
                        docx_builder.document.add_paragraph(f"Session 2: {diff['value2'][:200]}...")
                        docx_builder.document.add_paragraph(f"Ähnlichkeit: {diff.get('similarity', 0):.2%}")
                    else:
                        docx_builder.document.add_paragraph(f"Session 1: {diff.get('value1', 'N/A')}")
                        docx_builder.document.add_paragraph(f"Session 2: {diff.get('value2', 'N/A')}")
        
        # Hinzugefügte Schritte
        if comparison['added_steps']:
            docx_builder.document.add_heading('Hinzugefügte Schritte', level=1)
            
            for added in comparison['added_steps']:
                step = added['step']
                step_num = added['step_number']
                docx_builder.document.add_heading(f'Schritt {step_num} (nur in {added["session"]})', level=2)
                docx_builder.document.add_paragraph(step.get('description', 'Keine Beschreibung'))
        
        # Entfernte Schritte
        if comparison['removed_steps']:
            docx_builder.document.add_heading('Entfernte Schritte', level=1)
            
            for removed in comparison['removed_steps']:
                step = removed['step']
                step_num = removed['step_number']
                docx_builder.document.add_heading(f'Schritt {step_num} (nur in {removed["session"]})', level=2)
                docx_builder.document.add_paragraph(step.get('description', 'Keine Beschreibung'))
        
        # Speichere Dokument
        docx_builder.save(output_path)
        
        logger.info(f"Diff-Dokument erstellt: {output_path}")
        return output_path

