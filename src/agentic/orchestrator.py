"""Agent Orchestrator - Koordiniert Multi-Agent System"""

import logging
from typing import List, Dict, Optional
from .agents.documentation_agent import DocumentationAgent
from .agents.update_agent import UpdateAgent
from .agents.quality_agent import QualityAgent

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Koordiniert mehrere Agents"""
    
    def __init__(self):
        self.agents = {
            'documentation': DocumentationAgent(),
            'update': UpdateAgent(),
            'quality': QualityAgent()
        }
        self.active_tasks: Dict[str, Dict] = {}
    
    def execute_task(self, task_type: str, task_data: Dict) -> bool:
        """Führt Task mit passendem Agent aus"""
        try:
            if task_type in self.agents:
                agent = self.agents[task_type]
                result = agent.execute(task_data)
                self.active_tasks[task_type] = {
                    'data': task_data,
                    'result': result,
                    'status': 'completed'
                }
                return True
            return False
        except Exception as e:
            logger.error(f"Error executing task: {e}")
            return False
    
    def coordinate_multi_agent(self, tasks: List[Dict]) -> Dict:
        """Koordiniert mehrere Agents für komplexe Tasks"""
        results = {}
        for task in tasks:
            task_type = task.get('type')
            if task_type:
                results[task_type] = self.execute_task(task_type, task)
        return results
