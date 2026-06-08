import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import func, select

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Comment,
    CommentCreate,
    Media,
    MediaCreate,
    MediaPublic,
    MediasPublic,
    MediaTag,
    MediaUpdate,
    Message,
    UserRole,
)

router = APIRouter(prefix="/media", tags=["media"])


class UserTagCreate(BaseModel):
    tagged_user_id: uuid.UUID


class MediaTagCreate(BaseModel):
    tag_name: str
    confidence: float = 0.0


def _can_upload_media(*, current_user: CurrentUser) -> bool:
    return current_user.role in (
        UserRole.ADMIN,
        UserRole.PHOTOGRAPHER,
        UserRole.CLUB_MEMBER,
    )


def _can_manage_media(*, current_user: CurrentUser, media: Media) -> bool:
    if current_user.role == UserRole.ADMIN:
        return True
    return current_user.id == media.uploader_id


@router.get("/event/{event_id}", response_model=MediasPublic)
def read_media_by_event(
    session: SessionDep, event_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> Any:
    event = crud.get_event(session=session, event_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    count_statement = (
        select(func.count()).select_from(Media).where(Media.event_id == event_id)
    )
    count = session.exec(count_statement).one()
    media_items = crud.get_media_by_event(
        session=session, event_id=event_id, skip=skip, limit=limit
    )
    return MediasPublic(data=media_items, count=count)


@router.get("/album/{album_id}", response_model=MediasPublic)
def read_media_by_album(session: SessionDep, album_id: uuid.UUID) -> Any:
    album = crud.get_album(session=session, album_id=album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    media_items = crud.get_media_by_album(session=session, album_id=album_id)
    return MediasPublic(data=media_items, count=len(media_items))


@router.get("/{media_id}", response_model=MediaPublic)
def read_media(session: SessionDep, media_id: uuid.UUID) -> Any:
    media = crud.get_media(session=session, media_id=media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    return media


@router.post("/", response_model=MediaPublic)
def create_media(
    *, session: SessionDep, current_user: CurrentUser, media_in: MediaCreate
) -> Any:
    if not _can_upload_media(current_user=current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    event = crud.get_event(session=session, event_id=media_in.event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if media_in.album_id:
        album = crud.get_album(session=session, album_id=media_in.album_id)
        if not album or album.event_id != media_in.event_id:
            raise HTTPException(status_code=400, detail="Album does not belong to event")
    return crud.create_media(
        session=session, media_in=media_in, uploader_id=current_user.id
    )


@router.patch("/{media_id}", response_model=MediaPublic)
def update_media(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    media_id: uuid.UUID,
    media_in: MediaUpdate,
) -> Any:
    media = crud.get_media(session=session, media_id=media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    if not _can_manage_media(current_user=current_user, media=media):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.update_media(session=session, db_media=media, media_in=media_in)


@router.delete("/{media_id}")
def delete_media(
    session: SessionDep, current_user: CurrentUser, media_id: uuid.UUID
) -> Message:
    media = crud.get_media(session=session, media_id=media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    if not _can_manage_media(current_user=current_user, media=media):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    crud.delete_media(session=session, media_id=media_id)
    return Message(message="Media deleted successfully")


@router.post("/{media_id}/like", response_model=Message)
def like_media(
    session: SessionDep, current_user: CurrentUser, media_id: uuid.UUID
) -> Any:
    media = crud.get_media(session=session, media_id=media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    existing = crud.get_like(
        session=session, user_id=current_user.id, media_id=media_id
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already liked")
    crud.create_like(session=session, user_id=current_user.id, media_id=media_id)
    return Message(message="Media liked successfully")


@router.delete("/{media_id}/like", response_model=Message)
def unlike_media(
    session: SessionDep, current_user: CurrentUser, media_id: uuid.UUID
) -> Any:
    media = crud.get_media(session=session, media_id=media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    crud.delete_like(session=session, user_id=current_user.id, media_id=media_id)
    return Message(message="Like removed successfully")


@router.get("/{media_id}/comments", response_model=list[Comment])
def read_comments(session: SessionDep, media_id: uuid.UUID) -> Any:
    media = crud.get_media(session=session, media_id=media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    return crud.get_comments_by_media(session=session, media_id=media_id)


@router.post("/{media_id}/comments", response_model=Comment)
def create_comment(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    media_id: uuid.UUID,
    comment_in: CommentCreate,
) -> Any:
    if comment_in.media_id != media_id:
        raise HTTPException(status_code=400, detail="Media ID mismatch")
    media = crud.get_media(session=session, media_id=media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    return crud.create_comment(
        session=session, comment_in=comment_in, user_id=current_user.id
    )


@router.post("/{media_id}/favorites", response_model=MediaPublic)
def add_favorite(
    session: SessionDep, current_user: CurrentUser, media_id: uuid.UUID
) -> Any:
    media = crud.add_to_favorites(
        session=session, user_id=current_user.id, media_id=media_id
    )
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    return media


@router.delete("/{media_id}/favorites", response_model=Message)
def remove_favorite(
    session: SessionDep, current_user: CurrentUser, media_id: uuid.UUID
) -> Any:
    media = crud.remove_from_favorites(
        session=session, user_id=current_user.id, media_id=media_id
    )
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    return Message(message="Removed from favorites successfully")


@router.get("/{media_id}/tags", response_model=list[MediaTag])
def read_media_tags(session: SessionDep, media_id: uuid.UUID) -> Any:
    media = crud.get_media(session=session, media_id=media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    return crud.get_media_tags(session=session, media_id=media_id)


@router.post("/{media_id}/tags", response_model=MediaTag)
def create_media_tag(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    media_id: uuid.UUID,
    tag_in: MediaTagCreate,
) -> Any:
    media = crud.get_media(session=session, media_id=media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    if not _can_manage_media(current_user=current_user, media=media):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.create_media_tag(
        session=session,
        media_id=media_id,
        tag_name=tag_in.tag_name,
        confidence=tag_in.confidence,
    )


@router.post("/{media_id}/user-tags", response_model=Message)
def create_user_tag(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    media_id: uuid.UUID,
    tag_in: UserTagCreate,
) -> Any:
    media = crud.get_media(session=session, media_id=media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    crud.create_user_tag(
        session=session, media_id=media_id, tagged_user_id=tag_in.tagged_user_id
    )
    return Message(message="User tagged successfully")
