from google import genai
from fastapi import FastAPI
from ...core.config import Settings, get_settings
from ...core.logging import get_logger


logger = get_logger()

class GeminiClient:
    def __init__(self, settings : Settings) -> None:
        self.gemini_api_key = settings.gemini_api_key
        self.gemini_model = settings.gemini_model
        
        self.client = genai.Client(api_key=self.gemini_api_key )

    async def generate_response(self, message, schema=None):
            try:
                response = self.client.models.generate_content(
                model=self.gemini_model,
                contents=message,
                config = schema if schema else None
                )
                return response
            except Exception as e:
                logger.error("Exception Occurred in Gemini Response %s",e)
    

def initialise_gemini(app: FastAPI):
    settings = get_settings()
    gemini_client = GeminiClient(settings)
    app.state.gemini_client = gemini_client