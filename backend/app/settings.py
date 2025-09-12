# Purpose: Centralized typed settings (all envs used across the app)
from pydantic_settings import BaseSettings                           # Typed env loader
from pydantic import Field                                            # Defaults & aliases
from typing import List, Optional                                     # Typing


class Settings(BaseSettings):
    # --- App ---
    env: str = Field(default="dev", alias="ENV")                      # Environment name
    port: int = Field(default=8000, alias="PORT")                     # HTTP port

    # --- Database ---
    database_url: str = Field(                                        # Async SQLite by default
        default="sqlite+aiosqlite:///./app.db", 
        alias="DATABASE_URL"
    )

    # --- Google Maps ---
    google_maps_key: Optional[str] = Field(default=None, alias="GOOGLE_MAPS_API_KEY")

    # --- JWT / Auth ---
    jwt_secret: str = Field(default="please_change_me", alias="JWT_SECRET")
    jwt_expire_minutes: int = Field(default=120, alias="JWT_EXPIRE_MINUTES")
    jwt_alg: str = Field(default="HS256", alias="JWT_ALG")

    # --- LLM providers (Sprint 2/3) ---
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")

    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-haiku-20240307", alias="ANTHROPIC_MODEL")

    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-flash", alias="GEMINI_MODEL")

    llm_order_raw: str = Field(default="gemini,openai,anthropic", alias="LLM_ORDER")

    # --- Budget / Hotels (Sprint 3) ---
    hotel_api_key: Optional[str] = Field(default=None, alias="HOTEL_API_KEY")
    hotel_api_host: Optional[str] = Field(default=None, alias="HOTEL_API_HOST")
    hotel_api_endpoint: Optional[str] = Field(default=None, alias="HOTEL_API_ENDPOINT")

    # --- Heuristic per-day costs ---
    default_food_per_day: float = Field(default=35.0, alias="DEFAULT_FOOD_PER_DAY")
    default_transport_per_day: float = Field(default=20.0, alias="DEFAULT_TRANSPORT_PER_DAY")
    default_tickets_per_day: float = Field(default=25.0, alias="DEFAULT_TICKETS_PER_DAY")
    default_misc_per_day: float = Field(default=15.0, alias="DEFAULT_MISC_PER_DAY")

    # --- Verifier thresholds ---
    min_rating: float = Field(default=3.9, alias="MIN_RATING")

    # --- RAG toggle ---
    rag_enabled: bool = Field(default=True, alias="RAG_ENABLED")

    @property
    def llm_order(self) -> List[str]:
        """Provider priority list as a normalized array."""
        return [p.strip().lower() for p in self.llm_order_raw.split(",") if p.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
