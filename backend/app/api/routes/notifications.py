import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import Notification, NotificationPublic

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=list[NotificationPublic])
def read_notifications(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    return crud.get_notifications(
        session=session, user_id=current_user.id, skip=skip, limit=limit
    )


@router.patch("/{notification_id}/read", response_model=NotificationPublic)
def mark_notification_read(
    session: SessionDep,
    current_user: CurrentUser,
    notification_id: uuid.UUID,
) -> Any:
    notification = session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.mark_notification_as_read(
        session=session, notification_id=notification_id
    )
