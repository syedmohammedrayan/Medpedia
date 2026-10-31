"""
test_pdf_generator.py
─────────────────────
Unit tests for the publication-grade research PDF generator.
Verifies all non-negotiable content rules, visual branding, article preservation,
and strict content exclusion rules.
"""

import base64
import re
import zlib

from tools.pdf_generator import (
    _parse_markdown_table,
    _sanitize_for_reportlab,
    generate_research_pdf,
)


def extract_pdf_streams(pdf_bytes: bytes) -> str:
    """Extracts and decompresses all text streams from a PDF binary."""
    all_text = []
    # Match everything between stream and endstream
    for match in re.finditer(rb"stream[\r\n]+(.*?)[~]?[\r\n]*endstream", pdf_bytes, re.DOTALL):
        chunk = match.group(1).strip()
        if not chunk.endswith(b"~>"):
            chunk = chunk + b"~>"
        try:
            a85 = base64.a85decode(chunk, adobe=True)
            decomp = zlib.decompress(a85)
            all_text.append(decomp.decode("latin1", errors="ignore"))
        except Exception:
            try:
                decomp = zlib.decompress(chunk)
                all_text.append(decomp.decode("latin1", errors="ignore"))
            except Exception:
                pass
    return "\n".join(all_text)


SAMPLE_EVIDENCE_REPORT = """
## 1. Executive Summary
Recent double-blind clinical trials corroborate therapeutic efficacy of SGLT2 inhibitors in heart failure.

### PICO Evidence Matrix
| Trial | Design | Sample | GRADE Certainty | Outcome |
|---|---|---|---|---|
| DAPA-HF | Double-Blind RCT | 4,744 | High | 26% lower risk of worsening heart failure |
| EMPEROR-Reduced | Double-Blind RCT | 3,730 | High | 25% lower risk of cardiovascular death |

- Significant reduction in hospitalizations across cohorts.
- Favorable safety profile with minimal serious adverse events.
"""

SAMPLE_ARTICLES_REPORT = """
### Article #1
**Title:** Dapagliflozin in Patients with Heart Failure and Reduced Ejection Fraction
**Authors:** McMurray JJV, Solomon SD, Inzucchi SE, Köber L
**Journal:** New England Journal of Medicine
**Published Date:** 2019 Nov 21
**Summary:** [OBJECTIVE] Evaluate dapagliflozin efficacy in HFrEF. [METHODS] 4,744 patients randomized. [RESULTS] Primary outcome in 16.3% vs 21.2% in placebo. [CONCLUSIONS] Dapagliflozin reduced worsening heart failure.
**Links:**
- [PubMed](https://pubmed.ncbi.nlm.nih.gov/31535829/)
---
### Article #2
**Title:** Cardiovascular and Renal Outcomes with Empagliflozin in Heart Failure
**Authors:** Packer M, Anker SD, Butler J, Filippatos G
**Journal:** New England Journal of Medicine
**Published Date:** 2020 Oct 08
**Summary:** [OBJECTIVE] Assess cardiovascular outcomes. [METHODS] 3,730 patients randomized. [RESULTS] 19.4% in empagliflozin vs 24.7% in placebo. [CONCLUSIONS] Empagliflozin reduced combined risk.
**Links:**
- [PubMed](https://pubmed.ncbi.nlm.nih.gov/32865377/)
---
"""


# ── Test 1: Successful PDF Generation with Both Inputs ────────────────────────
def test_generate_research_pdf_success():
    """Verify PDF generates valid non-empty bytes with both report inputs."""
    pdf_bytes = generate_research_pdf(
        evidence_report=SAMPLE_EVIDENCE_REPORT,
        articles_list=SAMPLE_ARTICLES_REPORT,
        query="Compare SGLT2i vs GLP-1 efficacy in heart failure",
        recipient_email="clinician@hospital.edu",
        session_id="SESSION-TEST-123",
    )

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 2000
    assert pdf_bytes.startswith(b"%PDF-")


# ── Test 2: Strict Content Exclusions (Rule 1A) ───────────────────────────────
def test_pdf_strict_content_exclusions():
    """
    NON-NEGOTIABLE RULE 1A:
    The generated PDF must NOT contain:
    - About Medpedia
    - Medpedia website address / URLs
    - GitHub links
    - Technology stack / frameworks / architecture
    - Medical disclaimer
    - AI-generated content disclaimer
    """
    pdf_bytes = generate_research_pdf(
        evidence_report=SAMPLE_EVIDENCE_REPORT,
        articles_list=SAMPLE_ARTICLES_REPORT,
        query="Immunotherapy in glioblastoma",
        recipient_email="researcher@university.edu",
    )

    raw_pdf_text = pdf_bytes.decode("latin1", errors="ignore")

    # Exclusions
    assert "medpedia-smr.vercel.app" not in raw_pdf_text, "Website URL leaked into PDF!"
    assert "About Medpedia" not in raw_pdf_text, "'About Medpedia' leaked into PDF!"
    assert "github.com" not in raw_pdf_text, "GitHub link leaked into PDF!"
    assert "Medical Disclaimer" not in raw_pdf_text, "Medical disclaimer leaked into PDF!"
    assert "AI-generated" not in raw_pdf_text, "AI-generated disclaimer leaked into PDF!"
    assert "FastAPI" not in raw_pdf_text, "Tech stack leaked into PDF!"
    assert "React" not in raw_pdf_text, "Tech stack leaked into PDF!"
    assert "LangGraph" not in raw_pdf_text, "Tech stack leaked into PDF!"
    assert "Python" not in raw_pdf_text, "Tech stack leaked into PDF!"


# ── Test 3: Research Content & Heading Preservation ───────────────────────────
def test_pdf_preserves_research_content_and_headings():
    """Verify supplied headings, clinical findings, and conclusions are preserved."""
    pdf_bytes = generate_research_pdf(
        evidence_report=SAMPLE_EVIDENCE_REPORT,
        articles_list=SAMPLE_ARTICLES_REPORT,
        query="Compare SGLT2i vs GLP-1 efficacy in heart failure",
    )

    extracted_text = extract_pdf_streams(pdf_bytes)

    # Check that research content terms exist in the binary stream
    assert "Executive Evidence Summary" in extracted_text or "Executive Summary" in extracted_text
    assert "DAPA-HF" in extracted_text
    assert "EMPEROR-Reduced" in extracted_text
    assert "Dapagliflozin" in extracted_text
    assert "Empagliflozin" in extracted_text


# ── Test 4: Presence of Primary Source Links ──────────────────────────────────
def test_pdf_contains_pubmed_citations():
    """Verify PubMed/PMC links are extracted and present as clickable links."""
    pdf_bytes = generate_research_pdf(
        evidence_report=SAMPLE_EVIDENCE_REPORT,
        articles_list=SAMPLE_ARTICLES_REPORT,
        query="Heart Failure Treatment",
    )

    raw_pdf_text = pdf_bytes.decode("latin1", errors="ignore")
    assert "pubmed.ncbi.nlm.nih.gov" in raw_pdf_text
    assert "31535829" in raw_pdf_text
    assert "32865377" in raw_pdf_text


# ── Test 5: Clean Sanitization and Formatting ─────────────────────────────────
def test_sanitize_for_reportlab():
    """Verify XML escaping and markdown conversion in helper."""
    raw = "Normal & <bold> **bold** *italic* [Link](https://pubmed.ncbi.nlm.nih.gov/12345/)"
    sanitized = _sanitize_for_reportlab(raw)

    assert "&amp;" in sanitized
    assert "&lt;bold&gt;" in sanitized
    assert "<b>bold</b>" in sanitized
    assert "<i>italic</i>" in sanitized
    assert '<link href="https://pubmed.ncbi.nlm.nih.gov/12345/"' in sanitized


# ── Test 6: Markdown Table Parsing ───────────────────────────────────────────
def test_markdown_table_parsing():
    """Verify markdown tables convert to styled ReportLab Tables with repeat headers."""
    from reportlab.lib.styles import getSampleStyleSheet
    styles = getSampleStyleSheet()

    table_lines = [
        "| Study | Phase | Result |",
        "|---|---|---|",
        "| NCT001 | Phase 3 | Positive |",
        "| NCT002 | Phase 2 | Ongoing |",
    ]

    table = _parse_markdown_table(table_lines, 500, styles["Normal"], styles["Normal"])
    assert table is not None
    assert table.repeatRows == 1


# ── Test 7: Large Report Handling (No Silent Truncation) ──────────────────────
def test_large_report_preservation():
    """Verify large reports with dozens of articles are not silently truncated."""
    large_articles = []
    for i in range(1, 25):
        large_articles.append(f"""
### Article #{i}
**Title:** Comprehensive Study on Therapeutic Intervention #{i}
**Authors:** Author A, Author B, Author C
**Journal:** Journal of Clinical Medicine
**Published Date:** 2024
**Summary:** [OBJECTIVE] Test efficacy #{i}. [METHODS] Randomized trial #{i}. [RESULTS] Statistically significant outcome #{i}. [CONCLUSIONS] Positive findings #{i}.
**Links:**
- [PubMed](https://pubmed.ncbi.nlm.nih.gov/{1000000 + i}/)
---
""")
    large_articles_str = "\n".join(large_articles)

    pdf_bytes = generate_research_pdf(
        evidence_report=SAMPLE_EVIDENCE_REPORT,
        articles_list=large_articles_str,
        query="Large Cohort Analysis",
    )

    extracted_text = extract_pdf_streams(pdf_bytes)
    assert "Article #1" in extracted_text
    assert "Article #12" in extracted_text
    assert "Article #24" in extracted_text
