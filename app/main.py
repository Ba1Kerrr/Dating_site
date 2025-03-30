from requests import Response
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import info_user,find_all_users,profile
from app.routers.registers import router as register_router
from app.routers.login import router as login_router
from app.routers.forgot import router as forgot_router
from app.routers.logout import router as logout
#-----------------------------------------------------------------------------------------------------------------------------
#                                        set up fastapi
app = FastAPI()

app.include_router(logout)
app.include_router(register_router)
app.include_router(login_router)
app.include_router(forgot_router)

#add my static files(css,other)
app.mount("/static", StaticFiles(directory=Path(__file__).parent /"templates"), name="static")

# Middleware
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Template configuration
templates = Jinja2Templates(directory="app/templates")

#-----------------------------------------------------------------------------------------------------------------------------
#                                           base page
@app.get("/")
async def read_root(request: Request):
    user = request.session.get('user')
    if user == None:
        return templates.TemplateResponse("index.html", {"request": request})
    user_data = info_user(user)
    if 'location' in user_data and 'gender' in user_data:
        data = find_all_users(user_data['location'], user_data['gender'])
    else:
    # Обработка ошибки или возврат пустого значения
        data = []
    #тут бы работать с каким нибудь условным redis для ускорения работы
    return templates.TemplateResponse("index.html", {"request": request, "user": user,"data": data}, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})
#to add profile pages on main menu with filtres to find you second part
#add your avatar to the right corner

#-----------------------------------------------------------------------------------------------------------------------------
#                              Handling JavaScript Functions to add some dop-info on your profile(images)

@app.post("/upload")
async def upload():
    return 1
@app.get("/static/static/index.css")
def get_index_css():
    return Response(content="templates/static/index.css", media_type="text/css", headers={"Expires": "0"})
#                                           my_profile
@app.get("/users/{username}",response_class =HTMLResponse)
async def read_user(request: Request,username:str):
    user = profile(username)
    if user is None:
        return HTTPException(status_code=404)
    context = {
    "request": request,
    "user": user['username'],
    "avatar": user['avatar'],
    "age": user['age'],
    "gender": user['gender'],
    "name": user['name'],
    "location": user['location'],
    "email":user['email']
    }
    return templates.TemplateResponse("user.html", context)
    #сдесь нужно сделать так чтоб чел видел обычную страницу(нужно в html поменять display,увести все в левый угол,затем будем делать сами фотки этого человека как в той же инсте или вк )
                                        #!!!!полностью поменять оформление профиля!!!!!!

#-----------------------------------------------------------------------------------------------------------------------------
#                                                       logout


#-----------------------------------------------------------------------------------------------------------------------------
#                                                       dop-info about futures

#and finally steps are :
# to add profile pages on main menu with filtres to find you second part
#incude in my project redis,nginx
# in next steps is create and use server
#add redis,kafka

# ну верификацию сделал,но она работает очень коряво,
# нужно также сделать проверку js на то чтоб все данные были корректные(подключить модели)
# также почитать все в файле fastapi-help