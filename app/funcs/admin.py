from fastapi import HTTPException, Request
from database.database import ADMIN_USERNAME, ADMIN_EMAIL

async def require_fixed_admin(request: Request):
    """
    Проверяет что текущий пользователь - фиксированный админ
    """
    username = request.session.get("user")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if username != ADMIN_USERNAME:
        from database.database import info_user
        user = info_user(username)
        if not user or user.get("email") != ADMIN_EMAIL:
            raise HTTPException(status_code=403, detail="Admin access required")
    
    return username


async def require_admin_simple(request: Request):
    username = request.session.get("user")
    if not username or username != "Ba1kerr":
        raise HTTPException(status_code=403, detail="Access denied")
    return username