"""
Cloud-Integration: Upload zu OneDrive, SharePoint, Google Drive
"""

from pathlib import Path
from typing import Optional, Dict
import os

from src.utils.logger import get_logger

logger = get_logger(__name__)


class CloudExporter:
    """Exportiert Dokumente zu Cloud-Speichern"""
    
    def __init__(self):
        """Initialisiert den Cloud Exporter"""
        self.onedrive_client = None
        self.sharepoint_client = None
        self.google_drive_client = None
    
    def upload_to_onedrive(
        self,
        file_path: Path,
        folder_path: str = "/Documentation",
        access_token: Optional[str] = None
    ) -> Dict:
        """
        Lädt Datei zu OneDrive hoch
        
        Args:
            file_path: Pfad zur hochzuladenden Datei
            folder_path: Zielordner in OneDrive
            access_token: OAuth Access Token (falls nicht in Config)
            
        Returns:
            Dictionary mit Upload-Informationen
        """
        try:
            # Lade Access Token aus Config falls nicht angegeben
            if not access_token:
                access_token = os.getenv('ONEDRIVE_ACCESS_TOKEN')
            
            if not access_token:
                raise ValueError("OneDrive Access Token nicht gefunden. Bitte konfigurieren Sie ONEDRIVE_ACCESS_TOKEN.")
            
            # Microsoft Graph API Upload
            import requests
            
            file_name = file_path.name
            file_size = file_path.stat().st_size
            
            # Erstelle Upload-Session
            upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:{folder_path}/{file_name}:/createUploadSession"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            session_data = {
                'item': {
                    '@microsoft.graph.conflictBehavior': 'replace'
                }
            }
            
            response = requests.post(upload_url, json=session_data, headers=headers)
            
            if response.status_code not in [200, 201]:
                raise Exception(f"Upload-Session konnte nicht erstellt werden: {response.status_code} - {response.text}")
            
            upload_session = response.json()
            upload_url_session = upload_session['uploadUrl']
            
            # Upload Datei
            with open(file_path, 'rb') as f:
                upload_response = requests.put(
                    upload_url_session,
                    data=f.read(),
                    headers={
                        'Content-Length': str(file_size),
                        'Content-Range': f'bytes 0-{file_size - 1}/{file_size}'
                    }
                )
            
            if upload_response.status_code in [200, 201]:
                logger.info(f"Datei erfolgreich zu OneDrive hochgeladen: {file_name}")
                return {
                    'success': True,
                    'file_name': file_name,
                    'url': upload_response.json().get('webUrl', ''),
                    'service': 'onedrive'
                }
            else:
                raise Exception(f"Upload fehlgeschlagen: {upload_response.status_code} - {upload_response.text}")
        
        except ImportError:
            raise ImportError("requests-Bibliothek erforderlich für OneDrive-Upload. Installieren Sie sie mit: pip install requests")
        except Exception as e:
            logger.error(f"Fehler beim OneDrive-Upload: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'service': 'onedrive'
            }
    
    def upload_to_sharepoint(
        self,
        file_path: Path,
        site_url: str,
        folder_path: str = "/Documentation",
        access_token: Optional[str] = None
    ) -> Dict:
        """
        Lädt Datei zu SharePoint hoch
        
        Args:
            file_path: Pfad zur hochzuladenden Datei
            site_url: SharePoint Site URL
            folder_path: Zielordner
            access_token: OAuth Access Token
            
        Returns:
            Dictionary mit Upload-Informationen
        """
        try:
            import requests
            
            if not access_token:
                access_token = os.getenv('SHAREPOINT_ACCESS_TOKEN')
            
            if not access_token:
                raise ValueError("SharePoint Access Token nicht gefunden.")
            
            file_name = file_path.name
            
            # SharePoint REST API Upload
            upload_url = f"{site_url}/_api/web/GetFolderByServerRelativeUrl('{folder_path}')/Files/Add(url='{file_name}', overwrite=true)"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json;odata=verbose'
            }
            
            with open(file_path, 'rb') as f:
                response = requests.post(upload_url, data=f.read(), headers=headers)
            
            if response.status_code in [200, 201]:
                logger.info(f"Datei erfolgreich zu SharePoint hochgeladen: {file_name}")
                return {
                    'success': True,
                    'file_name': file_name,
                    'service': 'sharepoint'
                }
            else:
                raise Exception(f"Upload fehlgeschlagen: {response.status_code} - {response.text}")
        
        except Exception as e:
            logger.error(f"Fehler beim SharePoint-Upload: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'service': 'sharepoint'
            }
    
    def upload_to_google_drive(
        self,
        file_path: Path,
        folder_id: Optional[str] = None,
        access_token: Optional[str] = None
    ) -> Dict:
        """
        Lädt Datei zu Google Drive hoch
        
        Args:
            file_path: Pfad zur hochzuladenden Datei
            folder_id: Google Drive Ordner-ID (optional)
            access_token: OAuth Access Token
            
        Returns:
            Dictionary mit Upload-Informationen
        """
        try:
            import requests
            
            if not access_token:
                access_token = os.getenv('GOOGLE_DRIVE_ACCESS_TOKEN')
            
            if not access_token:
                raise ValueError("Google Drive Access Token nicht gefunden.")
            
            file_name = file_path.name
            
            # Google Drive API Upload
            metadata = {
                'name': file_name
            }
            
            if folder_id:
                metadata['parents'] = [folder_id]
            
            # Erstelle Datei-Metadaten
            files = {
                'data': ('metadata', str(metadata), 'application/json; charset=UTF-8'),
                'file': open(file_path, 'rb')
            }
            
            response = requests.post(
                'https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart',
                headers={'Authorization': f'Bearer {access_token}'},
                files=files
            )
            
            files['file'].close()
            
            if response.status_code in [200, 201]:
                file_data = response.json()
                logger.info(f"Datei erfolgreich zu Google Drive hochgeladen: {file_name}")
                return {
                    'success': True,
                    'file_name': file_name,
                    'file_id': file_data.get('id', ''),
                    'service': 'google_drive'
                }
            else:
                raise Exception(f"Upload fehlgeschlagen: {response.status_code} - {response.text}")
        
        except Exception as e:
            logger.error(f"Fehler beim Google Drive-Upload: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'service': 'google_drive'
            }
    
    def upload_multiple(
        self,
        files: list[Path],
        service: str,
        **kwargs
    ) -> Dict:
        """
        Lädt mehrere Dateien hoch
        
        Args:
            files: Liste von Dateipfaden
            service: Service ('onedrive', 'sharepoint', 'google_drive')
            **kwargs: Weitere Parameter für Upload
            
        Returns:
            Dictionary mit Upload-Ergebnissen
        """
        results = {
            'successful': [],
            'failed': []
        }
        
        for file_path in files:
            if service == 'onedrive':
                result = self.upload_to_onedrive(file_path, **kwargs)
            elif service == 'sharepoint':
                result = self.upload_to_sharepoint(file_path, **kwargs)
            elif service == 'google_drive':
                result = self.upload_to_google_drive(file_path, **kwargs)
            else:
                result = {'success': False, 'error': f'Unbekannter Service: {service}'}
            
            if result.get('success'):
                results['successful'].append(str(file_path))
            else:
                results['failed'].append({
                    'file': str(file_path),
                    'error': result.get('error', 'Unbekannter Fehler')
                })
        
        return results

