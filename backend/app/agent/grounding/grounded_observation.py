from pydantic import BaseModel

class GroundedObservation(BaseModel):
    dom_text: str
    # Later we will add fields for visual fallback like screenshot references etc.
    # screenshot_path: str | None = None
