from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import List, Dict
import json
from datetime import datetime
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.db.session import SessionLocal

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.chat_rooms: Dict[int, List[int]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        # Remove user from all chat rooms
        for room_id, users in self.chat_rooms.items():
            if user_id in users:
                users.remove(user_id)

    async def join_chat_room(self, user_id: int, room_id: int):
        if room_id not in self.chat_rooms:
            self.chat_rooms[room_id] = []
        if user_id not in self.chat_rooms[room_id]:
            self.chat_rooms[room_id].append(user_id)

    def leave_chat_room(self, user_id: int, room_id: int):
        if room_id in self.chat_rooms and user_id in self.chat_rooms[room_id]:
            self.chat_rooms[room_id].remove(user_id)

    async def broadcast_to_room(self, message: str, room_id: int, sender_id: int = None):
        if room_id in self.chat_rooms:
            for user_id in self.chat_rooms[room_id]:
                if user_id != sender_id and user_id in self.active_connections:
                    await self.active_connections[user_id].send_text(message)

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int, token: str):
    db = SessionLocal()
    try:
        # Authenticate user
        user = crud.user.authenticate_user(db, token=token)
        if not user:
            await websocket.close(code=4001)
            return
            
        await manager.connect(websocket, user.id)
        await manager.join_chat_room(user.id, room_id)
        
        try:
            while True:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Save message to database
                db_message = models.ForumPost(
                    content=message_data["content"],
                    topic_id=room_id,
                    creator_id=user.id
                )
                db.add(db_message)
                db.commit()
                db.refresh(db_message)
                
                # Prepare message to broadcast
                message = {
                    "type": "message",
                    "content": message_data["content"],
                    "sender_id": user.id,
                    "sender_name": user.full_name or user.username,
                    "timestamp": datetime.utcnow().isoformat(),
                    "message_id": db_message.id
                }
                
                # Broadcast to room
                await manager.broadcast_to_room(
                    json.dumps(message),
                    room_id=room_id,
                    sender_id=user.id
                )
                
        except WebSocketDisconnect:
            manager.disconnect(user.id)
            manager.leave_chat_room(user.id, room_id)
            
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        await websocket.close()
    finally:
        db.close()

# Add WebSocket endpoint to get online users in a room
@router.websocket("/ws/online/{room_id}")
async def online_users_websocket(websocket: WebSocket, room_id: int, token: str):
    db = SessionLocal()
    try:
        # Authenticate user
        user = crud.user.authenticate_user(db, token=token)
        if not user:
            await websocket.close(code=4001)
            return
            
        await websocket.accept()
        
        # Send initial list of online users
        online_users = await get_online_users(room_id, db)
        await websocket.send_json({
            "type": "online_users",
            "users": online_users
        })
        
        # Keep connection open
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"Online users WebSocket error: {str(e)}")
        await websocket.close()
    finally:
        db.close()

async def get_online_users(room_id: int, db: Session):
    if room_id in manager.chat_rooms:
        user_ids = manager.chat_rooms[room_id]
        users = db.query(models.User).filter(models.User.id.in_(user_ids)).all()
        return [{"id": user.id, "username": user.username, "full_name": user.full_name} for user in users]
    return []
