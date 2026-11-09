from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import Base, engine, get_db
import models
import auth

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/me")
def me(user: models.User = Depends(auth.get_current_user)):
    return {"id": user.id, "full_name": user.full_name,
            "email": user.email, "role": user.role,
            "manager_id": user.manager_id}


@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return [
        {"id": u.id, "full_name": u.full_name, "email": u.email,
         "role": u.role, "manager_id": u.manager_id}
        for u in users
    ]