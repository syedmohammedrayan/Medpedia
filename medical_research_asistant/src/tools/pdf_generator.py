"""pdf_generator.py
────────────────
Generates publication-quality, clinical-grade PDF evidence dossiers
from Medpedia's research synthesis, article citations, and clinical metadata.

STRICT CONTENT GOVERNANCE:
- Contains ONLY biomedical research report content.
- ZERO platform promotional information, ZERO website links, ZERO repository links,
  ZERO tech stack information, and ZERO medical/AI disclaimers (disclaimers reside exclusively in email).
- Fully branded with official Medpedia visual identity (Aubergine #3A0F34, Marigold #EAAA00,
  Warm Ivory #FAF8F5, Charcoal #211B20, Secondary Grey #6B5F69, Border #DDE3E8).
"""

import io
import json
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ──────────────────────────────────────────────────────────────────────────────
# Medpedia Brand Color Palette
# ──────────────────────────────────────────────────────────────────────────────
COLOR_AUBERGINE = colors.HexColor("#3A0F34")  # Primary Brand & Accent Dark
COLOR_MARIGOLD  = colors.HexColor("#EAAA00")  # Accent Gold & Highlights
COLOR_IVORY     = colors.HexColor("#FAF8F5")  # Warm Ivory Backgrounds
COLOR_CHARCOAL  = colors.HexColor("#211B20")  # Primary Editorial Body Text
COLOR_MUTED     = colors.HexColor("#6B5F69")  # Secondary Neutral / Meta
COLOR_BORDER    = colors.HexColor("#DDE3E8")  # Structure & Card Borders
COLOR_WHITE     = colors.HexColor("#FFFFFF")
COLOR_CARD_BG   = colors.HexColor("#FDFCFA")  # Subtle Card Background


# ──────────────────────────────────────────────────────────────────────────────
# Two-Pass Canvas for Dynamic Page Numbering & Clean Headers
# ──────────────────────────────────────────────────────────────────────────────
class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and render total page count
    (e.g., 'Page 2 of 5') along with running headers and footers.
    Strictly excludes website links, disclaimers, or platform promotions.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states: list[dict] = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages: int):
        # Page 1 is the editorial cover page — skip running headers/footers
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(COLOR_MUTED)

        page_width, page_height = letter

        # Running Header (Pages 2+)
        self.drawString(54, page_height - 36, "Medpedia | Medical Research Evidence Report")
        self.drawRightString(page_width - 54, page_height - 36, "Clinical Literature Dossier")
        self.setStrokeColor(COLOR_BORDER)
        self.setLineWidth(0.6)
        self.line(54, page_height - 42, page_width - 54, page_height - 42)

        # Running Footer (Pages 2+)
        self.line(54, 46, page_width - 54, 46)
        self.setFont("Helvetica", 8)
        self.drawString(54, 32, "Confidential Biomedical Literature Synthesis")
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(page_width - 54, 32, page_str)

        self.restoreState()


# ──────────────────────────────────────────────────────────────────────────────
# Sanitization & Formatting Helpers
# ──────────────────────────────────────────────────────────────────────────────
def _sanitize_for_reportlab(text: str) -> str:
    """Escapes XML entities while converting markdown bold, italic, and links
    to ReportLab flowable XML tags.
    """
    if not text:
        return ""

    # Strip raw XML entities first
    s = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Convert markdown bold **text** to <b>text</b>
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)

    # Convert markdown italic *text* or _text_ to <i>text</i>
    s = re.sub(r"\*(.+?)\*", r"<i>\1</i>", s)
    s = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"<i>\1</i>", s)

    # Convert markdown links [text](url) to ReportLab link tags
    # Notice: URL is extracted safely
    def _link_repl(match):
        label = match.group(1)
        url = match.group(2)
        # Restore basic entities in URL
        url_clean = url.replace("&amp;", "&")
        return f'<link href="{url_clean}" color="#3A0F34"><u>{label}</u></link>'

    s = re.sub(r"\[([^\]]+)\]\((https?://[^\s)]+)\)", _link_repl, s)
    return s


def _get_logo_path() -> str | None:
    """Finds the local static logo image asset if present."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, "assets", "medpedia_logo.png"),
        os.path.join(os.path.dirname(os.path.dirname(base_dir)), "static", "medpedia_logo.png"),
        os.path.join(base_dir, "..", "..", "static", "medpedia_logo.png"),
        os.path.join(os.getcwd(), "static", "medpedia_logo.png"),
    ]
    for c in candidates:
        if os.path.exists(c) and os.path.getsize(c) > 0:
            return os.path.abspath(c)
    return None


def _parse_markdown_table(lines: List[str], available_width: float, body_style: ParagraphStyle, header_style: ParagraphStyle) -> Table | None:
    """Parses a block of markdown table lines into a styled ReportLab Table.
    """
    rows_data: List[List[Paragraph]] = []
    is_header = True

    for line in lines:
        cleaned = line.strip().strip("|")
        if not cleaned:
            continue
        # Skip separator line (e.g. |---|---|)
        if re.match(r"^[\s\-:|]+$", cleaned):
            is_header = False
            continue

        raw_cells = [c.strip() for c in line.strip().strip("|").split("|")]
        row_paragraphs = []
        for cell in raw_cells:
            cell_sanitized = _sanitize_for_reportlab(cell)
            style_to_use = header_style if is_header else body_style
            row_paragraphs.append(Paragraph(cell_sanitized, style_to_use))
        if row_paragraphs:
            rows_data.append(row_paragraphs)

    if not rows_data:
        return None

    # Calculate column widths evenly
    num_cols = max(len(r) for r in rows_data)
    # Normalize row lengths
    for r in rows_data:
        while len(r) < num_cols:
            r.append(Paragraph("", body_style))

    col_width = available_width / max(1, num_cols)
    table = Table(rows_data, colWidths=[col_width] * num_cols, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_AUBERGINE),
        ("TEXTCOLOR", (0, 0), (-1, 0), COLOR_IVORY),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLOR_WHITE, COLOR_IVORY]),
    ]))
    return table


# ──────────────────────────────────────────────────────────────────────────────
# Core PDF Generation Function
# ──────────────────────────────────────────────────────────────────────────────
def generate_research_pdf(
    evidence_report: str,
    articles_list: str = "",
    query: str = "",
    recipient_email: str = "",
    session_id: str = "",
    timestamp: datetime | None = None,
) -> bytes:
    """Compiles complete biomedical research synthesis, PICO evidence tables,
    and retrieved primary literature citations into a publication-grade PDF dossier.

    Follows strict content governance:
    - NO About Medpedia, NO website address, NO disclaimers, NO tech stack.
    - Full research content only.

    Args:
        evidence_report: Synthesized evidence report Markdown.
        articles_list:   Raw/JSON or structured Markdown of retrieved articles.
        query:           Original clinical research question.
        recipient_email: Destination address (used strictly for document metadata).
        session_id:      Research session identifier.
        timestamp:       Generation timestamp (defaults to current UTC).

    Returns:
        bytes: Complete application/pdf document binary.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    page_content_width = letter[0] - 108  # 504 pt

    # Typography styles
    base_styles = getSampleStyleSheet()

    cover_brand_style = ParagraphStyle(
        "CoverBrand",
        parent=base_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=COLOR_MARIGOLD,
        textTransform="uppercase",
        spaceAfter=4,
    )

    cover_title_style = ParagraphStyle(
        "CoverTitle",
        parent=base_styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=COLOR_AUBERGINE,
        spaceAfter=6,
    )

    cover_subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=COLOR_MUTED,
        spaceAfter=14,
    )

    h1_style = ParagraphStyle(
        "SectionH1",
        parent=base_styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=COLOR_AUBERGINE,
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "SectionH2",
        parent=base_styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=COLOR_AUBERGINE,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "BodyCharcoal",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=COLOR_CHARCOAL,
        spaceAfter=6,
    )

    body_bold_style = ParagraphStyle(
        "BodyBold",
        parent=body_style,
        fontName="Helvetica-Bold",
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=base_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=COLOR_IVORY,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=COLOR_CHARCOAL,
    )

    bullet_style = ParagraphStyle(
        "BulletText",
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=4,
    )

    meta_label_style = ParagraphStyle(
        "MetaLabel",
        parent=base_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=12,
        textColor=COLOR_MUTED,
    )

    meta_val_style = ParagraphStyle(
        "MetaVal",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=COLOR_CHARCOAL,
    )

    story = []

    # ──────────────────────────────────────────────────────────────────────────
    # COVER PAGE
    # ──────────────────────────────────────────────────────────────────────────
    now_dt = timestamp or datetime.now(timezone.utc)
    date_str = now_dt.strftime("%B %d, %Y | %H:%M UTC")

    # 1. Medpedia Official Logo
    logo_path = _get_logo_path()
    if logo_path:
        story.append(Image(logo_path, width=1.0 * inch, height=1.0 * inch))
        story.append(Spacer(1, 14))

    story.append(Paragraph("MEDPEDIA", cover_brand_style))
    story.append(Paragraph("Medical Research Evidence Report", cover_title_style))
    story.append(Paragraph("Systematic Literature Synthesis & Clinical Evidence Extraction", cover_subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2.5, color=COLOR_MARIGOLD, spaceAfter=14))

    # 2. Clinical Inquiry Box
    clean_query = _sanitize_for_reportlab(query or "Comprehensive Biomedical Literature Inquiry")
    inquiry_table = Table(
        [
            [Paragraph("<b>CLINICAL RESEARCH INQUIRY</b>", meta_label_style)],
            [Paragraph(clean_query, ParagraphStyle("InquiryQuery", parent=body_style, fontName="Helvetica-Bold", fontSize=11, leading=15, textColor=COLOR_AUBERGINE))],
        ],
        colWidths=[page_content_width],
    )
    inquiry_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_IVORY),
        ("BOX", (0, 0), (-1, -1), 0.75, COLOR_BORDER),
        ("LINELEFT", (0, 0), (0, -1), 3.5, COLOR_AUBERGINE),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(inquiry_table)
    story.append(Spacer(1, 14))

    # 3. Document Metadata Grid
    meta_rows = [
        [
            Paragraph("Report Date:", meta_label_style),
            Paragraph(date_str, meta_val_style),
            Paragraph("Data Scope:", meta_label_style),
            Paragraph("MEDLINE & PubMed Central (PMC)", meta_val_style),
        ],
        [
            Paragraph("Session Identifier:", meta_label_style),
            Paragraph(session_id or f"MED-{now_dt.strftime('%Y%m%d%H%M')}", meta_val_style),
            Paragraph("Document Status:", meta_label_style),
            Paragraph("Compiled Literature Dossier", meta_val_style),
        ],
    ]
    if recipient_email:
        meta_rows.append([
            Paragraph("Prepared For:", meta_label_style),
            Paragraph(_sanitize_for_reportlab(recipient_email), meta_val_style),
            Paragraph("Classification:", meta_label_style),
            Paragraph("Biomedical Research Synthesis", meta_val_style),
        ])

    meta_table = Table(
        meta_rows,
        colWidths=[100, 152, 100, 152],
    )
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_CARD_BG),
        ("BOX", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # 4. Scope Note
    scope_note = (
        "<b>Notice of Compilation:</b> This document contains the synthesized clinical evidence, "
        "evidence-certainty classifications, comparative matrices, and complete primary publication records "
        "retrieved from peer-reviewed biomedical databases for the stated clinical inquiry. "
        "All citations reference original indexed literature records."
    )
    scope_table = Table([[Paragraph(scope_note, ParagraphStyle("ScopeNote", parent=body_style, fontSize=8.5, leading=12, textColor=COLOR_MUTED))]], colWidths=[page_content_width])
    scope_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_IVORY),
        ("BOX", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(scope_table)

    # Clean PageBreak to start research synthesis on Page 2
    story.append(PageBreak())

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 1: EXECUTIVE EVIDENCE SUMMARY
    # ──────────────────────────────────────────────────────────────────────────
    story.append(Paragraph("1. Executive Evidence Summary", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.0, color=COLOR_MARIGOLD, spaceAfter=10))

    table_buffer: List[str] = []
    in_markdown_table = False

    raw_evidence = evidence_report or "No synthesized evidence report provided."

    for line in raw_evidence.splitlines():
        stripped = line.strip()

        # Handle Markdown table lines
        if stripped.startswith("|") and stripped.endswith("|"):
            in_markdown_table = True
            table_buffer.append(stripped)
            continue
        else:
            if in_markdown_table and table_buffer:
                parsed_table = _parse_markdown_table(table_buffer, page_content_width, table_cell_style, table_header_style)
                if parsed_table:
                    story.append(Spacer(1, 4))
                    story.append(parsed_table)
                    story.append(Spacer(1, 6))
                table_buffer = []
                in_markdown_table = False

        if not stripped:
            continue

        # Separators
        if stripped in ("---", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "─────────────────────────────────────────────"):
            story.append(Spacer(1, 4))
            story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_BORDER, spaceAfter=8))
            continue

        # Section headings
        if stripped.startswith("### "):
            story.append(Paragraph(_sanitize_for_reportlab(stripped[4:]), h2_style))
        elif stripped.startswith("## "):
            story.append(Paragraph(_sanitize_for_reportlab(stripped[3:]), h1_style))
        elif stripped.startswith("# "):
            story.append(Paragraph(_sanitize_for_reportlab(stripped[2:]), h1_style))
        elif stripped.startswith("- ") or stripped.startswith("* "):
            clean_item = _sanitize_for_reportlab(stripped[2:])
            story.append(Paragraph(f"• &nbsp;{clean_item}", bullet_style))
        else:
            clean_text = _sanitize_for_reportlab(stripped)
            # Distinct card styling for Study Type or Evidence Grading blocks
            if "STUDY TYPE" in clean_text.upper() or "GRADE CERTAINTY" in clean_text.upper() or "EVIDENCE LEVEL" in clean_text.upper():
                box = Table([[Paragraph(clean_text, body_bold_style)]], colWidths=[page_content_width])
                box.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), COLOR_IVORY),
                    ("BOX", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                    ("LINELEFT", (0, 0), (0, -1), 3.0, COLOR_MARIGOLD),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]))
                story.append(Spacer(1, 4))
                story.append(box)
                story.append(Spacer(1, 4))
            else:
                story.append(Paragraph(clean_text, body_style))

    # Flush any lingering table buffer
    if in_markdown_table and table_buffer:
        parsed_table = _parse_markdown_table(table_buffer, page_content_width, table_cell_style, table_header_style)
        if parsed_table:
            story.append(parsed_table)
            story.append(Spacer(1, 6))
        table_buffer = []

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 2 & 3: COMPLETE SOURCE ARTICLE RECORDS & EVIDENCE OVERVIEW
    # ──────────────────────────────────────────────────────────────────────────
    parsed_articles: List[Dict[str, Any]] = []

    # Try parsing JSON articles if provided in articles_list
    if articles_list and articles_list.strip().startswith("[") and articles_list.strip().endswith("]"):
        try:
            parsed_articles = json.loads(articles_list)
        except Exception:
            parsed_articles = []

    # If articles_list is structured Markdown, or if articles were not JSON
    has_articles_content = bool(articles_list and articles_list.strip() and articles_list != "No articles list available." and articles_list != "No articles found.")

    if parsed_articles:
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1.0, color=COLOR_BORDER, spaceAfter=10))
        story.append(Paragraph("2. Complete Source Article Records", h1_style))

        for idx, art in enumerate(parsed_articles, start=1):
            title = _sanitize_for_reportlab(art.get("title", f"Source Article #{idx}"))
            authors = _sanitize_for_reportlab(", ".join(art.get("authors", [])) if isinstance(art.get("authors"), list) else str(art.get("authors", "Not reported")))
            journal = _sanitize_for_reportlab(art.get("journal", "Biomedical Literature"))
            pub_date = _sanitize_for_reportlab(art.get("published_date", "Date not recorded"))
            summary = _sanitize_for_reportlab(art.get("summary", "No abstract available."))
            url = art.get("url", "")

            art_rows = [
                [Paragraph(f"<b>Article #{idx}:</b> {title}", h2_style)],
                [Paragraph(f"<b>Authors:</b> {authors} &nbsp;|&nbsp; <b>Journal:</b> <i>{journal}</i> &nbsp;|&nbsp; <b>Published:</b> {pub_date}", meta_label_style)],
                [Paragraph(f"<b>Abstract / Extraction:</b><br/>{summary}", body_style)],
            ]

            if url:
                url_clean = url.replace("&", "&amp;")
                art_rows.append([Paragraph(f'<b>Primary Citation Link:</b> <link href="{url_clean}" color="#3A0F34"><u>{url_clean}</u></link>', ParagraphStyle("ArtUrl", parent=body_style, fontSize=8.5, textColor=COLOR_AUBERGINE))])

            art_table = Table(art_rows, colWidths=[page_content_width])
            art_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), COLOR_CARD_BG),
                ("BOX", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                ("LINELEFT", (0, 0), (0, -1), 3.0, COLOR_AUBERGINE),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ]))
            story.append(Spacer(1, 6))
            story.append(KeepTogether([art_table]))

    elif has_articles_content:
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1.0, color=COLOR_BORDER, spaceAfter=10))
        story.append(Paragraph("2. Complete Source Article Records", h1_style))

        current_article_lines: List[str] = []

        def _render_article_card(lines: List[str]):
            if not lines:
                return
            card_content = []
            for item_line in lines:
                l_str = item_line.strip()
                if not l_str:
                    continue
                if l_str.startswith("### "):
                    card_content.append(Paragraph(_sanitize_for_reportlab(l_str[4:]), h2_style))
                elif l_str.startswith("## "):
                    card_content.append(Paragraph(_sanitize_for_reportlab(l_str[3:]), h2_style))
                elif l_str.startswith("- "):
                    clean_l = _sanitize_for_reportlab(l_str[2:])
                    card_content.append(Paragraph(f"• &nbsp;{clean_l}", bullet_style))
                else:
                    card_content.append(Paragraph(_sanitize_for_reportlab(l_str), body_style))

            if not card_content:
                return

            box = Table([[item] for item in card_content], colWidths=[page_content_width])
            box.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), COLOR_CARD_BG),
                ("BOX", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                ("LINELEFT", (0, 0), (0, -1), 3.0, COLOR_AUBERGINE),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ]))
            story.append(Spacer(1, 6))
            story.append(KeepTogether([box]))

        for line in articles_list.splitlines():
            stripped = line.strip()
            if stripped.startswith("### Article #") or (stripped.startswith("### ") and "Article" in stripped):
                if current_article_lines:
                    _render_article_card(current_article_lines)
                    current_article_lines = []
            if stripped in ("---", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"):
                if current_article_lines:
                    _render_article_card(current_article_lines)
                    current_article_lines = []
                continue
            current_article_lines.append(line)

        if current_article_lines:
            _render_article_card(current_article_lines)

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 4: PRIMARY SOURCE REFERENCES
    # ──────────────────────────────────────────────────────────────────────────
    # Extract any unique PubMed / PMC links found in evidence or articles report
    all_text = (evidence_report or "") + "\n" + (articles_list or "")
    found_urls = re.findall(r"https?://(?:pubmed\.ncbi\.nlm\.nih\.gov/\d+/?|www\.ncbi\.nlm\.nih\.gov/pmc/articles/PMC\d+/?|doi\.org/[^\s)\"\']+)", all_text)
    unique_urls = list(dict.fromkeys(found_urls))

    if unique_urls:
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1.0, color=COLOR_BORDER, spaceAfter=10))
        story.append(Paragraph("3. Primary Source References", h1_style))

        ref_rows = []
        for i, u in enumerate(unique_urls, start=1):
            clean_u = u.replace("&", "&amp;")
            label = "PubMed / PMC Indexed Source"
            if "pubmed.ncbi.nlm.nih.gov" in u:
                pmid_match = re.search(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)", u)
                label = f"PubMed Record PMID: {pmid_match.group(1)}" if pmid_match else "PubMed Source"
            elif "pmc" in u.lower():
                pmc_match = re.search(r"(PMC\d+)", u, re.IGNORECASE)
                label = f"PubMed Central Article {pmc_match.group(1).upper()}" if pmc_match else "PMC Full Text"

            p = Paragraph(f"[{i}] &nbsp;<b>{label}:</b> &nbsp;<link href=\"{clean_u}\" color=\"#3A0F34\"><u>{clean_u}</u></link>", body_style)
            ref_rows.append([p])

        ref_table = Table(ref_rows, colWidths=[page_content_width])
        ref_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), COLOR_IVORY),
            ("BOX", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(ref_table)

    # Build the document binary
    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()
