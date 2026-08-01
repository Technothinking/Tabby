from enum import Enum
from pydantic import BaseModel
from playwright.async_api import Page
from typing import Any, Literal
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
    confidence: Literal["low", "medium", "high"] = "high"
    fallback_note: str | None = None

class ActionResult(BaseModel):
    success: bool
    message: str | None = None
    data: Any | None = None

class ActionDispatcher:
    @staticmethod
    async def execute(page: Page, action: ProposedAction) -> ActionResult:
        timeout = settings.browser_action_timeout_ms
        
        # If the planner proposes "el_2", we convert it to the grounding selector
        target_selector = f"[data-aboa-id='{action.target_id}']" if action.target_id else None
        
        try:
            if action.type == ActionType.NAVIGATE:
                await page.goto(action.value or "", timeout=timeout)
                await page.wait_for_load_state("networkidle", timeout=timeout)
                return ActionResult(success=True, message=f"Navigated to {action.value}")
            
            elif action.type == ActionType.CLICK:
                if not target_selector:
                    return ActionResult(success=False, message="Click requires a target_id")
                await page.locator(target_selector).click(timeout=timeout)
                return ActionResult(success=True, message=f"Clicked {target_selector}")

            elif action.type == ActionType.TYPE:
                if not target_selector or not action.value:
                    return ActionResult(success=False, message="Type requires target_id and value")
                await page.locator(target_selector).fill(action.value, timeout=timeout)
                return ActionResult(success=True, message=f"Typed into {target_selector}")
                
            elif action.type == ActionType.SCROLL:
                await page.mouse.wheel(0, 500)
                return ActionResult(success=True, message="Scrolled down")
                
            elif action.type == ActionType.SCREENSHOT:
                screenshot_bytes = await page.screenshot(full_page=True, timeout=timeout)
                return ActionResult(success=True, message="Screenshot taken", data=screenshot_bytes)
                
            elif action.type == ActionType.FINISH:
                return ActionResult(success=True, message="Task explicitly finished by LLM")
                
            else:
                return ActionResult(success=False, message=f"Action {action.type} not implemented for Phase 1")
        except Exception as e:
            return ActionResult(success=False, message=str(e))
