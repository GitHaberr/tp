from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import get_current_user
from constants import ACTION_LABELS, ALLOWED_TRANSITIONS, DONE, IN_PROGRESS, NEW, STATUS_LABELS, STATUSES, REVIEW
from database import get_db
from history import add_history
from notifications import add_notification
from models import Task, TaskHistory, User

def short_name(full_name: str) -> str:
    parts = full_name.split()
    return f"{parts[0]} {parts[1][0]}." if len(parts) > 1 else full_name

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    assignee_id: int
    deadline: date

class StatusChange(BaseModel):
    status: str

class CommentData(BaseModel):
    comment: str = ""


def task_to_dict(task: Task, db: Session) -> dict:
    author = db.get(User, task.author_id)
    assignee = db.get(User, task.assignee_id)
    return {
        "id": task.id,
        "author_id": task.author_id,
        "assignee_id": task.assignee_id,
        "title": task.title,
        "description": task.description,
        "author": author.full_name,
        "assignee": assignee.full_name,
        "deadline": task.deadline.isoformat(),
        "status": task.status,
        "status_label": STATUS_LABELS[task.status],
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
    db.flush()
    add_history(db, task.id, user.id, "created", None, NEW,
                f"назначил: {short_name(assignee.full_name)}")
    db.commit()
    db.refresh(task)
    return task_to_dict(task, db)


@router.get("")
def list_tasks(
    scope: str = "all",
    status: str | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if scope not in ("all", "mine", "review"):
        raise HTTPException(status_code=400, detail="Неизвестный раздел списка")
    if status is not None and status not in STATUSES:
        raise HTTPException(status_code=400, detail="Неизвестный статус")

    query = db.query(Task)

    if scope == "mine":
        query = query.filter(Task.assignee_id == user.id)
    else:
        if user.role == "boss":
            query = query.filter(Task.author_id == user.id)
        else:
            query = query.filter(Task.assignee_id == user.id)
        if scope == "review":
            query = query.filter(Task.status == REVIEW)

    if status is not None:
        query = query.filter(Task.status == status)

    tasks = query.order_by(Task.deadline).all()
    return [task_to_dict(t, db) for t in tasks]


@router.get("/{task_id}")
def get_task(
    task_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Поручение не найдено")

    if user.id not in (task.author_id, task.assignee_id):
        raise HTTPException(status_code=403, detail="Нет доступа к этому поручению")

    return task_to_dict(task, db)

@router.get("/{task_id}/history")
def get_task_history(
    task_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Поручение не найдено")

    if user.id not in (task.author_id, task.assignee_id):
        raise HTTPException(status_code=403, detail="Нет доступа к этому поручению")

    records = (
        db.query(TaskHistory)
        .filter(TaskHistory.task_id == task_id)
        .order_by(TaskHistory.created_at.desc(), TaskHistory.id.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "action": r.action,
            "action_label": ACTION_LABELS.get(r.action, r.action),
            "user": db.get(User, r.user_id).full_name,
            "old_status": r.old_status,
            "new_status": r.new_status,
            "old_status_label": STATUS_LABELS.get(r.old_status),
            "new_status_label": STATUS_LABELS.get(r.new_status),
            "comment": r.comment,
            "created_at": r.created_at.isoformat(),
        }
        for r in records
    ]

@router.patch("/{task_id}/status")
def change_status(
    task_id: int,
    data: StatusChange,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Поручение не найдено")

    if user.id not in (task.author_id, task.assignee_id):
        raise HTTPException(status_code=403, detail="Нет доступа к этому поручению")

    if user.id != task.assignee_id:
        raise HTTPException(status_code=403, detail="Менять статус может только исполнитель")

    if data.status not in STATUSES:
        raise HTTPException(status_code=400, detail="Неизвестный статус")

    if (task.status, data.status) not in ALLOWED_TRANSITIONS:
        raise HTTPException(status_code=400, detail="Недопустимое изменение статуса")

    old_status = task.status
    task.status = data.status
    task.updated_at = datetime.now()
    add_history(db, task.id, user.id, "status_changed", old_status, data.status)
    db.commit()
    db.refresh(task)
    return task_to_dict(task, db)

@router.post("/{task_id}/submit")
def submit_task(
    task_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Поручение не найдено")

    if user.id not in (task.author_id, task.assignee_id):
        raise HTTPException(status_code=403, detail="Нет доступа к этому поручению")

    if user.id != task.assignee_id:
        raise HTTPException(status_code=403, detail="Передать на проверку может только исполнитель")

    if task.status != IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Недопустимое изменение статуса")

    task.status = REVIEW
    task.updated_at = datetime.now()
    add_history(db, task.id, user.id, "submitted", IN_PROGRESS, REVIEW)
    add_notification(
        db,
        task.author_id,
        task.id,
        f"{short_name(user.full_name)} отметил поручение «{task.title}» выполненным. Требуется подтверждение.",
    )
    db.commit()
    db.refresh(task)
    return task_to_dict(task, db)


@router.post("/{task_id}/approve")
def approve_task(
    task_id: int,
    data: CommentData = CommentData(),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Поручение не найдено")

    if user.id not in (task.author_id, task.assignee_id):
        raise HTTPException(status_code=403, detail="Нет доступа к этому поручению")

    if user.id != task.author_id:
        raise HTTPException(status_code=403, detail="Подтвердить или вернуть поручение может только автор")

    if task.status != REVIEW:
        raise HTTPException(status_code=400, detail="Недопустимое изменение статуса")

    now = datetime.now()
    task.status = DONE
    task.updated_at = now
    task.closed_at = now
    add_history(db, task.id, user.id, "approved", REVIEW, DONE, data.comment.strip())
    add_notification(
        db,
        task.assignee_id,
        task.id,
        f"Поручение «{task.title}» подтверждено и закрыто.",
    )
    db.commit()
    db.refresh(task)
    return task_to_dict(task, db)


@router.post("/{task_id}/reject")
def reject_task(
    task_id: int,
    data: CommentData,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Поручение не найдено")

    if user.id not in (task.author_id, task.assignee_id):
        raise HTTPException(status_code=403, detail="Нет доступа к этому поручению")

    if user.id != task.author_id:
        raise HTTPException(status_code=403, detail="Подтвердить или вернуть поручение может только автор")

    if task.status != REVIEW:
        raise HTTPException(status_code=400, detail="Недопустимое изменение статуса")

    comment = data.comment.strip()
    if not comment:
        raise HTTPException(status_code=400, detail="Укажите комментарий — он обязателен при возврате поручения")

    task.status = IN_PROGRESS
    task.updated_at = datetime.now()
    add_history(db, task.id, user.id, "rejected", REVIEW, IN_PROGRESS, comment)
    add_notification(
        db,
        task.assignee_id,
        task.id,
        f"Поручение «{task.title}» возвращено в работу: {comment}",
    )
    db.commit()
    db.refresh(task)
    return task_to_dict(task, db)

@router.put("/{task_id}")
def update_task(
    task_id: int,
    data: TaskCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Поручение не найдено")

    if user.id not in (task.author_id, task.assignee_id):
        raise HTTPException(status_code=403, detail="Нет доступа к этому поручению")

    if user.id != task.author_id:
        raise HTTPException(status_code=403, detail="Редактировать поручение может только автор")

    if task.status == DONE:
        raise HTTPException(status_code=400, detail="Закрытое поручение нельзя редактировать")

    title = data.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Введите название поручения")

    assignee = db.get(User, data.assignee_id)
    if assignee is None or assignee.manager_id != user.id:
        raise HTTPException(status_code=400, detail="Выберите исполнителя из своих подчинённых")


    if data.deadline != task.deadline and data.deadline < date.today():
        raise HTTPException(status_code=400, detail="Срок не может быть раньше сегодняшней даты")

    changes = []
    if title != task.title:
        changes.append("название")
    if data.description != task.description:
        changes.append("описание")
    if assignee.id != task.assignee_id:
        old_assignee = db.get(User, task.assignee_id)
        changes.append(
            f"исполнитель: {short_name(old_assignee.full_name)} → {short_name(assignee.full_name)}"
        )
    if data.deadline != task.deadline:
        changes.append(
            f"срок: {task.deadline.strftime('%d.%m.%Y')} → {data.deadline.strftime('%d.%m.%Y')}"
        )

    if not changes:
        return task_to_dict(task, db)

    task.title = title
    task.description = data.description
    task.assignee_id = assignee.id
    task.deadline = data.deadline
    task.updated_at = datetime.now()
    add_history(db, task.id, user.id, "updated", None, None, "Изменено: " + "; ".join(changes))
    db.commit()
    db.refresh(task)
    return task_to_dict(task, db)