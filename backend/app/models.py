import enum
from datetime import datetime

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ContentType(str, enum.Enum):
    VOCABULARY = "vocabulary"
    GRAMMAR = "grammar"


class GeneratedContentType(str, enum.Enum):
    DIALOGUE = "dialogue"
    EXERCISE = "exercise"
    STORY = "story"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    learning_items: Mapped[list["LearningItem"]] = relationship(back_populates="user")
    generated_contents: Mapped[list["GeneratedContent"]] = relationship(back_populates="user")


class Language(Base):
    """A language the platform teaches, e.g. Korean. Kept as its own table so the
    schema supports multiple languages per user without any other changes."""

    __tablename__ = "languages"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(8), unique=True)  # e.g. "ko", "en"
    name: Mapped[str] = mapped_column(String(64))

    content_items: Mapped[list["ContentItem"]] = relationship(back_populates="language")


class ContentItem(Base):
    """A single piece of learnable content: a vocabulary word or a grammar rule.
    This is the static/curated catalog - not tied to any one user."""

    __tablename__ = "content_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    language_id: Mapped[int] = mapped_column(ForeignKey("languages.id"))
    item_type: Mapped[ContentType] = mapped_column(Enum(ContentType, native_enum=False))
    text: Mapped[str] = mapped_column(String(255))  # the word or grammar pattern itself
    translation: Mapped[str] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty_level: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    language: Mapped["Language"] = relationship(back_populates="content_items")
    learning_items: Mapped[list["LearningItem"]] = relationship(back_populates="content_item")


class LearningItem(Base):
    """Tracks one user's progress on one piece of content. This is the heart of the
    spaced-repetition system (SM-2 style): every review updates easiness_factor,
    interval_days and repetitions, which together determine next_review_at."""

    __tablename__ = "learning_items"
    __table_args__ = (UniqueConstraint("user_id", "content_item_id", name="uq_user_content_item"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    content_item_id: Mapped[int] = mapped_column(ForeignKey("content_items.id"))

    # SM-2 algorithm state. easiness_factor starts at 2.5 and shrinks when the user
    # struggles, which shortens future intervals for items they find hard.
    easiness_factor: Mapped[float] = mapped_column(Float, default=2.5)
    interval_days: Mapped[int] = mapped_column(Integer, default=0)
    repetitions: Mapped[int] = mapped_column(Integer, default=0)

    next_review_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="learning_items")
    content_item: Mapped["ContentItem"] = relationship(back_populates="learning_items")
    review_logs: Mapped[list["ReviewLog"]] = relationship(back_populates="learning_item")


class ReviewLog(Base):
    """Immutable history of every review attempt. Kept separate from LearningItem
    (which only holds current state) so we retain full history for analytics and
    for recomputing scheduling logic if the algorithm changes later."""

    __tablename__ = "review_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    learning_item_id: Mapped[int] = mapped_column(ForeignKey("learning_items.id"))
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    quality: Mapped[int] = mapped_column(Integer)  # SM-2 quality score, 0-5
    was_correct: Mapped[bool] = mapped_column(default=False)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    learning_item: Mapped["LearningItem"] = relationship(back_populates="review_logs")


class GeneratedContent(Base):
    """An AI-generated dialogue/exercise/story produced for a specific user, targeted
    at their current weak points (see GeneratedContentTarget)."""

    __tablename__ = "generated_contents"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    language_id: Mapped[int] = mapped_column(ForeignKey("languages.id"))
    content_type: Mapped[GeneratedContentType] = mapped_column(Enum(GeneratedContentType, native_enum=False))
    generated_text: Mapped[str] = mapped_column(Text)
    prompt_context: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="generated_contents")
    targets: Mapped[list["GeneratedContentTarget"]] = relationship(back_populates="generated_content")


class GeneratedContentTarget(Base):
    """Association table recording which ContentItems (weak points) a given
    GeneratedContent was generated to help the user practice."""

    __tablename__ = "generated_content_targets"

    generated_content_id: Mapped[int] = mapped_column(
        ForeignKey("generated_contents.id"), primary_key=True
    )
    content_item_id: Mapped[int] = mapped_column(ForeignKey("content_items.id"), primary_key=True)

    generated_content: Mapped["GeneratedContent"] = relationship(back_populates="targets")
    content_item: Mapped["ContentItem"] = relationship()
