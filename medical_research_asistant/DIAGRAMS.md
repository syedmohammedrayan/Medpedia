# MedGraph — System Architecture Diagrams

---

## Figure 1: Complete System Architecture (Full Color)

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'primaryColor': '#1565C0',
    'primaryTextColor': '#FFFFFF',
    'primaryBorderColor': '#0D47A1',
    'lineColor': '#455A64',
    'secondaryColor': '#E3F2FD',
    'tertiaryColor': '#F3F4F6',
    'fontSize': '15px',
    'fontFamily': 'arial'
  }
}}%%

graph TB

    %% ── USER ──
    USER(["👤  Clinician / Researcher\n      Free-text Clinical Query"])

    %% ── FRONTEND ──
    subgraph FE["  🖥️  Web Frontend  "]
        WUI["Query Input\n+ Live Streaming\nResult Display"]
    end

    %% ── API LAYER ──
    subgraph APIL["  🌐  FastAPI REST Layer  (src/api/)  "]
        EP1(["POST  /research/start\n─────────────────\nthread_id + query"])
        EP2(["POST  /research/resume-email\n──────────────────────────\nthread_id + email"])
        SSE["Server-Sent Events\nastream_events v2\n────────────────\nnode_start · token\nnode_end · interrupt"]
    end

    %% ── LANGGRAPH PIPELINE ──
    subgraph LG["  🔄  LangGraph Agentic Pipeline  —  src/agent/graph.py  "]

        subgraph N1["  Node ①  med_query_ingestor  "]
            RA["🤖  ReAct Agent\nGemini 2.5 Flash\n(OpenRouter)"]
            PT["🔧  pubmed_to_pmc_\nfull_text_search\ntool"]
            RA <-->|"Tool\nInvocation"| PT
        end

        subgraph N2["  Node ②  med_evidence_builder  "]
            DL["🧠  Direct LLM Call\nGemini 2.5 Flash\n(no tool loop)"]
            EC["📊  Evidence Classifier\n────────────────\n10 Study Type Categories\n🟢 Strong · 🟡 Moderate\n🔴 Preliminary"]
            DL --> EC
        end

        subgraph N3["  Node ③  email_collector  "]
            IR["⏸️  interrupt()\nHuman-in-the-Loop\nPauses graph execution\nawaits user input"]
        end

        subgraph N4["  Node ④  med_email_dispatcher  "]
            TC["⚡  Direct Tool Call\n(No LLM — avoids\ntoken limit issue)"]
            SE["📧  send_email tool\nMarkdown → Styled HTML\nMedical Disclaimer Footer"]
            TC --> SE
        end

        N1 -->|"state.articles_report\n10 article cards"| N2
        N2 -->|"state.evidence_report\n10 evidence cards"| N3
        N3 -->|"state.recipient_email\nresume via API"| N4
    end

    %% ── NCBI ──
    subgraph NCBI["  🔬  NCBI E-Utilities API  "]
        ES["esearch\nQuery → PMIDs\n(retmax=10)"]
        EM["esummary\nPMIDs → Metadata\nTitle·Authors·Journal"]
        EF["efetch\nPMIDs → XML\nAbstract Text"]
        ES -->|"PMID list"| EM -->|"metadata"| EF
    end

    %% ── STATE ──
    subgraph MEM["  💾  MedResearchState  +  MemorySaver  "]
        ST["messages  │  articles_report\nevidence_report  │  recipient_email\nemail_status\n──────────────────────\nThread-based Checkpointing\nEnables interrupt resumption"]
    end

    %% ── EMAIL ──
    subgraph MAIL["  📬  Email Delivery  "]
        SMTP["SMTP Server\nGmail · TLS 587"]
        INB["User Inbox\nStyled HTML Report\n+ Evidence Badges\n+ Article Links"]
        SMTP -->|"TLS delivery"| INB
    end

    %% ── CONNECTIONS ──
    USER -->|"clinical query"| WUI
    WUI -->|"HTTP POST"| EP1
    EP1 --> SSE
    SSE -->|"stream events"| WUI
    SSE -->|"invoke graph"| LG

    PT <-->|"REST · NCBI API Key"| NCBI

    N4 -->|"HTML email"| SMTP

    C1 -->|"pause · emit interrupt event"| SSE
    SSE -->|"interrupt prompt"| WUI
    WUI -->|"user enters email"| EP2
    EP2 -->|"resume graph"| IR

    LG <-->|"read / write state"| MEM

    %% ── STYLES ──
    classDef userStyle fill:#0277BD,stroke:#01579B,color:#fff,rx:20px
    classDef feStyle fill:#5C6BC0,stroke:#3949AB,color:#fff
    classDef apiStyle fill:#00838F,stroke:#006064,color:#fff
    classDef node1Style fill:#1B5E20,stroke:#2E7D32,color:#fff
    classDef node2Style fill:#E65100,stroke:#BF360C,color:#fff
    classDef node3Style fill:#4A148C,stroke:#6A1B9A,color:#fff
    classDef node4Style fill:#880E4F,stroke:#AD1457,color:#fff
    classDef ncbiStyle fill:#33691E,stroke:#558B2F,color:#fff
    classDef memStyle fill:#37474F,stroke:#546E7A,color:#fff
    classDef mailStyle fill:#1A237E,stroke:#283593,color:#fff

    class USER userStyle
    class WUI feStyle
    class EP1,EP2,SSE apiStyle
    class RA,PT node1Style
    class DL,EC node2Style
    class IR node3Style
    class TC,SE node4Style
    class ES,EM,EF ncbiStyle
    class ST memStyle
    class SMTP,INB mailStyle
```

---

## Figure 2: Four-Node Sequential Pipeline (Left → Right)

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'primaryColor': '#1565C0',
    'primaryTextColor': '#fff',
    'lineColor': '#455A64',
    'fontSize': '14px'
  }
}}%%

flowchart LR

    S(["▶ START\nUser Query"])

    subgraph N1["① med_query_ingestor\n🤖 ReAct Agent · Gemini 2.5 Flash"]
        direction TB
        A["🔍 Parse clinical query\n+ identify entities"]
        B["📚 Expand with\nMeSH terminology"]
        C["⚙️ Invoke PubMed\nE-utilities tool"]
        D["📄 Format 10\nstructured article cards"]
        A --> B --> C --> D
    end

    subgraph N2["② med_evidence_builder\n🧠 Direct LLM · Gemini 2.5 Flash"]
        direction TB
        E["📥 Receive articles_report"]
        F["🔬 Classify study type\n10 categories"]
        G["🏷️ Assign evidence badge\n🟢 🟡 🔴"]
        H["📊 Generate\nevidence cards"]
        E --> F --> G --> H
    end

    subgraph N3["③ email_collector\n⏸️ Human-in-the-Loop"]
        direction TB
        I["interrupt()\nPause execution"]
        J["💬 Prompt user\nfor email address"]
        K["✅ Store email\nResume graph"]
        I --> J --> K
    end

    subgraph N4["④ med_email_dispatcher\n⚡ Direct Tool Call · No LLM"]
        direction TB
        L["🔄 Convert Markdown\n→ Styled HTML"]
        M["🎨 Apply email\ntemplate + footer"]
        N["📧 Send via\nSMTP · TLS 587"]
        L --> M --> N
    end

    E2(["⏹ END\nEmail Delivered ✅"])

    S --> N1 --> N2 --> N3 --> N4 --> E2

    classDef startEnd fill:#263238,stroke:#37474F,color:#fff
    classDef n1 fill:#1B5E20,stroke:#388E3C,color:#fff
    classDef n2 fill:#E65100,stroke:#F57C00,color:#fff
    classDef n3 fill:#4A148C,stroke:#7B1FA2,color:#fff
    classDef n4 fill:#880E4F,stroke:#C2185B,color:#fff
    classDef step fill:#ECEFF1,stroke:#90A4AE,color:#263238

    class S,E2 startEnd
    class A,B,C,D n1
    class E,F,G,H n2
    class I,J,K n3
    class L,M,N n4
```

---

## Figure 3: End-to-End Sequence Diagram

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'actorBkg': '#1565C0',
    'actorTextColor': '#fff',
    'actorBorderColor': '#0D47A1',
    'signalColor': '#455A64',
    'signalTextColor': '#263238',
    'labelBoxBkgColor': '#E3F2FD',
    'fontSize': '13px'
  }
}}%%

sequenceDiagram
    autonumber

    actor User as 👤 User
    participant UI as 🖥️ Frontend
    participant API as 🌐 FastAPI
    participant N1 as 🤖 Node 1<br/>Query Ingestor
    participant NCBI as 🔬 NCBI<br/>PubMed
    participant N2 as 🧠 Node 2<br/>Evidence Builder
    participant N3 as ⏸️ Node 3<br/>Email Collector
    participant N4 as ⚡ Node 4<br/>Dispatcher
    participant SMTP as 📧 SMTP

    User->>UI: Enter clinical question
    UI->>API: POST /research/start {query, thread_id}
    API-->>UI: SSE stream opened

    Note over API,N1: Graph execution begins
    API->>N1: Invoke med_query_ingestor
    activate N1
    N1->>NCBI: esearch (query + MeSH terms)
    NCBI-->>N1: [PMID list — up to 10]
    N1->>NCBI: esummary (PMIDs)
    NCBI-->>N1: [Title, Authors, Journal, Date]
    N1->>NCBI: efetch (PMIDs → XML)
    NCBI-->>N1: [Abstract text — XML]
    N1-->>API: articles_report (10 structured cards)
    deactivate N1
    API-->>UI: SSE: node_end (Node 1)

    API->>N2: Invoke med_evidence_builder
    activate N2
    N2->>N2: Classify each article (10 study types)
    N2->>N2: Assign 🟢🟡🔴 evidence badge
    N2-->>API: evidence_report (10 evidence cards)
    deactivate N2
    API-->>UI: SSE: node_end (Node 2)

    API->>N3: Invoke email_collector
    activate N3
    N3->>N3: interrupt() — pause graph
    N3-->>API: SSE: interrupt event
    API-->>UI: SSE: interrupt (show email prompt)
    UI-->>User: 📧 "Please enter your email address"
    deactivate N3

    User->>UI: Enter email address
    UI->>API: POST /research/resume-email {email, thread_id}
    API->>N3: Resume graph with email
    activate N3
    N3->>N3: Store recipient_email in state
    deactivate N3

    API->>N4: Invoke med_email_dispatcher
    activate N4
    N4->>N4: Markdown → Styled HTML conversion
    N4->>SMTP: send_email (HTML report)
    SMTP-->>N4: Delivery confirmed ✅
    N4-->>API: email_status = "sent"
    deactivate N4

    API-->>UI: SSE: node_end (Node 4) — Done
    UI-->>User: ✅ "Email sent successfully"
    SMTP-->>User: 📬 Styled HTML evidence report
```

---

## Figure 4: State Data Flow Through Pipeline

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'primaryColor': '#37474F',
    'primaryTextColor': '#fff',
    'lineColor': '#546E7A',
    'fontSize': '14px'
  }
}}%%

flowchart TD

    Q(["🔤 Free-text Clinical Query\ne.g. 'Latest treatments for Type 2 Diabetes?'"])

    subgraph STATE["💾  MedResearchState  —  MemorySaver Checkpointer"]
        direction LR
        S1["📩 messages\nHumanMessage\n(original query)"]
        S2["📄 articles_report\n10 structured\narticle cards\n─────────────\nTitle · Authors\nJournal · Date\nAbstract · URL"]
        S3["📊 evidence_report\n10 classified\nevidence cards\n─────────────\nStudy Type\nEvidence Badge\nKey Finding\nTakeaway"]
        S4["📧 recipient_email\nUser-provided\nvia interrupt()"]
        S5["✅ email_status\nSMTP delivery\nconfirmation"]
    end

    Q --> S1

    S1 -->|"Node 1\nReAct Agent\n~35s"| S2
    S2 -->|"Node 2\nDirect LLM\n~8s"| S3
    S3 -->|"Node 3\nHuman Input\n(variable)"| S4
    S4 -->|"Node 4\nDirect Tool\n~2s"| S5

    S2 --> OUT1["📋 Article Cards\n─────────────────\n• Title & Authors\n• Journal & Date\n• Abstract Summary\n• PubMed URL"]
    S3 --> OUT2["🏷️ Evidence Cards\n─────────────────\n• 🟢 Strong Evidence\n• 🟡 Moderate Evidence\n• 🔴 Preliminary\n• Plain-English Takeaway"]
    S5 --> OUT3["📬 Email Delivered\n─────────────────\n• Styled HTML\n• Inter font\n• Blue theme\n• Medical disclaimer"]

    classDef queryStyle fill:#0277BD,stroke:#01579B,color:#fff
    classDef stateStyle fill:#37474F,stroke:#546E7A,color:#fff
    classDef outStyle fill:#1B5E20,stroke:#388E3C,color:#fff

    class Q queryStyle
    class S1,S2,S3,S4,S5 stateStyle
    class OUT1,OUT2,OUT3 outStyle
```

---

## Figure 5: Evidence Classification Taxonomy

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'primaryColor': '#1565C0',
    'primaryTextColor': '#fff',
    'lineColor': '#455A64',
    'fontSize': '14px'
  }
}}%%

graph TD

    ART(["📄 Retrieved PubMed Article"])

    ART --> CLF{"🧠 LLM Evidence\nClassifier\nGemini 2.5 Flash"}

    CLF --> T1["📚 Systematic Review\n/ Meta-Analysis"]
    CLF --> T2["💊 Randomized\nControlled Trial"]
    CLF --> T3["👥 Cohort Study\nProspective / Retrospective"]
    CLF --> T4["🔬 Case-Control\nStudy"]
    CLF --> T5["📊 Cross-Sectional\nStudy"]
    CLF --> T6["📋 Case Report\n/ Case Series"]
    CLF --> T7["📖 Narrative\nReview"]
    CLF --> T8["🧬 GWAS Study"]
    CLF --> T9["🐭 Lab / Animal\nStudy"]
    CLF --> T10["📜 Clinical\nGuideline"]

    T1 --> STRONG["🟢  STRONG EVIDENCE\n────────────────────────\nHigh methodological quality\nLarge sample sizes\nLow risk of bias\nGeneralizable findings"]
    T2 --> STRONG

    T3 --> MOD["🟡  MODERATE EVIDENCE\n────────────────────────\nControlled methodology\nSome bias risk\nModerate generalizability"]
    T4 --> MOD
    T10 --> MOD

    T5 --> PREL["🔴  PRELIMINARY\n────────────────────────\nLimited causal inference\nSmall samples or models\nNeeds further validation"]
    T6 --> PREL
    T7 --> PREL
    T8 --> PREL
    T9 --> PREL

    classDef articleStyle fill:#0277BD,stroke:#01579B,color:#fff
    classDef classifierStyle fill:#37474F,stroke:#546E7A,color:#fff
    classDef typeStyle fill:#E8EAF6,stroke:#5C6BC0,color:#1A237E
    classDef strongStyle fill:#1B5E20,stroke:#2E7D32,color:#fff
    classDef modStyle fill:#E65100,stroke:#BF360C,color:#fff
    classDef prelStyle fill:#B71C1C,stroke:#C62828,color:#fff

    class ART articleStyle
    class CLF classifierStyle
    class T1,T2,T3,T4,T5,T6,T7,T8,T9,T10 typeStyle
    class STRONG strongStyle
    class MOD modStyle
    class PREL prelStyle
```

---

## Figure 6: Technology Stack

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'primaryColor': '#1565C0',
    'lineColor': '#455A64',
    'fontSize': '14px'
  }
}}%%

graph LR

    subgraph CORE["Core AI / Orchestration"]
        LG["LangGraph 1.0+\nGraph Orchestration"]
        LC["LangChain Core\nTool + Message API"]
        OR["OpenRouter\nAPI Gateway"]
        GM["Google Gemini\n2.5 Flash\nLLM Backend"]
        LG --> LC --> OR --> GM
    end

    subgraph DATA["Data Layer"]
        NCBI2["NCBI E-Utilities\nPubMed REST API"]
        MEM2["MemorySaver\nIn-Memory Checkpointer"]
    end

    subgraph WEB["Web / API Layer"]
        FA["FastAPI\nREST Framework"]
        UV["Uvicorn\nASGI Server"]
        SSE2["SSE Streaming\nastream_events v2"]
        FA --> UV
        FA --> SSE2
    end

    subgraph EMAIL2["Email Layer"]
        SMTP2["smtplib\nSMTP Client"]
        HTML["html.parser\nMarkdown → HTML"]
        SMTP2 --> HTML
    end

    subgraph DEV["Developer Tools"]
        LGSV["LangGraph Studio\nVisual Debugger"]
        LSM["LangSmith\nObservability"]
        UV2["uv\nPackage Manager"]
    end

    CORE --> DATA
    CORE --> WEB
    CORE --> EMAIL2

    classDef coreStyle fill:#1565C0,stroke:#0D47A1,color:#fff
    classDef dataStyle fill:#1B5E20,stroke:#2E7D32,color:#fff
    classDef webStyle fill:#4A148C,stroke:#6A1B9A,color:#fff
    classDef emailStyle fill:#880E4F,stroke:#AD1457,color:#fff
    classDef devStyle fill:#37474F,stroke:#546E7A,color:#fff

    class LG,LC,OR,GM coreStyle
    class NCBI2,MEM2 dataStyle
    class FA,UV,SSE2 webStyle
    class SMTP2,HTML emailStyle
    class LGSV,LSM,UV2 devStyle
```

---

## How to Export as High-Quality PNG/SVG

### Option 1: Mermaid Live Editor (Recommended for Paper)
1. Go to **mermaid.live**
2. Paste any diagram code block
3. Click **PNG** or **SVG** — download
4. Use SVG for best print quality

### Option 2: VS Code Preview
1. Install: **Markdown Preview Mermaid Support**
2. Open this file → Press `Ctrl+Shift+V`
3. Right-click any diagram → Save Image

### Option 3: GitHub Auto-Render
Push to GitHub — all diagrams render automatically in `.md` files.

---

**For Paper Submission:**
- Use **Figure 1** as main architecture diagram
- Use **Figure 2** as pipeline flow figure
- Use **Figure 3** as sequence diagram in Implementation section
- Use **Figure 5** as evidence taxonomy in System Design section
