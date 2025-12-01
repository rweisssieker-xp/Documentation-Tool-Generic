"""
WebSocket Real-Time Handler
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio

from src.utils.logger import get_logger

logger = get_logger(__name__)


class WebSocketHandler:
    """WebSocket handler for real-time updates"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.user_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str = None):
        """Accept WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        
        if user_id:
            self.user_connections[user_id] = websocket
        
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    async def disconnect(self, websocket: WebSocket, user_id: str = None):
        """Handle WebSocket disconnect"""
        self.active_connections.discard(websocket)
        
        if user_id and user_id in self.user_connections:
            del self.user_connections[user_id]
        
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.add(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.active_connections.discard(connection)
    
    async def handle(self, websocket: WebSocket, user_id: str = None):
        """Handle WebSocket connection"""
        await self.connect(websocket, user_id)
        
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                msg_type = message.get('type')
                
                if msg_type == 'ping':
                    await self.send_personal_message({'type': 'pong'}, websocket)
                elif msg_type == 'subscribe':
                    # Handle subscription to specific channels
                    channel = message.get('channel')
                    logger.info(f"Client subscribed to channel: {channel}")
                elif msg_type == 'message':
                    # Broadcast message to all clients
                    await self.broadcast(message)
                else:
                    logger.warning(f"Unknown message type: {msg_type}")
        
        except WebSocketDisconnect:
            await self.disconnect(websocket, user_id)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            await self.disconnect(websocket, user_id)

