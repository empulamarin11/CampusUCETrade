from datetime import datetime, timezone
from typing import Dict, Set, List
from uuid import uuid4

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.db import get_db, SessionLocal
from app.models import ChatMessage

router = APIRouter(tags=["chat"])

# In-memory rooms (connections only). Messages are persisted in Postgres.
_ROOMS: Dict[str, Set[WebSocket]] = {}


class RoomInfo(BaseModel):
    room: str
    connections: int


class MessageOut(BaseModel):
    id: str
    room: str
    user: str
    message: str
    created_at: str


class MessagesResponse(BaseModel):
    room: str
    items: List[MessageOut]


@router.get("/health")
def health():
    return {"status": "ok", "service": "chat-service"}


@router.get("/rooms", response_model=list[RoomInfo])
def list_rooms():
    return [{"room": r, "connections": len(conns)} for r, conns in _ROOMS.items()]


@router.get("/messages", response_model=MessagesResponse)
def list_messages(
    room: str = Query(default="general"),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.room == room)
        .order_by(desc(ChatMessage.created_at))
        .limit(limit)
    )
    rows = db.execute(stmt).scalars().all()

    # Return ascending order (oldest -> newest)
    rows = list(reversed(rows))

    return MessagesResponse(
        room=room,
        items=[
            MessageOut(
                id=r.id,
                room=r.room,
                user=r.user,
                message=r.message,
                created_at=r.created_at.isoformat().replace("+00:00", "Z"),
            )
            for r in rows
        ],
    )


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

    await _broadcast(
        room,
        {
            "type": "system",
            "room": room,
            "message": f"{user} joined",
            "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        },
    )

    try:
        while True:
            text = await websocket.receive_text()

            # Persist message in Postgres
            msg_id = str(uuid4())
            now = datetime.now(timezone.utc)

            # We open a short DB session inside the WS loop
            # to avoid keeping a Session tied to the socket lifetime.
            db = SessionLocal()
            try:
                row = ChatMessage(
                    id=msg_id,
                    room=room,
                    user=user,
                    message=text,
                    created_at=now,
                )
                db.add(row)
                db.commit()
            finally:
                db.close()

            await _broadcast(
                room,
                {
                    "type": "message",
                    "id": msg_id,
                    "room": room,
                    "user": user,
                    "message": text,
                    "ts": now.isoformat().replace("+00:00", "Z"),
                },
            )

    except WebSocketDisconnect:
        _ROOMS.get(room, set()).discard(websocket)
        await _broadcast(
            room,
            {
                "type": "system",
                "room": room,
                "message": f"{user} left",
                "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            },
        )
