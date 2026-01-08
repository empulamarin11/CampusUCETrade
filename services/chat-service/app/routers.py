from datetime import datetime
from typing import Dict, Set

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

router = APIRouter()

# In-memory rooms (MVP). Later: Redis pub/sub or Kafka + persistence.
_ROOMS: Dict[str, Set[WebSocket]] = {}

class RoomInfo(BaseModel):
    room: str
    connections: int

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/rooms", response_model=list[RoomInfo])
def list_rooms():
    return [{"room": r, "connections": len(conns)} for r, conns in _ROOMS.items()]

async def _broadcast(room: str, payload: dict):
    conns = list(_ROOMS.get(room, set()))
    dead: list[WebSocket] = []
    for ws in conns:
        try:
            await ws.send_json(payload)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _ROOMS.get(room, set()).discard(ws)

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    room: str = Query(default="general"),
    user: str = Query(default="anonymous"),
):
    await websocket.accept()

    if room not in _ROOMS:
        _ROOMS[room] = set()

    _ROOMS[room].add(websocket)

    await _broadcast(room, {
        "type": "system",
        "room": room,
        "message": f"{user} joined",
        "ts": datetime.utcnow().isoformat() + "Z",
    })

    try:
        while True:
            text = await websocket.receive_text()
            await _broadcast(room, {
                "type": "message",
                "room": room,
                "user": user,
                "message": text,
                "ts": datetime.utcnow().isoformat() + "Z",
            })
    except WebSocketDisconnect:
        _ROOMS.get(room, set()).discard(websocket)
        await _broadcast(room, {
            "type": "system",
            "room": room,
            "message": f"{user} left",
            "ts": datetime.utcnow().isoformat() + "Z",
        })
