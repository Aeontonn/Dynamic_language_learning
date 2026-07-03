from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ContentItem, LearningItem, ReviewLog, User
from app.schemas import LearningItemRead, ReviewSubmit
from app.spaced_repetition import apply_review

router = APIRouter(tags=["learning"])


@router.post("/users/{user_id}/learning-items/{content_item_id}", response_model=LearningItemRead, status_code=201)
def enroll_content_item(user_id: int, content_item_id: int, db: Session = Depends(get_db)) -> LearningItem:
    """Start tracking a piece of content (word/grammar rule) for a user."""
    if db.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db.get(ContentItem, content_item_id) is None:
        raise HTTPException(status_code=404, detail="Content item not found")

    existing = db.scalar(
        select(LearningItem).where(
            LearningItem.user_id == user_id, LearningItem.content_item_id == content_item_id
        )
    )
    if existing is not None:
        return existing

    item = LearningItem(user_id=user_id, content_item_id=content_item_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/users/{user_id}/due", response_model=list[LearningItemRead])
def get_due_items(user_id: int, db: Session = Depends(get_db)) -> list[LearningItem]:
    """Return everything the user should practice right now, i.e. items whose
    next_review_at has already passed, soonest-due first."""
    if db.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")

    return list(
        db.scalars(
            select(LearningItem)
            .where(LearningItem.user_id == user_id, LearningItem.next_review_at <= datetime.now(timezone.utc))
            .order_by(LearningItem.next_review_at)
        )
    )


@router.post("/reviews", response_model=LearningItemRead)
def submit_review(payload: ReviewSubmit, db: Session = Depends(get_db)) -> LearningItem:
    """Record the outcome of a review attempt and reschedule the item via SM-2."""
    item = db.get(LearningItem, payload.learning_item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Learning item not found")
    if not 0 <= payload.quality <= 5:
        raise HTTPException(status_code=422, detail="quality must be between 0 and 5")

    db.add(
        ReviewLog(
            learning_item_id=item.id,
            quality=payload.quality,
            was_correct=payload.quality >= 3,
            response_time_ms=payload.response_time_ms,
        )
    )
    apply_review(item, payload.quality)
    db.commit()
    db.refresh(item)
    return item
