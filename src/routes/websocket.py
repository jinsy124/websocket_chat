from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.utility import verify_token
from src.database import SessionLocal
from sqlalchemy import select
from src.models import Message, Conversation

router = APIRouter()
connections = {}


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008, reason="Token required")
        return

    try:
        payload = verify_token(token)
        user_id = int(payload.get("sub"))
        # Using a global conversation for now to match frontend behavior
        conversation_id = 1
    except Exception:
        await websocket.close(code=1008, reason="Invalid token")
        return

    await websocket.accept()
    if user_id not in connections:
        connections[user_id] = set()
    connections[user_id].add(websocket)
    print(f"User {user_id} connected")

    try:
        while True:
            data = await websocket.receive_json()
            conversation_id = data.get("conversation_id")
            text = data.get("text")

            if not conversation_id or not text:
                continue

            async with SessionLocal() as session:
                # Find the receiver from conversation
                result = await session.execute(select(Conversation).where(Conversation.id == conversation_id))
                conversation = result.scalar_one_or_none()

                if not conversation:
                    continue

                receiver_id = conversation.user2 if conversation.user1 == user_id else conversation.user1

                # Store message in database
                msg = Message(
                    conversation_id=conversation_id,
                    sender_id=user_id,
                    text=text
                )
                session.add(msg)

                # Update conversation last message
                conversation.last_message = text[:50] + \
                    "..." if len(text) > 50 else text

                await session.commit()
                await session.refresh(msg)

                # Payload to send
                # Fetch sender user to get name for notification
                from src.models import User
                sender_result = await session.execute(select(User).where(User.id == user_id))
                sender = sender_result.scalar_one_or_none()

                message_payload = {
                    "id": msg.id,
                    "conversation_id": conversation_id,
                    "sender_id": user_id,
                    "sender_name": sender.name if sender else "someone",
                    "text": text,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None
                }

            # If receiver is online -> Send message instantly via WebSocket to all their open tabs
            if receiver_id in connections:
                # Copy the set to gracefully handle disconnections mid-loop
                for conn in list(connections[receiver_id]):
                    try:
                        await conn.send_json(message_payload)
                    except Exception:
                        pass

            # Send message back to sender so they can render it locally across all their tabs
            if user_id in connections:
                for conn in list(connections[user_id]):
                    try:
                        await conn.send_json(message_payload)
                    except Exception:
                        pass
    except WebSocketDisconnect:
        if user_id in connections:
            if websocket in connections[user_id]:
                connections[user_id].remove(websocket)
            if not connections[user_id]:
                del connections[user_id]
        print(f"User {user_id} disconnected")
