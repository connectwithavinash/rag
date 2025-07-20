from openai import AzureOpenAI
from fastapi import FastAPI
from ...core.config import Settings, get_settings
from ...core.logging import get_logger


logger = get_logger()

class AzureOpenAIClient:
    def __init__(self, settings : Settings) -> None:
        self.azure_openai_api_key = settings.azure_openai_api_key
        self.azure_openai_endpoint = settings.azure_openai_endpoint
        self.azure_openai_model = settings.azure_openai_model
        
        self.client = AzureOpenAI(
            api_key=self.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=self.azure_openai_endpoint
        )

    async def generate_response(self, message, schema=None):
            try:
                response = self.client.completions.create(
                model=self.azure_openai_model,
                prompt=message
                )
                return response
            except Exception as e:
                logger.error("Exception Occurred in AzureOpenAI Response %s",e)
    

def initialise_azure_openai(app: FastAPI):
    settings = get_settings()
    azure_openai_client = AzureOpenAIClient(settings)
    app.state.azure_openai_client = azure_openai_client