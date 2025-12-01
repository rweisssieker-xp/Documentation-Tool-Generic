"""
Collaboration REST API
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from src.collaboration import RealtimeServer, CRDTEngine, PresenceManager, CommentSystem
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CommentCreateRequest(BaseModel):
    """Comment creation request"""
    content: str
    position: tuple
    author: str


class CollaborationAPI:
    """Collaboration API"""
    
    def __init__(self):
        self.router = APIRouter()
        self.crdt_engine = CRDTEngine()
        self.presence_manager = PresenceManager()
        self.comment_system = CommentSystem()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes"""
        @self.router.get("/presence")
        async def get_presence():
            """Get active users"""
            try:
                users = self.presence_manager.get_active_users()
                return {"users": users}
            except Exception as e:
                logger.error(f"Error getting presence: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/comments")
        async def create_comment(request: CommentCreateRequest):
            """Create comment"""
            try:
                from datetime import datetime
                from src.collaboration.comment_system import Comment, CommentStatus
                
                comment = Comment(
                    id=f"comment_{datetime.now().timestamp()}",
                    author=request.author,
                    content=request.content,
                    position=request.position,
                    status=CommentStatus.OPEN,
                    created_at=datetime.now(),
                )
                
                comment_id = self.comment_system.add_comment(comment)
                return {"id": comment_id, "comment": comment}
            except Exception as e:
                logger.error(f"Error creating comment: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/comments")
        async def list_comments():
            """List all comments"""
            try:
                comments = self.comment_system.get_comments()
                return {"comments": comments}
            except Exception as e:
                logger.error(f"Error listing comments: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/crdt/state")
        async def get_crdt_state():
            """Get CRDT state"""
            try:
                state = self.crdt_engine.get_state()
                return {"state": state}
            except Exception as e:
                logger.error(f"Error getting CRDT state: {e}")
                raise HTTPException(status_code=500, detail=str(e))

