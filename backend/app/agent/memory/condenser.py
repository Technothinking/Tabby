from pydantic import BaseModel
from typing import List, Literal, Optional
from app.agent.state import AgentState
from app.config.settings import settings
from google.genai import types
from google import genai
from google.genai.errors import ClientError
import json
from tenacity import retry, retry_if_exception_type, wait_exponential_jitter, stop_after_attempt

class Strategy(BaseModel):
    entry_point: str
    key_steps: List[str]
    pitfalls: List[str]
    avg_steps: int

class TraceSummaryOut(BaseModel):
    domain: str
    goal_category: str
    strategy_json: Strategy
    outcome: Literal["success", "partial", "failure"]

class TraceCondenser:
    @staticmethod
    @retry(
        retry=retry_if_exception_type(ClientError),
        wait=wait_exponential_jitter(initial=5, max=60),
        stop=stop_after_attempt(5)
    )
    async def condense(state: AgentState) -> TraceSummaryOut:
        client = genai.Client(api_key=settings.gemini_api_key)
        
        goal = state.get("goal")
        history = []
        for a in state.get("action_history", []):
            if "proposed_action" in a and a["proposed_action"]:
                history.append((a["proposed_action"].type, a["proposed_action"].target_id, a["proposed_action"].rationale, a.get("result_status", False)))
                
        status = state.get("status")
        
        prompt = f"""
We just executed a web browser agent run.
GOAL: {goal}
OUTCOME STATUS: {status}
ACTION HISTORY:
{json.dumps(history, indent=2)}

Please condense this into a structured TraceSummary indicating the overarching strategy, the core steps taken, any pitfalls, and the domain.
        """
        
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=TraceSummaryOut,
                temperature=0.0
            ) 
        )
        return TraceSummaryOut.model_validate_json(response.text)
