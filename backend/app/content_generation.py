from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ContentItem, GeneratedContentType, Language, LearningItem


def get_weak_content_items(
    db: Session, user_id: int, language_id: int, limit: int = 5
) -> list[ContentItem]:
    """Return the user's weakest ContentItems for a language, i.e. the ones with
    the lowest SM-2 easiness_factor - the items they consistently find hardest."""
    rows = db.scalars(
        select(ContentItem)
        .join(LearningItem, LearningItem.content_item_id == ContentItem.id)
        .where(LearningItem.user_id == user_id, ContentItem.language_id == language_id)
        .order_by(LearningItem.easiness_factor)
        .limit(limit)
    )
    return list(rows)


def build_prompt(
    content_items: list[ContentItem], language: Language, content_type: GeneratedContentType
) -> str:
    words = ", ".join(f"{item.text} ({item.translation})" for item in content_items)
    kind = {
        GeneratedContentType.DIALOGUE: "a short beginner-friendly dialogue between two speakers",
        GeneratedContentType.EXERCISE: "a short fill-in-the-blank exercise",
        GeneratedContentType.STORY: "a short beginner-friendly story",
    }[content_type]

    return (
        f"Write {kind} in {language.name}. "
        f"Naturally incorporate these words/grammar points the learner is struggling with: {words}. "
        "Keep the language simple and appropriate for a beginner. "
        "After the text, add a line-by-line English translation."
    )
