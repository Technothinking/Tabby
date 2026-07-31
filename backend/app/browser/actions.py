from enum import Enum
from pydantic import BaseModel
from playwright.async_api import Page
from typing import Any
from app.config.settings import settings

class ActionType(str, Enum):
    CLICK = "click"
    TYPE = "type"
    SELECT = "select"
    SCROLL = "scroll"
    NAVIGATE = "navigate"
    WAIT = "wait"
    EXTRACT = "extract"
    HOVER = "hover"
    PRESS_KEY = "press_key"
    SCREENSHOT = "screenshot"
    ASK_HUMAN = "ask_human"
    FINISH = "finish"

class ProposedAction(BaseModel):
    type: ActionType
    target_id: str | None = None
    value: str | None = None
    expected_effect: str | None = None
    rationale: str | None = None
    confidence: str | None = None

class ActionResult(BaseModel):
    success: bool
    message: str | None = None
    data: Any | None = None

class ActionDispatcher:
    @staticmethod
    async def execute(page: Page, action: ProposedAction) -> ActionResult:
        timeout = settings.browser_action_timeout_ms
        try:
            if action.type == ActionType.NAVIGATE:
                await page.goto(action.value or "", timeout=timeout)
                await page.wait_for_load_state("networkidle", timeout=timeout)
                return ActionResult(success=True, message=f"Navigated to {action.value}")
            
            elif action.type == ActionType.CLICK:
                locator = page.locator(f"[{action.target_id}]") if action.target_id and "=" in action.target_id else page.locator(action.target_id) # Simplify for phase 1 mock testing
                await locator.click(timeout=timeout)
                return ActionResult(success=True, message=f"Clicked {action.target_id}")

            elif action.type == ActionType.TYPE:
                locator = page.locator(f"[{action.target_id}]") if action.target_id and "=" in action.target_id else page.locator(action.target_id)
                await locator.fill(action.value or "", timeout=timeout)
                return ActionResult(success=True, message=f"Typed in {action.target_id}")
                
            elif action.type == ActionType.SCROLL:
                await page.mouse.wheel(0, 500)
                return ActionResult(success=True, message="Scrolled down")
                
            elif action.type == ActionType.SCREENSHOT:
                screenshot_bytes = await page.screenshot(full_page=True, timeout=timeout)
                return ActionResult(success=True, message="Screenshot taken", data=screenshot_bytes)
                
            else:
                return ActionResult(success=False, message=f"Action {action.type} not implemented for Phase 1")
        except Exception as e:
            return ActionResult(success=False, message=str(e))
