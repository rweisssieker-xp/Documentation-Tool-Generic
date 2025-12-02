"""
Tests for Predictive Documentation Maintenance
"""

import pytest

from src.predictive import PredictiveMaintenanceEngine


class TestPredictiveMaintenanceEngine:
    """Test Predictive Maintenance Engine"""
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        engine = PredictiveMaintenanceEngine()
        assert engine.ast_parser is not None
        assert engine.diff_detector is not None
        assert engine.screenshot_diff is not None
    
    def test_analyze_documentation(self):
        """Test documentation analysis"""
        engine = PredictiveMaintenanceEngine()
        issues = engine.analyze_documentation("test_session")
        
        assert isinstance(issues, list)


class TestASTParser:
    """Test AST Parser"""
    
    def test_parser_initialization(self):
        """Test parser initialization"""
        from src.predictive.code_analysis.ast_parser import ASTParser
        
        parser = ASTParser()
        assert parser is not None
    
    def test_extract_functions(self):
        """Test function extraction"""
        from src.predictive.code_analysis.ast_parser import ASTParser
        import ast
        
        parser = ASTParser()
        code = "def test_function(): pass"
        ast_tree = ast.parse(code)
        
        functions = parser.extract_functions(ast_tree)
        assert "test_function" in functions



