# routers/chat.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database.database import (
    get_messages, save_message, check_match_exists, get_user_chats
)

router = APIRouter(prefix="/chat", tags=["chat"])
templates = Jinja2Templates(directory="templates")


# ─── Connection Manager ───────────────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        # { "user1:user2": [ws1, ws2] }
        self.rooms: dict[str, list[WebSocket]] = {}

    def _room_key(self, user1: str, user2: str) -> str:
        # сортируем чтобы "ivan:anna" == "anna:ivan"
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


# ─── REST ─────────────────────────────────────────────────────────────────────

@router.get("", response_class=HTMLResponse)
async def chat_list(request: Request):
    """Список всех чатов пользователя"""
    username = request.session.get("user")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")

    chats = get_user_chats(username)
    return templates.TemplateResponse("chat_list.html", {
        "request": request,
        "user": username,
        "chats": chats,
    })


@router.get("/{companion}", response_class=HTMLResponse)
async def chat_room(request: Request, companion: str):
    """Страница чата с конкретным пользователем"""
    username = request.session.get("user")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Проверяем что между ними есть мэтч
    if not check_match_exists(username, companion):
        raise HTTPException(status_code=403, detail="No match with this user")

    messages = get_messages(username, companion, limit=50)
    return templates.TemplateResponse("chat_room.html", {
        "request": request,
        "user": username,
        "companion": companion,
        "messages": messages,
    })


@router.get("/{companion}/history")
async def chat_history(request: Request, companion: str, limit: int = 50, offset: int = 0):
    """История сообщений — для подгрузки старых (infinite scroll)"""
    username = request.session.get("user")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if not check_match_exists(username, companion):
        raise HTTPException(status_code=403, detail="No match with this user")

    messages = get_messages(username, companion, limit=limit, offset=offset)
    return {"messages": messages}


# ─── WebSocket ────────────────────────────────────────────────────────────────

@router.websocket("/ws/{companion}")
async def websocket_chat(websocket: WebSocket, companion: str):
    """
    WebSocket чат. Клиент должен передать username в query param:
    ws://localhost:8000/chat/ws/anna?username=ivan
    """
    username = websocket.query_params.get("username")

    if not username:
        await websocket.close(code=4001, reason="username required")
        return

    # Проверяем мэтч
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

            # Сохраняем в БД
            message_id = save_message(
                sender=username,
                receiver=companion,
                text=text,
            )

            # Рассылаем обоим участникам
            await manager.broadcast(
                {
                    "id":       message_id,
                    "sender":   username,
                    "receiver": companion,
                    "text":     text,
                    "type":     "message",
                },
                username,
                companion,
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket, username, companion)
        await manager.broadcast(
            {"type": "status", "text": f"{username} отключился"},
            username,
            companion,
        )
    except Exception as e:
        manager.disconnect(websocket, username, companion)