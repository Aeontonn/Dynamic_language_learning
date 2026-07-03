from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.content_generation import build_prompt, get_weak_content_items
from app.database import get_db
from app.llm_client import LLMClient, get_llm_client
from app.models import GeneratedContent, GeneratedContentTarget, Language, User
from app.schemas import GenerateContentRequest, GeneratedContentRead

router = APIRouter(tags=["generation"])


@router.post("/users/{user_id}/generate", response_model=GeneratedContentRead)
def generate_content(
    user_id: int,
    payload: GenerateContentRequest,
    db: Session = Depends(get_db),
    llm: LLMClient = Depends(get_llm_client),
) -> GeneratedContentRead:
    if db.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")

    language = db.get(Language, payload.language_id)
    if language is None:
        raise HTTPException(status_code=404, detail="Language not found")

    weak_items = get_weak_content_items(db, user_id, payload.language_id)
    if not weak_items:
        raise HTTPException(
            status_code=400,
            detail="User has no learning items in this language yet - nothing to target",
        )

    prompt = build_prompt(weak_items, language, payload.content_type)

    try:
        generated_text = llm.generate(prompt)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM generation failed: {exc}") from exc

    content = GeneratedContent(
        user_id=user_id,
        language_id=payload.language_id,
        content_type=payload.content_type,
        generated_text=generated_text,
    )
    content.targets = [GeneratedContentTarget(content_item_id=item.id) for item in weak_items]
    db.add(content)
    db.commit()
    db.refresh(content)

    return GeneratedContentRead.from_orm_with_targets(content)
