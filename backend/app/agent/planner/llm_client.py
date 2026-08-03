from google import genai
from google.genai import types
from google.genai.errors import ClientError
from app.browser.actions import ProposedAction
from app.config.settings import settings
import json
from tenacity import retry, retry_if_exception_type, wait_exponential_jitter, stop_after_attempt

def is_rate_limit(exception):
    return isinstance(exception, ClientError) and exception.code == 429

class LLMClient:
    def __init__(self, model_name: str = "gemini-flash-latest"):
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is missing from environment variables.")
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = model_name
    
    @retry(
        retry=retry_if_exception_type(ClientError),
        wait=wait_exponential_jitter(initial=5, max=60),
        stop=stop_after_attempt(5)
    )
    async def propose_action(self, system_prompt: str, user_prompt: str) -> ProposedAction:
        try:
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
            return response.parsed
        except ClientError as e:
            if e.code == 429:
                print(f"Rate limited (429) detected! Sleeping via Tenacity... Details: {str(e)}")
            raise e

class FakeLLMClient:
    def __init__(self, predefined_actions: list[ProposedAction]):
        self.actions = predefined_actions
        self.call_count = 0
        
    async def propose_action(self, system_prompt: str, user_prompt: str) -> ProposedAction:
        action = self.actions[self.call_count % len(self.actions)]
        self.call_count += 1
        return action
