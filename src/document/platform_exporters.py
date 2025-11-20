"""
Platform Exporters: Export zu Confluence, Notion, SharePoint
"""

from pathlib import Path
from typing import List, Dict, Optional
import os
import requests

from src.utils.logger import get_logger

logger = get_logger(__name__)


class PlatformExporters:
    """Exportiert Dokumente zu verschiedenen Plattformen"""
    
    def __init__(self):
        """Initialisiert die Platform Exporters"""
        pass
    
    def export_to_confluence(
        self,
        steps: List[Dict],
        space_key: str,
        title: str,
        parent_id: Optional[str] = None,
        base_url: Optional[str] = None,
        username: Optional[str] = None,
        api_token: Optional[str] = None
    ) -> Dict:
        """
        Exportiert zu Confluence
        
        Args:
            steps: Liste von Schritten
            space_key: Confluence Space Key
            title: Seitentitel
            parent_id: Parent Page ID (optional)
            base_url: Confluence Base URL
            username: Confluence Username
            api_token: Confluence API Token
            
        Returns:
            Dictionary mit Export-Ergebnissen
        """
        try:
            if not base_url:
                base_url = os.getenv('CONFLUENCE_BASE_URL')
            if not username:
                username = os.getenv('CONFLUENCE_USERNAME')
            if not api_token:
                api_token = os.getenv('CONFLUENCE_API_TOKEN')
            
            if not all([base_url, username, api_token]):
                raise ValueError("Confluence-Konfiguration unvollständig. Bitte setzen Sie CONFLUENCE_BASE_URL, CONFLUENCE_USERNAME und CONFLUENCE_API_TOKEN.")
            
            # Generiere Confluence-Wiki-Markup
            wiki_content = self._generate_confluence_wiki(steps, title)
            
            # Erstelle/Update Seite
            url = f"{base_url}/rest/api/content"
            
            headers = {
                'Authorization': f'Basic {self._encode_auth(username, api_token)}',
                'Content-Type': 'application/json'
            }
            
            page_data = {
                'type': 'page',
                'title': title,
                'space': {'key': space_key},
                'body': {
                    'storage': {
                        'value': wiki_content,
                        'representation': 'wiki'
                    }
                }
            }
            
            if parent_id:
                page_data['ancestors'] = [{'id': parent_id}]
            
            response = requests.post(url, json=page_data, headers=headers)
            
            if response.status_code in [200, 201]:
                page_info = response.json()
                logger.info(f"Seite erfolgreich zu Confluence exportiert: {title}")
                return {
                    'success': True,
                    'page_id': page_info.get('id', ''),
                    'page_url': f"{base_url}/pages/viewpage.action?pageId={page_info.get('id', '')}",
                    'platform': 'confluence'
                }
            else:
                raise Exception(f"Export fehlgeschlagen: {response.status_code} - {response.text}")
        
        except Exception as e:
            logger.error(f"Fehler beim Confluence-Export: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'platform': 'confluence'
            }
    
    def export_to_notion(
        self,
        steps: List[Dict],
        database_id: str,
        title: str,
        notion_token: Optional[str] = None
    ) -> Dict:
        """
        Exportiert zu Notion
        
        Args:
            steps: Liste von Schritten
            database_id: Notion Database ID
            title: Seitentitel
            notion_token: Notion Integration Token
            
        Returns:
            Dictionary mit Export-Ergebnissen
        """
        try:
            if not notion_token:
                notion_token = os.getenv('NOTION_TOKEN')
            
            if not notion_token:
                raise ValueError("Notion Token nicht gefunden. Bitte setzen Sie NOTION_TOKEN.")
            
            # Notion API v1
            url = "https://api.notion.com/v1/pages"
            
            headers = {
                'Authorization': f'Bearer {notion_token}',
                'Content-Type': 'application/json',
                'Notion-Version': '2022-06-28'
            }
            
            # Erstelle Page in Database
            page_data = {
                'parent': {'database_id': database_id},
                'properties': {
                    'title': {
                        'title': [{'text': {'content': title}}]
                    }
                },
                'children': self._generate_notion_blocks(steps)
            }
            
            response = requests.post(url, json=page_data, headers=headers)
            
            if response.status_code in [200, 201]:
                page_info = response.json()
                logger.info(f"Seite erfolgreich zu Notion exportiert: {title}")
                return {
                    'success': True,
                    'page_id': page_info.get('id', ''),
                    'platform': 'notion'
                }
            else:
                raise Exception(f"Export fehlgeschlagen: {response.status_code} - {response.text}")
        
        except Exception as e:
            logger.error(f"Fehler beim Notion-Export: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'platform': 'notion'
            }
    
    def export_to_sharepoint(
        self,
        steps: List[Dict],
        site_url: str,
        folder_path: str,
        title: str,
        access_token: Optional[str] = None
    ) -> Dict:
        """
        Exportiert zu SharePoint (verwendet Microsoft Graph API)
        
        Args:
            steps: Liste von Schritten
            site_url: SharePoint Site URL
            folder_path: Zielordner
            title: Dokumenttitel
            access_token: OAuth Access Token
            
        Returns:
            Dictionary mit Export-Ergebnissen
        """
        try:
            if not access_token:
                access_token = os.getenv('SHAREPOINT_ACCESS_TOKEN')
            
            if not access_token:
                raise ValueError("SharePoint Access Token nicht gefunden.")
            
            # Erstelle Markdown-Inhalt
            from src.document.markdown_exporter import MarkdownExporter
            
            markdown_exporter = MarkdownExporter()
            temp_md = Path("temp") / f"{title}.md"
            temp_md.parent.mkdir(exist_ok=True)
            
            markdown_exporter.export(
                steps=steps,
                output_path=temp_md,
                title=title,
                include_screenshots=True
            )
            
            # Upload zu SharePoint
            from src.document.cloud_exporter import CloudExporter
            
            cloud_exporter = CloudExporter()
            result = cloud_exporter.upload_to_sharepoint(
                file_path=temp_md,
                site_url=site_url,
                folder_path=folder_path,
                access_token=access_token
            )
            
            # Lösche temporäre Datei
            if temp_md.exists():
                temp_md.unlink()
            
            if result.get('success'):
                logger.info(f"Dokument erfolgreich zu SharePoint exportiert: {title}")
            
            return result
        
        except Exception as e:
            logger.error(f"Fehler beim SharePoint-Export: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'platform': 'sharepoint'
            }
    
    def _generate_confluence_wiki(self, steps: List[Dict], title: str) -> str:
        """Generiert Confluence Wiki-Markup"""
        lines = [
            f"h1. {title}",
            "",
        ]
        
        for step in steps:
            step_num = step.get('step_number', '?')
            window_title = step.get('window_title', 'Unbekannt')
            description = step.get('description', '')
            
            lines.append(f"h2. Schritt {step_num}: {window_title}")
            lines.append("")
            
            if description:
                lines.append(description)
                lines.append("")
            
            screenshot_path = step.get('screenshot_path', '')
            if screenshot_path and Path(screenshot_path).exists():
                # Confluence Image-Syntax
                lines.append(f"!{screenshot_path}!")
                lines.append("")
        
        return "\n".join(lines)
    
    def _generate_notion_blocks(self, steps: List[Dict]) -> List[Dict]:
        """Generiert Notion Blocks"""
        blocks = []
        
        for step in steps:
            step_num = step.get('step_number', '?')
            window_title = step.get('window_title', 'Unbekannt')
            description = step.get('description', '')
            
            # Heading
            blocks.append({
                'object': 'block',
                'type': 'heading_2',
                'heading_2': {
                    'rich_text': [{'text': {'content': f'Schritt {step_num}: {window_title}'}}]
                }
            })
            
            # Description
            if description:
                blocks.append({
                    'object': 'block',
                    'type': 'paragraph',
                    'paragraph': {
                        'rich_text': [{'text': {'content': description}}]
                    }
                })
            
            # Screenshot (als Link)
            screenshot_path = step.get('screenshot_path', '')
            if screenshot_path:
                blocks.append({
                    'object': 'block',
                    'type': 'paragraph',
                    'paragraph': {
                        'rich_text': [{'text': {'content': f'Screenshot: {screenshot_path}'}}]
                    }
                })
        
        return blocks
    
    def _encode_auth(self, username: str, password: str) -> str:
        """Kodiert Basic Auth"""
        import base64
        credentials = f"{username}:{password}"
        return base64.b64encode(credentials.encode()).decode()

