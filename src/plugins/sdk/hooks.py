"""
Hook System - Plugin Hooks
"""

from typing import Dict, List, Callable, Any
from collections import defaultdict

from src.utils.logger import get_logger

logger = get_logger(__name__)


class HookSystem:
    """Hook system for plugins"""
    
    def __init__(self):
        self.hooks: Dict[str, List[Callable]] = defaultdict(list)
    
    def register_hook(self, hook_name: str, callback: Callable):
        """Register hook callback"""
        self.hooks[hook_name].append(callback)
        logger.debug(f"Registered hook: {hook_name}")
    
    def unregister_hook(self, hook_name: str, callback: Callable):
        """Unregister hook callback"""
        if hook_name in self.hooks:
            self.hooks[hook_name].remove(callback)
    
    def execute_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Execute hook"""
        results = []
        
        for callback in self.hooks.get(hook_name, []):
            try:
                result = callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Error executing hook {hook_name}: {e}")
        
        return results

