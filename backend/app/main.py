from fastapi import FastAPI

from app.routers import learning, users

app = FastAPI(title="Dynamic Language Learning Platform")

app.include_router(users.router)
app.include_router(learning.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
