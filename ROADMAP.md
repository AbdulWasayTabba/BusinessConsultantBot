# Roadmap

- [x] Remove committed __pycache__/*.pyc from git (git rm -r --cached) and keep them ignored
- [x] Rename requirement.txt -> requirements.txt with pinned versions
- [x] Add .env.example listing required env vars (names only, no values)
- [x] Write a professional README (overview, architecture with bizgpt_graph.png, setup, usage, env vars)
- [x] Add centralized config module (pydantic-settings) replacing scattered os.getenv
- [x] Add structured logging
- [x] Add error handling + retries around LLM calls
- [x] Add pytest setup and first unit tests for state/graph wiring (mock LLM)
- [x] Add ruff config + pre-commit
- [x] Add GitHub Actions CI (ruff + pytest)
- [x] Make ruff lint job blocking in CI (fix existing violations, drop `continue-on-error`)
- [ ] Add FastAPI REST API exposing the consultant graph (/health, /consult)
- [ ] Add Dockerfile + .dockerignore
- [ ] Add docker-compose.yml
- [ ] Add streaming responses endpoint
- [ ] Add conversation/session persistence (LangGraph checkpointer, SQLite then Postgres-ready)
- [ ] Add rate limiting + API key auth
- [ ] Add type hints + mypy across nodes
- [ ] Add deployment guide (Render/Railway/Fly.io) to README
- [ ] Add LICENSE (MIT) and CONTRIBUTING.md
- [ ] Add evaluation script with sample business scenarios
- [ ] Add caching for repeated LLM calls
- [ ] Add observability hooks (LangSmith optional)
- [ ] Improve frontend in app/ (UI polish, export report as PDF/Markdown)

## Changelog

- 2026-11-09: Untracked committed `__pycache__`/`*.pyc` files (already ignored via .gitignore); added this roadmap.
- 2026-11-10: Renamed requirement.txt -> requirements.txt and pinned versions.
- 2026-11-11: Added .env.example (LangSmith + Ollama vars, names only).
- 2026-11-14: docs: add professional README (overview, architecture, setup, usage, env vars)
- 2026-11-14: Added `config.py` (pydantic-settings, `BIZGPT_` env prefix) with `get_llm()`; all agents/nodes now take model names and Ollama URL from config instead of hardcoded `ChatOllama(...)`.
- 2026-11-14: Added `logging_setup.py` (stdlib logging, optional JSON lines via `BIZGPT_LOG_JSON`, level via `BIZGPT_LOG_LEVEL`); replaced node `print` calls with structured `node_enter` log events. Note: local .venv base interpreter is missing, so only syntax/formatter checks were run.
- 2026-11-15: Added `ResilientChatOllama` in `config.py`: `get_llm()` now retries failed LLM calls with exponential backoff and retries structured-output parse/validation failures (`BIZGPT_LLM_MAX_ATTEMPTS`, `BIZGPT_LLM_RETRY_BACKOFF`), logging `llm_call_retry`/`llm_call_failed` events.
- 2026-11-16: test: add pytest setup (pytest.ini, conftest) and offline tests for state contract + graph routers (graph tests skip if langgraph missing; local .venv points to a missing Python 3.11 and needs recreating).
- 2026-11-17: chore: add `ruff.toml` (E/F/I/B/UP, py311, line 100), `.pre-commit-config.yaml` (ruff + ruff-format + hygiene hooks incl. detect-private-key) and `requirements-dev.txt`. Ruff not installed locally, so no lint pass run yet; CI item will surface any existing violations.
- 2026-11-18: ci: add GitHub Actions workflow `.github/workflows/ci.yml` (ruff lint + format check, pytest on Python 3.11 with pip cache). Lint job is non-blocking for now since ruff has never been run on the codebase; follow-up item added. Not verified locally (no working venv) - first run on GitHub is the check.
- 2026-11-19: ruff lint is now blocking in CI — auto-fixed/formatted the codebase, hoisted late imports in graph/graph.py, documented intentional E402 in app/app.py and main.py.
