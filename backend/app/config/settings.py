from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "aboa"
    postgres_user: str = "aboa"
    postgres_password: str = "password"
    redis_url: str = "redis://redis:6379/0"
    
    browser_cdp_url: str = "http://browser:9222"
    browser_headless: bool = True
    browser_action_timeout_ms: int = 10000
    
    gemini_api_key: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
