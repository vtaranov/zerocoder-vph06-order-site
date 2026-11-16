import os
import secrets
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_token, require_admin, TOKEN_MINUTES
from app.models.admin import Admin

router = APIRouter(prefix="/api/auth", tags=["Авторизация"])
class Credentials(BaseModel):
    username: str = Field(min_length=3, max_length=80, pattern=r"^[a-zA-Z0-9_.-]+$")
    password: str = Field(min_length=12, max_length=128)

@router.get("/check")
def check(db: Session = Depends(get_db)):
    return {"registration_open": db.get(Admin, 1) is None}

@router.post("/register", status_code=201)
def register(data: Credentials, x_bootstrap_token: str = Header(default=""), db: Session = Depends(get_db)):
    if db.get(Admin, 1): raise HTTPException(409, "Администратор уже зарегистрирован")
    expected = os.environ.get("BOOTSTRAP_TOKEN", "")
    if not expected or not secrets.compare_digest(x_bootstrap_token.encode(), expected.encode()):
        raise HTTPException(403, "Нужен одноразовый ключ настройки сервера")
    admin = Admin(id=1, username=data.username, password_hash=hash_password(data.password))
    try:
        db.add(admin); db.commit()
    except IntegrityError:
        db.rollback(); raise HTTPException(409, "Администратор уже зарегистрирован")
    return {"username":admin.username, "registration_open":False}

@router.post("/login")
def login(data: Credentials, db: Session = Depends(get_db)):
    admin = db.get(Admin, 1)
    # A dummy hash keeps the password hashing cost on unknown usernames too.
    encoded = admin.password_hash if admin else hash_password("dummy-password-for-login")
    valid = verify_password(data.password, encoded)
    if not admin or not secrets.compare_digest(data.username.encode(), admin.username.encode()) or not valid:
        raise HTTPException(401, "Неверный логин или пароль")
    return {"access_token":create_token(admin), "token_type":"bearer", "expires_in":TOKEN_MINUTES*60}

@router.get("/me")
def me(admin: Admin = Depends(require_admin)):
    return {"id":admin.id, "username":admin.username}
