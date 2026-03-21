"""
app/routers/blocks.py

Эндпоинты блокировок и жалоб:

  POST   /api/users/{username}/block          — заблокировать
  DELETE /api/users/{username}/block          — разблокировать
  GET    /api/users/blocks                    — мой чёрный список
  POST   /api/users/{username}/report         — пожаловаться

  GET    /api/admin/reports                   — очередь жалоб [admin]
  POST   /api/admin/reports/{id}/review       — обработать жалобу [admin]
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from funcs.jwt_auth import get_current_user_flexible as get_current_user
from funcs.blocks import (
    block_user, unblock_user, get_blocked_list,
    create_report, get_reports, review_report,
)
from database.database import get_user_role

router = APIRouter(tags=["blocks"])



@router.post("/api/users/{username}/block")
async def block(username: str, current_user: str = Depends(get_current_user)):
    """Заблокировать пользователя."""
    result = block_user(current_user, username)
    if not result["ok"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
    return {"status": "blocked", "target": username}


@router.delete("/api/users/{username}/block")
async def unblock(username: str, current_user: str = Depends(get_current_user)):
    """Разблокировать пользователя."""
    result = unblock_user(current_user, username)
    if not result["ok"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
    return {"status": "unblocked", "target": username}


@router.get("/api/users/blocks")
async def my_blocks(current_user: str = Depends(get_current_user)):
    """Мой чёрный список."""
    return {"blocked": get_blocked_list(current_user)}



class ReportBody(BaseModel):
    reason:  str               # spam | fake | abuse | underage | other
    comment: Optional[str] = None


@router.post("/api/users/{username}/report")
async def report(
    username: str,
    body: ReportBody,
    current_user: str = Depends(get_current_user),
):
    """Пожаловаться на пользователя."""
    result = create_report(current_user, username, body.reason, body.comment)
    if not result["ok"]:
        err = result.get("error", "")
        status = 409 if err == "already_reported" else 400
        raise HTTPException(status_code=status, detail=err)
    return {"status": "reported", "target": username}



def _require_admin(current_user: str = Depends(get_current_user)):
    if get_user_role(current_user) not in ("admin", "super_admin", "moderator"):
        raise HTTPException(status_code=403, detail="Admin only")
    return current_user


class ReviewBody(BaseModel):
    action: str   # dismiss | ban


@router.get("/api/admin/reports")
async def admin_reports(
    status: str = Query("pending", regex="^(pending|reviewed|dismissed)$"),
    limit:  int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    admin:  str = Depends(_require_admin),
):
    """[Admin/Moderator] Список жалоб."""
    reports = get_reports(status=status, limit=limit, offset=offset)
    return {"reports": reports, "count": len(reports)}


@router.post("/api/admin/reports/{report_id}/review")
async def admin_review(
    report_id: int,
    body: ReviewBody,
    admin: str = Depends(_require_admin),
):
    """[Admin/Moderator] Обработать жалобу: dismiss или ban."""
    result = review_report(report_id, admin, body.action)
    if not result["ok"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result