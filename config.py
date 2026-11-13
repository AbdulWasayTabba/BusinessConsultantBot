"""Centralized application configuration.

Values are read from environment variables (or a local `.env` file) so the
bot can be reconfigured per environment without code changes, e.g.

    BIZGPT_AGENT_MODEL=llama3.1:8b
    BIZGPT_OLLAMA_BASE_URL=http://ollama:11434
"""

from functools import lru_cache
from typing import Optional

from langchain_ollama import ChatOllama
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="BIZGPT_", env_file=".env", extra="ignore"
    )

    # Model used by the specialist agents, profiler and chat router.
    agent_model: str = "phi3:mini"
    # Larger model used for the final consultant synthesis.
    consultant_model: str = "qwen3:8b"
    # Small model used by the judge and research-gap analyzer.
    judge_model: str = "llama3.2:3b"
    # Ollama server URL; None lets langchain-ollama use its default.
    ollama_base_url: Optional[str] = None
    temperature: Optional[float] = None


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_llm(model: Optional[str] = None, **kwargs) -> ChatOllama:
    """Build a ChatOllama client from settings; kwargs override defaults."""
    s = get_settings()
    params = {"model": model or s.agent_model}
    if s.ollama_base_url:
        params["base_url"] = s.ollama_base_url
    if s.temperature is not None:
        params["temperature"] = s.temperature
    params.update(kwargs)
    return ChatOllama(**params)
