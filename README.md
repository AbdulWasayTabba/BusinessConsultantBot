# BizGPT — Multi-Agent AI Business Consultant

[![CI](https://github.com/AbdulWasayTabba/BusinessConsultantBot/actions/workflows/ci.yml/badge.svg)](https://github.com/AbdulWasayTabba/BusinessConsultantBot/actions/workflows/ci.yml)

BizGPT is a multi-agent "business consultant" built with **LangGraph** and local LLMs served by **Ollama**. Describe your business and a problem; a graph of specialised agents profiles the business, asks clarifying questions, researches market, competitor, customer, finance, marketing and operations angles, then produces a prioritised, reviewed action plan and report.

## Features

- **Intent routing** — casual chat goes to a chat agent; consulting requests enter the full pipeline.
- **Human-in-the-loop clarification** — the graph pauses (LangGraph `interrupt`) to ask for missing information, then resumes.
- **Dynamic agent selection** — only the domain agents relevant to the problem run.
- **Research → synthesis → gap analysis loop** — targeted research fills gaps before diagnosis.
- **Judge & replanning** — a judge agent reviews output quality and can trigger replanning.
- **Final report** — prioritised recommendations, implementation plan, and risk/change review.
- **Streamlit UI** with live workflow events.
- **FastAPI REST API** (`/health`, `/consult`) with the same clarification flow via `thread_id`.
- **Docker image** for the API, with a `/health` healthcheck.

## Architecture

![BizGPT graph](bizgpt_graph.png)

```
agents/    Domain specialists (market, competitor, customer, finance, marketing, operations)
nodes/     Pipeline steps (intent router, profiler, clarification, planner, diagnosis, judge, report, ...)
graph/     State definition (state.py) and graph wiring (graph.py)
prompts/   One prompt template per agent/node (.txt)
app/       Streamlit frontend
api/       FastAPI REST interface
config.py  Settings (models, Ollama URL, logging, LLM retries) from env vars
tests/     Offline pytest suite (API, graph routing, state)
main.py    CLI entry point
```

## Setup

Requirements: Python 3.10+ and [Ollama](https://ollama.com) running locally.

```bash
git clone https://github.com/AbdulWasayTabba/BusinessConsultantBot.git
cd BusinessConsultantBot
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
ollama pull phi3:mini
cp .env.example .env        # then fill in values as needed
```

## Usage

Streamlit UI:

```bash
streamlit run app/app.py
```

Command line:

```bash
python main.py
```

## Docker

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec ollama ollama pull phi3:mini   # also qwen3:8b, llama3.2:3b
curl http://localhost:8000/health
```

The compose stack runs the API and an Ollama server; models persist in the `ollama-models` volume.

## Environment variables

See `.env.example`. All are optional.

| Variable | Purpose |
| --- | --- |
| `OLLAMA_HOST` | Ollama server URL (default `http://localhost:11434`) |
| `LANGCHAIN_API_KEY` | LangSmith API key for tracing |
| `LANGCHAIN_TRACING_V2` | Set `true` to enable LangSmith tracing |
| `LANGCHAIN_PROJECT` | LangSmith project name |

Never commit your `.env` file.

## REST API

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

- `GET /health` — liveness check.
- `POST /consult` — body `{"message": "...", "thread_id": null}`. Returns `status` `needs_clarification` (with a `question`) or `completed` (with a `report`). Send the answer back with the same `thread_id` to resume.

Docker:

```bash
docker build -t bizgpt .
docker run -p 8000:8000 -e BIZGPT_OLLAMA_BASE_URL=http://host.docker.internal:11434 bizgpt
```

## Model configuration

Settings are read from `BIZGPT_*` environment variables (see `config.py`). Defaults:

| Variable | Default | Used by |
| --- | --- | --- |
| `BIZGPT_AGENT_MODEL` | `phi3:mini` | specialist agents, profiler, chat router |
| `BIZGPT_CONSULTANT_MODEL` | `qwen3:8b` | final consultant synthesis |
| `BIZGPT_JUDGE_MODEL` | `llama3.2:3b` | judge and research-gap analyzer |
| `BIZGPT_OLLAMA_BASE_URL` | Ollama default | Ollama server |

Pull every model you use (e.g. `ollama pull qwen3:8b`).

## Tests & CI

```bash
pip install -r requirements-dev.txt
pytest
ruff check . && ruff format --check .
```

Tests run offline (no LLM or API keys). GitHub Actions runs ruff and pytest on every push to `main`.

## Status

The API, Docker image, config module, logging, tests and CI on the roadmap are done; CI passes on `main`. The tests use stubs, so answer quality depends on the local models you pick and has not been benchmarked. Remaining ideas are in [ROADMAP.md](ROADMAP.md).
