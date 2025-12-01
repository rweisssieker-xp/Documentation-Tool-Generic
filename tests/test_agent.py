"""
Tests for Autonomous Agent Module
"""

import pytest
from unittest.mock import Mock, patch

from src.agent.tool_executor import ToolExecutor, ToolResult, ToolType
from src.agent.autonomous_agent import AutonomousAgent, AgentState
from src.agent.navigation_controller import NavigationController
from src.agent.question_engine import QuestionEngine


class TestToolExecutor:
    """Tests for ToolExecutor class."""
    
    def test_tool_executor_initialization(self):
        """Test ToolExecutor initialization."""
        executor = ToolExecutor()
        # May not be available without pyautogui
        assert executor is not None
    
    @patch('src.agent.tool_executor.PYAUTOGUI_AVAILABLE', True)
    @patch('src.agent.tool_executor.pyautogui')
    def test_execute_click_tool(self, mock_pyautogui):
        """Test executing click tool."""
        executor = ToolExecutor()
        executor.available = True
        
        result = executor.execute_tool("click", {"x": 100, "y": 200})
        
        assert isinstance(result, ToolResult)
        assert result.success == True
    
    def test_execute_unknown_tool(self):
        """Test executing unknown tool."""
        executor = ToolExecutor()
        
        result = executor.execute_tool("unknown", {})
        
        assert result.success == False
        assert "Unknown tool" in result.error


class TestAutonomousAgent:
    """Tests for AutonomousAgent class."""
    
    def test_autonomous_agent_initialization(self):
        """Test AutonomousAgent initialization."""
        agent = AutonomousAgent()
        assert agent.model == "gpt-4o"
        assert agent.tool_executor is not None
    
    def test_agent_state(self):
        """Test AgentState."""
        state = AgentState(
            current_step=0,
            completed_steps=[],
            goal="Test goal",
            observations=[]
        )
        
        assert state.goal == "Test goal"
        assert len(state.completed_steps) == 0


class TestNavigationController:
    """Tests for NavigationController class."""
    
    def test_navigation_controller_initialization(self):
        """Test NavigationController initialization."""
        controller = NavigationController()
        assert controller is not None
    
    def test_navigate_to_url(self):
        """Test navigating to URL."""
        controller = NavigationController()
        
        result = controller.navigate_to_url("https://example.com")
        # Should return True (mock implementation)
        assert result == True


class TestQuestionEngine:
    """Tests for QuestionEngine class."""
    
    def test_question_engine_initialization(self):
        """Test QuestionEngine initialization."""
        engine = QuestionEngine()
        assert engine.model == "gpt-4o"
    
    @patch('src.agent.question_engine.OPENAI_AVAILABLE', True)
    @patch('src.agent.question_engine.OpenAI')
    def test_generate_question(self, mock_openai_class):
        """Test generating question."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "What is the purpose?"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        engine = QuestionEngine()
        engine.client = mock_client
        
        question = engine.generate_question("Context", "Uncertainty")
        
        assert question == "What is the purpose?"

