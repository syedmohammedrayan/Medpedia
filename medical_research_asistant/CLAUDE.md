# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run the FastAPI server (hot reload)
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Run the LangGraph development server (LangGraph Studio integration)
uv run langgraph dev

# Lint and type-check
make lint          # ruff + mypy strict
make format        # ruff format

# Tests
make test                     # unit tests only
make integration_tests        # integration tests (requires API keys)

# Run a single test file
uv run pytest tests/unit_tests/test_configuration.py -v

# Spell check
make spell_check
```

## Environment Variables

Copy `.env.example` to `.env` and populate:

| Variable | Purpose |
|---|---|
| `OPENROUTER_API_KEY` | LLM access (Google Gemini 2.5 Flash via OpenRouter) |
| `NCBI_API_KEY` | PubMed/PMC literature search |
| `SMTP_USER` / `SMTP_PASSWORD` | Email delivery (Gmail tested) |
| `SMTP_HOST` / `SMTP_PORT` | Email server (defaults: smtp.gmail.com:587) |
| `LANGSMITH_API_KEY` / `LANGSMITH_PROJECT` | Tracing and observability |

## Architecture

This is a **LangGraph-powered medical research assistant** that searches PubMed, synthesizes evidence, and emails results to users. The graph is defined in [src/agent/graph.py](src/agent/graph.py) and exposed via a FastAPI server in [src/main.py](src/main.py).

### Graph Pipeline (4 nodes, sequential)

```
START → med_query_ingestor → med_evidence_builder → email_collector → med_email_dispatcher → END
```

1. **`med_query_ingestor`** — ReAct agent (Gemini 2.5 Flash + `pubmed_to_pmc_full_text_search` tool). Parses the medical query, enhances it with MeSH terms, fetches PubMed articles, and outputs formatted article cards into `state.articles_report`.

2. **`med_evidence_builder`** — Direct LLM call (no tool loop). Classifies each article by study type (RCT, Systematic Review, Cohort, etc.) and assigns evidence strength badges (🟢 Strong / 🟡 Moderate / 🔴 Preliminary). Outputs into `state.evidence_report`.

3. **`email_collector`** — Human-in-the-loop node. Calls `interrupt()` to pause execution and wait for the recipient's email address. The graph must be resumed via the API with the email value.

4. **`med_email_dispatcher`** — Calls `send_email` tool directly (bypasses LLM to avoid token limits with large reports). Sends combined evidence + articles as a styled HTML email.

### State

`MedResearchState` (extends `MessagesState`) in [src/agent/graph.py](src/agent/graph.py):
- `messages` — inherited LangChain message history
- `articles_report` — raw article cards from node 1
- `evidence_report` — classified evidence from node 2
- `recipient_email` — collected via interrupt in node 3
- `email_status` — delivery confirmation from node 4

Persistence uses `MemorySaver` checkpointer, enabling thread-based state resumption after the interrupt.

### Tools

- **[src/tools/pubmed.py](src/tools/pubmed.py)** — `pubmed_to_pmc_full_text_search`: Hits NCBI E-utilities (esearch → esummary → efetch) to return structured article metadata and abstracts as JSON.
- **[src/tools/send_email_tool.py](src/tools/send_email_tool.py)** — `send_email`: Converts markdown reports to styled HTML and sends via SMTP.

### API Layer

- **[src/api/routers/research_router.py](src/api/routers/research_router.py)** — Two endpoints:
  - `POST /research/start` — starts a new research session, streams events via SSE
  - `POST /research/resume-email` — resumes graph after interrupt with the user's email
- **[src/api/controllers/research_controller.py](src/api/controllers/research_controller.py)** — Uses `astream_events` v2 API to emit node lifecycle and token events as Server-Sent Events (JSON payloads).

### Prompts

All system prompts are in [src/agent/prompts.py](src/agent/prompts.py). This is the primary place to tune agent behavior, study-type classification logic, email formatting instructions, and rejection/fallback responses.

### LangGraph Server Mode

`langgraph.json` points the LangGraph CLI at `src/agent/graph.py:graph`. Running `uv run langgraph dev` starts a local LangGraph server compatible with LangGraph Studio for visual graph debugging and thread inspection.
