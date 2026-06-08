import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import EmailStr
from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


# ====== ENUMS ======
class UserRole(str, Enum):
    ADMIN = "admin"
    PHOTOGRAPHER = "photographer"
    CLUB_MEMBER = "club_member"
    VIEWER = "viewer"


class MediaType(str, Enum):
    PHOTO = "photo"
    VIDEO = "video"


class AccessLevel(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"


class NotificationType(str, Enum):
    LIKE = "like"
    COMMENT = "comment"
    TAG = "tag"


# ====== USER MODELS ======
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    full_name: str | None = Field(default=None, max_length=255)
    role: UserRole = UserRole.VIEWER


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)
    role: UserRole | None = None


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class MediaFavorite(SQLModel, table=True):
    media_id: uuid.UUID = Field(foreign_key="media.id", primary_key=True, ondelete="CASCADE")
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True, ondelete="CASCADE")


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    # Relationships
    events: list["Event"] = Relationship(back_populates="creator", cascade_delete=True)
    media: list["Media"] = Relationship(back_populates="uploader", cascade_delete=True)
    likes: list["Like"] = Relationship(back_populates="user", cascade_delete=True)
    comments: list["Comment"] = Relationship(back_populates="user", cascade_delete=True)
    notifications: list["Notification"] = Relationship(back_populates="user", cascade_delete=True)
    face_reference: Optional["FaceRecognition"] = Relationship(back_populates="user",cascade_delete=True)
    favorite_media: list["Media"] = Relationship(back_populates="favorited_by", link_model=MediaFavorite)


class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# ====== EVENT MODELS ======
class EventBase(SQLModel):
    name: str = Field(min_length=1, max_length=255, index=True)
    description: str | None = Field(default=None, max_length=1000)
    category: str | None = Field(default=None, max_length=255)
    event_date: datetime | None = None


class EventCreate(EventBase):
    pass


class EventUpdate(EventBase):
    name: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


class Event(EventBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    creator_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    creator: User = Relationship(back_populates="events")
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    # Relationships
    albums: list["Album"] = Relationship(back_populates="event", cascade_delete=True)
    media: list["Media"] = Relationship(back_populates="event", cascade_delete=True)


class EventPublic(EventBase):
    id: uuid.UUID
    creator_id: uuid.UUID
    created_at: datetime | None = None


class EventsPublic(SQLModel):
    data: list[EventPublic]
    count: int


# ====== ALBUM MODELS ======
class AlbumBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)


class AlbumCreate(AlbumBase):
    event_id: uuid.UUID


class AlbumUpdate(AlbumBase):
    name: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


class Album(AlbumBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    event_id: uuid.UUID = Field(foreign_key="event.id", nullable=False, ondelete="CASCADE")
    event: Event = Relationship(back_populates="albums")
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    # Relationships
    media: list["Media"] = Relationship(back_populates="album", cascade_delete=True)


class AlbumPublic(AlbumBase):
    id: uuid.UUID
    event_id: uuid.UUID
    created_at: datetime | None = None


class AlbumsPublic(SQLModel):
    data: list[AlbumPublic]
    count: int


# ====== MEDIA MODELS ======
class MediaBase(SQLModel):
    filename: str = Field(max_length=500)
    media_type: MediaType
    access_level: AccessLevel = AccessLevel.PRIVATE
    file_size: int = 0
    file_path: str | None = Field(default=None, max_length=1000)


class MediaCreate(MediaBase):
    event_id: uuid.UUID
    album_id: uuid.UUID | None = None


class MediaUpdate(SQLModel):
    access_level: AccessLevel | None = None


class Media(MediaBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    uploader_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    uploader: User = Relationship(back_populates="media")
    event_id: uuid.UUID = Field(foreign_key="event.id", nullable=False, ondelete="CASCADE")
    event: Event = Relationship(back_populates="media")
    album_id: uuid.UUID | None = Field(foreign_key="album.id", default=None, ondelete="CASCADE")
    album: Optional["Album"] = Relationship(back_populates="media")
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    # Relationships
    likes: list["Like"] = Relationship(back_populates="media", cascade_delete=True)
    comments: list["Comment"] = Relationship(back_populates="media", cascade_delete=True)
    tags: list["MediaTag"] = Relationship(back_populates="media", cascade_delete=True)
    user_tags: list["UserTag"] = Relationship(back_populates="media", cascade_delete=True)
    favorited_by: list[User] = Relationship(back_populates="favorite_media", link_model=MediaFavorite)
    face_detections: list["FaceDetection"] = Relationship(back_populates="media", cascade_delete=True)


class MediaPublic(MediaBase):
    id: uuid.UUID
    uploader_id: uuid.UUID
    event_id: uuid.UUID
    album_id: uuid.UUID | None = None
    created_at: datetime | None = None


class MediasPublic(SQLModel):
    data: list[MediaPublic]
    count: int


# ====== SOCIAL INTERACTION MODELS ======
class Like(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    user: User = Relationship(back_populates="likes")
    media_id: uuid.UUID = Field(foreign_key="media.id", nullable=False, ondelete="CASCADE")
    media: Media = Relationship(back_populates="likes")
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class CommentBase(SQLModel):
    text: str = Field(min_length=1, max_length=1000)


class CommentCreate(CommentBase):
    media_id: uuid.UUID


class Comment(CommentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    user: User = Relationship(back_populates="comments")
    media_id: uuid.UUID = Field(foreign_key="media.id", nullable=False, ondelete="CASCADE")
    media: Media = Relationship(back_populates="comments")
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class UserTag(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tagged_user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    tagged_user: User = Relationship()
    media_id: uuid.UUID = Field(foreign_key="media.id", nullable=False, ondelete="CASCADE")
    media: Media = Relationship(back_populates="user_tags")
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


# ====== AI/ML MODELS ======
class MediaTag(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tag_name: str = Field(max_length=255, index=True)
    confidence: float = 0.0
    media_id: uuid.UUID = Field(foreign_key="media.id", nullable=False, ondelete="CASCADE")
    media: Media = Relationship(back_populates="tags")
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class FaceRecognition(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE", unique=True)
    user: User = Relationship(back_populates="face_reference")
    reference_image_path: str = Field(max_length=1000)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    detections: list["FaceDetection"] = Relationship(back_populates="reference", cascade_delete=True)


class FaceDetection(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    media_id: uuid.UUID = Field(foreign_key="media.id", nullable=False, ondelete="CASCADE")
    media: Media = Relationship(back_populates="face_detections")
    face_reference_id: uuid.UUID = Field(foreign_key="facerecognition.id", nullable=False, ondelete="CASCADE")
    reference: FaceRecognition = Relationship(back_populates="detections")
    confidence: float = 0.0
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


# ====== NOTIFICATION MODEL ======
class NotificationBase(SQLModel):
    type: NotificationType
    message: str = Field(max_length=500)


class Notification(NotificationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    user: User = Relationship(back_populates="notifications")
    is_read: bool = False
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class NotificationPublic(NotificationBase):
    id: uuid.UUID
    user_id: uuid.UUID
    is_read: bool
    created_at: datetime | None = None


# ====== GENERIC MODELS ======
class Message(SQLModel):
    message: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
