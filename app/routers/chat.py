from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Request, Depends
from database.database import get_messages, save_message, check_match_exists, get_user_chats
from funcs.jwt_auth import get_current_user, get_user_from_websocket

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ConnectionManager:
    def __init__(self):
        self.rooms: dict[str, list[WebSocket]] = {}

    def _room_key(self, user1: str, user2: str) -> str:
        return ":".join(sorted([user1, user2]))

    async def connect(self, websocket: WebSocket, current_user: str, companion: str):
        await websocket.accept()
        key = self._room_key(current_user, companion)
        if key not in self.rooms:
            self.rooms[key] = []
        self.rooms[key].append(websocket)

    def disconnect(self, websocket: WebSocket, current_user: str, companion: str):
        key = self._room_key(current_user, companion)
        if key in self.rooms:
            self.rooms[key].remove(websocket)
            if not self.rooms[key]:
                del self.rooms[key]

    async def broadcast(self, message: dict, current_user: str, companion: str):
        key = self._room_key(current_user, companion)
        for ws in self.rooms.get(key, []):
            await ws.send_json(message)


manager = ConnectionManager()


@router.get("/list")
async def chat_list(username: str = Depends(get_current_user)):
    return {"chats": get_user_chats(username)}


@router.get("/{companion}/history")
async def chat_history(
    companion: str,
    limit: int = 50,
    offset: int = 0,
    username: str = Depends(get_current_user),
):
    if not check_match_exists(username, companion):
        raise HTTPException(status_code=403, detail="No match with this user")
    return {"messages": get_messages(username, companion, limit=limit, offset=offset)}


@router.websocket("/ws/{companion}")
async def websocket_chat(websocket: WebSocket, companion: str):
    token = websocket.query_params.get("token")
    if token:
        try:
            username = get_user_from_websocket(websocket)
        except HTTPException:
            await websocket.close(code=4001, reason="Invalid token")
            return
    else:
        username = websocket.query_params.get("username")
        if not username:
            await websocket.close(code=4001, reason="token or username required")
            return

    if not check_match_exists(username, companion):
        await websocket.close(code=4003, reason="No match with this user")
        return

    await manager.connect(websocket, username, companion)

    try:
        while True:
            data = await websocket.receive_json()
            text = data.get("text", "").strip()
            if not text:
                continue
            if len(text) > 1000:
                await websocket.send_json({"error": "Message too long (max 1000 chars)"})
                continue
            message_id = save_message(sender=username, receiver=companion, text=text)
            await manager.broadcast(
                {"id": message_id, "sender": username, "receiver": companion,
                 "text": text, "type": "message"},
                username, companion,
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket, username, companion)
        await manager.broadcast(
            {"type": "status", "text": f"{username} отключился"},
            username, companion,
        )
    except Exception:
        manager.disconnect(websocket, username, companion)