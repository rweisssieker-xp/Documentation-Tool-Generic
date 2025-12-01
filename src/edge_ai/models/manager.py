"""
Model Manager - Verwaltet lokale Modelle
"""

from pathlib import Path
from typing import Dict, Optional, List
import json

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ModelManager:
    """Model Manager"""
    
    def __init__(self, models_dir: str = "data/models"):
        """
        Initialize Model Manager.
        
        Args:
            models_dir: Directory for models
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.models: Dict[str, Dict] = {}
        self._load_models()
    
    def _load_models(self):
        """Load model registry"""
        registry_file = self.models_dir / "registry.json"
        if registry_file.exists():
            try:
                with open(registry_file, 'r', encoding='utf-8') as f:
                    self.models = json.load(f)
            except Exception as e:
                logger.error(f"Error loading model registry: {e}")
                self.models = {}
        else:
            self.models = {}
    
    def register_model(self, model_id: str, model_path: str, model_type: str, metadata: Dict):
        """Register model"""
        self.models[model_id] = {
            'path': model_path,
            'type': model_type,
            'metadata': metadata,
        }
        self._save_registry()
    
    def get_model(self, model_id: str) -> Optional[Dict]:
        """Get model info"""
        return self.models.get(model_id)
    
    def list_models(self) -> List[Dict]:
        """List all models"""
        return list(self.models.values())
    
    def download_model(self, model_id: str, model_url: str):
        """Download model"""
        # This would implement model downloading
        # For now, just a placeholder
        logger.info(f"Downloading model {model_id} from {model_url}")
    
    def _save_registry(self):
        """Save model registry"""
        registry_file = self.models_dir / "registry.json"
        try:
            with open(registry_file, 'w', encoding='utf-8') as f:
                json.dump(self.models, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving model registry: {e}")

