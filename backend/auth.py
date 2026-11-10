import jwt
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import User, PasswordResetToken
from security import check_password, hash_password

SECRET_KEY = "change-me-for-study-project"
ALGORITHM = "HS256"

router = APIRouter(prefix="/auth", tags=["auth"])
bearer = HTTPBearer()


class LoginData(BaseModel):
    email: str
    password: str


class ForgotData(BaseModel):
    email: str


class ResetData(BaseModel):
    token: str
    new_password: str


@router.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if user is None or not check_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    payload = {
        "sub": str(user.id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=8),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Нужно войти в систему")

    user = db.get(User, int(payload["sub"]))
    if user is None:
        raise HTTPException(status_code=401, detail="Нужно войти в систему")
    return user


@router.post("/forgot")
def forgot_password(data: ForgotData, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь с таким email не найден")

    token = secrets.token_urlsafe(32)
    db.add(PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=datetime.now() + timedelta(hours=1),
    ))
    db.commit()

    print(f"ПИСЬМО для {user.email}: http://localhost:5173/reset?token={token}")
    return {"message": "Письмо отправлено"}


@router.post("/reset")
def reset_password(data: ResetData, db: Session = Depends(get_db)):
    record = db.query(PasswordResetToken).filter(PasswordResetToken.token == data.token).first()
    if record is None or record.used or record.expires_at < datetime.now():
        raise HTTPException(status_code=400, detail="Ссылка недействительна или устарела")

    if len(data.new_password) < 4:
        raise HTTPException(status_code=400, detail="Пароль должен быть не короче 4 символов")

    user = db.get(User, record.user_id)
    user.password_hash = hash_password(data.new_password)
    record.used = True
    db.commit()
    return {"message": "Пароль изменён"}


@router.post("/logout")
def logout(user: User = Depends(get_current_user)):
    return {"message": "Вы вышли из системы"}