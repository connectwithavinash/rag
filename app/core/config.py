from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    app_name : Optional[str] = None
    api_key : Optional[str] = None
    base_url: Optional[str] = None
    mongo_host : str
    mongo_username : str
    mongo_password : str
    mongo_database : str
    gemini_api_key : str
    gemini_model : str
    gemini_rate_limit: int = 5
    qdrant_url: str = "http://localhost:6333"
    mongo_host_local : str
    mongo_username_local: str
    mongo_password_local: str
    qdrant_sparse_model : str
    qdrant_dense_model : str
    azure_openai_api_key : str
    azure_openai_endpoint : str
    azure_openai_model : str
    azure_openai_api_version : str

    #reading environmental variables from .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

@lru_cache
def get_settings():
    return Settings()