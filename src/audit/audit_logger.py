"""
Audit Logger für revisionssichere Protokollierung
"""

import hashlib
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import os


class AuditLogger:
    """Revisionssichere Protokollierung mit SHA-256 Hashes"""
    
    def __init__(self, session_id: str, output_dir: Optional[Path] = None):
        """
        Initialisiert den Audit Logger
        
        Args:
            session_id: Eindeutige Session-ID
            output_dir: Ausgabeverzeichnis für Audit-Logs
        """
        self.session_id = session_id
        self.username = os.getenv('USERNAME', os.getenv('USER', 'unknown'))
        self.systemname = os.getenv('COMPUTERNAME', os.getenv('HOSTNAME', 'unknown'))
        
        if output_dir is None:
            output_dir = Path("data") / "sessions"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.audit_entries = []
        self.session_start_time = datetime.now()
    
    def log_step(self, step_number: int, screenshot_path: Path, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Protokolliert einen Schritt mit Screenshot-Hash
        
        Args:
            step_number: Schrittnummer
            screenshot_path: Pfad zum Screenshot
            metadata: Zusätzliche Metadaten
            
        Returns:
            Audit-Eintrag als Dictionary
        """
        timestamp = datetime.now()
        
        # Berechne SHA-256 Hash des Screenshots
        screenshot_hash = self._calculate_file_hash(screenshot_path)
        
        audit_entry = {
            "session_id": self.session_id,
            "step_number": step_number,
            "timestamp": timestamp.isoformat(),
            "username": self.username,
            "systemname": self.systemname,
            "screenshot_path": str(screenshot_path),
            "screenshot_hash": screenshot_hash,
            "metadata": metadata
        }
        
        self.audit_entries.append(audit_entry)
        return audit_entry
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """
        Berechnet SHA-256 Hash einer Datei
        
        Args:
            file_path: Pfad zur Datei
            
        Returns:
            Hex-String des Hash-Werts
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def export_json(self, filename: Optional[str] = None) -> Path:
        """
        Exportiert Audit-Trail als JSON
        
        Args:
            filename: Optionaler Dateiname
            
        Returns:
            Pfad zur erstellten JSON-Datei
        """
        if filename is None:
            filename = f"audit_{self.session_id}.json"
        
        output_path = self.output_dir / filename
        
        audit_data = {
            "session_id": self.session_id,
            "session_start": self.session_start_time.isoformat(),
            "session_end": datetime.now().isoformat(),
            "username": self.username,
            "systemname": self.systemname,
            "entries": self.audit_entries
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(audit_data, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def export_csv(self, filename: Optional[str] = None) -> Path:
        """
        Exportiert Audit-Trail als CSV
        
        Args:
            filename: Optionaler Dateiname
            
        Returns:
            Pfad zur erstellten CSV-Datei
        """
        if filename is None:
            filename = f"audit_{self.session_id}.csv"
        
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            if not self.audit_entries:
                return output_path
            
            writer = csv.DictWriter(f, fieldnames=self.audit_entries[0].keys())
            writer.writeheader()
            
            for entry in self.audit_entries:
                # Flatten metadata für CSV
                row = entry.copy()
                if 'metadata' in row:
                    row['metadata'] = json.dumps(row['metadata'])
                writer.writerow(row)
        
        return output_path


