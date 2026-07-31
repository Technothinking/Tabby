from fastapi import FastAPI, Depends
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "aboa"
    postgres_user: str = "aboa"
    postgres_password: str = "password"
    redis_url: str = "redis://redis:6379/0"

    class Config:
        env_file = ".env"

settings = Settings()

app = FastAPI(title="Autonomous Browser-Operating Agent (ABOA) API")

@app.get("/health")
async def health_check():
    # Phase 0 mock healthcheck (will implement actual ping soon) #TODO ping real DB/Redis
    return {"status": "ok", "db": "ok", "redis": "ok"}
