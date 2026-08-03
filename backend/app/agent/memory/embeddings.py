from google import genai
from app.config.settings import settings

class Embedder:
    @staticmethod
    async def embed_trace(trace: dict) -> list[float]:
        text = f"{trace.get('goal_category', '')}: {trace.get('domain', '')} - Strategy: {trace.get('strategy_json', {})}"
        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text
        )
        return response.embeddings[0].values
    
    @staticmethod
    async def embed_query(goal: str, domain_hint: str) -> list[float]:
        text = f"Goal: {goal} | Domain: {domain_hint}"
        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text
        )
        return response.embeddings[0].values
