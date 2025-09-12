# Purpose: Centralized typed settings (keys, models, provider order, budget providers)
from pydantic_settings import BaseSettings  # For typed env configuration
from pydantic import Field  # For default/alias
from typing import List, Optional  # Typing helpers


class Settings(BaseSettings):
    # App
    env: str = Field(default="dev", alias="ENV")  # Environment name (dev/staging/prod)
    port: int = Field(default=8000, alias="PORT")  # HTTP port

    # Google Maps
    google_maps_key: Optional[str] = Field(default=None, alias="GOOGLE_MAPS_API_KEY")

    # LLM providers (Sprint 2)
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")

    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(
        default="claude-3-haiku-20240307", alias="ANTHROPIC_MODEL"
    )

    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-flash", alias="GEMINI_MODEL")

    llm_order_raw: str = Field(default="gemini,openai,anthropic", alias="LLM_ORDER")

    # Budget (Sprint 3): generic hotel pricing provider (RapidAPI / custom)
    hotel_api_key: Optional[str] = Field(
        default=None, alias="HOTEL_API_KEY"
    )  # e.g., RapidAPI key
    hotel_api_host: Optional[str] = Field(
        default=None, alias="HOTEL_API_HOST"
    )  # e.g., "skyscanner50.p.rapidapi.com"
    hotel_api_endpoint: Optional[str] = Field(
        default=None, alias="HOTEL_API_ENDPOINT"
    )  # Full endpoint URL if needed

    # Defaults for budgeting heuristics (used when provider not configured)
    default_food_per_day: float = Field(default=35.0, alias="DEFAULT_FOOD_PER_DAY")
    default_transport_per_day: float = Field(
        default=20.0, alias="DEFAULT_TRANSPORT_PER_DAY"
    )
    default_tickets_per_day: float = Field(
        default=25.0, alias="DEFAULT_TICKETS_PER_DAY"
    )
    default_misc_per_day: float = Field(default=15.0, alias="DEFAULT_MISC_PER_DAY")

    # Verifier thresholds
    min_rating: float = Field(
        default=3.9, alias="MIN_RATING"
    )  # Filter out low-rated POIs

    @property
    def llm_order(self) -> List[str]:
        # Split comma-separated provider names and normalize
        return [p.strip().lower() for p in self.llm_order_raw.split(",") if p.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
