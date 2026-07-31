from fastapi import FastAPI, Depends, Request
from fastapi.responses import Response
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from app.browser.actions import ProposedAction, ActionDispatcher
from app.browser.driver import BrowserDriver
from app.agent.grounding.dom_extractor import DOMExtractor

class ObserveRequest(BaseModel):
    url: str

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

@app.post("/debug/execute-action")
async def execute_action(action: ProposedAction):
    driver = BrowserDriver()
    try:
        context = await driver.new_context()
        page = await context.new_page()
        # For simplicity in debug endpoint, if it's not a navigate action and we're not on a page yet,
        # fail or assume the caller knows what they are doing. 
        result = await ActionDispatcher.execute(page, action)
        if result.success and action.type.value == "screenshot" and result.data:
            return Response(content=result.data, media_type="image/png")
        return {"success": result.success, "message": result.message}
    finally:
        await driver.close()

@app.post("/debug/observe")
async def observe_page(req: ObserveRequest):
    driver = BrowserDriver()
    try:
        context = await driver.new_context()
        page = await context.new_page()
        await page.goto(req.url, wait_until="networkidle")
        observation = await DOMExtractor.extract(page)
        return {"success": True, "dom_text": observation.dom_text}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        await driver.close()
