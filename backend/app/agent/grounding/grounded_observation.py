from typing import Optional
from pydantic import BaseModel

class GroundedObservation(BaseModel):
    dom_text: str
    screenshot_b64: Optional[str] = None
