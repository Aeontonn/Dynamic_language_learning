# Dynamic Language Learning Platform

An AI-driven language learning web app (starting with Korean) that generates
dynamic content tailored to each user's weak points, instead of static
flashcards.

**Stack:** FastAPI (Python) + PostgreSQL + React/TypeScript.

## Step 1: Database schema

The schema lives in [`backend/app/models.py`](backend/app/models.py) and is
managed with Alembic migrations in `backend/alembic/versions/`.

```
Language ──< ContentItem ──< LearningItem >── User
                  │                │
                  │                └──< ReviewLog
                  │
                  └──< GeneratedContentTarget >── GeneratedContent >── User
```

- **User** — account.
- **Language** — a language taught on the platform (e.g. Korean), so the
  schema supports adding more languages later without changes.
- **ContentItem** — the static catalog of vocabulary words / grammar rules.
- **LearningItem** — one user's progress on one `ContentItem`. Holds the
  SM-2 spaced-repetition state (`easiness_factor`, `interval_days`,
  `repetitions`, `next_review_at`). This is what "what should the user
  practice today" queries against.
- **ReviewLog** — immutable history of every review attempt, kept separate
  from `LearningItem` (current state) so history survives even if the
  scheduling algorithm changes later.
- **GeneratedContent** / **GeneratedContentTarget** — AI-generated
  dialogues/exercises for a user, linked to the specific `ContentItem`s
  (weak points) they were generated to help practice.

### Running it locally

```bash
docker compose up -d          # starts Postgres on localhost:5432
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # adjust DATABASE_URL if needed
alembic upgrade head          # applies the initial schema
```
