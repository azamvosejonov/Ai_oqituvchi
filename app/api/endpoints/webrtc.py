import json
import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.db.session import SessionLocal

router = APIRouter()
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.rooms: Dict[str, List[str]] = {}
        self.user_room_map: Dict[str, str] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            
            # Remove from room if in any
            room_id = self.user_room_map.get(user_id)
            if room_id and room_id in self.rooms:
                if user_id in self.rooms[room_id]:
                    self.rooms[room_id].remove(user_id)
                    
                    # Notify other users in the room
                    self._notify_room_members(room_id, {
                        "type": "user-left",
                        "userId": user_id
                    })
                    
                    # Clean up empty rooms
                    if not self.rooms[room_id]:
                        del self.rooms[room_id]
                
                # Remove from user-room mapping
                del self.user_room_map[user_id]
        
        logger.info(f"User {user_id} disconnected")

    async def join_room(self, user_id: str, room_id: str):
        # Leave current room if any
        await self.leave_room(user_id)
        
        # Join new room
        if room_id not in self.rooms:
            self.rooms[room_id] = []
            
        if user_id not in self.rooms[room_id]:
            self.rooms[room_id].append(user_id)
            self.user_room_map[user_id] = room_id
            
            # Notify other users in the room
            await self._notify_room_members(room_id, {
                "type": "user-joined",
                "userId": user_id,
                "usersInRoom": [u for u in self.rooms[room_id] if u != user_id]
            }, exclude_user_id=user_id)
            
            logger.info(f"User {user_id} joined room {room_id}")
            
            # Send list of existing users to the new user
            if user_id in self.active_connections:
                await self.active_connections[user_id].send_json({
                    "type": "room-joined",
                    "roomId": room_id,
                    "usersInRoom": [u for u in self.rooms[room_id] if u != user_id]
                })

    async def leave_room(self, user_id: str):
        if user_id in self.user_room_map:
            room_id = self.user_room_map[user_id]
            if room_id in self.rooms and user_id in self.rooms[room_id]:
                self.rooms[room_id].remove(user_id)
                
                # Notify other users in the room
                await self._notify_room_members(room_id, {
                    "type": "user-left",
                    "userId": user_id
                }, exclude_user_id=user_id)
                
                # Clean up empty rooms
                if not self.rooms[room_id]:
                    del self.rooms[room_id]
            
            # Remove from user-room mapping
            del self.user_room_map[user_id]
            logger.info(f"User {user_id} left room {room_id}")

    async def _notify_room_members(self, room_id: str, message: dict, exclude_user_id: str = None):
        if room_id in self.rooms:
            for user_id in self.rooms[room_id]:
                if user_id != exclude_user_id and user_id in self.active_connections:
                    try:
                        await self.active_connections[user_id].send_json(message)
                    except Exception as e:
                        logger.error(f"Error sending message to {user_id}: {e}")

    async def send_message(self, sender_id: str, target_id: str, message: dict):
        if target_id in self.active_connections:
            try:
                # Add sender info to the message
                message["senderId"] = sender_id
                await self.active_connections[target_id].send_json(message)
                return True
            except Exception as e:
                logger.error(f"Error sending message from {sender_id} to {target_id}: {e}")
        return False

# Global connection manager
manager = ConnectionManager()

@router.websocket("/ws/webrtc/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, token: str = None):
    """
    WebSocket endpoint for WebRTC signaling.
    
    Query Parameters:
    - token: JWT token for authentication (required for non-demo users)
    """
    # In a production environment, you would validate the token here
    # For demo purposes, we'll just accept any connection
    
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await handle_webrtc_message(user_id, message)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received from {user_id}")
            except Exception as e:
                logger.error(f"Error processing message from {user_id}: {e}")
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id)

async def handle_webrtc_message(sender_id: str, message: dict):
    """Handle incoming WebRTC signaling messages"""
    msg_type = message.get("type")
    
    if msg_type == "join-room":
        room_id = message.get("roomId")
        if room_id:
            await manager.join_room(sender_id, room_id)
    
    elif msg_type == "leave-room":
        await manager.leave_room(sender_id)
    
    elif msg_type in ["offer", "answer", "ice-candidate"]:
        target_id = message.get("targetId")
        if target_id:
            await manager.send_message(sender_id, target_id, message)
    
    elif msg_type == "end-call":
        target_id = message.get("targetId")
        if target_id:
            await manager.send_message(sender_id, target_id, {
                "type": "call-ended",
                "userId": sender_id
            })
    
    else:
        logger.warning(f"Unknown message type: {msg_type}")

# API Endpoints for Room Management
@router.post("/rooms/create", response_model=dict)
async def create_room(
    room_data: dict,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)
):
    """
    Create a new video call room.
    
    - **name**: Room name (optional)
    - **is_private**: Whether the room requires authentication (default: True)
    - **max_participants**: Maximum number of participants (default: 10)
    """
    # In a real app, you would save the room to the database
    room_id = f"room_{len(manager.rooms) + 1}"
    return {
        "roomId": room_id,
        "name": room_data.get("name", f"Room {len(manager.rooms) + 1}"),
        "isPrivate": room_data.get("is_private", True),
        "maxParticipants": room_data.get("max_participants", 10),
        "createdBy": current_user.id
    }

@router.get("/rooms/{room_id}/users", response_model=List[dict])
async def get_room_users(
    room_id: str,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Get list of users in a room"""
    if room_id in manager.rooms:
        return [{"userId": user_id} for user_id in manager.rooms[room_id]]
    return []

@router.post("/rooms/{room_id}/end")
async def end_room(
    room_id: str,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """End a room and disconnect all users"""
    if room_id in manager.rooms:
        # Notify all users in the room
        for user_id in manager.rooms[room_id]:
            if user_id in manager.active_connections:
                try:
                    await manager.active_connections[user_id].send_json({
                        "type": "room-ended",
                        "roomId": room_id,
                        "endedBy": current_user.id
                    })
                except Exception as e:
                    logger.error(f"Error notifying user {user_id}: {e}")
        
        # Clean up
        for user_id in manager.rooms[room_id]:
            if user_id in manager.user_room_map:
                del manager.user_room_map[user_id]
        
        del manager.rooms[room_id]
        return {"status": "success", "message": f"Room {room_id} ended"}
    
    raise HTTPException(status_code=404, detail="Room not found")
