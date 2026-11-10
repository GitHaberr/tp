from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/subordinates")
def list_subordinates(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role != "boss":
        raise HTTPException(status_code=403, detail="Список подчинённых доступен только начальнику")

    subordinates = db.query(User).filter(User.manager_id == user.id).all()
    return [{"id": u.id, "full_name": u.full_name} for u in subordinates]