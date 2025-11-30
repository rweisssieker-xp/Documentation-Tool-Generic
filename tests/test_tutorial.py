"""
Tests for Interactive Tutorial Generator Module
"""

import pytest
from unittest.mock import Mock, patch


class TestTutorialGenerator:
    """Tests for TutorialGenerator class."""
    
    def test_tutorial_generator_initialization(self):
        """Test TutorialGenerator initialization."""
        from src.tutorial.tutorial_generator import TutorialGenerator
        
        generator = TutorialGenerator()
        assert generator.include_quizzes == True
    
    def test_generate_tutorial(self):
        """Test generating a tutorial."""
        from src.tutorial.tutorial_generator import TutorialGenerator
        
        generator = TutorialGenerator(include_quizzes=False)
        
        session_data = {
            "session_id": "sess_001",
            "name": "Login Tutorial",
            "description": "Learn how to login",
            "steps": [
                {"title": "Open App", "description": "Open the application"},
                {"title": "Enter Username", "description": "Enter your username"},
                {"title": "Click Login", "description": "Click the login button"}
            ]
        }
        
        tutorial = generator.generate_tutorial(session_data)
        
        assert tutorial.title == "Login Tutorial"
        assert len(tutorial.steps) == 3
        assert tutorial.difficulty in ["Anfänger", "Fortgeschritten", "Experte"]
    
    def test_export_html(self, tmp_path):
        """Test HTML export."""
        from src.tutorial.tutorial_generator import TutorialGenerator, Tutorial, TutorialStep
        
        generator = TutorialGenerator(include_quizzes=False)
        
        tutorial = Tutorial(
            id="tut_001",
            title="Test Tutorial",
            description="A test tutorial",
            steps=[
                TutorialStep(id="s1", title="Step 1", content="First step"),
                TutorialStep(id="s2", title="Step 2", content="Second step")
            ],
            prerequisites=["Basic knowledge"],
            learning_objectives=["Learn basics"],
            difficulty="Anfänger",
            estimated_duration=300,
            tags=["test"]
        )
        
        output_path = str(tmp_path / "tutorial.html")
        html = generator.export_html(tutorial, output_path)
        
        assert "Test Tutorial" in html
        assert "Step 1" in html
        assert "</html>" in html


class TestQuizGenerator:
    """Tests for QuizGenerator class."""
    
    def test_quiz_generator_initialization(self):
        """Test QuizGenerator initialization."""
        from src.tutorial.quiz_generator import QuizGenerator
        
        generator = QuizGenerator(use_ai=False)
        assert generator.use_ai == False
    
    def test_generate_template_quiz(self):
        """Test template-based quiz generation."""
        from src.tutorial.quiz_generator import QuizGenerator
        
        generator = QuizGenerator(use_ai=False)
        
        step = {
            "description": "Click on the submit button",
            "title": "Submit Form"
        }
        
        quiz = generator.generate_quiz_for_step(step)
        
        assert quiz is not None
        assert "question" in quiz
        assert "answers" in quiz
    
    def test_generate_quiz_for_input_step(self):
        """Test quiz generation for input step."""
        from src.tutorial.quiz_generator import QuizGenerator
        
        generator = QuizGenerator(use_ai=False)
        
        step = {
            "description": "Enter your email address",
            "input_value": "test@example.com"
        }
        
        quiz = generator.generate_quiz_for_step(step)
        
        assert quiz is not None


class TestSCORMExporter:
    """Tests for SCORMExporter class."""
    
    def test_scorm_exporter_initialization(self):
        """Test SCORMExporter initialization."""
        from src.tutorial.scorm_exporter import SCORMExporter
        
        exporter = SCORMExporter(organization_id="TEST")
        assert exporter.organization_id == "TEST"
    
    def test_create_manifest(self):
        """Test SCORM manifest creation."""
        from src.tutorial.scorm_exporter import SCORMExporter
        from src.tutorial.tutorial_generator import Tutorial, TutorialStep
        
        exporter = SCORMExporter()
        
        tutorial = Tutorial(
            id="tut_001",
            title="Test Tutorial",
            description="Description",
            steps=[TutorialStep(id="s1", title="Step 1", content="Content")],
            prerequisites=[],
            learning_objectives=[],
            difficulty="Anfänger",
            estimated_duration=300,
            tags=[]
        )
        
        manifest = exporter._create_manifest(tutorial)
        
        assert '<?xml version="1.0"' in manifest
        assert "ADL SCORM" in manifest
        assert "Test Tutorial" in manifest


class TestLearningPathOptimizer:
    """Tests for LearningPathOptimizer class."""
    
    def test_learning_path_initialization(self):
        """Test LearningPathOptimizer initialization."""
        from src.tutorial.learning_path import LearningPathOptimizer
        
        optimizer = LearningPathOptimizer()
        assert optimizer is not None
    
    def test_optimize_path_beginner(self):
        """Test optimizing path for beginner."""
        from src.tutorial.learning_path import LearningPathOptimizer, LearningNode, LearnerLevel
        
        optimizer = LearningPathOptimizer()
        
        nodes = [
            LearningNode(id="n1", content="Easy", difficulty=0.2, prerequisites=[], estimated_time=60, importance=0.8),
            LearningNode(id="n2", content="Medium", difficulty=0.5, prerequisites=["n1"], estimated_time=120, importance=0.7),
            LearningNode(id="n3", content="Hard", difficulty=0.9, prerequisites=["n2"], estimated_time=180, importance=0.6)
        ]
        
        optimized = optimizer.optimize_path(nodes, learner_level=LearnerLevel.BEGINNER)
        
        assert len(optimized) >= 1
        # Beginner should start with easy content
        assert optimized[0].difficulty <= 0.5
    
    def test_optimize_path_with_time_constraint(self):
        """Test path optimization with time constraint."""
        from src.tutorial.learning_path import LearningPathOptimizer, LearningNode, LearnerLevel
        
        optimizer = LearningPathOptimizer()
        
        nodes = [
            LearningNode(id="n1", content="Quick", difficulty=0.3, prerequisites=[], estimated_time=60, importance=0.9),
            LearningNode(id="n2", content="Long", difficulty=0.5, prerequisites=[], estimated_time=300, importance=0.5)
        ]
        
        # Only 100 seconds available
        optimized = optimizer.optimize_path(nodes, available_time=100)
        
        # Should select shorter, high-importance node
        assert len(optimized) == 1
        assert optimized[0].id == "n1"
    
    def test_suggest_next(self):
        """Test suggesting next learning node."""
        from src.tutorial.learning_path import LearningPathOptimizer, LearningNode
        
        optimizer = LearningPathOptimizer()
        
        nodes = [
            LearningNode(id="n1", content="Done", difficulty=0.2, prerequisites=[], estimated_time=60, importance=0.8),
            LearningNode(id="n2", content="Next", difficulty=0.4, prerequisites=["n1"], estimated_time=60, importance=0.8)
        ]
        
        suggestion = optimizer.suggest_next(
            completed_nodes=["n1"],
            all_nodes=nodes,
            performance=0.8
        )
        
        assert suggestion is not None
        assert suggestion.id == "n2"

