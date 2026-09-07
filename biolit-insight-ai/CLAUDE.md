# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
npm run dev        # Start dev server (Vite, http://localhost:5173)
npm run build      # Production build
npm run build:dev  # Development build
npm run lint       # ESLint check
npm run preview    # Preview production build
```

There is no test suite configured.

## Architecture

**BioEvidence AI** is a React + TypeScript SPA that serves as the frontend for an agentic clinical evidence synthesis tool. It connects to a Python backend at `http://localhost:8000`.

### Routing

Two real routes in [src/App.tsx](src/App.tsx):
- `/` → `Index` — landing page with hero search bar
- `/search` → `Search` — the chat/agent workspace

Query is passed from `Index` to `Search` via `react-router-dom` location state (`location.state.query`).

### Backend API contract

The `Search` page ([src/pages/Search.tsx](src/pages/Search.tsx)) communicates with the backend via two SSE (Server-Sent Events) endpoints using the Fetch Streams API:

- `POST /research/start` — starts a new research session with `{ query, thread_id }`
- `POST /research/resume-email` — resumes after email collection interrupt with `{ email, thread_id }`

The backend streams `data: <json>\n\n` events. The frontend handles these event types in `handleServerMessage`:
- `token` — appends streamed text to the last agent message
- `node_start` / `node_end` — appends whitespace between pipeline sections
- `interrupt` — signals the agent needs the user's email; sets `waitingForEmailRef` to redirect the next message to the resume endpoint
- `error` — displays an error message

### Message rendering pipeline

`ChatMessage` ([src/components/ChatMessage.tsx](src/components/ChatMessage.tsx)) dispatches on the `content` string of agent messages to render rich components:
- `"progress"` + `data.steps` → `ProgressSteps` (live agent step list)
- `"articles"` + `data.articles` → `ArticleCard` list (PubMed article cards)
- `"evidence-table"` + `data` → `EvidenceTable` (structured evidence matrix with columns: study, design, n, outcome, effect, pvalue, limitations)
- `"synthesis"` + `data` → `NarrativeSynthesis` (full synthesis text + positive/negative/neutral verdict)
- anything else → `MarkdownRenderer` (custom markdown parser)

`MarkdownRenderer` ([src/components/MarkdownRenderer.tsx](src/components/MarkdownRenderer.tsx)) is a hand-rolled markdown parser — it is NOT using `react-markdown`. It handles headings, lists, blockquotes, tables, bold, links, and a set of hardcoded clinical section headers (`Key Findings`, `Consistent Results`, `Discrepancies`, `Evidence Gaps`) that get special icon treatment.

### Design system

Light-mode only. Design language is "Clinical Minimalist": white cards, slate-900 text, indigo-600 primary accent. Glassmorphism is intentionally avoided (supervisor requirement).

Styling layers:
1. **Tailwind** — utility classes throughout; primary color palette is indigo/violet/cyan/emerald/slate
2. **CSS custom classes** in [src/index.css](src/index.css) — semantic class names used across components:
   - `.hero-premium` — landing page background (radial gradient mesh)
   - `.navbar-glass` — frosted glass navbar
   - `.card-elevated` — white card with indigo shadow
   - `.feat-card`, `.stat-card` — feature/stat card variants
   - `.search-wrap` — search input container
   - `.btn-primary` — indigo gradient button
   - `.bubble-agent` — agent chat bubble
   - `.text-gradient-vivid`, `.text-gradient-pro` — indigo-to-violet gradient text
   - `.badge-gradient` — header badge
   - `.agent-workspace`, `.cta-gradient` — page-level backgrounds
3. **shadcn/ui** components in [src/components/ui/](src/components/ui/) — Radix UI primitives with Tailwind variants, used for Table, Dialog, Toast, etc.
4. **Framer Motion** — all entry animations; `whileHover` micro-interactions on cards

Fonts: `Inter` (sans) and `IBM Plex Mono` (mono), loaded via CSS/Google Fonts.

### Session management

The `Search` page maintains a `sessionRef` (a `thread-<timestamp>` string) that persists across follow-up questions in the same browser session. An `AbortController` ref cancels the previous SSE stream when a new query is submitted.
