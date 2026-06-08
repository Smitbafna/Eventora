import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Event,
    EventCreate,
    EventPublic,
    EventsPublic,
    EventUpdate,
    Message,
    UserRole,
)

router = APIRouter(prefix="/events", tags=["events"])


def _can_manage_event(*, current_user: CurrentUser, creator_id: uuid.UUID) -> bool:
    return current_user.role == UserRole.ADMIN or current_user.id == creator_id


@router.get("/", response_model=EventsPublic)
def read_events(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    count_statement = select(func.count()).select_from(Event)
    count = session.exec(count_statement).one()
    events = crud.get_events(session=session, skip=skip, limit=limit)
    return EventsPublic(data=events, count=count)


@router.get("/{event_id}", response_model=EventPublic)
def read_event(session: SessionDep, event_id: uuid.UUID) -> Any:
    event = crud.get_event(session=session, event_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/", response_model=EventPublic)
def create_event(
    *, session: SessionDep, current_user: CurrentUser, event_in: EventCreate
) -> Any:
    return crud.create_event(
        session=session, event_in=event_in, creator_id=current_user.id
    )


@router.patch("/{event_id}", response_model=EventPublic)
def update_event(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    event_id: uuid.UUID,
    event_in: EventUpdate,
) -> Any:
    event = crud.get_event(session=session, event_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not _can_manage_event(current_user=current_user, creator_id=event.creator_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.update_event(session=session, db_event=event, event_in=event_in)


@router.delete("/{event_id}")
def delete_event(
    session: SessionDep, current_user: CurrentUser, event_id: uuid.UUID
) -> Message:
    event = crud.get_event(session=session, event_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not _can_manage_event(current_user=current_user, creator_id=event.creator_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    crud.delete_event(session=session, event_id=event_id)
    return Message(message="Event deleted successfully")
