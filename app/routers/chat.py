# routers/chat.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database.database import get_messages, save_message, check_match_exists, get_user_chats
from funcs.jwt_auth import get_current_user, get_user_from_websocket

router = APIRouter(prefix="/chat", tags=["chat"])
templates = Jinja2Templates(directory="templates")


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


# ─── REST (сессия — для браузера) ─────────────────────────────────────────────

@router.get("", response_class=HTMLResponse)
async def chat_list(request: Request):
    username = request.session.get("user")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    chats = get_user_chats(username)
    return templates.TemplateResponse("chat_list.html", {
        "request": request, "user": username, "chats": chats,
    })


# ─── REST (Bearer — для API клиентов) ────────────────────────────────────────

@router.get("/api/list")
async def api_chat_list(username: str = Depends(get_current_user)):
    """Список чатов через Bearer токен"""
    return {"chats": get_user_chats(username)}


@router.get("/api/{companion}/history")
async def api_chat_history(
    companion: str,
    limit: int = 50,
    offset: int = 0,
    username: str = Depends(get_current_user),
):
    """История сообщений через Bearer токен"""
    if not check_match_exists(username, companion):
        raise HTTPException(status_code=403, detail="No match with this user")
    messages = get_messages(username, companion, limit=limit, offset=offset)
    return {"messages": messages}


# ─── REST (сессия — для браузера) ─────────────────────────────────────────────

@router.get("", response_class=HTMLResponse)
async def chat_list(request: Request):
    username = request.session.get("user")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    chats = get_user_chats(username)
    return templates.TemplateResponse("chat_list.html", {
        "request": request, "user": username, "chats": chats,
    })


@router.get("/{companion}", response_class=HTMLResponse)
async def chat_room(request: Request, companion: str):
    username = request.session.get("user")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not check_match_exists(username, companion):
        raise HTTPException(status_code=403, detail="No match with this user")
    messages = get_messages(username, companion, limit=50)
    return templates.TemplateResponse("chat_room.html", {
        "request": request, "user": username,
        "companion": companion, "messages": messages,
    })


# ─── WebSocket ────────────────────────────────────────────────────────────────

@router.websocket("/ws/{companion}")
async def websocket_chat(websocket: WebSocket, companion: str):
    """
    Поддерживает два способа авторизации:
    1. Bearer JWT:  ws://host/chat/ws/anna?token=eyJ...
    2. Session:     ws://host/chat/ws/anna?username=ivan  (браузер)
    """
    # Пробуем JWT сначала
    token = websocket.query_params.get("token")
    if token:
        try:
            username = get_user_from_websocket(websocket)
        except HTTPException:
            await websocket.close(code=4001, reason="Invalid token")
            return
    else:
        # Fallback на session username (браузер)
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