from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "aboa"
    postgres_user: str = "aboa"
    postgres_password: str = "password"
    
    browser_cdp_url: str = "http://browser:9222"
    browser_headless: bool = True
    browser_action_timeout_ms: int = 10000
    
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    database_url: str = Field(default="postgresql+asyncpg://aboa:password@postgres:5432/aboa", env="DATABASE_URL")
    redis_url: str = Field(default="redis://redis:6379/0", env="REDIS_URL")

    class Config:
        env_file = ".env"

settings = Settings()
