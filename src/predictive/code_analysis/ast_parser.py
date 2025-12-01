"""
AST Parser - Analysiert Code-Struktur
"""

from typing import Dict, Any, Optional, List
import ast

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ASTParser:
    """AST Parser"""
    
    def parse_file(self, file_path: str) -> Optional[ast.AST]:
        """Parse Python file to AST"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            return ast.parse(code)
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}")
            return None
    
    def extract_functions(self, ast_tree: ast.AST) -> List[str]:
        """Extract function names from AST"""
        functions = []
        
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
        
        return functions
    
    def extract_classes(self, ast_tree: ast.AST) -> List[str]:
        """Extract class names from AST"""
        classes = []
        
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
        
        return classes

