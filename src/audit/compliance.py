"""
Compliance-Modul für SHA-256 und Zeitstempel
"""

import hashlib
import os
import platform
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict


class Compliance:
    """Utilities für Compliance-Anforderungen"""
    
    @staticmethod
    def calculate_sha256(file_path: Path) -> str:
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
    
    @staticmethod
    def get_timestamp(format: str = "iso") -> str:
        """
        Gibt aktuellen Zeitstempel zurück
        
        Args:
            format: Format ('iso', 'filename', 'human')
            
        Returns:
            Formatierter Zeitstempel
        """
        now = datetime.now()
        
        if format == "iso":
            return now.isoformat()
        elif format == "filename":
            return now.strftime("%Y%m%d_%H%M%S")
        elif format == "human":
            return now.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return now.isoformat()
    
    @staticmethod
    def verify_file_integrity(file_path: Path, expected_hash: str) -> bool:
        """
        Verifiziert Integrität einer Datei gegen erwarteten Hash
        
        Args:
            file_path: Pfad zur Datei
            expected_hash: Erwarteter SHA-256 Hash
            
        Returns:
            True wenn Hash übereinstimmt
        """
        actual_hash = Compliance.calculate_sha256(file_path)
        return actual_hash == expected_hash
    
    @staticmethod
    def get_user_info() -> Dict[str, str]:
        """
        Gibt Benutzerinformationen zurück
        
        Returns:
            Dictionary mit username und system_name
        """
        return {
            'username': os.getenv('USERNAME', os.getenv('USER', 'unknown')),
            'system_name': platform.node()
        }


