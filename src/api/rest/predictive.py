"""
Predictive Maintenance REST API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from src.predictive import PredictiveMaintenanceEngine
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PredictiveIssue(BaseModel):
    """Predictive issue"""
    type: str
    priority: float
    confidence: float = 0.0
    description: str = ""
    session_id: str


class PredictiveAnalysisResponse(BaseModel):
    """Predictive analysis response"""
    session_id: str
    issues: List[PredictiveIssue]
    total_issues: int


class PredictiveAPI:
    """Predictive Maintenance API"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        self.engine = PredictiveMaintenanceEngine()
    
    def _setup_routes(self):
        """Setup routes"""
        @self.router.get("/analyze/{session_id}", response_model=PredictiveAnalysisResponse)
        async def analyze_documentation(session_id: str):
            """Analyze documentation for outdated content"""
            try:
                issues = self.engine.analyze_documentation(session_id)
                
                # Send alerts for high-priority issues
                self.engine.send_alerts(issues)
                
                # Convert issues to PredictiveIssue models
                issue_models = []
                for issue in issues:
                    issue_models.append(PredictiveIssue(
                        type=issue.get('type', 'unknown'),
                        priority=issue.get('priority', 0.0),
                        confidence=issue.get('confidence', 0.0),
                        description=issue.get('description', ''),
                        session_id=session_id,
                    ))
                
                return PredictiveAnalysisResponse(
                    session_id=session_id,
                    issues=issue_models,
                    total_issues=len(issue_models),
                )
            except Exception as e:
                logger.error(f"Error analyzing documentation: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/issues")
        async def get_all_issues():
            """Get all detected issues"""
            # TODO: Implement issue storage and retrieval
            return {"issues": []}
