# BioEvidence AI
## Recruiter-Facing Project Report

**Project type:** Full-stack AI research assistant  
**Status:** Working prototype with end-to-end local workflow  
**Primary use case:** Rapid biomedical literature discovery and evidence synthesis  

## Executive Summary

BioEvidence AI is a full-stack biomedical research assistant designed to reduce the friction between asking a clinical research question and producing a structured first-pass literature brief. A user submits a natural-language question through a React interface. The backend expands the question, searches PubMed, synthesizes the returned studies, classifies evidence strength, streams progress back to the browser, and optionally sends the completed report by email.

The project demonstrates applied AI engineering rather than a standalone chatbot: tool-using agents, graph-based orchestration, typed state, streaming APIs, human-in-the-loop execution, external data retrieval, and report delivery are combined into one user workflow.

## Problem

Clinicians, researchers, and students often need a rapid overview of current biomedical evidence, but manual searching requires query design, article screening, study-type interpretation, synthesis, and report preparation. General-purpose language models can summarize text but may lack current sources and a transparent retrieval step.

This project addresses that workflow by grounding synthesis in PubMed results and separating retrieval, interpretation, user interaction, and delivery into explicit pipeline stages.

## Core User Workflow

1. The user enters a clinical or biomedical question.
2. The query ingestor uses a ReAct agent to refine the question and call the PubMed retrieval tool.
3. The evidence builder converts retrieved article metadata and abstracts into an evidence matrix and narrative synthesis.
4. The API streams node activity and generated content to the frontend over SSE.
5. The graph pauses with a LangGraph interrupt to request an email address.
6. The user resumes the same thread and the dispatcher converts the report to HTML and sends it over SMTP.

## System Architecture

```text
+----------------------+       SSE        +-------------------------+
| React research UI   | <--------------> | FastAPI research API   |
| TypeScript / Vite   |                  | Pydantic request models |
+----------+-----------+                  +------------+------------+
           |                                           |
           | POST /research/start                      |
           | POST /research/resume-email               v
           |                                  +----------------------+
           |                                  | LangGraph workflow  |
           |                                  |                      |
           |                                  | Query -> Evidence   |
           |                                  |   -> Email input    |
           |                                  |   -> SMTP delivery   |
           |                                  +----+------------+----+
           |                                       |            |
           |                                       v            v
           |                                  PubMed API     SMTP
```

### Backend graph nodes

| Node | Responsibility | Design choice |
| --- | --- | --- |
| `med_query_ingestor` | Understands the question and retrieves articles | ReAct agent with a PubMed tool |
| `med_evidence_builder` | Creates evidence cards and narrative synthesis | Direct LLM call because no tool loop is needed |
| `email_collector` | Requests the report recipient | LangGraph `interrupt()` preserves state while waiting |
| `med_email_dispatcher` | Builds and sends the final report | Direct tool call avoids sending large reports through another LLM loop |

## Technical Implementation

### Frontend

The frontend is a Vite-powered React and TypeScript single-page application. It provides a landing page and a research workspace with:

- Clinical query entry and example prompts
- Streaming agent messages and progress states
- PubMed article cards with source links
- Evidence matrix and narrative synthesis rendering
- Markdown rendering for structured research output
- Email collection interaction
- Responsive visual components built with Tailwind, Radix UI, Lucide icons, and Framer Motion

The research workspace uses the Fetch Streams API to parse SSE messages and keeps a thread identifier so a paused graph can be resumed.

### Backend

The backend exposes a FastAPI application with two research routes:

- `POST /research/start` accepts `{ "query": string, "thread_id": string }`.
- `POST /research/resume-email` accepts `{ "email": string, "thread_id": string }`.

The controller translates LangGraph events into frontend-friendly event types including `node_start`, `node_end`, `token`, `interrupt`, `error`, and `[DONE]`.

### Retrieval and synthesis

The PubMed tool uses NCBI E-utilities to search for recent records and fetch metadata and abstracts. The synthesis prompt classifies studies into categories such as systematic review, randomized controlled trial, cohort study, case-control study, cross-sectional study, case report, narrative review, GWAS, laboratory/animal study, and clinical guideline or consensus statement. It also assigns Strong, Moderate, or Preliminary evidence labels based on the requested classification rules.

## Engineering Decisions

- **Graph orchestration:** LangGraph makes the multi-stage workflow explicit and enables resumable human input.
- **Stateful threads:** A thread ID connects the initial research request with the later email-resume request.
- **SSE instead of polling:** Users see progress and generated content as it becomes available.
- **Separated retrieval and synthesis:** The system keeps source gathering distinct from interpretation, which makes the workflow easier to inspect and extend.
- **Direct email dispatch:** Large reports bypass an additional LLM call and are passed directly to the email tool.
- **Source-grounded output:** The report is based on retrieved PubMed records rather than only model memory.

## Demonstrated Outcomes

The accompanying evaluation draft reports tests across five medical domains, with ten retrieved articles per query, an average runtime of approximately 44.6 seconds, and successful email delivery in all five test cases. These figures are documented project results rather than continuously reproduced CI benchmarks; external credentials and live APIs are required to rerun them.

The evaluation also surfaced realistic retrieval issues, including duplicate records and query scope drift. Calling out those limitations is important for responsible use in a medical research context.

## Repository Map

```text
biolit-insight-ai/          React frontend
medical_research_asistant/ Python backend and LangGraph workflow
PROJECT_REPORT.md           This recruiter-facing report
README.md                   Quick-start repository overview
```

Key implementation files:

- [`biolit-insight-ai/src/pages/Search.tsx`](biolit-insight-ai/src/pages/Search.tsx) - streaming research workspace and API client
- [`medical_research_asistant/src/main.py`](medical_research_asistant/src/main.py) - FastAPI application entry point
- [`medical_research_asistant/src/api/routers/research_router.py`](medical_research_asistant/src/api/routers/research_router.py) - research API contract
- [`medical_research_asistant/src/agent/graph.py`](medical_research_asistant/src/agent/graph.py) - stateful LangGraph workflow
- [`medical_research_asistant/src/tools/pubmed.py`](medical_research_asistant/src/tools/pubmed.py) - PubMed integration
- [`medical_research_asistant/src/tools/send_email_tool.py`](medical_research_asistant/src/tools/send_email_tool.py) - report formatting and SMTP delivery

## Local Setup

### Backend

```bash
cd medical_research_asistant
uv sync
# Copy .env.example to .env and add credentials
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd biolit-insight-ai
npm install
npm run dev
```

Required configuration includes `OPENROUTER_API_KEY`; SMTP and optional LangSmith settings are described in [`medical_research_asistant/.env.example`](medical_research_asistant/.env.example).

## Current Scope and Production Roadmap

The current implementation is intentionally a prototype. The highest-value next steps are:

- Replace in-memory `MemorySaver` with durable, production-safe checkpoint storage.
- Restrict CORS and validate query and email inputs server-side.
- Move the frontend API URL into environment configuration.
- Add retrieval deduplication, pagination, richer source validation, and reproducible evaluation fixtures.
- Add frontend component tests and backend tests that mock PubMed, the model provider, and SMTP.
- Connect advertised export actions to implemented backend endpoints.
- Add authentication, rate limiting, observability, and deployment configuration before handling real users or sensitive data.

## Portfolio Summary

This project showcases full-stack ownership across product design, frontend interaction, API design, LLM orchestration, external data integration, streaming UX, state management, and responsible documentation of limitations. The strongest engineering story is the explicit workflow boundary: retrieval, synthesis, human approval, and delivery are implemented as inspectable stages rather than hidden inside one opaque prompt.
