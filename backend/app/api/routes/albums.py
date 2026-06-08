import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    AlbumCreate,
    AlbumPublic,
    AlbumsPublic,
    AlbumUpdate,
    Message,
    UserRole,
)

router = APIRouter(prefix="/albums", tags=["albums"])


def _can_manage_event_album(
    *, session: SessionDep, current_user: CurrentUser, event_id: uuid.UUID
) -> bool:
    if current_user.role == UserRole.ADMIN:
        return True
    event = crud.get_event(session=session, event_id=event_id)
    return event is not None and event.creator_id == current_user.id


@router.get("/event/{event_id}", response_model=AlbumsPublic)
def read_albums_by_event(session: SessionDep, event_id: uuid.UUID) -> Any:
    event = crud.get_event(session=session, event_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    albums = crud.get_albums_by_event(session=session, event_id=event_id)
    return AlbumsPublic(data=albums, count=len(albums))


@router.get("/{album_id}", response_model=AlbumPublic)
def read_album(session: SessionDep, album_id: uuid.UUID) -> Any:
    album = crud.get_album(session=session, album_id=album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    return album


@router.post("/", response_model=AlbumPublic)
def create_album(
    *, session: SessionDep, current_user: CurrentUser, album_in: AlbumCreate
) -> Any:
    event = crud.get_event(session=session, event_id=album_in.event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not _can_manage_event_album(
        session=session, current_user=current_user, event_id=album_in.event_id
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.create_album(session=session, album_in=album_in)


@router.patch("/{album_id}", response_model=AlbumPublic)
def update_album(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    album_id: uuid.UUID,
    album_in: AlbumUpdate,
) -> Any:
    album = crud.get_album(session=session, album_id=album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    if not _can_manage_event_album(
        session=session, current_user=current_user, event_id=album.event_id
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.update_album(session=session, db_album=album, album_in=album_in)


@router.delete("/{album_id}")
def delete_album(
    session: SessionDep, current_user: CurrentUser, album_id: uuid.UUID
) -> Message:
    album = crud.get_album(session=session, album_id=album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    if not _can_manage_event_album(
        session=session, current_user=current_user, event_id=album.event_id
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    crud.delete_album(session=session, album_id=album_id)
    return Message(message="Album deleted successfully")
