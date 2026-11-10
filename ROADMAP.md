# Roadmap

- [x] Remove committed __pycache__/*.pyc from git (git rm -r --cached) and keep them ignored
- [x] Rename requirement.txt -> requirements.txt with pinned versions
- [ ] Add .env.example listing required env vars (names only, no values)
- [ ] Write a professional README (overview, architecture with bizgpt_graph.png, setup, usage, env vars)
- [ ] Add centralized config module (pydantic-settings) replacing scattered os.getenv
- [ ] Add structured logging
- [ ] Add error handling + retries around LLM calls
- [ ] Add pytest setup and first unit tests for state/graph wiring (mock LLM)
- [ ] Add ruff config + pre-commit
- [ ] Add GitHub Actions CI (ruff + pytest)
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
