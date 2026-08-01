from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

class RunCreate(BaseModel):
    goal: str = Field(..., example="Book a flight from BOM to DEL")
    task_id: Optional[uuid.UUID] = None
    constraints: Optional[Dict[str, Any]] = Field(default_factory=dict)
    mode: str = Field(default="live")
    max_steps: int = Field(default=40)

class ProposedActionResponse(BaseModel):
    type: str
    target_id: Optional[str] = None
    expected_effect: Optional[str] = None
    value: Optional[str] = None

class StepResponse(BaseModel):
    step_index: int
    node_name: str
    proposed_action: Optional[ProposedActionResponse] = None
    guardrail_decision: Optional[str] = None
    status: str
    latency_ms: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

class RunResponse(BaseModel):
    id: uuid.UUID
    goal: str
    status: str
    steps: List[StepResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class ApprovalRequestPayload(BaseModel):
    decision: str = Field(..., description="Must be 'approved' or 'rejected'")
    decided_by: str = Field(..., description="The ID or email of the approving Guardian")
