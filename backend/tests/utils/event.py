from sqlmodel import Session

from app import crud
from app.models import EventCreate
from tests.utils.user import create_random_user
from tests.utils.utils import random_lower_string


def create_random_event(db: Session):
    user = create_random_user(db)
    event_in = EventCreate(
        name=random_lower_string(),
        description=random_lower_string(),
        category="test",
    )
    return crud.create_event(session=db, event_in=event_in, creator_id=user.id)
