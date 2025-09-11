# Purpose: Provide a unified LLM router with multiple providers (Gemini, OpenAI, Anthropic)
#          The router requests JSON output (schema) and returns parsed Python dict.
#          Each provider wrapper focuses on: (a) correct JSON mode, (b) simple prompt, (c) graceful fallback.

from __future__ import annotations                         # Enable future annotations (nice for type hints)
from typing import Any, Dict, Optional, Tuple              # Import common typing helpers
import json                                                # Parse JSON strings
from tenacity import retry, stop_after_attempt, wait_exponential  # Reliable retry for flaky network calls

# Provider SDKs (all optional — only used if the API key exists)
import os                                                 # Access environment for safety checks
import httpx                                              # We keep httpx for potential low-level calls
                                                         # (not strictly used here but handy for future functions)

# Import our typed settings
from ..settings import Settings                           # Settings loader (keys, models, provider order)

# --- Guard: lazily import SDKs to avoid import errors when keys are missing ---
try:
    import google.generativeai as genai                   # Gemini SDK import
except Exception:
    genai = None                                          # If import fails, we leave it None

try:
    import openai                                         # OpenAI SDK import
except Exception:
    openai = None                                         # If import fails, we leave it None

try:
    import anthropic                                      # Anthropic SDK import
except Exception:
    anthropic = None                                      # If import fails, we leave it None


# Helper: strict JSON parsing with helpful error
def _force_json(text: str) -> Dict[str, Any]:
    """Try to parse JSON; raise a clear ValueError if invalid JSON is returned by the LLM."""
    text = text.strip()                                   # Remove leading/trailing whitespace
    # Some providers wrap JSON in code fences; we attempt to strip them safely
    if text.startswith("```"):
        # Remove possible markdown code fences to extract the pure JSON
        text = text.strip("`")                            # Strip backticks
        # After stripping, try to find the first { ... } block (best-effort)
        start = text.find("{")                            # Locate opening brace
        end = text.rfind("}")                             # Locate closing brace
        if start != -1 and end != -1 and end > start:     # Verify indices are valid
            text = text[start : end + 1]                  # Slice the JSON segment
    try:
        return json.loads(text)                           # Attempt to load JSON
    except Exception as e:                                # On failure, raise descriptive error
        raise ValueError(f"LLM did not return valid JSON. Raw output: {text[:500]}") from e  # Limit raw preview


# Build prompt template for POI generation (compact; enforce JSON-only response)
def build_poi_prompt(city: str, preferences: list[str], days: int, budget: float) -> Tuple[str, Dict[str, Any]]:
    """
    Return (system_message, user_message_dict) for chat-based LLMs.
    We enforce JSON output with a small schema so downstream code can parse deterministically.
    """
    # Compose system instruction (role + constraints)
    system = (
        "You are a travel planner agent. "
        "Return ONLY JSON matching this schema: "
        "{\"pois\": [{\"name\": string, \"category\": string}]} "
        "No commentary. No markdown. No code fences."
    )                                                     # System: describe role and output format

    # Compose user message (inputs and soft constraints)
    user = {
        "city": city,                                     # Target city for the itinerary
        "preferences": preferences or [],                 # User's interests (e.g., food, culture)
        "days": days,                                     # Duration of the trip (days)
        "budget": budget,                                 # Budget in user's currency
        "requirements": {
            "count": 8,                                   # Aim to produce ~8 candidates (we will pick top few)
            "deduplicate": True,                          # Avoid duplicates / aliases
            "high_quality": True,                         # Prefer well-known, legitimate POIs
            "category_from_preferences": True             # Map preferences into 'category' field when possible
        }
    }                                                     # User payload gives the facts and constraints

    return system, user                                   # Return the pair for providers that support chat format


# Provider wrapper: Gemini
class GeminiProvider:
    """Wrapper around Google Gemini to request JSON output."""

    def __init__(self, api_key: str, model: str):         # Store credentials and default model
        self.api_key = api_key                             # Save API key locally
        self.model = model                                 # Save model name
        if genai:                                          # If SDK is available
            genai.configure(api_key=api_key)               # Configure SDK globally with API key

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.5, max=4))
    def generate_pois(self, city: str, preferences: list[str], days: int, budget: float) -> Dict[str, Any]:
        """Call Gemini with strict JSON response."""
        if not genai:                                      # If SDK is missing, raise an informative error
            raise RuntimeError("google-generativeai SDK is not installed")

        system, user = build_poi_prompt(city, preferences, days, budget)  # Build the prompt messages
        model = genai.GenerativeModel(                     # Create a GenerativeModel instance
            model_name=self.model,                         # Use the configured model
            system_instruction=system                      # Provide system instruction (role + output constraints)
        )
        response = model.generate_content(                 # Call the model to generate content
            [                                              # Provide a list of parts to the model
                {"role": "user", "parts": [                # User role with parts
                    {"text": json.dumps(user)}             # Send JSON string as the user content
                ]}
            ],
            generation_config={                            # Generation config to enforce JSON
                "response_mime_type": "application/json"   # Ask for JSON-only response
            },
        )
        # Extract text (Gemini SDK returns a response object with .text)
        text = response.text or ""                         # Get returned text (should be JSON)
        return _force_json(text)                           # Parse into Python dict or raise if invalid


# Provider wrapper: OpenAI
class OpenAIProvider:
    """Wrapper around OpenAI to request JSON output."""

    def __init__(self, api_key: str, model: str):         # Store credentials and default model
        if not openai:                                     # Ensure SDK is installed
            raise RuntimeError("openai SDK is not installed")
        self.client = openai.OpenAI(api_key=api_key)       # Instantiate OpenAI client with API key
        self.model = model                                 # Save model name

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.5, max=4))
    def generate_pois(self, city: str, preferences: list[str], days: int, budget: float) -> Dict[str, Any]:
        """Call OpenAI Chat Completions (JSON mode) to get POI list."""
        system, user = build_poi_prompt(city, preferences, days, budget)  # Build messages
        resp = self.client.chat.completions.create(        # Create a chat completion request
            model=self.model,                              # Target model
            response_format={"type": "json_object"},       # Ask OpenAI to return valid JSON
            messages=[                                     # Chat messages array (system + user)
                {"role": "system", "content": system},     # System instruction (format + role)
                {"role": "user", "content": json.dumps(user)}  # User content as JSON string
            ],
            temperature=0.2                                # Lower temperature for determinism
        )
        text = resp.choices[0].message.content or ""       # Extract the assistant content (should be JSON)
        return _force_json(text)                           # Parse into Python dict or raise if invalid


# Provider wrapper: Anthropic
class AnthropicProvider:
    """Wrapper around Anthropic Claude to request JSON output."""

    def __init__(self, api_key: str, model: str):         # Store credentials and default model
        if not anthropic:                                  # Ensure SDK is installed
            raise RuntimeError("anthropic SDK is not installed")
        self.client = anthropic.Anthropic(api_key=api_key) # Instantiate Anthropic client with API key
        self.model = model                                 # Save model name

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.5, max=4))
    def generate_pois(self, city: str, preferences: list[str], days: int, budget: float) -> Dict[str, Any]:
        """Call Claude Messages API and request JSON content."""
        system, user = build_poi_prompt(city, preferences, days, budget)  # Build messages
        resp = self.client.messages.create(                # Create a Claude message request
            model=self.model,                              # Target model
            system=system,                                 # System instruction (role + JSON schema)
            messages=[                                     # Conversation stack
                {"role": "user", "content": json.dumps(user)}  # Provide user content as JSON string
            ],
            temperature=0.2,                               # Lower temperature for stability
            max_tokens=1024                                # Reasonable cap for response length
        )
        # Claude returns structured content; we extract text from the first content block
        text = ""                                          # Initialize empty text
        if resp and resp.content and len(resp.content) > 0:  # Ensure content is available
            block = resp.content[0]                        # Take the first block
            if getattr(block, "text", None):               # If it has a 'text' attribute
                text = block.text                          # Use block.text
            elif isinstance(block, dict) and "text" in block:  # Or sometimes dict-like
                text = block["text"]                       # Use dict['text']
        return _force_json(text)                           # Parse into Python dict or raise if invalid


# High-level router that selects the first available provider
class LLMRouter:
    """Try providers in configured order until one succeeds, returning a POI JSON."""

    def __init__(self, settings: Settings):                # Initialize with our Settings instance
        self.s = settings                                  # Keep settings for access to keys, models, and order

    def _providers(self) -> list[Tuple[str, Any]]:         # Build an ordered list of (name, instance) pairs
        providers: list[Tuple[str, Any]] = []              # Start with empty list
        for name in self.s.llm_order:                      # Iterate configured order
            if name == "gemini" and self.s.gemini_api_key: # If gemini is configured
                providers.append(("gemini", GeminiProvider(self.s.gemini_api_key, self.s.gemini_model)))  # Add Gemini
            if name == "openai" and self.s.openai_api_key: # If openai is configured
                providers.append(("openai", OpenAIProvider(self.s.openai_api_key, self.s.openai_model)))  # Add OpenAI
            if name == "anthropic" and self.s.anthropic_api_key:  # If anthropic is configured
                providers.append(("anthropic", AnthropicProvider(self.s.anthropic_api_key, self.s.anthropic_model)))  # Add Claude
        return providers                                    # Return the ordered list

    def generate_pois(self, city: str, preferences: list[str], days: int, budget: float) -> Dict[str, Any]:
        """Try providers in order and return the first valid JSON response with 'pois'."""
        last_error: Optional[Exception] = None             # Keep last error for diagnostics
        for name, provider in self._providers():           # Iterate over available providers
            try:
                data = provider.generate_pois(city, preferences, days, budget)  # Call provider
                if isinstance(data, dict) and "pois" in data:                  # Verify minimal schema
                    return data                                                 # Return on success
            except Exception as e:                           # Catch errors (network, invalid JSON, quota, etc.)
                last_error = e                               # Record error and continue to next provider
        # If we reach here, no provider succeeded; raise a helpful error
        raise RuntimeError(f"All LLM providers failed. Last error: {last_error}")
