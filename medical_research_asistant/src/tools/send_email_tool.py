"""
send_email_tool.py
──────────────────
Provides the `send_email` LangChain-compatible tool used by the
med_email_dispatcher node in the LangGraph pipeline.

Sends the full clinical evidence report and attached publication-grade
PDF dossier directly through the Google Gmail REST API over HTTPS
(Port 443 — works seamlessly on Render Free Tier and all cloud hosts)
with direct Gmail SMTP (port 587) fallback for local development.
"""

import base64
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

            if "Article #" in processed or "STUDY TYPE" in processed.upper() or "EVIDENCE" in processed.upper():
                html_lines.append(f'<div class="card">{processed}</div>')
            else:
                html_lines.append(f"<p>{processed}</p>")

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


# ──────────────────────────────────────────────────────────────────────────────
# Helper — Email Validation
# ──────────────────────────────────────────────────────────────────────────────

_EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9]+([.-][a-zA-Z0-9]+)*\.[a-zA-Z]{2,}$")

def _validate_recipient_email(email_str: str) -> tuple[bool, str]:
    """Validates recipient email address for safety, syntax, and header injection."""
    if not email_str or not isinstance(email_str, str) or not email_str.strip():
        return False, "Error: Recipient email address is required and cannot be empty."

    cleaned = email_str.strip()

    if "\r" in cleaned or "\n" in cleaned:
        return False, "Error: Invalid recipient email address: contains prohibited newline characters."

    if "," in cleaned or ";" in cleaned or " " in cleaned:
        return False, "Error: Only a single recipient email address is allowed."

    if not _EMAIL_REGEX.match(cleaned):
        return False, f"Error: Invalid recipient email address format: '{cleaned}'."

    return True, cleaned


# ──────────────────────────────────────────────────────────────────────────────
# Primary Transport: Official Google Gmail REST API (HTTPS Port 443)
# ──────────────────────────────────────────────────────────────────────────────

def _get_gmail_access_token(
    client_id: str,
    client_secret: str,
    refresh_token: str,
    timeout: float = 10.0,
) -> tuple[bool, str]:
    """Exchanges a Google OAuth2 refresh token for an active access token."""
    try:
        resp = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=timeout,
        )
        if resp.status_code == 200:
            token_data = resp.json()
            access_token = token_data.get("access_token")
            if access_token:
                return True, access_token
            return False, "Google OAuth response did not contain an access_token."
        return False, f"Google OAuth token refresh failed ({resp.status_code}): {resp.text}"
    except Exception as exc:
        return False, f"Network error refreshing Google OAuth token: {exc}"


def _dispatch_via_gmail_api(
    sender_email: str,
    recipient_email: str,
    subject: str,
    plain_text: str,
    html_body: str,
    pdf_bytes: Optional[bytes],
    client_id: str,
    client_secret: str,
    refresh_token: str,
    timeout: float = 20.0,
) -> str:
    """
    Sends an RFC 2822 multipart email with PDF attachment directly through
    Google's official Gmail REST API over HTTPS Port 443.
    Supports up to 35 MB per message with zero intermediary services.
    """
    # 1. Obtain fresh Google OAuth access token
    ok, token_or_err = _get_gmail_access_token(client_id, client_secret, refresh_token, timeout=timeout)
    if not ok:
        return f"Error: {token_or_err}"
    access_token = token_or_err

    # 2. Build standard MIME message
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = formataddr(("Medpedia", sender_email))
    msg["To"] = recipient_email

    alt_body = MIMEMultipart("alternative")
    alt_body.attach(MIMEText(plain_text, "plain", "utf-8"))
    alt_body.attach(MIMEText(html_body, "html", "utf-8"))
    msg.attach(alt_body)

    if pdf_bytes:
        pdf_part = MIMEApplication(pdf_bytes, _subtype="pdf", Name="Medpedia_Evidence_Report.pdf")
        pdf_part["Content-Disposition"] = 'attachment; filename="Medpedia_Evidence_Report.pdf"'
        msg.attach(pdf_part)

    # 3. Base64url encode the entire RFC 2822 message
    raw_b64 = base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")

    # 4. Dispatch directly via Gmail REST API
    try:
        resp = requests.post(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json={"raw": raw_b64},
            timeout=timeout,
        )
        if resp.status_code in (200, 201):
            return "Email sent successfully."
        return f"Error from Gmail API ({resp.status_code}): {resp.text}"
    except Exception as exc:
        return f"Error sending via Gmail API: {exc}"


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

    Dispatches via the official Google Gmail REST API over HTTPS (Port 443),
    with direct Gmail SMTP (port 587) fallback.

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

            {report_html}
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

    # 3. Primary Dispatcher: Google Gmail REST API (HTTPS Port 443 — Render Free Tier compatible)
    gmail_client_id = (os.getenv("GMAIL_CLIENT_ID") or "").strip()
    gmail_client_secret = (os.getenv("GMAIL_CLIENT_SECRET") or "").strip()
    gmail_refresh_token = (os.getenv("GMAIL_REFRESH_TOKEN") or "").strip()
    gmail_sender = (os.getenv("GMAIL_SENDER_EMAIL") or os.getenv("SMTP_USER") or "hello051507@gmail.com").strip()

    if gmail_client_id and gmail_client_secret and gmail_refresh_token:
        res = _dispatch_via_gmail_api(
            sender_email=gmail_sender,
            recipient_email=target_recipient,
            subject=subject,
            plain_text=plain_text,
            html_body=html_body,
            pdf_bytes=pdf_bytes,
            client_id=gmail_client_id,
            client_secret=gmail_client_secret,
            refresh_token=gmail_refresh_token,
        )
        if res == "Email sent successfully.":
            return res

    # 4. Secondary Dispatcher: Direct Gmail SMTP (Port 587 STARTTLS)
    smtp_user = (os.getenv("SMTP_USER") or "").strip()
    smtp_password = (os.getenv("SMTP_PASSWORD") or "").strip()

    if not smtp_user or not smtp_password:
        if gmail_client_id and gmail_refresh_token:
            return res
        return "Error: Missing email credentials. Configure GMAIL_* or SMTP_* in environment variables."

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
                "Configure GMAIL_* environment variables to send via Google Gmail REST API over HTTPS Port 443."
            )
        return f"Error: Network OS error ({getattr(exc, 'errno', 'unknown')}): {exc}"
    except Exception as exc:
        return f"Error: Unexpected error while sending email: {exc}"
