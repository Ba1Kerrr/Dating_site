from fastapi import APIRouter, Request, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from funcs.jwt_auth import get_current_user_flexible as get_current_user  # ИЗМЕНЕНО
from database.database import get_user_chats, get_messages, check_match_exists

router = APIRouter()

@router.get("/api/chat/list")
async def chat_list(
    request: Request,
    current_user: str = Depends(get_current_user)  # Теперь работает и с сессией, и с JWT
):
    """Список чатов пользователя"""
    chats = get_user_chats(current_user)
    return JSONResponse(content={"chats": chats})

@router.get("/api/chat/{companion}/history")
async def chat_history(
    companion: str,
    request: Request,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: str = Depends(get_current_user)
):
    if not check_match_exists(current_user, companion):
        raise HTTPException(status_code=403, detail="No match found")
    
    messages = get_messages(current_user, companion, limit, offset)
    return JSONResponse(content={"messages": messages})
