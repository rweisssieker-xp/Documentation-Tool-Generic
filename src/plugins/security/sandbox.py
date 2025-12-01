"""
Sandbox Executor - Sicherer Plugin-Execution
"""

from typing import Any, Optional
import sys
import importlib.util

from src.utils.logger import get_logger

logger = get_logger(__name__)


class SandboxExecutor:
    """Sandbox executor for plugins"""
    
    def __init__(self):
        """Initialize sandbox"""
        self.allowed_modules = {
            'json', 'pathlib', 'datetime', 'typing', 'dataclasses',
            'collections', 'enum', 'logging',
        }
        self.blocked_modules = {
            'os', 'sys', 'subprocess', 'socket', 'urllib',
            'pickle', 'marshal', 'ctypes',
        }
    
    def execute_plugin(self, plugin_code: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute plugin code in sandbox.
        
        Args:
            plugin_code: Plugin code to execute
            context: Execution context
        
        Returns:
            Execution result
        """
        # Create restricted globals
        restricted_globals = {
            '__builtins__': {
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'isinstance': isinstance,
                'hasattr': hasattr,
                'getattr': getattr,
                'setattr': setattr,
            },
        }
        
        # Add allowed modules
        for module_name in self.allowed_modules:
            try:
                module = __import__(module_name)
                restricted_globals[module_name] = module
            except ImportError:
                pass
        
        # Add context
        if context:
            restricted_globals.update(context)
        
        try:
            # Execute in restricted environment
            exec(plugin_code, restricted_globals)
            return restricted_globals.get('result')
        except Exception as e:
            logger.error(f"Sandbox execution error: {e}")
            raise
    
    def validate_plugin(self, plugin_code: str) -> bool:
        """Validate plugin code"""
        # Check for blocked imports
        for blocked in self.blocked_modules:
            if f"import {blocked}" in plugin_code or f"from {blocked}" in plugin_code:
                logger.warning(f"Plugin uses blocked module: {blocked}")
                return False
        
        return True

