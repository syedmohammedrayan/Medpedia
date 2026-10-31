"""
pdf_generator.py
────────────────
Generates publication-quality, clinical-grade PDF evidence dossiers
from Medpedia's research synthesis, article citations, and clinical metadata.
"""

import io
import re
from datetime import datetime, timezone
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and render total page count
    (e.g., 'Page 1 of 4') along with running headers and footers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

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
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#718096"))

        # Running header (on pages 2 and above)
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "Medpedia | Clinical Evidence Dossier")
            self.drawRightString(letter[0] - 54, letter[1] - 36, "Confidential & Research Inscription")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        # Running footer (all pages)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 46, letter[0] - 54, 46)

        self.drawString(54, 32, "Medpedia AI Biomedical Synthesis | medpedia-smr.vercel.app")
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(letter[0] - 54, 32, page_str)
        self.restoreState()


def _sanitize_for_reportlab(text: str) -> str:
    """Escapes XML entities while preserving simple <b>, <i>, and <a> formatting."""
    # Replace markdown bold and italic
    s = text.replace("&", "&amp;")
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\*(.+?)\*", r"<i>\1</i>", s)
    # Convert markdown links [text](url) to <a href="url">text</a>
    s = re.sub(r"\[([^\]]+)\]\((https?://[^\s)]+)\)", r'<link href="\2" color="#2B6CB0"><u>\1</u></link>', s)
    return s


def generate_research_pdf(
    evidence_report: str,
    articles_list: str = "",
    query: str = "",
    recipient_email: str = "",
) -> bytes:
    """
    Compiles full evidence synthesis, source articles, websites, and medical
    disclaimers into a standardized, publication-grade PDF binary.
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

    base_styles = getSampleStyleSheet()

    # Custom typography hierarchy
    title_style = ParagraphStyle(
        "DocTitle",
        parent=base_styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#4A5568"),
        spaceAfter=14,
    )

    h1_style = ParagraphStyle(
        "SectionH1",
        parent=base_styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1A365D"),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "SectionH2",
        parent=base_styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "BodyDark",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        "BulletText",
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=4,
    )

    card_style = ParagraphStyle(
        "CardText",
        parent=body_style,
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#1A365D"),
    )

    disclaimer_style = ParagraphStyle(
        "DisclaimerText",
        parent=base_styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#718096"),
    )

    story = []

    # 1. Header Banner
    now_str = datetime.now(timezone.utc).strftime("%B %d, %Y | %H:%M UTC")
    story.append(Paragraph("🔬 MEDPEDIA CLINICAL EVIDENCE DOSSIER", title_style))
    meta_info = f"<b>Generated:</b> {now_str} &nbsp;|&nbsp; <b>Platform:</b> medpedia-smr.vercel.app"
    if recipient_email:
        meta_info += f" &nbsp;|&nbsp; <b>Prepared for:</b> {recipient_email}"
    story.append(Paragraph(meta_info, subtitle_style))

    if query:
        query_sanitized = _sanitize_for_reportlab(query)
        query_box = Table(
            [[Paragraph(f"<b>Clinical Inquiry:</b> {query_sanitized}", body_style)]],
            colWidths=[letter[0] - 108],
        )
        query_box.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EBF8FF")),
            ("BORDER", (0, 0), (-1, -1), 1, colors.HexColor("#BEE3F8")),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(query_box)
        story.append(Spacer(1, 12))

    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2B6CB0"), spaceAfter=14))

    # 2. Executive Evidence Summary Section
    story.append(Paragraph("Executive Evidence Summary", h1_style))

    # Parse and add evidence report content
    for line in evidence_report.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped in ("---", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "─────────────────────────────────────────────"):
            story.append(Spacer(1, 6))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E0"), spaceAfter=8))
            continue
        if stripped.startswith("### "):
            story.append(Paragraph(_sanitize_for_reportlab(stripped[4:]), h2_style))
        elif stripped.startswith("## "):
            story.append(Paragraph(_sanitize_for_reportlab(stripped[3:]), h1_style))
        elif stripped.startswith("# "):
            story.append(Paragraph(_sanitize_for_reportlab(stripped[2:]), h1_style))
        elif stripped.startswith("- "):
            clean_item = _sanitize_for_reportlab(stripped[2:])
            story.append(Paragraph(f"• &nbsp;{clean_item}", bullet_style))
        else:
            clean_text = _sanitize_for_reportlab(stripped)
            if "Article #" in clean_text or "STUDY TYPE" in clean_text.upper() or "EVIDENCE" in clean_text.upper():
                box = Table([[Paragraph(clean_text, card_style)]], colWidths=[letter[0] - 108])
                box.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
                    ("LINELEFT", (0, 0), (0, -1), 3.5, colors.HexColor("#4299E1")),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]))
                story.append(Spacer(1, 4))
                story.append(box)
                story.append(Spacer(1, 4))
            else:
                story.append(Paragraph(clean_text, body_style))

    # 3. Source Articles Bibliography Section
    if articles_list and articles_list.strip() and articles_list != "No articles list available.":
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E0"), spaceAfter=10))
        story.append(Paragraph("Retrieved Biomedical Articles & Citations", h1_style))

        for line in articles_list.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("### "):
                story.append(Paragraph(_sanitize_for_reportlab(stripped[4:]), h2_style))
            elif stripped.startswith("## "):
                story.append(Paragraph(_sanitize_for_reportlab(stripped[3:]), h1_style))
            elif stripped.startswith("- "):
                clean_item = _sanitize_for_reportlab(stripped[2:])
                story.append(Paragraph(f"• &nbsp;{clean_item}", bullet_style))
            else:
                clean_text = _sanitize_for_reportlab(stripped)
                story.append(Paragraph(clean_text, body_style))

    # 4. Mandatory Disclaimers & Medpedia Platform Details
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=10))

    disclaimer_box = Table(
        [[
            Paragraph(
                "<b>Medical & Regulatory Disclaimer:</b><br/>"
                "This report is generated by Medpedia's AI biomedical synthesis pipeline "
                "for academic and clinical research purposes only. It does not constitute formal "
                "medical advice, clinical diagnosis, or therapeutic guidelines. Healthcare providers "
                "must exercise independent professional clinical judgment and verify primary citations "
                "before taking patient care actions.<br/><br/>"
                "<b>Websites & Sources:</b> Medpedia (https://medpedia-smr.vercel.app) • "
                "National Center for Biotechnology Information (NCBI) • PubMed / PubMed Central.",
                disclaimer_style,
            )
        ]],
        colWidths=[letter[0] - 108],
    )
    disclaimer_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BORDER", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(KeepTogether([disclaimer_box]))

    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()
