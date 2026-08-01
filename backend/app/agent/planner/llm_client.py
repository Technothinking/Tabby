from google import genai
from google.genai import types
from app.browser.actions import ProposedAction
from app.config.settings import settings
import json

class LLMClient:
    def __init__(self):
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is missing from environment variables.")
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = "gemini-2.5-flash"
    
    async def propose_action(self, system_prompt: str, user_prompt: str) -> ProposedAction:
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=ProposedAction,
                temperature=0.0
            ),
        )
        # response.parsed returns the parsed Pydantic object when response_schema is provided!
        return response.parsed

class FakeLLMClient:
    def __init__(self, predefined_actions: list[ProposedAction]):
        self.actions = predefined_actions
        self.call_count = 0
        
    async def propose_action(self, system_prompt: str, user_prompt: str) -> ProposedAction:
        action = self.actions[self.call_count % len(self.actions)]
        self.call_count += 1
        return action
