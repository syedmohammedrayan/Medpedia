# Medpedia Frontend (BioLit Insight AI)

The React, TypeScript, and Vite frontend for the Medpedia Autonomous Clinical Research Assistant.

## Features

- **Editorial Masthead**: Clean, magazine-inspired horizontal navigation with persistent scrolling.
- **Auditable Agent Trace**: Real-time Server-Sent Events (SSE) streaming progress milestones and tokens directly from the LangGraph backend.
- **Evidence Matrices & Adaptive Cards**: Structured clinical trial data, GRADE certainty badges, and interactive synthesis reports.
- **Responsive Workspace**: Seamlessly scales across desktop, tablet, and mobile devices.

## Development

```bash
# Install dependencies
npm install

# Start local dev server
npm run dev
```

The app will be available at `http://localhost:8080/` (or port configured in `vite.config.ts`).

## Build

```bash
# Type check and production build
npm run build
```
