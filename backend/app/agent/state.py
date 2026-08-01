from typing import TypedDict, Literal, List, Optional
from app.browser.actions import ProposedAction
from app.agent.grounding.grounded_observation import GroundedObservation

class ExecutedAction(TypedDict):
    proposed_action: ProposedAction
    result_status: bool
    result_message: str

class VerificationResult(TypedDict):
    success: bool
    reason: str

class AgentState(TypedDict):
    run_id: str
    goal: str
    constraints: dict
    memory_hints: List[str] # Simplified for now
    observation: Optional[GroundedObservation]
    action_history: List[ExecutedAction]
    proposed_action: Optional[ProposedAction]
    guardrail_decision: Optional[Literal["ALLOW", "DENY", "REQUIRE_HUMAN_APPROVAL"]]
    last_verification: Optional[VerificationResult]
    retry_count: int
    step_index: int
    status: Literal["running", "awaiting_approval", "completed", "failed", "aborted"]
    finish_reason: Optional[str]
