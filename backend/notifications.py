from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import Notification, User

router = APIRouter(prefix="/notifications", tags=["notifications"])


def add_notification(db: Session, user_id: int, task_id: int, text: str):
    db.add(Notification(user_id=user_id, task_id=task_id, text=text))


def notification_to_dict(n: Notification) -> dict:
    return {
        "id": n.id,
        "task_id": n.task_id,
        "text": n.text,
        "read": n.is_read,
        "created_at": n.created_at.isoformat(),
    }


@router.get("")
def list_notifications(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc(), Notification.id.desc())
        .all()
    )
    return [notification_to_dict(n) for n in notifications]


@router.post("/{notification_id}/read")
def mark_read(
    notification_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    n = db.get(Notification, notification_id)
    if n is None or n.user_id != user.id:
        raise HTTPException(status_code=404, detail="Уведомление не найдено")

    n.is_read = True
    db.commit()
    return notification_to_dict(n)