# BioEvidence AI

> Agentic biomedical literature search and evidence synthesis platform

BioEvidence AI is an end-to-end biomedical research assistant that turns a natural-language clinical question into a structured, evidence-oriented literature brief. It combines a React research workspace with a FastAPI and LangGraph backend that retrieves current PubMed literature, synthesizes study findings, classifies evidence strength, streams progress to the browser, and can deliver the completed report by email.

## Why It Matters

Biomedical literature is large, fast-moving, and difficult to review under time pressure. This project explores a practical human-in-the-loop workflow for helping clinicians, researchers, and students move from a clinical question to a traceable first-pass evidence summary in minutes.

> This tool supports literature discovery and synthesis. It is not a diagnostic system or a replacement for clinical judgment.

## Product Highlights

- Natural-language clinical research questions
- PubMed retrieval through NCBI E-utilities (`esearch`, `esummary`, and `efetch`)
- Agentic query expansion with Gemini 2.5 Flash through OpenRouter
- Structured evidence cards, study-type classification, and narrative synthesis
- Real-time Server-Sent Events for pipeline progress and streamed responses
- Human-in-the-loop email collection using LangGraph `interrupt()` and resumable threads
- Styled HTML report delivery over SMTP
- Responsive React interface with article cards, evidence tables, markdown rendering, and synthesis views

## Architecture

```text
React + TypeScript + Vite
          |
          | POST /research/start and POST /research/resume-email
          | Server-Sent Events
          v
FastAPI API
          |
          v
LangGraph workflow
  1. Query ingestor (ReAct + PubMed tool)
  2. Evidence builder (structured LLM synthesis)
  3. Email collector (human-in-the-loop interrupt)
  4. Email dispatcher (Markdown -> HTML -> SMTP)
```

The frontend lives in [`biolit-insight-ai/`](biolit-insight-ai/). The backend lives in [`medical_research_asistant/`](medical_research_asistant/). A detailed recruiter-facing report is available in [`PROJECT_REPORT.md`](PROJECT_REPORT.md).

## Repository Structure

```text
BioEvidence-AI/
├── biolit-insight-ai/          # React + TypeScript frontend
│   ├── src/components/         # Research UI and reusable components
│   ├── src/pages/              # Landing and research workspace pages
│   └── package.json
├── medical_research_asistant/  # FastAPI + LangGraph backend
│   ├── src/agent/              # Research workflow and prompts
│   ├── src/api/                # API routes and controllers
│   ├── src/tools/              # PubMed and email tools
│   └── tests/                  # Backend tests
├── PROJECT_REPORT.md           # Recruiter-facing technical report
└── README.md
```

## Technology

| Area | Stack |
| --- | --- |
| Frontend | React, TypeScript, Vite, Tailwind CSS, Radix UI, Framer Motion |
| Backend | Python, FastAPI, Uvicorn, Pydantic |
| AI orchestration | LangGraph, LangChain, ReAct agents |
| Model provider | Google Gemini 2.5 Flash through OpenRouter |
| Literature source | NCBI PubMed E-utilities |
| Streaming | Server-Sent Events and Fetch Streams API |
| Delivery | SMTP with TLS/STARTTLS |
| Python tooling | `uv` |

## Run Locally

### Backend

```bash
cd medical_research_asistant
uv sync
# Create .env from .env.example and add your provider credentials
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd biolit-insight-ai
npm install
npm run dev
```

Open the Vite URL shown in the terminal. The current frontend expects the API at `http://localhost:8000`.

### Environment

The backend requires an OpenRouter key. NCBI and SMTP settings are also needed for literature retrieval and email delivery. See [`medical_research_asistant/.env.example`](medical_research_asistant/.env.example).

## Validation

```bash
cd biolit-insight-ai
npm run lint
npm run build

cd ../medical_research_asistant
uv run pytest
```

The repository currently has limited automated coverage. The backend integration path depends on external model and service credentials, and no frontend test suite is configured yet.

## Project Status

This is a working academic/prototype system with a complete demonstrated flow. Before production deployment, the next engineering priorities are durable checkpoint storage, strict CORS and input validation, configurable API URLs, stronger evidence evaluation, deduplication, and connecting every visible export action to a real backend implementation.
