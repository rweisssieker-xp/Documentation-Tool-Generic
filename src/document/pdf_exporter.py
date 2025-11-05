"""
PDF-Export aus DOCX
"""

from pathlib import Path
from typing import Optional
import os


class PDFExporter:
    """Exportiert DOCX-Dokumente als PDF"""
    
    def __init__(self):
        """Initialisiert den PDF Exporter"""
        self.use_docx2pdf = self._check_docx2pdf()
    
    def _check_docx2pdf(self) -> bool:
        """
        Prüft ob docx2pdf verfügbar ist
        
        Returns:
            True wenn docx2pdf verfügbar ist
        """
        try:
            import docx2pdf
            return True
        except ImportError:
            return False
    
    def export(self, docx_path: Path, pdf_path: Optional[Path] = None) -> Path:
        """
        Exportiert DOCX als PDF
        
        Args:
            docx_path: Pfad zur DOCX-Datei
            pdf_path: Pfad zur PDF-Datei (None = automatisch)
            
        Returns:
            Pfad zur erstellten PDF-Datei
        """
        docx_path = Path(docx_path)
        
        if not docx_path.exists():
            raise FileNotFoundError(f"DOCX-Datei nicht gefunden: {docx_path}")
        
        if pdf_path is None:
            pdf_path = docx_path.with_suffix('.pdf')
        else:
            pdf_path = Path(pdf_path)
        
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.use_docx2pdf:
            return self._export_with_docx2pdf(docx_path, pdf_path)
        else:
            # Fallback: Verwende reportlab (wird später implementiert falls nötig)
            raise NotImplementedError(
                "docx2pdf nicht verfügbar. Bitte installieren Sie docx2pdf mit: pip install docx2pdf"
            )
    
    def _export_with_docx2pdf(self, docx_path: Path, pdf_path: Path) -> Path:
        """
        Exportiert mit docx2pdf
        
        Args:
            docx_path: Pfad zur DOCX-Datei
            pdf_path: Pfad zur PDF-Datei
            
        Returns:
            Pfad zur erstellten PDF-Datei
        """
        try:
            from docx2pdf import convert
            
            # docx2pdf erwartet absolute Pfade auf Windows
            docx_abs = docx_path.resolve()
            pdf_abs = pdf_path.resolve()
            
            convert(str(docx_abs), str(pdf_abs))
            
            return pdf_path
        
        except Exception as e:
            raise Exception(f"Fehler beim PDF-Export: {str(e)}")
    
    def is_available(self) -> bool:
        """
        Prüft ob PDF-Export verfügbar ist
        
        Returns:
            True wenn PDF-Export verfügbar ist
        """
        return self.use_docx2pdf


