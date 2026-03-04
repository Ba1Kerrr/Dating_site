from fastapi import APIRouter, HTTPException, Request, Form , Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database.database import info_user
from funcs.hash import verify_password
from funcs.rate_limit import login_rate_limit

router = APIRouter(prefix='/login', tags=["login"])

templates = Jinja2Templates(directory="templates")

@router.get("", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("")
async def login(request: Request,username: str = Form(...), password: str = Form(...),_=Depends(login_rate_limit),):
    user = info_user(username) # - {'username': 'smth', 'email': '12345@text.com', 'password': 'hashedpassw'}
    if user is None or not verify_password(password, user.get('password_hash', '')):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    request.session['user'] = username
    return RedirectResponse(url="/", status_code=303)
