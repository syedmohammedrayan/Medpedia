"""
send_email_tool.py
──────────────────
Provides the `send_email` LangChain-compatible tool used by the
med_email_dispatcher node in the LangGraph pipeline.

Sends the full evidence report (evidence cards + synthesis) as a
styled HTML email using EmailJS over HTTPS (Port 443 — works seamlessly
on Render Free Tier) with direct Gmail SMTP (port 587) fallback.
"""

import html
import json
import os
import re
import smtplib
import socket
import ssl
from datetime import datetime, timezone
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Optional

import requests
from langchain_core.tools import tool

from tools.pdf_generator import generate_research_pdf


# ──────────────────────────────────────────────────────────────────────────────
# Helper — convert Markdown to styled HTML
# ──────────────────────────────────────────────────────────────────────────────

def _markdown_to_html(md: str) -> str:
    """
    Enhanced Markdown → HTML converter for the evidence report.
    Converts headers, lists, links, bold, and card-style sections
    while ensuring safe HTML escaping of untrusted input.
    Generates compact markup using CSS classes to avoid 50KB payload bloat.
    """
    link_re   = re.compile(r'\[([^\]]+)\]\((https?://[^\s)"\']+)\)')
    bold_re   = re.compile(r'\*\*(.+?)\*\*')
    italic_re = re.compile(r'\*(.+?)\*')

    html_lines: list[str] = []
    in_list = False

    for line in md.splitlines():
        stripped = line.strip()

        # Handle separators
        if stripped in (
            "---",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "─────────────────────────────────────────────",
            "──────────────────",
        ):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append("<hr>")
            continue

        # Handle headings
        if stripped.startswith("### "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            title = html.escape(stripped[4:])
            html_lines.append(f"<h3>{title}</h3>")
        elif stripped.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            title = html.escape(stripped[3:])
            html_lines.append(f"<h2>{title}</h2>")
        elif stripped.startswith("# "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            title = html.escape(stripped[2:])
            html_lines.append(f"<h1>{title}</h1>")

        # Handle lists
        elif stripped.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            content = html.escape(stripped[2:])
            content = link_re.sub(r'<a href="\2">\1</a>', content)
            content = bold_re.sub(r"<strong>\1</strong>", content)
            content = italic_re.sub(r"<em>\1</em>", content)
            html_lines.append(f"<li>{content}</li>")

        # Handle empty lines
        elif stripped == "":
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append("<br>")

        # Handle regular text
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            processed = html.escape(stripped)
            processed = link_re.sub(r'<a href="\2">\1</a>', processed)
            processed = bold_re.sub(r"<strong>\1</strong>", processed)
            processed = italic_re.sub(r"<em>\1</em>", processed)

            # Special check for article "Cards" header or badges
            if "Article #" in processed or "STUDY TYPE" in processed.upper() or "EVIDENCE" in processed.upper():
                html_lines.append(f'<div class="card">{processed}</div>')
            else:
                html_lines.append(f"<p>{processed}</p>")

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


def _fit_report_html(report_html: str, max_allowed_bytes: int = 38000) -> str:
    """
    Guarantees that the generated HTML content strictly fits within
    EmailJS's 50KB total variables payload limit (51,200 bytes).
    If report_html exceeds max_allowed_bytes, gracefully truncates at a
    clean block boundary and appends a professional dashboard reference notice.
    """
    raw = report_html.encode("utf-8")
    if len(raw) <= max_allowed_bytes:
        return report_html

    notice = (
        '<div class="notice-card">'
        '<em>📄 Note: Additional bibliography records condensed to meet email delivery limit (50KB). '
        'The complete synthesis and full literature records are saved on your Medpedia Web Dashboard.</em>'
        '</div>'
    )
    notice_bytes_len = len(notice.encode("utf-8"))
    target_bytes = max_allowed_bytes - notice_bytes_len - 150
    sliced = raw[:target_bytes].decode("utf-8", errors="ignore")

    # Find the nearest clean tag boundary
    best_cut = -1
    for marker in ("</p>", "</div>", "</li>", "</ul>", "</h3>", "</h2>", "<hr>"):
        idx = sliced.rfind(marker)
        if idx > best_cut:
            best_cut = idx + len(marker)

    if best_cut > 1000:
        safe_cut = sliced[:best_cut]
    else:
        safe_cut = sliced

    if safe_cut.count("<ul>") > safe_cut.count("</ul>"):
        safe_cut += "</ul>"

    return safe_cut + "\n" + notice


# ──────────────────────────────────────────────────────────────────────────────
# Helper — Email Validation
# ──────────────────────────────────────────────────────────────────────────────

_EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9]+([.-][a-zA-Z0-9]+)*\.[a-zA-Z]{2,}$")

def _validate_recipient_email(email_str: str) -> tuple[bool, str]:
    """
    Validates recipient email address for safety, syntax, and header injection.
    """
    if not email_str or not isinstance(email_str, str) or not email_str.strip():
        return False, "Error: Recipient email address is required and cannot be empty."

    cleaned = email_str.strip()

    # Reject newline characters and header-injection attempts
    if "\r" in cleaned or "\n" in cleaned:
        return False, "Error: Invalid recipient email address: contains prohibited newline characters."

    # Reject multiple addresses (single recipient expected)
    if "," in cleaned or ";" in cleaned or " " in cleaned:
        return False, "Error: Only a single recipient email address is allowed."

    if not _EMAIL_REGEX.match(cleaned):
        return False, f"Error: Invalid recipient email address format: '{cleaned}'."

    return True, cleaned


# ──────────────────────────────────────────────────────────────────────────────
# Helper — Dispatch via EmailJS (HTTPS Port 443)
# ──────────────────────────────────────────────────────────────────────────────

def _dispatch_via_emailjs(
    service_id: str,
    template_id: str,
    public_key: str,
    private_key: str,
    recipient_email: str,
    subject: str,
    html_body: str,
    pdf_bytes: Optional[bytes] = None,
    timeout: float = 20.0,
) -> str:
    """
    Dispatches email via EmailJS REST API over HTTPS (Port 443).
    Attaches the clinical PDF dossier via /send-form, falling back to /send.
    """
    safe_body = html_body
    params_test = {
        "to_email": recipient_email,
        "subject": subject,
        "message_html": safe_body,
    }
    test_bytes = len(json.dumps(params_test).encode("utf-8"))
    if test_bytes > 48000:
        overage = test_bytes - 46000
        safe_body = safe_body[:-overage] + "</div></div></body></html>"

    # 1. Attempt /send-form with attached PDF
    if pdf_bytes:
        try:
            files = {
                "content": ("Medpedia_Evidence_Report.pdf", pdf_bytes, "application/pdf")
            }
            data = {
                "service_id": service_id,
                "template_id": template_id,
                "user_id": public_key,
                "to_email": recipient_email,
                "subject": subject,
                "message_html": safe_body,
            }
            if private_key:
                data["accessToken"] = private_key

            resp = requests.post(
                "https://api.emailjs.com/api/v1.0/email/send-form",
                data=data,
                files=files,
                timeout=timeout,
            )
            if resp.status_code == 200:
                return "Email sent successfully."
        except Exception:
            pass  # Fall through to standard /send

    # 2. Standard /send fallback
    try:
        payload = {
            "service_id": service_id,
            "template_id": template_id,
            "user_id": public_key,
            "template_params": {
                "to_email": recipient_email,
                "subject": subject,
                "message_html": safe_body,
            },
        }
        if private_key:
            payload["accessToken"] = private_key

        resp = requests.post(
            "https://api.emailjs.com/api/v1.0/email/send",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=timeout,
        )
        if resp.status_code == 200:
            return "Email sent successfully."
        return f"Error from EmailJS API ({resp.status_code}): {resp.text}"
    except Exception as exc:
        return f"Error sending via EmailJS: {exc}"


# ──────────────────────────────────────────────────────────────────────────────
# LangChain Tool
# ──────────────────────────────────────────────────────────────────────────────

@tool
def send_email(
    evidence_report: str,
    recipient_email: str,
    articles_list: str = "",
    query: str = "",
) -> str:
    """
    Composes and sends the full evidence report as a styled HTML email with
    an attached clinical PDF report containing complete literature citations,
    websites, Medpedia details, and medical disclaimers.
    Supports EmailJS HTTPS REST API (Port 443 — works on Render Free Tier)
    and direct Gmail SMTP (STARTTLS on port 587).

    Args:
        evidence_report:  The complete Markdown output from the evidence
                          builder agent (article cards + Overall Evidence
                          Summary). This is rendered as HTML in the email body.
        recipient_email:  Destination email address.
        articles_list:    Retrieved literature citations and abstracts.
        query:            Initial clinical question asked by the clinician.

    Returns:
        "Email sent successfully." on success, or an informative error description.
    """
    # 1. Validate recipient email
    is_valid, validation_result = _validate_recipient_email(recipient_email)
    if not is_valid:
        return validation_result
    target_recipient = validation_result

    # 2. Validate evidence report
    if not evidence_report or not evidence_report.strip():
        return "Error: Evidence report is empty. Nothing to dispatch."

    now = datetime.now(timezone.utc).strftime("%B %d, %Y")
    report_html = _markdown_to_html(evidence_report)
    fitted_report_html = _fit_report_html(report_html, max_allowed_bytes=38000)
    subject = f"🔬 Medical Research Insights – {now}"

    # Generate comprehensive PDF clinical dossier
    pdf_bytes: Optional[bytes] = None
    try:
        pdf_bytes = generate_research_pdf(
            evidence_report=evidence_report,
            articles_list=articles_list,
            query=query,
            recipient_email=target_recipient,
        )
    except Exception as exc:
        print(f"[WARN] PDF generation error: {exc}")

    # Build styled HTML body
    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #2D3748;
            background-color: #F8FAFC;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 680px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border: 1px solid #E2E8F0;
        }}
        .header {{
            background: linear-gradient(135deg, #1A365D 0%, #2B6CB0 100%);
            color: #ffffff;
            padding: 30px 24px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: 700;
            color: #ffffff;
        }}
        .header p {{
            margin: 8px 0 0;
            opacity: 0.9;
            font-size: 14px;
            color: #E2E8F0;
        }}
        .content {{
            padding: 24px;
        }}
        h1 {{ color: #1A365D; font-size: 22px; margin-top: 28px; margin-bottom: 14px; }}
        h2 {{ color: #2A4365; font-size: 18px; border-bottom: 2px solid #EBF8FF; padding-bottom: 6px; margin-top: 24px; margin-bottom: 12px; }}
        h3 {{ color: #2D3748; font-size: 16px; margin-top: 18px; margin-bottom: 8px; }}
        p {{ margin: 6px 0; font-size: 14px; color: #4A5568; line-height: 1.5; }}
        ul {{ padding-left: 20px; color: #4A5568; margin: 8px 0; }}
        li {{ margin-bottom: 6px; font-size: 14px; }}
        a {{ color: #3182CE; text-decoration: none; font-weight: 500; }}
        strong {{ color: #2D3748; }}
        hr {{ border: none; border-top: 1px solid #E2E8F0; margin: 24px 0; }}
        .card {{
            margin: 8px 0;
            font-size: 14px;
            color: #2D3748;
            background-color: #F7FAFC;
            padding: 8px 12px;
            border-left: 4px solid #4299E1;
            border-radius: 4px;
        }}
        .notice-card {{
            margin: 20px 0;
            padding: 12px 16px;
            background-color: #EDF2F7;
            border-radius: 6px;
            font-size: 13px;
            color: #4A5568;
            text-align: center;
        }}
        .pdf-banner {{
            background: linear-gradient(135deg, #EBF8FF 0%, #F0F4F8 100%);
            border: 1px solid #BEE3F8;
            border-left: 4px solid #3182CE;
            border-radius: 8px;
            padding: 14px 18px;
            margin: 18px 0;
        }}
        .footer {{
            background-color: #F7FAFC;
            padding: 20px 24px;
            text-align: center;
            font-size: 12px;
            color: #718096;
            border-top: 1px solid #E2E8F0;
        }}
        .disclaimer {{
            font-style: italic;
            margin-top: 8px;
            display: block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 Medical Research Insights</h1>
            <p>Personalized Evidence Synthesis | {now}</p>
        </div>
        
        <div class="content">
            <div class="pdf-banner">
                <div style="font-weight: 700; color: #1A365D; font-size: 15px; margin-bottom: 4px;">
                    📎 Attached Document: Medpedia_Evidence_Report.pdf
                </div>
                <div style="font-size: 13px; color: #4A5568; line-height: 1.4;">
                    A publication-grade clinical evidence dossier containing complete PubMed/PMC literature citations, study details, websites, and medical disclaimers is attached to this email.
                </div>
            </div>

            {fitted_report_html}
        </div>

        <div class="footer">
            <p>Generated by <strong>Medpedia</strong> AI Biomedical Synthesis</p>
            <p style="margin: 4px 0;"><a href="https://medpedia-smr.vercel.app" style="color: #3182CE; font-weight: 600;">Visit Medpedia Research Platform</a> &bull; Medline & PMC Citations</p>
            <span class="disclaimer">
                <strong>Medical Disclaimer:</strong> This dossier is for informational and educational purposes only and does not constitute medical advice or clinical guidelines. Always seek the advice of a qualified physician or healthcare provider with any clinical questions.
            </span>
        </div>
    </div>
</body>
</html>"""

    # 3. Primary Dispatcher: EmailJS over HTTPS Port 443 (Works on Render Free Tier)
    emailjs_service_id = (os.getenv("EMAILJS_SERVICE_ID") or "").strip()
    emailjs_template_id = (os.getenv("EMAILJS_TEMPLATE_ID") or "").strip()
    emailjs_public_key = (os.getenv("EMAILJS_PUBLIC_KEY") or os.getenv("EMAILJS_USER_ID") or "").strip()
    emailjs_private_key = (os.getenv("EMAILJS_PRIVATE_KEY") or os.getenv("EMAILJS_ACCESS_TOKEN") or "").strip()

    if emailjs_service_id and emailjs_template_id and emailjs_public_key:
        res = _dispatch_via_emailjs(
            service_id=emailjs_service_id,
            template_id=emailjs_template_id,
            public_key=emailjs_public_key,
            private_key=emailjs_private_key,
            recipient_email=target_recipient,
            subject=subject,
            html_body=html_body,
            pdf_bytes=pdf_bytes,
        )
        if res == "Email sent successfully.":
            return res

    # 4. Secondary / Direct Dispatcher: Gmail SMTP (Port 587 STARTTLS)
    smtp_user = (os.getenv("SMTP_USER") or "").strip()
    smtp_password = (os.getenv("SMTP_PASSWORD") or "").strip()

    if not smtp_user or not smtp_password:
        if emailjs_service_id and emailjs_template_id:
            return res
        return "Error: Missing email credentials. Configure EMAILJS_* or SMTP_* in environment variables."

    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
    smtp_port_raw = os.getenv("SMTP_PORT", "587").strip()
    try:
        smtp_port = int(smtp_port_raw)
    except ValueError:
        smtp_port = 587

    timeout_raw = os.getenv("SMTP_TIMEOUT", "15").strip()
    try:
        smtp_timeout = float(timeout_raw)
    except ValueError:
        smtp_timeout = 15.0

    plain_text = (
        f"Medical Research Insights – {now}\n\n"
        f"📎 Attached Document: Medpedia_Evidence_Report.pdf (Full Clinical Evidence Dossier)\n\n"
        f"{evidence_report.strip()}\n\n"
        f"─────────────────────────────────────────────\n"
        f"Generated by Medpedia Agentic Pipeline\n"
        f"Platform: https://medpedia-smr.vercel.app\n"
        f"Medical Disclaimer: This report is for informational purposes only and does not constitute medical advice. "
        f"Always seek the advice of a physician or other qualified health provider with any questions regarding a medical condition.\n"
    )

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = formataddr(("Medpedia", smtp_user))
    msg["To"] = target_recipient

    alt_body = MIMEMultipart("alternative")
    alt_body.attach(MIMEText(plain_text, "plain", "utf-8"))
    alt_body.attach(MIMEText(html_body, "html", "utf-8"))
    msg.attach(alt_body)

    if pdf_bytes:
        pdf_part = MIMEApplication(pdf_bytes, _subtype="pdf", Name="Medpedia_Evidence_Report.pdf")
        pdf_part["Content-Disposition"] = 'attachment; filename="Medpedia_Evidence_Report.pdf"'
        msg.attach(pdf_part)


    try:
        connect_host = smtp_host
        try:
            addr_info = socket.getaddrinfo(smtp_host, smtp_port, socket.AF_INET, socket.SOCK_STREAM)
            if addr_info:
                connect_host = addr_info[0][4][0]
        except Exception:
            connect_host = smtp_host

        context = ssl.create_default_context()
        with smtplib.SMTP(connect_host, smtp_port, timeout=smtp_timeout) as server:
            server._host = smtp_host
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        return "Email sent successfully."
    except smtplib.SMTPAuthenticationError:
        return "Error: Gmail SMTP authentication failed. Check your SMTP_USER and Google App Password."
    except smtplib.SMTPRecipientsRefused:
        return f"Error: Recipient address '{target_recipient}' was refused by the SMTP server."
    except smtplib.SMTPSenderRefused:
        return "Error: Sender address was refused by the SMTP server."
    except smtplib.SMTPDataError as exc:
        err_msg = exc.smtp_error.decode("utf-8", errors="replace") if hasattr(exc, "smtp_error") and isinstance(exc.smtp_error, bytes) else str(exc)
        return f"Error: SMTP server refused message data: {err_msg}"
    except (socket.timeout, TimeoutError):
        return (
            f"Error: SMTP connection timed out after {smtp_timeout} seconds. "
            f"Please verify network connectivity and that outbound port {smtp_port} is not blocked by your hosting provider."
        )
    except socket.gaierror:
        return f"Error: DNS resolution failed for SMTP host '{smtp_host}'. Check your network or SMTP_HOST configuration."
    except smtplib.SMTPConnectError as exc:
        return f"Error: Failed to connect to SMTP server '{smtp_host}:{smtp_port}': {exc}"
    except smtplib.SMTPException as exc:
        return f"Error: SMTP protocol error occurred: {exc}"
    except OSError as exc:
        if getattr(exc, "errno", None) == 101 or "unreachable" in str(exc).lower():
            return (
                "Error: Network is unreachable [Errno 101]. "
                "Render Free Tier blocks outbound SMTP traffic on ports 25, 465, and 587. "
                "Configure EMAILJS_* environment variables to send via HTTPS Port 443."
            )
        return f"Error: Network OS error ({getattr(exc, 'errno', 'unknown')}): {exc}"
    except Exception as exc:
        return f"Error: Unexpected error while sending email: {exc}"
