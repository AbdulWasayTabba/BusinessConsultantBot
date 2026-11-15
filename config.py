"""Centralized application configuration.

Values are read from environment variables (or a local `.env` file) so the
bot can be reconfigured per environment without code changes, e.g.

    BIZGPT_AGENT_MODEL=llama3.1:8b
    BIZGPT_OLLAMA_BASE_URL=http://ollama:11434
"""

import logging
import time
from functools import lru_cache
from typing import Any, Optional

from langchain_ollama import ChatOllama
from langchain_core.exceptions import OutputParserException
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


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
    # Logging: level name and whether to emit JSON lines.
    log_level: str = "INFO"
    log_json: bool = False
    # LLM resilience: total attempts per call and base backoff (seconds).
    llm_max_attempts: int = 3
    llm_retry_backoff: float = 1.0


@lru_cache
def get_settings() -> Settings:
    return Settings()


class ResilientChatOllama(ChatOllama):
    """ChatOllama that retries failed calls with exponential backoff.

    - ``invoke`` retries transport/server errors (connection refused,
      timeouts, 5xx) up to ``llm_max_attempts`` times.
    - ``with_structured_output`` additionally retries when a small model
      returns output that fails to parse/validate against the schema.
    """

    def invoke(self, input: Any, config: Any = None, **kwargs: Any) -> Any:
        s = get_settings()
        attempts = max(1, s.llm_max_attempts)
        for attempt in range(1, attempts + 1):
            try:
                return super().invoke(input, config, **kwargs)
            except Exception as exc:  # noqa: BLE001 - re-raised after last try
                if attempt == attempts:
                    logger.error(
                        "llm_call_failed",
                        extra={"model": self.model, "attempts": attempt},
                    )
                    raise
                delay = s.llm_retry_backoff * (2 ** (attempt - 1))
                logger.warning(
                    "llm_call_retry",
                    extra={
                        "model": self.model,
                        "attempt": attempt,
                        "delay_s": delay,
                        "error": repr(exc)[:200],
                    },
                )
                time.sleep(delay)

    def with_structured_output(self, *args: Any, **kwargs: Any) -> Any:
        runnable = super().with_structured_output(*args, **kwargs)
        return runnable.with_retry(
            retry_if_exception_type=(OutputParserException, ValidationError),
            stop_after_attempt=max(1, get_settings().llm_max_attempts),
            wait_exponential_jitter=True,
        )


def get_llm(model: Optional[str] = None, **kwargs) -> ChatOllama:
    """Build a ChatOllama client from settings; kwargs override defaults."""
    s = get_settings()
    params = {"model": model or s.agent_model}
    if s.ollama_base_url:
        params["base_url"] = s.ollama_base_url
    if s.temperature is not None:
        params["temperature"] = s.temperature
    params.update(kwargs)
    return ResilientChatOllama(**params)
