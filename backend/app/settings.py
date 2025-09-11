# Purpose: Provide typed settings for the whole backend (models, keys, model names, and provider order)
from pydantic_settings import BaseSettings  # Import BaseSettings to declare typed env config
from pydantic import Field                  # Import Field for defaults and validation helpers
from typing import List                      # Import List type for LLM order parsing


class Settings(BaseSettings):  # Define a Settings class that reads from env and .env files
    env: str = Field(default="dev", alias="ENV")  # Environment name (e.g., dev, prod)
    port: int = Field(default=8000, alias="PORT") # Port for running the server

    google_maps_key: str | None = Field(default=None, alias="GOOGLE_MAPS_API_KEY")  # Google Maps API key (optional for local tests)

    # OpenAI credentials and model selection
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")  # OpenAI API key (optional)
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")     # Default OpenAI model

    # Anthropic credentials and model selection
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")  # Anthropic API key (optional)
    anthropic_model: str = Field(default="claude-3-haiku-20240307", alias="ANTHROPIC_MODEL")  # Default Anthropic model

    # Google Gemini credentials and model selection
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")  # Gemini API key (optional)
    gemini_model: str = Field(default="gemini-1.5-flash", alias="GEMINI_MODEL")  # Default Gemini model

    # Provider priority list (router will try in this order and fallback)
    llm_order_raw: str = Field(default="gemini,openai,anthropic", alias="LLM_ORDER")  # Comma-separated provider names

    @property
    def llm_order(self) -> List[str]:  # Expose provider order as a list
        return [p.strip().lower() for p in self.llm_order_raw.split(",") if p.strip()]  # Split, trim, and lowercase items

    class Config:  # Configuration for BaseSettings
        env_file = ".env"       # Enable loading from .env file by default
        env_file_encoding = "utf-8"  # Use UTF-8 encoding to avoid issues
