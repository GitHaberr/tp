from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import Task, User

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    assignee_id: int
    deadline: date


def task_to_dict(task: Task, db: Session) -> dict:
    author = db.get(User, task.author_id)
    assignee = db.get(User, task.assignee_id)
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "author": author.full_name,
        "assignee": assignee.full_name,
        "deadline": task.deadline.isoformat(),
        "status": task.status,
    }


@router.post("")
def create_task(
    data: TaskCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role != "boss":
        raise HTTPException(status_code=403, detail="Создавать поручения может только начальник")

    if not data.title.strip():
        raise HTTPException(status_code=400, detail="Введите название поручения")

    assignee = db.get(User, data.assignee_id)
    if assignee is None or assignee.manager_id != user.id:
        raise HTTPException(status_code=400, detail="Выберите исполнителя из своих подчинённых")

    if data.deadline < date.today():
        raise HTTPException(status_code=400, detail="Срок не может быть раньше сегодняшней даты")

    task = Task(
        title=data.title.strip(),
        description=data.description,
        author_id=user.id,
        assignee_id=assignee.id,
        deadline=data.deadline,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task_to_dict(task, db)


@router.get("")
def list_tasks(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role == "boss":
        tasks = db.query(Task).filter(Task.author_id == user.id).all()
    else:
        tasks = db.query(Task).filter(Task.assignee_id == user.id).all()
    return [task_to_dict(t, db) for t in tasks]