from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.utility import verify_token
from src.database import SessionLocal
from src.models import Message

router = APIRouter()
connections = {}

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008, reason="Token required")
        return
    try:
        username = verify_token(token)
    except:
        await websocket.close(code=1008, reason="Invalid token")
        return

    await websocket.accept()
    connections[username] = websocket
    print(f"{username} connected")

    try:
        while True:
            message = await websocket.receive_text()
            async with SessionLocal() as session:
                msg = Message(username=username, text=message)
                session.add(msg)
                await session.commit()
            for user, conn in connections.items():
                try:
                    await conn.send_text(f"{username}: {message}")
                except:
                    pass
    except WebSocketDisconnect:
        if username in connections:
            del connections[username]
        print(f"{username} disconnected")