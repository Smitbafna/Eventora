import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    Album,
    AlbumCreate,
    AlbumUpdate,
    Comment,
    CommentCreate,
    Event,
    EventCreate,
    EventUpdate,
    FaceDetection,
    FaceRecognition,
    Like,
    Media,
    MediaCreate,
    MediaUpdate,
    MediaTag,
    get_datetime_utc,
    Notification,
    User,
    UserCreate,
    UserTag,
    UserUpdate,
)


# ====== USER CRUD ======
def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


# Dummy hash to use for timing attack prevention when user is not found
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        verify_password(password, DUMMY_HASH)
        return None
    verified, updated_password_hash = verify_password(password, db_user.hashed_password)
    if not verified:
        return None
    if updated_password_hash:
        db_user.hashed_password = updated_password_hash
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    return db_user


# ====== EVENT CRUD ======
def create_event(*, session: Session, event_in: EventCreate, creator_id: uuid.UUID) -> Event:
    db_event = Event.model_validate(event_in, update={"creator_id": creator_id})
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event


def get_event(*, session: Session, event_id: uuid.UUID) -> Event | None:
    return session.get(Event, event_id)


def get_events(*, session: Session, skip: int = 0, limit: int = 100) -> list[Event]:
    statement = select(Event).offset(skip).limit(limit)
    return session.exec(statement).all()


def update_event(*, session: Session, db_event: Event, event_in: EventUpdate) -> Event:
    event_data = event_in.model_dump(exclude_unset=True)
    db_event.sqlmodel_update(event_data, update={"updated_at": get_datetime_utc()})
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event


def delete_event(*, session: Session, event_id: uuid.UUID) -> None:
    event = get_event(session=session, event_id=event_id)
    if event:
        session.delete(event)
        session.commit()


# ====== ALBUM CRUD ======
def create_album(*, session: Session, album_in: AlbumCreate) -> Album:
    db_album = Album.model_validate(album_in)
    session.add(db_album)
    session.commit()
    session.refresh(db_album)
    return db_album


def get_album(*, session: Session, album_id: uuid.UUID) -> Album | None:
    return session.get(Album, album_id)


def get_albums_by_event(*, session: Session, event_id: uuid.UUID) -> list[Album]:
    statement = select(Album).where(Album.event_id == event_id)
    return session.exec(statement).all()


def update_album(*, session: Session, db_album: Album, album_in: AlbumUpdate) -> Album:
    album_data = album_in.model_dump(exclude_unset=True)
    db_album.sqlmodel_update(album_data)
    session.add(db_album)
    session.commit()
    session.refresh(db_album)
    return db_album


def delete_album(*, session: Session, album_id: uuid.UUID) -> None:
    album = get_album(session=session, album_id=album_id)
    if album:
        session.delete(album)
        session.commit()


# ====== MEDIA CRUD ======
def create_media(*, session: Session, media_in: MediaCreate, uploader_id: uuid.UUID) -> Media:
    db_media = Media.model_validate(media_in, update={"uploader_id": uploader_id})
    session.add(db_media)
    session.commit()
    session.refresh(db_media)
    return db_media


def get_media(*, session: Session, media_id: uuid.UUID) -> Media | None:
    return session.get(Media, media_id)


def get_media_by_event(*, session: Session, event_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[Media]:
    statement = select(Media).where(Media.event_id == event_id).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_media_by_album(*, session: Session, album_id: uuid.UUID) -> list[Media]:
    statement = select(Media).where(Media.album_id == album_id)
    return session.exec(statement).all()


def update_media(*, session: Session, db_media: Media, media_in: MediaUpdate) -> Media:
    media_data = media_in.model_dump(exclude_unset=True)
    db_media.sqlmodel_update(media_data)
    session.add(db_media)
    session.commit()
    session.refresh(db_media)
    return db_media


def delete_media(*, session: Session, media_id: uuid.UUID) -> None:
    media = get_media(session=session, media_id=media_id)
    if media:
        session.delete(media)
        session.commit()


# ====== LIKE CRUD ======
def create_like(*, session: Session, user_id: uuid.UUID, media_id: uuid.UUID) -> Like:
    db_like = Like(user_id=user_id, media_id=media_id)
    session.add(db_like)
    session.commit()
    session.refresh(db_like)
    return db_like


def get_like(*, session: Session, user_id: uuid.UUID, media_id: uuid.UUID) -> Like | None:
    statement = select(Like).where(Like.user_id == user_id).where(Like.media_id == media_id)
    return session.exec(statement).first()


def delete_like(*, session: Session, user_id: uuid.UUID, media_id: uuid.UUID) -> None:
    like = get_like(session=session, user_id=user_id, media_id=media_id)
    if like:
        session.delete(like)
        session.commit()


# ====== COMMENT CRUD ======
def create_comment(*, session: Session, comment_in: CommentCreate, user_id: uuid.UUID) -> Comment:
    db_comment = Comment.model_validate(comment_in, update={"user_id": user_id})
    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    return db_comment


def get_comments_by_media(*, session: Session, media_id: uuid.UUID) -> list[Comment]:
    statement = select(Comment).where(Comment.media_id == media_id)
    return session.exec(statement).all()


# ====== TAG CRUD ======
def create_user_tag(*, session: Session, media_id: uuid.UUID, tagged_user_id: uuid.UUID) -> UserTag:
    db_tag = UserTag(media_id=media_id, tagged_user_id=tagged_user_id)
    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)
    return db_tag


def create_media_tag(*, session: Session, media_id: uuid.UUID, tag_name: str, confidence: float = 0.0) -> MediaTag:
    db_tag = MediaTag(media_id=media_id, tag_name=tag_name, confidence=confidence)
    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)
    return db_tag


def get_media_tags(*, session: Session, media_id: uuid.UUID) -> list[MediaTag]:
    statement = select(MediaTag).where(MediaTag.media_id == media_id)
    return session.exec(statement).all()


def get_media_by_tag(*, session: Session, tag_name: str) -> list[Media]:
    statement = select(Media).join(MediaTag).where(MediaTag.tag_name == tag_name)
    return session.exec(statement).all()


# ====== NOTIFICATION CRUD ======
def create_notification(*, session: Session, notification_in: dict[str, Any], user_id: uuid.UUID) -> Notification:
    db_notification = Notification(**notification_in, user_id=user_id)
    session.add(db_notification)
    session.commit()
    session.refresh(db_notification)
    return db_notification


def get_notifications(*, session: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[Notification]:
    statement = select(Notification).where(Notification.user_id == user_id).offset(skip).limit(limit)
    return session.exec(statement).all()


def mark_notification_as_read(*, session: Session, notification_id: uuid.UUID) -> Notification | None:
    notification = session.get(Notification, notification_id)
    if notification:
        notification.is_read = True
        session.add(notification)
        session.commit()
        session.refresh(notification)
    return notification


# ====== FACE RECOGNITION CRUD ======
def create_face_reference(*, session: Session, user_id: uuid.UUID, reference_image_path: str) -> FaceRecognition:
    db_face = FaceRecognition(user_id=user_id, reference_image_path=reference_image_path)
    session.add(db_face)
    session.commit()
    session.refresh(db_face)
    return db_face


def get_face_reference(*, session: Session, user_id: uuid.UUID) -> FaceRecognition | None:
    statement = select(FaceRecognition).where(FaceRecognition.user_id == user_id)
    return session.exec(statement).first()


def create_face_detection(*, session: Session, media_id: uuid.UUID, face_reference_id: uuid.UUID, confidence: float) -> FaceDetection:
    db_detection = FaceDetection(media_id=media_id, face_reference_id=face_reference_id, confidence=confidence)
    session.add(db_detection)
    session.commit()
    session.refresh(db_detection)
    return db_detection


def get_face_detections(*, session: Session, face_reference_id: uuid.UUID) -> list[FaceDetection]:
    statement = select(FaceDetection).where(FaceDetection.face_reference_id == face_reference_id)
    return session.exec(statement).all()


# ====== FAVORITE CRUD ======
def add_to_favorites(*, session: Session, user_id: uuid.UUID, media_id: uuid.UUID) -> Media | None:
    media = get_media(session=session, media_id=media_id)
    if media and user_id not in [u.id for u in media.favorited_by]:
        user = session.get(User, user_id)
        if user:
            media.favorited_by.append(user)
            session.add(media)
            session.commit()
            session.refresh(media)
    return media


def remove_from_favorites(*, session: Session, user_id: uuid.UUID, media_id: uuid.UUID) -> Media | None:
    media = get_media(session=session, media_id=media_id)
    if media:
        user = session.get(User, user_id)
        if user and user in media.favorited_by:
            media.favorited_by.remove(user)
            session.add(media)
            session.commit()
            session.refresh(media)
    return media
