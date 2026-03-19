from fastapi import APIRouter, Request

router = APIRouter(prefix='/api', tags=["logout"])

@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return {"status": "ok"}