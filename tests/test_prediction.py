"""
Tests for Predictive Documentation Assistant Module
"""

import pytest
from unittest.mock import Mock, patch


class TestStepPredictor:
    """Tests for StepPredictor class."""
    
    def test_step_predictor_initialization(self, tmp_path):
        """Test StepPredictor initialization."""
        from src.prediction.step_predictor import StepPredictor
        
        predictor = StepPredictor(model_dir=str(tmp_path))
        assert predictor.min_confidence == 0.3
    
    def test_learn_from_session(self, tmp_path):
        """Test learning patterns from session."""
        from src.prediction.step_predictor import StepPredictor
        
        predictor = StepPredictor(model_dir=str(tmp_path))
        
        session_steps = [
            {"action_type": "click", "window_title": "App"},
            {"action_type": "input", "window_title": "App"},
            {"action_type": "save", "window_title": "App"}
        ]
        
        patterns_learned = predictor.learn_from_session(session_steps, "TestApp")
        assert patterns_learned > 0
    
    def test_predict_next_with_patterns(self, tmp_path):
        """Test prediction with learned patterns."""
        from src.prediction.step_predictor import StepPredictor
        
        predictor = StepPredictor(model_dir=str(tmp_path), min_pattern_frequency=1)
        
        # Learn a pattern
        session_steps = [
            {"action_type": "open"},
            {"action_type": "edit"},
            {"action_type": "save"}
        ]
        predictor.learn_from_session(session_steps)
        predictor.learn_from_session(session_steps)  # Learn twice for frequency
        
        # Predict based on partial sequence
        predictions = predictor.predict_next([
            {"action_type": "open"},
            {"action_type": "edit"}
        ])
        
        # Should predict something
        assert isinstance(predictions, list)
    
    def test_get_pattern_statistics(self, tmp_path):
        """Test getting pattern statistics."""
        from src.prediction.step_predictor import StepPredictor
        
        predictor = StepPredictor(model_dir=str(tmp_path))
        
        stats = predictor.get_pattern_statistics()
        assert "global_patterns" in stats
        assert "workflow_templates" in stats


class TestGapAnalyzer:
    """Tests for GapAnalyzer class."""
    
    def test_gap_analyzer_initialization(self):
        """Test GapAnalyzer initialization."""
        from src.prediction.gap_analyzer import GapAnalyzer
        
        analyzer = GapAnalyzer()
        assert analyzer is not None
    
    def test_analyze_empty_session(self):
        """Test analyzing empty session."""
        from src.prediction.gap_analyzer import GapAnalyzer, GapSeverity
        
        analyzer = GapAnalyzer()
        
        gaps = analyzer.analyze_session({"steps": []})
        
        assert len(gaps) > 0
        assert any(g.severity == GapSeverity.CRITICAL for g in gaps)
    
    def test_analyze_step_quality(self):
        """Test step quality analysis."""
        from src.prediction.gap_analyzer import GapAnalyzer, GapSeverity
        
        analyzer = GapAnalyzer()
        
        session = {
            "steps": [
                {"id": "1", "description": "Short"},  # Too short
                {"id": "2", "description": "This is a proper step description with details"}
            ]
        }
        
        gaps = analyzer.analyze_session(session, check_quality=True)
        
        # Should find gaps for missing screenshots and short descriptions
        assert len(gaps) > 0
    
    def test_get_completeness_score(self):
        """Test completeness score calculation."""
        from src.prediction.gap_analyzer import GapAnalyzer
        
        analyzer = GapAnalyzer()
        
        session = {
            "steps": [
                {"screenshot": "img1.png", "description": "Step 1 description", "action_type": "click"},
                {"description": "Step 2 without screenshot"}
            ]
        }
        
        score = analyzer.get_completeness_score(session)
        
        assert "overall_score" in score
        assert "screenshot_coverage" in score
        assert score["total_steps"] == 2


class TestAutoCompleter:
    """Tests for AutoCompleter class."""
    
    @patch('src.prediction.auto_completer.OPENAI_AVAILABLE', True)
    @patch('src.prediction.auto_completer.OpenAI')
    def test_auto_completer_initialization(self, mock_openai):
        """Test AutoCompleter initialization."""
        from src.prediction.auto_completer import AutoCompleter
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
            completer = AutoCompleter()
            assert completer.model == "gpt-4o-mini"


class TestWorkflowLearner:
    """Tests for WorkflowLearner class."""
    
    def test_workflow_learner_initialization(self, tmp_path):
        """Test WorkflowLearner initialization."""
        from src.prediction.workflow_learner import WorkflowLearner
        
        learner = WorkflowLearner(storage_dir=str(tmp_path))
        assert learner.min_frequency == 2
    
    def test_create_template(self, tmp_path):
        """Test creating a workflow template."""
        from src.prediction.workflow_learner import WorkflowLearner
        
        learner = WorkflowLearner(storage_dir=str(tmp_path))
        
        template = learner.create_template(
            name="Login Workflow",
            steps=["open", "enter_username", "enter_password", "click_login"],
            application="TestApp"
        )
        
        assert template.name == "Login Workflow"
        assert len(template.steps) == 4
    
    def test_recognize_workflow(self, tmp_path):
        """Test workflow recognition."""
        from src.prediction.workflow_learner import WorkflowLearner
        
        learner = WorkflowLearner(storage_dir=str(tmp_path))
        
        # Create template
        learner.create_template(
            name="Test Workflow",
            steps=["step1", "step2", "step3"]
        )
        
        # Recognize partial match
        current_steps = [{"action_type": "step1"}, {"action_type": "step2"}]
        
        matches = learner.recognize_workflow(current_steps, threshold=0.5)
        
        assert isinstance(matches, list)

