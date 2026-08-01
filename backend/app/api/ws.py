import uuid
import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# Temporary in-memory connection manager for the MVP
# In a real environment, this utilizes Redis PubSub for multiple workers
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[uuid.UUID, list[WebSocket]] = {}

    async def connect(self, run_id: uuid.UUID, websocket: WebSocket):
        await websocket.accept()
        if run_id not in self.active_connections:
            self.active_connections[run_id] = []
        self.active_connections[run_id].append(websocket)

    def disconnect(self, run_id: uuid.UUID, websocket: WebSocket):
        if run_id in self.active_connections:
            self.active_connections[run_id].remove(websocket)

    async def broadcast_to_run(self, run_id: uuid.UUID, event: str, data: dict):
        if run_id in self.active_connections:
            message = json.dumps({"event": event, "data": data})
            for connection in self.active_connections[run_id]:
                await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/{run_id}")
async def websocket_endpoint(websocket: WebSocket, run_id: uuid.UUID):
    await manager.connect(run_id, websocket)
    try:
        while True:
            # Client can send commands (e.g. approve shortcuts)
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            if payload.get("action") == "approve":
                # Handle shortcut
                pass
                
    except WebSocketDisconnect:
        manager.disconnect(run_id, websocket)
