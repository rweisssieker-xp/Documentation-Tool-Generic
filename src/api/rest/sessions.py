"""
Session Management REST API
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import json

from src.utils.logger import get_logger

logger = get_logger(__name__)


class SessionCreate(BaseModel):
    """Session creation request"""
    name: str
    app_name: Optional[str] = None
    description: Optional[str] = None


class SessionUpdate(BaseModel):
    """Session update request"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class SessionResponse(BaseModel):
    """Session response"""
    id: str
    name: str
    app_name: Optional[str]
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    step_count: int


class SessionAPI:
    """Session Management API"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        self.sessions_dir = Path("data/sessions")
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
    
    def _setup_routes(self):
        """Setup routes"""
        @self.router.get("/", response_model=List[SessionResponse])
        async def list_sessions():
            """List all sessions"""
            sessions = []
            for session_file in self.sessions_dir.glob("*.json"):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        sessions.append(SessionResponse(
                            id=session_file.stem,
                            name=data.get('name', 'Unnamed Session'),
                            app_name=data.get('app_name'),
                            description=data.get('description'),
                            status=data.get('status', 'stopped'),
                            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
                            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat())),
                            step_count=len(data.get('steps', [])),
                        ))
                except Exception as e:
                    logger.error(f"Error reading session {session_file}: {e}")
            return sessions
        
        @self.router.post("/", response_model=SessionResponse)
        async def create_session(session: SessionCreate):
            """Create new session"""
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            session_data = {
                'id': session_id,
                'name': session.name,
                'app_name': session.app_name,
                'description': session.description,
                'status': 'stopped',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'steps': [],
            }
            
            session_file = self.sessions_dir / f"{session_id}.json"
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            return SessionResponse(
                id=session_id,
                name=session.name,
                app_name=session.app_name,
                description=session.description,
                status='stopped',
                created_at=datetime.now(),
                updated_at=datetime.now(),
                step_count=0,
            )
        
        @self.router.get("/{session_id}", response_model=SessionResponse)
        async def get_session(session_id: str):
            """Get session by ID"""
            session_file = self.sessions_dir / f"{session_id}.json"
            if not session_file.exists():
                raise HTTPException(status_code=404, detail="Session not found")
            
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return SessionResponse(
                id=session_id,
                name=data.get('name', 'Unnamed Session'),
                app_name=data.get('app_name'),
                description=data.get('description'),
                status=data.get('status', 'stopped'),
                created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
                updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat())),
                step_count=len(data.get('steps', [])),
            )
        
        @self.router.put("/{session_id}", response_model=SessionResponse)
        async def update_session(session_id: str, update: SessionUpdate):
            """Update session"""
            session_file = self.sessions_dir / f"{session_id}.json"
            if not session_file.exists():
                raise HTTPException(status_code=404, detail="Session not found")
            
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if update.name:
                data['name'] = update.name
            if update.description:
                data['description'] = update.description
            if update.status:
                data['status'] = update.status
            
            data['updated_at'] = datetime.now().isoformat()
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return SessionResponse(
                id=session_id,
                name=data.get('name', 'Unnamed Session'),
                app_name=data.get('app_name'),
                description=data.get('description'),
                status=data.get('status', 'stopped'),
                created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
                updated_at=datetime.now(),
                step_count=len(data.get('steps', [])),
            )
        
        @self.router.delete("/{session_id}")
        async def delete_session(session_id: str):
            """Delete session"""
            session_file = self.sessions_dir / f"{session_id}.json"
            if not session_file.exists():
                raise HTTPException(status_code=404, detail="Session not found")
            
            session_file.unlink()
            return {"message": "Session deleted"}

