"""
app/funcs/blocks.py
Функции для работы с блокировками и жалобами.
Стиль — engine + text(), как в database.py.
"""
from sqlalchemy import text
from database.database import engine


def block_user(blocker: str, blocked: str) -> dict:
    """Заблокировать пользователя. Возвращает {ok, already_blocked}."""
    if blocker == blocked:
        return {"ok": False, "error": "cannot_block_self"}
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO blocks (blocker_id, blocked_id)
                SELECT b.id, t.id
                FROM users b, users t
                WHERE b.username = :blocker AND t.username = :blocked
                ON CONFLICT (blocker_id, blocked_id) DO NOTHING
            """), {"blocker": blocker, "blocked": blocked})
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def unblock_user(blocker: str, blocked: str) -> dict:
    """Разблокировать пользователя."""
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                DELETE FROM blocks
                WHERE blocker_id = (SELECT id FROM users WHERE username = :blocker)
                  AND blocked_id = (SELECT id FROM users WHERE username = :blocked)
            """), {"blocker": blocker, "blocked": blocked})
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def is_blocked(blocker: str, blocked: str) -> bool:
    """Проверить — заблокировал ли blocker пользователя blocked."""
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT 1 FROM blocks
            WHERE blocker_id = (SELECT id FROM users WHERE username = :blocker)
              AND blocked_id = (SELECT id FROM users WHERE username = :blocked)
        """), {"blocker": blocker, "blocked": blocked}).fetchone()
    return row is not None


def is_blocked_any(user1: str, user2: str) -> bool:
    """Заблокировал ли кто-нибудь из двух другого (в любую сторону)."""
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT 1 FROM blocks
            WHERE (blocker_id = (SELECT id FROM users WHERE username = :u1)
                   AND blocked_id = (SELECT id FROM users WHERE username = :u2))
               OR (blocker_id = (SELECT id FROM users WHERE username = :u2)
                   AND blocked_id = (SELECT id FROM users WHERE username = :u1))
            LIMIT 1
        """), {"u1": user1, "u2": user2}).fetchone()
    return row is not None


def get_blocked_list(username: str) -> list[dict]:
    """Список пользователей, которых заблокировал username."""
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT u.username, u.name, u.avatar,
                   b.created_at AT TIME ZONE 'UTC' AS blocked_at
            FROM blocks b
            JOIN users blocker ON blocker.id = b.blocker_id
            JOIN users u       ON u.id       = b.blocked_id
            WHERE blocker.username = :u
            ORDER BY b.created_at DESC
        """), {"u": username}).fetchall()
    return [
        {"username": r[0], "name": r[1], "avatar": r[2],
         "blocked_at": r[3].isoformat() if r[3] else None}
        for r in rows
    ]



VALID_REASONS = {"spam", "fake", "abuse", "underage", "other"}


def create_report(reporter: str, target: str, reason: str, comment: str | None = None) -> dict:
    """Создать жалобу. Один пользователь не может жаловаться дважды на одного."""
    if reporter == target:
        return {"ok": False, "error": "cannot_report_self"}
    if reason not in VALID_REASONS:
        return {"ok": False, "error": f"invalid_reason, use: {VALID_REASONS}"}
    try:
        with engine.begin() as conn:
            # Проверяем — уже есть pending жалоба от этого юзера на этого
            exists = conn.execute(text("""
                SELECT 1 FROM reports
                WHERE reporter_id = (SELECT id FROM users WHERE username = :reporter)
                  AND target_id   = (SELECT id FROM users WHERE username = :target)
                  AND status = 'pending'
            """), {"reporter": reporter, "target": target}).fetchone()
            if exists:
                return {"ok": False, "error": "already_reported"}

            conn.execute(text("""
                INSERT INTO reports (reporter_id, target_id, reason, comment)
                SELECT r.id, t.id, :reason, :comment
                FROM users r, users t
                WHERE r.username = :reporter AND t.username = :target
            """), {"reporter": reporter, "target": target,
                   "reason": reason, "comment": comment})
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def get_reports(status: str = "pending", limit: int = 50, offset: int = 0) -> list[dict]:
    """Список жалоб для админа."""
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT r.id,
                   reporter.username AS reporter,
                   target.username   AS target,
                   target.avatar     AS target_avatar,
                   r.reason, r.comment, r.status,
                   r.created_at AT TIME ZONE 'UTC' AS created_at,
                   r.reviewed_at AT TIME ZONE 'UTC' AS reviewed_at
            FROM reports r
            JOIN users reporter ON reporter.id = r.reporter_id
            JOIN users target   ON target.id   = r.target_id
            WHERE r.status = :status
            ORDER BY r.created_at DESC
            LIMIT :limit OFFSET :offset
        """), {"status": status, "limit": limit, "offset": offset}).fetchall()
    keys = ["id", "reporter", "target", "target_avatar",
            "reason", "comment", "status", "created_at", "reviewed_at"]
    result = []
    for r in rows:
        d = dict(zip(keys, r))
        d["created_at"]  = d["created_at"].isoformat()  if d["created_at"]  else None
        d["reviewed_at"] = d["reviewed_at"].isoformat() if d["reviewed_at"] else None
        result.append(d)
    return result


def review_report(report_id: int, admin_username: str, action: str) -> dict:
    """
    Обработать жалобу.
    action: 'dismiss' — отклонить, 'ban' — забанить нарушителя
    """
    if action not in ("dismiss", "ban"):
        return {"ok": False, "error": "action must be 'dismiss' or 'ban'"}
    try:
        with engine.begin() as conn:
            # Меняем статус жалобы
            new_status = "dismissed" if action == "dismiss" else "reviewed"
            conn.execute(text("""
                UPDATE reports
                SET status      = :status,
                    reviewed_by = (SELECT id FROM users WHERE username = :admin),
                    reviewed_at = NOW()
                WHERE id = :rid
            """), {"status": new_status, "admin": admin_username, "rid": report_id})

            if action == "ban":
                # Баним нарушителя
                conn.execute(text("""
                    UPDATE users SET status = 'banned'
                    WHERE id = (
                        SELECT target_id FROM reports WHERE id = :rid
                    )
                """), {"rid": report_id})

        return {"ok": True, "action": action}
    except Exception as e:
        return {"ok": False, "error": str(e)}