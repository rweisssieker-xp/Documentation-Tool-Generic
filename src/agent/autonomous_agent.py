"""Autonomous Agent - Main agent with ReAct loop"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from src.agent.tool_executor import ToolExecutor, ToolResult
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AgentState:
    """Agent state."""
    current_step: int
    completed_steps: List[Dict[str, Any]]
    goal: str
    observations: List[str]


class AutonomousAgent:
    """
    Autonomous documentation agent using ReAct pattern.
    Plans and executes documentation tasks autonomously.
    """
    
    def __init__(self, model: str = "gpt-4o"):
        """
        Initialize autonomous agent.
        
        Args:
            model: OpenAI model to use
        """
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
            else:
                self.client = None
        else:
            self.client = None
        
        self.model = model
        self.tool_executor = ToolExecutor()
        self.state = None
    
    def execute_task(self, goal: str, max_steps: int = 20) -> List[Dict[str, Any]]:
        """
        Execute documentation task autonomously.
        
        Args:
            goal: Task goal description
            max_steps: Maximum steps to execute
            
        Returns:
            List of executed steps
        """
        if not self.client:
            logger.warning("OpenAI not available, autonomous agent disabled")
            return []
        
        self.state = AgentState(
            current_step=0,
            completed_steps=[],
            goal=goal,
            observations=[]
        )
        
        for step in range(max_steps):
            # ReAct loop: Reason -> Act -> Observe
            action = self._reason()
            if action.get('type') == 'complete':
                break
            
            result = self._act(action)
            self._observe(result)
        
        return self.state.completed_steps
    
    def _reason(self) -> Dict[str, Any]:
        """Reasoning step - decide next action."""
        prompt = f"""You are an autonomous documentation agent. Your goal: {self.state.goal}

Completed steps: {len(self.state.completed_steps)}
Observations: {self.state.observations[-3:] if self.state.observations else []}

Decide next action. Available tools: click, type, navigate, screenshot, verify.
Return JSON with: {{"type": "tool_name", "parameters": {{...}}}}
Or {{"type": "complete"}} if goal is achieved."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            import json
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Reasoning error: {e}")
            return {"type": "complete"}
    
    def _act(self, action: Dict[str, Any]) -> ToolResult:
        """Act - execute tool."""
        tool_name = action.get('type')
        params = action.get('parameters', {})
        
        result = self.tool_executor.execute_tool(tool_name, params)
        
        step = {
            'action': tool_name,
            'parameters': params,
            'result': result.result,
            'success': result.success
        }
        self.state.completed_steps.append(step)
        
        return result
    
    def _observe(self, result: ToolResult):
        """Observe - record result."""
        obs = f"Action result: {result.result}" if result.success else f"Error: {result.error}"
        self.state.observations.append(obs)

