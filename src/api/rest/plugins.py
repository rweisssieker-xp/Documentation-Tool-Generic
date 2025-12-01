"""
Plugin System REST API
"""

from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from src.plugins import PluginManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PluginInfo(BaseModel):
    """Plugin information"""
    id: str
    name: str
    version: str
    description: Optional[str] = None
    author: Optional[str] = None


class PluginAPI:
    """Plugin System API"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        self.manager = PluginManager()
    
    def _setup_routes(self):
        """Setup routes"""
        @self.router.get("/list", response_model=List[PluginInfo])
        async def list_plugins():
            """List all loaded plugins"""
            try:
                plugins = self.manager.list_plugins()
                result = []
                for plugin_data in plugins:
                    if isinstance(plugin_data, dict):
                        metadata = plugin_data.get('metadata', {})
                        result.append(PluginInfo(
                            id=plugin_data.get('id', 'unknown'),
                            name=metadata.get('name', 'Unknown'),
                            version=metadata.get('version', '1.0.0'),
                            description=metadata.get('description'),
                            author=metadata.get('author'),
                        ))
                return result
            except Exception as e:
                logger.error(f"Error listing plugins: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/load")
        async def load_plugin(plugin_path: str):
            """Load plugin from path"""
            try:
                success = self.manager.load_plugin(plugin_path)
                if not success:
                    raise HTTPException(status_code=400, detail="Failed to load plugin")
                return {"status": "loaded", "path": plugin_path}
            except Exception as e:
                logger.error(f"Error loading plugin: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/upload")
        async def upload_plugin(plugin_file: UploadFile = File(...)):
            """Upload and load plugin"""
            try:
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
                    content = await plugin_file.read()
                    tmp.write(content)
                    tmp_path = tmp.name
                
                success = self.manager.load_plugin(tmp_path)
                os.unlink(tmp_path)
                
                if not success:
                    raise HTTPException(status_code=400, detail="Failed to load plugin")
                return {"status": "uploaded_and_loaded"}
            except Exception as e:
                logger.error(f"Error uploading plugin: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.delete("/unload/{plugin_id}")
        async def unload_plugin(plugin_id: str):
            """Unload plugin"""
            try:
                success = self.manager.unload_plugin(plugin_id)
                if not success:
                    raise HTTPException(status_code=404, detail="Plugin not found")
                return {"status": "unloaded", "plugin_id": plugin_id}
            except Exception as e:
                logger.error(f"Error unloading plugin: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/{plugin_id}")
        async def get_plugin(plugin_id: str):
            """Get plugin information"""
            try:
                plugin = self.manager.get_plugin(plugin_id)
                if not plugin:
                    raise HTTPException(status_code=404, detail="Plugin not found")
                return {"id": plugin_id, "loaded": True}
            except Exception as e:
                logger.error(f"Error getting plugin: {e}")
                raise HTTPException(status_code=500, detail=str(e))
