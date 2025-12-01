"""
GraphQL Schema
"""

try:
    from strawberry import Schema, Query, Mutation, Field, type as strawberry_type
    from strawberry.fastapi import GraphQLRouter
    from typing import List, Optional
    from datetime import datetime
    import json
    from pathlib import Path
    
    STRAWBERRY_AVAILABLE = True
except ImportError:
    STRAWBERRY_AVAILABLE = False

from src.utils.logger import get_logger

logger = get_logger(__name__)


if STRAWBERRY_AVAILABLE:
    @strawberry_type
    class Session:
        id: str
        name: str
        app_name: Optional[str]
        status: str
        step_count: int
        created_at: str
    
    @strawberry_type
    class Document:
        id: str
        session_id: str
        format: str
        path: str
        size: int
    
    class Query:
        @Field
        def sessions(self) -> List[Session]:
            """Get all sessions"""
            sessions = []
            sessions_dir = Path("data/sessions")
            
            for session_file in sessions_dir.glob("*.json"):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        sessions.append(Session(
                            id=session_file.stem,
                            name=data.get('name', 'Unnamed Session'),
                            app_name=data.get('app_name'),
                            status=data.get('status', 'stopped'),
                            step_count=len(data.get('steps', [])),
                            created_at=data.get('created_at', datetime.now().isoformat()),
                        ))
                except Exception as e:
                    logger.error(f"Error reading session {session_file}: {e}")
            
            return sessions
        
        @Field
        def session(self, session_id: str) -> Optional[Session]:
            """Get session by ID"""
            session_file = Path("data/sessions") / f"{session_id}.json"
            if not session_file.exists():
                return None
            
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return Session(
                id=session_id,
                name=data.get('name', 'Unnamed Session'),
                app_name=data.get('app_name'),
                status=data.get('status', 'stopped'),
                step_count=len(data.get('steps', [])),
                created_at=data.get('created_at', datetime.now().isoformat()),
            )
    
    schema = Schema(query=Query)
    graphql_app = GraphQLRouter(schema)
else:
    # Fallback if strawberry not available
    class GraphQLSchema:
        def __init__(self):
            logger.warning("strawberry not available. Install with: pip install strawberry-graphql")
            self.graphql_app = None

