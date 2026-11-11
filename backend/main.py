from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from constants import STATUS_LABELS

from database import Base, engine
import models
import auth
import tasks
import users

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(users.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/me")
def me(user: models.User = Depends(auth.get_current_user)):
    return {"id": user.id, "full_name": user.full_name,
            "email": user.email, "role": user.role,
            "manager_id": user.manager_id}

@app.get("/statuses")
def statuses():
    return [{"value": k, "label": v} for k, v in STATUS_LABELS.items()]
