from google import genai
from google.genai import types
from app.config.settings import settings

class VLMGrounder:
    @staticmethod
    async def resolve_target(screenshot_b64: str, goal: str, observation_text: str) -> str:
        """
        Takes an annotated Set-Of-Marks screenshot and the agent's goal,
        and uses the Vision Language Model to pinpoint the numeric ID of the target element.
        Returns the data-aboa-id e.g. "el_5".
        """
        client = genai.Client(api_key=settings.gemini_api_key)
        
        prompt = f"""
        You are a Visual GUI Agent working on a browser.
        The current goal is: "{goal}"
        
        The image provided is a screenshot of the browser viewport.
        Interactive elements have been outlined with red bounding boxes and labeled with numbers.
        
        Here is the textual DOM representation for context:
        {observation_text}
        
        Identify the single most appropriate element to interact with next to accomplish the goal.
        You MUST return ONLY the integer number of the label. Do not include any explanations, JSON, or additional text.
        For example, if the best element is labeled "12", just return "12".
        """
        
        # In the new google-genai SDK, Part can be constructed from a base64 string
        # by passing the correct mime_type and the raw decoded bytes, or formatting the payload.
        # Alternatively, we can pass it as a dict matching structure, or create a Part object.
        import base64
        image_bytes = base64.b64decode(screenshot_b64)
        
        response = await client.aio.models.generate_content(
            model="gemini-flash-latest",
            contents=[prompt, types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")],
            config=types.GenerateContentConfig(
                temperature=0.0
            ) 
        )
        
        output = response.text.strip()
        print(f"RAW VLM RESPONSE: {output}")
        # Clean up any non-numeric output just in case
        import re
        matches = re.findall(r'\d+', output)
        if matches:
            return f"el_{matches[0]}"
        return ""
