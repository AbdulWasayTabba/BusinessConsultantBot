"""API key auth and in-memory rate limiting for the BizGPT API.

Configuration (read per request, so changes apply without restart in tests):
- ``BIZGPT_API_KEYS``: comma-separated allowed keys sent via ``X-API-Key``.
  Empty/unset disables auth (local dev).
- ``BIZGPT_RATE_LIMIT``: max requests per client per minute (default 30, 0 disables).
  Clients are identified by API key, else by IP. Single-process only; use a
  shared store (e.g. Redis) when running multiple workers.
"""

from __future__ import annotations

import os
import threading
import time
from collections import defaultdict, deque

from fastapi import Header, HTTPException, Request

WINDOW_SECONDS = 60.0

_lock = threading.Lock()
_hits: dict[str, deque[float]] = defaultdict(deque)


def _allowed_keys() -> set[str]:
    raw = os.getenv("BIZGPT_API_KEYS", "")
    return {k.strip() for k in raw.split(",") if k.strip()}


def _rate_limit() -> int:
    try:
        return max(0, int(os.getenv("BIZGPT_RATE_LIMIT", "30")))
    except ValueError:
        return 30


def reset_rate_limits() -> None:
    """Clear all counters (used by tests)."""
    with _lock:
        _hits.clear()


def _check_rate(client_id: str) -> None:
    limit = _rate_limit()
    if limit == 0:
        return
    now = time.monotonic()
    with _lock:
        window = _hits[client_id]
        while window and now - window[0] >= WINDOW_SECONDS:
            window.popleft()
        if len(window) >= limit:
            retry = int(WINDOW_SECONDS - (now - window[0])) + 1
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(retry)},
            )
        window.append(now)


def require_client(
    request: Request, x_api_key: str | None = Header(default=None)
) -> str:
    """FastAPI dependency: enforce API key (if configured) and rate limit."""
    keys = _allowed_keys()
    if keys and x_api_key not in keys:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    host = request.client.host if request.client else "unknown"
    client_id = f"key:{x_api_key}" if keys else f"ip:{host}"
    _check_rate(client_id)
    return client_id
