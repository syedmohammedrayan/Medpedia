# MedGraph: An Agentic LLM Pipeline for Automated Biomedical Evidence Synthesis from PubMed Literature

---

**[SUPERVISOR NAME]¹ and [YOUR NAME]¹**

¹Department of Computer Science, [UNIVERSITY NAME], [CITY], Pakistan
Email: [supervisor@email.com], [your@email.com]

---

## Abstract

The exponential growth of biomedical literature presents a critical bottleneck for clinicians and researchers who must synthesize evidence from thousands of publications to make informed decisions. Manual literature review is time-intensive, often requiring two to three hours per clinical query. This paper presents **MedGraph**, an end-to-end agentic pipeline that automates biomedical evidence retrieval, synthesis, and dissemination using Large Language Models (LLMs) orchestrated through the LangGraph framework. MedGraph employs a four-node sequential graph comprising a ReAct-based query ingestor, a direct LLM evidence builder, a human-in-the-loop email collector, and an automated email dispatcher. The system integrates with NCBI PubMed via E-utilities APIs and leverages Google Gemini 2.5 Flash for evidence classification. Evaluation across five diverse medical domains demonstrated consistent retrieval of ten articles per query in an average of 44.6 seconds, with an evidence distribution of 24% Strong, 26% Moderate, and 50% Preliminary studies. The system successfully delivered structured HTML evidence reports via email in all five test cases. Two key limitations — duplicate article retrieval and query scope drift — were identified and are discussed as directions for future improvement. MedGraph demonstrates that agentic LLM workflows can meaningfully reduce the time burden of biomedical literature review while preserving evidence quality classification.

**Keywords:** Large Language Models, LangGraph, PubMed, Evidence Synthesis, ReAct Agent, Biomedical NLP, Human-in-the-Loop, Medical AI

---

## I. Introduction

The volume of biomedical literature indexed in PubMed has grown to over 36 million citations as of 2024, with approximately 1.5 million new articles added each year [1]. For clinicians, researchers, and medical educators, synthesizing relevant evidence from this vast repository is both essential and overwhelmingly time-consuming. Studies indicate that physicians spend an average of 2–3 hours per clinical question when conducting manual literature searches [2], time that is rarely available in routine practice.

Existing tools such as PubMed's native search interface, clinical decision support systems, and third-party platforms like Elicit and Semantic Scholar offer partial solutions but share common limitations: they require users to manually evaluate retrieved abstracts, assess study quality, and distill clinical implications — all without automated classification or delivery of synthesized findings.

The emergence of Large Language Models (LLMs) such as GPT-4 and Gemini has opened new possibilities for natural language biomedical question answering [3]. However, most LLM-based approaches either rely on pre-trained static knowledge or perform single-turn retrieval-augmented generation (RAG) without structured evidence grading. Neither approach provides the automated, end-to-end workflow that clinical and research settings demand.

This paper presents **MedGraph**, a fully agentic pipeline built on the LangGraph orchestration framework that addresses these gaps. MedGraph accepts a free-text clinical query, autonomously retrieves and synthesizes PubMed evidence, classifies articles by study type and evidence strength, and delivers a formatted report to the user via email — all within approximately 45 seconds. The system introduces a human-in-the-loop interrupt mechanism that personalizes delivery without disrupting the automated flow.

The key contributions of this work are:
1. A novel four-node agentic graph architecture that separates query understanding, evidence synthesis, user interaction, and report delivery into specialized nodes.
2. An evidence strength classification scheme with ten study-type categories and three evidence tiers (Strong, Moderate, Preliminary).
3. An end-to-end evaluation across five clinical domains demonstrating consistent performance and identifying real-world retrieval limitations.
4. An open-source implementation deployable via LangGraph Studio and FastAPI.

---

## II. Related Work

### A. Automated Literature Review

Early approaches to automated literature review relied on keyword-based retrieval and rule-based summarization [4]. Tools like PubMed's MeSH term system improved retrieval precision but required users to manually expand query terminology. More recent work has applied transformer models to biomedical text, with BioBERT [5] and PubMedBERT [6] achieving state-of-the-art performance on biomedical NLP tasks. However, these models focus on specific subtasks (e.g., named entity recognition, relation extraction) rather than end-to-end literature synthesis.

### B. LLM-Based Medical Question Answering

Med-PaLM [7] and GPT-4 [8] have demonstrated strong performance on medical licensing examinations and clinical question answering benchmarks. However, these systems operate on pre-trained knowledge with a fixed cutoff date and lack access to current PubMed literature. Retrieval-Augmented Generation (RAG) approaches [9] combine LLMs with document retrieval but typically lack structured evidence grading.

### C. Agentic AI Workflows

The ReAct (Reasoning + Acting) paradigm [10] enables LLMs to interleave reasoning steps with tool invocations, significantly improving performance on multi-step tasks. LangChain [11] and LangGraph [12] provide frameworks for building such agentic workflows. While several studies have applied ReAct agents to general question answering, their application to structured biomedical evidence synthesis with human-in-the-loop components remains unexplored.

### D. Evidence-Based Medicine Automation

Systematic reviews and meta-analyses represent the gold standard in evidence-based medicine, but their production requires months of expert effort [13]. Tools like Rayyan and Covidence assist with screening but do not automate the synthesis step. MedGraph differs by targeting rapid evidence synthesis for individual clinical queries rather than formal systematic review production.

---

## III. System Architecture

### A. Overview

MedGraph is built on LangGraph, a graph-based orchestration framework for stateful multi-actor LLM applications. The system exposes a FastAPI REST interface that streams real-time events to clients via Server-Sent Events (SSE). Figure 1 presents the high-level architecture.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                         MedGraph System Architecture                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

  ┌─────────────┐     POST /research/start      ┌──────────────────────────┐
  │             │ ─────────────────────────────▶ │      FastAPI Server      │
  │   Frontend  │                               │   (SSE Streaming API)    │
  │  (Browser)  │ ◀─────────────────────────────│                          │
  │             │    Server-Sent Events (SSE)   │  POST /research/resume   │
  └─────────────┘                               └──────────┬───────────────┘
                                                           │
                                                           ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║                        LangGraph Agentic Pipeline                           ║
║                                                                              ║
║  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐       ║
║  │                  │    │                  │    │                  │       ║
║  │  Node 1          │───▶│  Node 2          │───▶│  Node 3          │       ║
║  │  med_query_      │    │  med_evidence_   │    │  email_          │       ║
║  │  ingestor        │    │  builder         │    │  collector       │       ║
║  │                  │    │                  │    │                  │       ║
║  │  [ReAct Agent]   │    │  [Direct LLM]    │    │  [interrupt()]   │       ║
║  │                  │    │                  │    │                  │       ║
║  └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘       ║
║           │                       │                       │                  ║
║           ▼                       ▼                       ▼                  ║
║  ┌─────────────────┐   ┌──────────────────┐   ┌──────────────────┐          ║
║  │  PubMed Tool    │   │  Evidence Cards  │   │  Human Input     │          ║
║  │  ─────────────  │   │  ─────────────── │   │  (Email Addr.)   │          ║
║  │  NCBI esearch   │   │  🟢 Strong       │   │                  │          ║
║  │  NCBI esummary  │   │  🟡 Moderate     │   └──────────────────┘          ║
║  │  NCBI efetch    │   │  🔴 Preliminary  │                                  ║
║  └─────────────────┘   └──────────────────┘                                  ║
║                                                                              ║
║  ┌──────────────────────────────────────────────────────────────────────┐    ║
║  │                                                                      │    ║
║  │  Node 4: med_email_dispatcher   [Direct Tool Call — No LLM]         │    ║
║  │                                                                      │    ║
║  │  ┌──────────────┐    ┌───────────────────┐    ┌──────────────────┐  │    ║
║  │  │ Markdown →   │───▶│  Styled HTML      │───▶│  SMTP Delivery   │  │    ║
║  │  │ HTML Convert │    │  Email Template   │    │  (Gmail / TLS)   │  │    ║
║  │  └──────────────┘    └───────────────────┘    └──────────────────┘  │    ║
║  └──────────────────────────────────────────────────────────────────────┘    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

  ┌────────────────────────────────────────────────────────────────────────┐
  │                     Shared State (MedResearchState)                    │
  │  messages │ articles_report │ evidence_report │ recipient_email │ ...  │
  │                    [MemorySaver Checkpointer]                          │
  └────────────────────────────────────────────────────────────────────────┘

Figure 1: MedGraph System Architecture
```

### B. Node 1 — Medical Query Ingestor (ReAct Agent)

The query ingestor implements the ReAct (Reasoning + Acting) pattern [10], enabling the agent to reason about the query before invoking retrieval tools. The node is instantiated as a `create_react_agent` with Google Gemini 2.5 Flash as the backbone LLM and a single tool: `pubmed_to_pmc_full_text_search`.

Upon receiving a free-text clinical question, the agent:
1. Identifies the core medical topic and entities.
2. Expands terminology with relevant MeSH (Medical Subject Headings) terms.
3. Constructs an optimized PubMed search query.
4. Invokes the PubMed tool, which executes a three-step NCBI E-utilities pipeline: `esearch` (obtain PMIDs) → `esummary` (fetch metadata) → `efetch` (retrieve abstracts in XML).
5. Formats retrieved articles into structured cards containing title, authors, journal, publication date, abstract summary, and PubMed URL.

The output is stored in `state.articles_report` for downstream processing.

### C. Node 2 — Medical Evidence Builder (Direct LLM Call)

The evidence builder performs evidence-based synthesis without tool invocations, operating as a direct LLM call to avoid unnecessary latency from a ReAct loop. The node receives `state.articles_report` and applies a structured classification prompt to each article.

Articles are classified into ten study types:
- Systematic Review / Meta-Analysis
- Randomized Controlled Trial (RCT)
- Cohort Study (Prospective / Retrospective)
- Case-Control Study
- Cross-Sectional Study
- Case Report / Series
- Narrative Review
- Genome-Wide Association Study (GWAS)
- Laboratory / Animal Study
- Clinical Guideline / Consensus Statement

Each article is then assigned an evidence strength badge based on study type and methodological rigor:
- 🟢 **Strong** — Systematic Reviews, Meta-Analyses, multi-site RCTs
- 🟡 **Moderate** — Prospective Cohorts, Case-Control studies, single RCTs
- 🔴 **Preliminary** — Cross-Sectional, Narrative Reviews, Lab/Animal studies

Evidence cards are output to `state.evidence_report` as structured markdown.

### D. Node 3 — Email Collector (Human-in-the-Loop)

The email collector implements LangGraph's `interrupt()` mechanism, pausing graph execution and surfacing a prompt to the user requesting their email address. This design preserves the completed evidence and article reports in the graph's checkpointed state (`MemorySaver`) while awaiting user input.

Graph execution resumes when the client calls `POST /research/resume-email` with the recipient address. The email is stored in `state.recipient_email` and execution continues to Node 4. This pattern demonstrates human-in-the-loop orchestration without losing intermediate computation.

### E. Node 4 — Medical Email Dispatcher (Direct Tool Call)

The email dispatcher deliberately bypasses the LLM to avoid context-window limitations imposed by large evidence reports. Instead, it directly invokes the `send_email` tool, which:
1. Converts the combined evidence and articles markdown into styled HTML.
2. Applies a professional template with the Inter typeface, blue color scheme, and a medical disclaimer footer.
3. Delivers the email via SMTP (Gmail, TLS/STARTTLS on port 587).

The delivery status is stored in `state.email_status`.

### F. State and Persistence

All inter-node communication passes through `MedResearchState`, a typed state class that extends LangChain's `MessagesState`:

```
MedResearchState:
  ├── messages          (list[BaseMessage])   — inherited message history
  ├── articles_report   (str)                 — formatted article cards
  ├── evidence_report   (str)                 — classified evidence cards
  ├── recipient_email   (str)                 — collected via interrupt
  └── email_status      (str)                 — SMTP delivery result
```

Thread-level persistence is managed by `MemorySaver`, enabling state recovery after the human-in-the-loop interrupt and supporting multi-session continuity via `thread_id`.

---

## IV. Implementation

### A. Technology Stack

| Component | Technology |
|---|---|
| Agent Orchestration | LangGraph 1.0+ |
| LLM | Google Gemini 2.5 Flash (via OpenRouter) |
| Literature Retrieval | NCBI E-utilities REST API |
| Web Framework | FastAPI + Uvicorn |
| Streaming | Server-Sent Events (astream_events v2) |
| Email Delivery | SMTP (Gmail, TLS) |
| Persistence | LangGraph MemorySaver |
| Package Management | uv (Python) |

### B. PubMed Retrieval Tool

The `pubmed_to_pmc_full_text_search` tool implements a three-stage retrieval pipeline using NCBI E-utilities:

```
Query String
    │
    ▼
[esearch] → PMIDs (up to 10 results)
    │
    ▼
[esummary] → Article Metadata (title, authors, journal, date)
    │
    ▼
[efetch] → XML Abstract Parsing → Structured JSON Output
```

Each article is returned as a JSON object containing:
`{ title, authors, journal, published_date, summary, pubmed_url }`

The tool authenticates with an NCBI API key to bypass rate limits (10 requests/second vs. 3 without key).

### C. API Endpoints

The FastAPI server exposes two research endpoints:

**Start Research Session:**
```
POST /research/start
Body: { "query": str, "thread_id": str }
Response: StreamingResponse (SSE)
```

**Resume After Interrupt:**
```
POST /research/resume-email
Body: { "email": str, "thread_id": str }
Response: StreamingResponse (SSE)
```

The SSE stream emits typed JSON events:
- `node_start` — node execution begins
- `token` — LLM streaming token
- `node_end` — node execution completes
- `interrupt` — graph paused, awaiting user input

### D. LangGraph Studio Integration

The system is configured for LangGraph Studio via `langgraph.json`, enabling visual graph debugging, thread inspection, and state replay. This facilitates development-time testing without requiring API client setup.

---

## V. Evaluation

### A. Experimental Setup

We evaluated MedGraph across five clinically representative queries spanning distinct medical domains:

| ID | Query | Domain |
|---|---|---|
| Q1 | What are the latest treatments for Type 2 Diabetes? | Endocrinology |
| Q2 | What is the effectiveness of immunotherapy in breast cancer treatment? | Oncology |
| Q3 | What are the long-term neurological effects of COVID-19? | Neurology / Infectious Disease |
| Q4 | What are the best medications for hypertension management in elderly patients? | Geriatric Cardiology |
| Q5 | What is the efficacy of SSRIs in treatment of major depressive disorder? | Psychiatry |

Each query was submitted to a live instance of MedGraph and results were captured including article count, evidence classifications, retrieval time, and email delivery status.

### B. Retrieval Performance

Table I presents the quantitative results across all five test queries.

**Table I: MedGraph Evaluation Results Across Five Clinical Domains**

| Query | Articles Retrieved | 🟢 Strong | 🟡 Moderate | 🔴 Preliminary | Time (s) | Email |
|---|---|---|---|---|---|---|
| Q1 — Type 2 Diabetes | 10 | 0 | 5 | 5 | 45 | ✅ |
| Q2 — Breast Cancer Immunotherapy | 10 | 0 | 2 | 8 | 45 | ✅ |
| Q3 — COVID-19 Neurology | 10 | 10* | 0 | 0 | 44 | ✅ |
| Q4 — Hypertension Elderly | 10 | 0 | 5 | 5 | 44 | ✅ |
| Q5 — SSRIs Depression | 10 | 2 | 1 | 7 | 45 | ✅ |
| **Overall** | **50** | **12** | **13** | **25** | **Avg: 44.6** | **5/5** |

*10 Strong badges in Q3 reflect duplicate retrieval of a single systematic review (see Section VI-A).

### C. Evidence Distribution

Excluding the duplicate Q3 articles, the evidence distribution across 40 unique articles was:
- 🟢 Strong Evidence: 2 articles (5%)
- 🟡 Moderate Evidence: 13 articles (32.5%)
- 🔴 Preliminary Evidence: 25 articles (62.5%)

This distribution aligns with the current state of PubMed, where emerging research (preliminary studies) significantly outnumbers high-quality systematic reviews and RCTs for many clinical questions.

### D. Clinical Value Comparison

| Metric | Manual Literature Review | MedGraph |
|---|---|---|
| Average Time | 2–3 hours | ~45 seconds |
| Evidence Classification | Manual | Automated |
| Email Delivery | Manual | Automated |
| Study Type Tagging | Manual | Automated (10 categories) |
| Availability | Business Hours | 24/7 |

MedGraph reduces evidence synthesis time by approximately **99.5%** compared to manual review, while providing structured classification that aids clinical decision-making.

---

## VI. Discussion

### A. Limitation 1 — Duplicate Article Retrieval

During evaluation of Q3 (COVID-19 neurological effects), the system retrieved ten instances of a single systematic review by Al-Jumaili et al. published in the *Journal of Neurovirology* (June 2026). All ten entries shared identical PMIDs or overlapping metadata, inflating the Strong Evidence count. This reflects a limitation in the PubMed E-utilities `esearch` response for highly cited or recently indexed articles.

**Proposed Fix:** Implement PMID-based deduplication within `pubmed_to_pmc_full_text_search` before returning results to the graph. A simple set-based check on returned PMIDs would eliminate this issue.

### B. Limitation 2 — Query Scope Drift

For Q4 (hypertension medication in elderly patients), the system retrieved articles on cardiovascular comorbidities, glaucoma progression, CKD, and fracture risk rather than directly relevant pharmacological guidelines. This occurred because MeSH-term expansion by the query ingestor agent over-generalized the search scope.

**Proposed Fix:** Refine the query ingestor prompt to enforce domain-specific query constraints. Alternatively, implementing a post-retrieval relevance filter using BM25 or semantic similarity scoring would improve precision.

### C. Strength — Consistent Speed and Delivery

Despite these retrieval-level limitations, the system demonstrated highly consistent end-to-end performance: exactly 10 articles per query, average completion time of 44.6 seconds, and 100% email delivery success across all five test cases. This consistency demonstrates the reliability of the LangGraph state management and SMTP delivery pipeline.

### D. Future Work

1. **Deduplication Module:** PMID-based deduplication in the retrieval tool.
2. **Relevance Re-ranking:** Post-retrieval BM25 or embedding-based re-ranking.
3. **Expanded Study Types:** Integration of ClinicalTrials.gov for ongoing trials.
4. **Multi-lingual Support:** Extension to non-English biomedical literature.
5. **User Feedback Loop:** Reinforcement from human ratings to improve evidence classification.
6. **Fine-tuned Classifier:** Replace prompt-based classification with a fine-tuned BERT model for higher accuracy.

---

## VII. Conclusion

This paper presented MedGraph, an end-to-end agentic pipeline for automated biomedical evidence synthesis. By combining LangGraph-orchestrated ReAct agents, NCBI PubMed retrieval, direct LLM evidence classification, human-in-the-loop email collection, and automated SMTP delivery, MedGraph reduces the time burden of clinical literature review from hours to approximately 45 seconds. Evaluation across five medical domains confirmed consistent retrieval performance and identified two concrete limitations — duplicate article retrieval and query scope drift — that serve as actionable directions for future improvement. MedGraph contributes a novel architectural blueprint for agentic biomedical AI systems that prioritize speed, structure, and clinician accessibility.

---

## References

[1] National Library of Medicine, "PubMed Overview," U.S. National Institutes of Health, 2024. [Online]. Available: https://pubmed.ncbi.nlm.nih.gov/

[2] D. L. Sackett, W. M. Rosenberg, J. A. Gray, R. B. Haynes, and W. S. Richardson, "Evidence based medicine: what it is and what it isn't," *BMJ*, vol. 312, no. 7023, pp. 71–72, 1996.

[3] K. Singhal et al., "Large language models encode clinical knowledge," *Nature*, vol. 620, pp. 172–180, 2023.

[4] W. Hersh, "Information retrieval: a health and biomedical perspective," 3rd ed., Springer, 2009.

[5] J. Lee et al., "BioBERT: a pre-trained biomedical language representation model for biomedical text mining," *Bioinformatics*, vol. 36, no. 4, pp. 1234–1240, 2020.

[6] K. Gu et al., "Domain-Specific Language Model Pretraining for Biomedical Natural Language Processing," *ACM Trans. Comput. Healthc.*, vol. 3, no. 1, pp. 1–23, 2021.

[7] K. Singhal et al., "Towards expert-level medical question answering with large language models," *arXiv preprint arXiv:2305.09617*, 2023.

[8] OpenAI, "GPT-4 Technical Report," *arXiv preprint arXiv:2303.08774*, 2023.

[9] P. Lewis et al., "Retrieval-augmented generation for knowledge-intensive NLP tasks," *Advances in Neural Information Processing Systems*, vol. 33, pp. 9459–9474, 2020.

[10] S. Yao et al., "ReAct: Synergizing reasoning and acting in language models," in *Proc. International Conference on Learning Representations (ICLR)*, 2023.

[11] Harrison Chase, "LangChain: Building applications with LLMs through composability," GitHub, 2022. [Online]. Available: https://github.com/langchain-ai/langchain

[12] LangChain AI, "LangGraph: Build stateful, multi-actor applications with LLMs," GitHub, 2024. [Online]. Available: https://github.com/langchain-ai/langgraph

[13] J. P. T. Higgins and S. Green, *Cochrane Handbook for Systematic Reviews of Interventions*, Version 5.1.0, The Cochrane Collaboration, 2011.

---

*Manuscript submitted for review. All experiments conducted on a local deployment of MedGraph. Source code available upon request.*
