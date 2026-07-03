from datetime import datetime, timedelta, timezone

from app.models import LearningItem

MIN_EASINESS_FACTOR = 1.3


def apply_review(item: LearningItem, quality: int) -> None:
    """Update a LearningItem's SM-2 state in place based on a review's quality score.

    quality is 0-5: 0-2 means the user got it wrong, 3-5 means they got it right
    (3 = correct but hard, 5 = correct and easy).
    """
    now = datetime.now(timezone.utc)

    if quality < 3:
        # A wrong answer resets the streak - review again tomorrow regardless of
        # how well-established this item was before.
        item.repetitions = 0
        item.interval_days = 1
    else:
        if item.repetitions == 0:
            item.interval_days = 1
        elif item.repetitions == 1:
            item.interval_days = 6
        else:
            item.interval_days = round(item.interval_days * item.easiness_factor)
        item.repetitions += 1

    item.easiness_factor = max(
        MIN_EASINESS_FACTOR,
        item.easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)),
    )

    item.last_reviewed_at = now
    item.next_review_at = now + timedelta(days=item.interval_days)
