import base64
import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.admin import Admin

bearer = HTTPBearer(auto_error=False)
SECRET_KEY = os.environ["SECRET_KEY"]
if len(SECRET_KEY) < 32:
    raise RuntimeError("SECRET_KEY must contain at least 32 characters")
TOKEN_MINUTES = 30

def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)
    return "scrypt$" + base64.b64encode(salt).decode() + "$" + base64.b64encode(digest).decode()

def verify_password(password, encoded):
    try:
        algorithm, salt, expected = encoded.split("$")
        if algorithm != "scrypt": return False
        digest = hashlib.scrypt(password.encode(), salt=base64.b64decode(salt), n=16384, r=8, p=1)
        return secrets.compare_digest(digest, base64.b64decode(expected))
    except (ValueError, TypeError):
        return False

def create_token(admin):
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub":str(admin.id), "iat":now, "exp":now+timedelta(minutes=TOKEN_MINUTES), "iss":"atelier", "aud":"atelier-admin"}, SECRET_KEY, algorithm="HS256")

def require_admin(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)):
    error = HTTPException(401, "Войдите в панель администратора", headers={"WWW-Authenticate":"Bearer"})
    if credentials is None: raise error
    try:
        claims = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"], audience="atelier-admin", issuer="atelier", options={"require":["exp","iat","sub","aud","iss"]})
        admin = db.get(Admin, int(claims["sub"]))
        if admin is None: raise error
        return admin
    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise error
