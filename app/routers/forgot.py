from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import update_password,update_password_email
from database import info_user,info_user_email,detect_username_from_email
from hash import hash_password
router = APIRouter(prefix='/forgot', tags=["forgot"])

templates = Jinja2Templates(directory="templates")
@router.post("/password")
async def update_password(request: Request, username: str = Form(...), new_password: str = Form(...)):
    user = info_user(username)
    #здесь будет штука,получающая email из переменной user(это делается - user['email']) и отправляющая письмо
    #затем мы отправлям с функцию js в самом фронтенде,когда пользователь отправил свой username(для этого создать отдельный button) и обрабатываем ее на бэке
    #после этого ждем отправки от пользователя с формы ключ для восстановления
    #затем в случаи успеха(желательно это также сделать в js(передать js инпут от пользователя)),затем даем челу ввести новый пароль
    hashed_new_password = hash_password(new_password)
    success = update_password(username, hashed_new_password)
    if not success:
        raise HTTPException(status_code=400)
    request.session['user'] = username
    return RedirectResponse(url="/", status_code=303)

@router.get('/forgot_password',response_class=HTMLResponse)
async def forgot_password_get(request: Request):
    return templates.TemplateResponse("forgot-password.html", {"request": request})
#-----------------------------------------------------------------------------------------------------------------------------
#                                            if u forgot username

@router.get("/username",response_class = HTMLResponse)
async def forgot_usrname_get(request: Request):
    return templates.TemplateResponse("Forgot_username.html", {"request": request})

@router.post("/username")
async def forgot_usrname(request: Request, email: str = Form(...), new_password: str = Form(...)):
    user = info_user_email(email)
    #даем ему ввести email,высылаем код,проверяем его,потом даем ему ввести новый пароль
    hashed_new_password = hash_password(new_password)
    success = update_password_email(info_user_email, hashed_new_password)
    if not success:
        raise HTTPException(status_code=400)
    request.session['user'] = detect_username_from_email(email)
    return RedirectResponse(url="/", status_code=303)