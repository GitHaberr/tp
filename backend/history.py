from sqlalchemy.orm import Session

from models import TaskHistory


def add_history(
    db: Session,
    task_id: int,
    user_id: int,
    action: str,
    old_status: str | None = None,
    new_status: str | None = None,
    comment: str = "",
):
    db.add(TaskHistory(
        task_id=task_id,
        user_id=user_id,
        action=action,
        old_status=old_status,
        new_status=new_status,
        comment=comment,
    ))