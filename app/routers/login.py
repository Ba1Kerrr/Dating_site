from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database.database import info_user
from app.hash import verify_password
router = APIRouter(prefix='/login', tags=["login"])

templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("")
async def login(request: Request,username: str = Form(...), password: str = Form(...)):
    user = info_user(username) # - {'username': 'smth', 'email': '12345@text.com', 'password': 'hashedpassw'}
    if user is None or not verify_password(password, user['password']):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    request.session['user'] = username
    return RedirectResponse(url="/", status_code=303)
#-----------------------------------------------------------------------------------------------------------------------------
#                               logout
@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)