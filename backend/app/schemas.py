from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models import ContentType


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: str
    created_at: datetime


class ContentItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    item_type: ContentType
    text: str
    translation: str
    notes: str | None
    difficulty_level: int


class LearningItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content_item: ContentItemRead
    easiness_factor: float
    interval_days: int
    repetitions: int
    next_review_at: datetime
    last_reviewed_at: datetime | None


class ReviewSubmit(BaseModel):
    learning_item_id: int
    quality: int  # 0-5, SM-2 quality score
    response_time_ms: int | None = None
