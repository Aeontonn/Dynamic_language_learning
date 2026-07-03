from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import generation, learning, users

app = FastAPI(title="Dynamic Language Learning Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(learning.router)
app.include_router(generation.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
