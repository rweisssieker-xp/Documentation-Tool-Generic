"""
Document Generation REST API
"""

from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pathlib import Path
import json

from src.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentGenerateRequest(BaseModel):
    """Document generation request"""
    session_id: str
    format: str = "docx"  # docx, pdf, markdown, html, latex
    template: Optional[str] = None
    language: Optional[str] = None


class DocumentResponse(BaseModel):
    """Document response"""
    id: str
    session_id: str
    format: str
    path: str
    created_at: str
    size: int


class DocumentAPI:
    """Document Generation API"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        self.sessions_dir = Path("data/sessions")
        self.documents_dir = Path("data/documents")
        self.documents_dir.mkdir(parents=True, exist_ok=True)
    
    def _setup_routes(self):
        """Setup routes"""
        @self.router.post("/generate", response_model=DocumentResponse)
        async def generate_document(request: DocumentGenerateRequest):
            """Generate document from session"""
            session_file = self.sessions_dir / f"{request.session_id}.json"
            if not session_file.exists():
                raise HTTPException(status_code=404, detail="Session not found")
            
            # Import document generators
            from src.document.docx_builder import DOCXBuilder
            from src.document.pdf_exporter import PDFExporter
            from src.document.markdown_exporter import MarkdownExporter
            from src.document.html_exporter import HTMLExporter
            from src.document.latex_exporter import LaTeXExporter
            
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Generate document based on format
            document_id = f"doc_{request.session_id}_{request.format}"
            output_path = self.documents_dir / f"{document_id}.{request.format}"
            
            try:
                if request.format == "docx":
                    builder = DOCXBuilder()
                    builder.build_document(session_data, str(output_path))
                elif request.format == "pdf":
                    exporter = PDFExporter()
                    exporter.export(session_data, str(output_path))
                elif request.format == "markdown":
                    exporter = MarkdownExporter()
                    exporter.export(session_data, str(output_path))
                elif request.format == "html":
                    exporter = HTMLExporter()
                    exporter.export(session_data, str(output_path))
                elif request.format == "latex":
                    exporter = LaTeXExporter()
                    exporter.export(session_data, str(output_path))
                else:
                    raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")
                
                return DocumentResponse(
                    id=document_id,
                    session_id=request.session_id,
                    format=request.format,
                    path=str(output_path),
                    created_at=Path(output_path).stat().st_mtime,
                    size=output_path.stat().st_size,
                )
            except Exception as e:
                logger.error(f"Error generating document: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/{document_id}")
        async def get_document(document_id: str):
            """Get document by ID"""
            # Find document file
            for ext in ['docx', 'pdf', 'md', 'html', 'tex']:
                doc_file = self.documents_dir / f"{document_id}.{ext}"
                if doc_file.exists():
                    return {"id": document_id, "path": str(doc_file), "format": ext}
            
            raise HTTPException(status_code=404, detail="Document not found")
        
        @self.router.get("/session/{session_id}", response_model=List[DocumentResponse])
        async def list_session_documents(session_id: str):
            """List all documents for a session"""
            documents = []
            prefix = f"doc_{session_id}_"
            
            for doc_file in self.documents_dir.glob(f"{prefix}*"):
                ext = doc_file.suffix[1:]  # Remove dot
                doc_id = doc_file.stem
                
                documents.append(DocumentResponse(
                    id=doc_id,
                    session_id=session_id,
                    format=ext,
                    path=str(doc_file),
                    created_at=str(doc_file.stat().st_mtime),
                    size=doc_file.stat().st_size,
                ))
            
            return documents

