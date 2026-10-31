# Medpedia

> Agentic biomedical literature search and evidence synthesis platform

Medpedia is an end-to-end biomedical research assistant that turns a natural-language clinical question into a structured, evidence-oriented literature brief. It combines a React research workspace with a FastAPI and LangGraph backend that retrieves current PubMed literature, synthesizes study findings, classifies evidence strength, streams progress to the browser, and can deliver the completed report by email.

## Why It Matters

Biomedical literature is large, fast-moving, and difficult to review under time pressure. This project explores a practical human-in-the-loop workflow for helping clinicians, researchers, and students move from a clinical question to a traceable first-pass evidence summary in minutes.

> This tool supports literature discovery and synthesis. It is not a diagnostic system or a replacement for clinical judgment.

## Product Highlights

- Natural-language clinical research questions
- PubMed retrieval through NCBI E-utilities (`esearch`, `esummary`, and `efetch`)
- Agentic query expansion with Gemini 3.5 Flash Lite through the Google Gemini API
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
Medpedia/
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
| Model provider | Google Gemini 3.5 Flash Lite via Google Gemini API |
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

### Environment & Email Configuration

The backend requires a Gemini API key (`GEMINI_API_KEY`). NCBI and SMTP settings are also needed for literature retrieval and email delivery. See [`medical_research_asistant/.env.example`](medical_research_asistant/.env.example).

#### Gmail SMTP Setup

Medpedia uses standard Gmail SMTP (`smtp.gmail.com:587` with STARTTLS) to deliver structured evidence reports to any valid recipient email address (Gmail, Outlook, Yahoo, institutional `.edu` addresses, etc.) without requiring a custom domain purchase.

##### Why Resend Was Replaced
Previously, Resend was used for REST-based dispatch. However, Resend restricts delivery on unverified free-tier accounts strictly to the account owner's email address and requires purchasing and configuring a custom DNS domain to email external recipients. Gmail SMTP removes this barrier, enabling any first-time visitor to receive reports at their own email address using a personal Gmail account and App Password.

##### Generating a Google App Password
1. Enable **2-Step Verification** on your Google Account: [Google Account Security](https://myaccount.google.com/security).
2. Go to **App Passwords**: [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).
3. Under *App Name*, enter `Medpedia` and click **Create**.
4. Copy the generated 16-character passcode (e.g., `abcd efgh ijkl mnop`).
5. Reference official documentation: [Sign in with app passwords](https://support.google.com/mail/answer/185833).

##### Environment Variables Configuration

Configure the following variables in `medical_research_asistant/.env` for local development, or in your backend hosting platform's environment variables dashboard (e.g. Render, Railway, Fly.io):

```env
# Gmail SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=syedmohammedrayan2007@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_TIMEOUT=15
```

##### Sending Limits & Hosting Notes
- **Daily Sending Limits**: Standard personal Gmail accounts are subject to Google's daily sending limit of 500 emails per 24-hour rolling period.
- **Port Restrictions**: Render Free Tier blocks outbound TCP traffic on ports 25, 465, and 587. For production deployment on Render, use a paid instance or host the backend on providers that permit outbound SMTP (such as Railway, Fly.io, Koyeb, DigitalOcean, or AWS).
- **Troubleshooting**:
  - `535 Authentication failed`: Ensure 2-Step Verification is enabled and that you are using the 16-character App Password (without spaces), NOT your regular Google password.
  - `Connection timed out`: Verify network firewall or hosting provider allows outbound traffic to `smtp.gmail.com:587`.
  - `Only a single recipient email address is allowed`: Ensure you enter a single clean email address without commas or semicolons.

## Validation

```bash
cd biolit-insight-ai
npm run lint
npm run build

cd ../medical_research_asistant
uv run pytest
```

The backend unit test suite covers SMTP configuration, connection protocol sequence, dynamic recipient handling, sender integrity, error handling, HTML report payload generation, and LangGraph workflow dispatch.

## Project Status

This is a working academic/prototype system with a complete demonstrated flow. Before production deployment, the next engineering priorities are durable checkpoint storage, strict CORS and input validation, configurable API URLs, stronger evidence evaluation, deduplication, and connecting every visible export action to a real backend implementation.

