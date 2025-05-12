from fastapi import FastAPI, Request, Form, Depends, Response, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User
import dbtools
import auth

app = FastAPI()
templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user_dep(request: Request, db: Session = Depends(get_db)):
    return auth.get_current_user(request, db)

@app.get("/")
def index(request: Request, current_user=Depends(get_current_user_dep)):
    return templates.TemplateResponse("index.html", {"request": request, "current_user": current_user})


@app.get("/register")
def index(request: Request, current_user=Depends(get_current_user_dep)):
    if current_user:
        return RedirectResponse("/login", status_code=302)
    return templates.TemplateResponse("register.html", {"request": request, "current_user": current_user})

@app.post("/register")
def register(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    gender: str = Form(...),
    nationality: str = Form(...),
    organization: str = Form(...),
    position: str = Form(...),
    dob: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Паролі не збігаються"})

    if dbtools.get_user_by_email(db, email):
        return templates.TemplateResponse("register.html", {"request": request, "error": "Користувач вже існує"})

    hashed_password = auth.get_password_hash(password)
    dbtools.create_user(db, first_name, last_name, gender, nationality, organization, position, dob, email, hashed_password)
    return RedirectResponse("/login", status_code=302)

@app.get("/login")
def login_form(request: Request, current_user=Depends(get_current_user_dep)):
    if current_user:
        return RedirectResponse("/members", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_dep)
):
    user = dbtools.get_user_by_email(db, email)
    if not user or not auth.verify_password(password, user.password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Невірні дані"})

    session_token = auth.create_session(user.id)
    response = RedirectResponse("/members", status_code=302)
    response.set_cookie(key="session", value=session_token, httponly=True)
    return response

@app.get("/members")
def members(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user_dep)):
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    users = dbtools.get_all_users(db)
    return templates.TemplateResponse("members.html", {"request": request, "users": users, "current_user": current_user})

@app.get("/edit/{user_id}")
def edit_form(user_id: int, request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user_dep)):
    current_user = auth.get_current_user(request, db)
    if not current_user or current_user.id != user_id:
        return templates.TemplateResponse("403.html", {"request": request, "current_user": current_user}, status_code=403)
    return templates.TemplateResponse("edit.html", {"request": request, "current_user": current_user})

@app.post("/edit/{user_id}")
def edit(user_id: int,
         request: Request,
         first_name: str = Form(...),
         last_name: str = Form(...),
         organization: str = Form(...),
         position: str = Form(...),
         old_password: str = Form(None),
         new_password: str = Form(None),
         confirm_password: str = Form(None),
         db: Session = Depends(get_db),
         current_user=Depends(get_current_user_dep)):


    if not current_user or current_user.id != user_id:
        raise HTTPException(status_code=403)

    dbtools.update_user(db, user_id, first_name, last_name, organization, position)

    if old_password or new_password or confirm_password:
        if not auth.verify_password(old_password, current_user.password):
            return templates.TemplateResponse("edit.html", {
                "request": request,
                "current_user": current_user,
                "error": "Старий пароль невірний"
            })
        if not new_password:
            return templates.TemplateResponse("edit.html", {
                "request": request,
                "current_user": current_user,
                "error": "Новий пароль не повинен бути пустим"
            })
        if new_password != confirm_password:
            return templates.TemplateResponse("edit.html", {
                "request": request,
                "current_user": current_user,
                "error": "Нові паролі не збігаються"
            })
        if old_password == old_password:
            return templates.TemplateResponse("edit.html", {
                "request": request,
                "current_user": current_user,
                "error": "Новий та старий пароль однакові"
            })

        hashed = auth.get_password_hash(new_password)
        dbtools.update_user_password(db, user_id, hashed)
        return templates.TemplateResponse("edit.html", {
            "request": request,
            "current_user": current_user,
            "message": "Пароль успішно змінено"
        })

    return templates.TemplateResponse("edit.html", {
        "request": request,
        "current_user": current_user,
        "message": "Дані успішно оновлено"
    })



@app.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("session")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
