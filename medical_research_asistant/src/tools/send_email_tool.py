"""send_email_tool.py
──────────────────
Provides the `send_email` LangChain-compatible tool used by the
med_email_dispatcher node in the LangGraph pipeline.

Sends the professional Medpedia research dispatch email with the
comprehensive clinical evidence PDF dossier attached as an authentic binary.

STRICT CONTENT GOVERNANCE:
- Email body contains:
  * Official Medpedia branding and logo
  * Recipient address and original clinical research question
  * Concise notification of attached research dossier
  * Comprehensive About Medpedia introduction
  * Public website URL and contact email
  * Mandatory Medical & AI-generated content disclaimer (EXCLUSIVE to email)
  * PDF attachment details
- Email body strictly EXCLUDES:
  * Technology stack, programming languages, backend/frontend architecture,
    internal libraries, infrastructure, or GitHub links.

DELIVERY TRANSPORTS (Optimized for Render Free Tier):
1. Primary: Official Google Cloud Gmail REST API over HTTPS Port 443 (supports up to 35MB attachments).
2. Secondary / Local: Direct Gmail SMTP (Port 587 STARTTLS).
"""

import base64
import html
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
from typing import Tuple

import requests
from langchain_core.tools import tool

from tools.pdf_generator import generate_research_pdf

# ──────────────────────────────────────────────────────────────────────────────
# Constant Content Definitions (Strict Recipient Governance)
# ──────────────────────────────────────────────────────────────────────────────
MANDATORY_MEDICAL_DISCLAIMER = (
    "Medical Disclaimer: Medpedia is intended to support biomedical literature discovery "
    "and research. The information and evidence summaries provided are AI-generated and may "
    "contain inaccuracies or omissions. They are intended for informational and educational "
    "purposes only and do not constitute medical advice, diagnosis or treatment recommendations. "
    "Always verify the original research publications and consult qualified healthcare "
    "professionals before making clinical decisions."
)

ATTACHMENT_FILENAME = "Medpedia_Comprehensive_Evidence_Report.pdf"


# ──────────────────────────────────────────────────────────────────────────────
# Helper — Email Address Validation
# ──────────────────────────────────────────────────────────────────────────────
_EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9]+([.-][a-zA-Z0-9]+)*\.[a-zA-Z]{2,}$")

def _validate_recipient_email(email_str: str) -> Tuple[bool, str]:
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
# Professional HTML Email Builder
# ──────────────────────────────────────────────────────────────────────────────
def build_medpedia_email_html(
    query: str,
    recipient_email: str,
    pdf_size_bytes: int,
    generation_date_str: str,
    public_url: str,
    logo_url: str,
    contact_email: str,
) -> str:
    """Constructs an editorial, responsive, email-client-compatible HTML email body.
    Adheres strictly to content rules: includes About Medpedia, website link,
    attachment info, and medical disclaimer; excludes tech stack & GitHub info.
    """
    pdf_size_kb = max(1, round(pdf_size_bytes / 1024))
    escaped_query = html.escape(query or "Biomedical Literature Research Inquiry")
    escaped_recipient = html.escape(recipient_email)
    escaped_url = html.escape(public_url)
    escaped_contact = html.escape(contact_email)
    current_year = datetime.now(timezone.utc).year

    # Embedded Logo SVG / Image Fallback
    logo_img_tag = (
        f'<img src="{html.escape(logo_url)}" alt="Medpedia" width="48" height="48" style="display: block; border: 0; border-radius: 10px;" />'
        if logo_url
        else (
            '<div style="width: 44px; height: 44px; background-color: #3A0F34; border-radius: 10px; '
            'border: 1px solid #240720; text-align: center; line-height: 44px; color: #EAAA00; '
            'font-family: Helvetica, Arial, sans-serif; font-size: 22px; font-weight: bold; margin: 0 auto;">'
            'M</div>'
        )
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Medpedia Research Evidence Report is Ready</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: #FAF8F5;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            color: #211B20;
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }}
        table {{
            border-collapse: collapse;
        }}
        .container {{
            max-width: 640px;
            margin: 24px auto;
            background-color: #FFFFFF;
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid #DDE3E8;
            box-shadow: 0 4px 16px rgba(58, 15, 52, 0.05);
        }}
        .header {{
            background: linear-gradient(135deg, #3A0F34 0%, #240720 100%);
            padding: 32px 28px;
            text-align: center;
            color: #FAF8F5;
            border-bottom: 3px solid #EAAA00;
        }}
        .header-title {{
            font-size: 22px;
            font-weight: 700;
            letter-spacing: 0.5px;
            margin: 12px 0 4px 0;
            color: #FAF8F5;
        }}
        .header-badge {{
            display: inline-block;
            background-color: rgba(234, 170, 0, 0.18);
            color: #EAAA00;
            border: 1px solid rgba(234, 170, 0, 0.4);
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            padding: 4px 12px;
            border-radius: 20px;
        }}
        .content {{
            padding: 28px 28px 20px 28px;
        }}
        .greeting {{
            font-size: 15px;
            color: #211B20;
            margin-bottom: 16px;
        }}
        .inquiry-card {{
            background-color: #FAF8F5;
            border: 1px solid #DDE3E8;
            border-left: 4px solid #3A0F34;
            border-radius: 8px;
            padding: 16px 18px;
            margin: 18px 0;
        }}
        .inquiry-label {{
            font-size: 11px;
            font-weight: 700;
            color: #6B5F69;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 6px;
        }}
        .inquiry-query {{
            font-size: 14px;
            font-weight: 600;
            color: #3A0F34;
            line-height: 1.5;
        }}
        .attachment-card {{
            background: linear-gradient(135deg, #FAF8F5 0%, #F5F1EB 100%);
            border: 1px solid #DDE3E8;
            border-radius: 10px;
            padding: 16px 18px;
            margin: 20px 0;
        }}
        .attachment-header {{
            font-size: 13px;
            font-weight: 700;
            color: #3A0F34;
            margin-bottom: 4px;
        }}
        .attachment-desc {{
            font-size: 12px;
            color: #6B5F69;
            line-height: 1.5;
        }}
        .section-title {{
            font-size: 15px;
            font-weight: 700;
            color: #3A0F34;
            margin-top: 24px;
            margin-bottom: 8px;
            border-bottom: 1px solid #DDE3E8;
            padding-bottom: 6px;
        }}
        .about-text {{
            font-size: 13px;
            color: #4A4048;
            line-height: 1.6;
            margin-bottom: 12px;
        }}
        .portal-btn {{
            display: inline-block;
            background-color: #3A0F34;
            color: #FAF8F5 !important;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.5px;
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            margin-top: 6px;
        }}
        .disclaimer-section {{
            background-color: #F8F6F3;
            border-top: 1px solid #DDE3E8;
            border-bottom: 1px solid #DDE3E8;
            padding: 18px 28px;
            font-size: 11px;
            color: #6B5F69;
            line-height: 1.55;
            font-style: italic;
        }}
        .footer {{
            background-color: #FAF8F5;
            padding: 24px 28px;
            text-align: center;
            font-size: 11px;
            color: #6B5F69;
        }}
        .footer a {{
            color: #3A0F34;
            text-decoration: none;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div style="text-align: center; margin-bottom: 10px;">
                {logo_img_tag}
            </div>
            <div class="header-badge">EVIDENCE REPORT DELIVERY</div>
            <div class="header-title">Medpedia Biomedical Research</div>
        </div>

        <!-- Main Content -->
        <div class="content">
            <p class="greeting">
                Hello,<br><br>
                Your requested biomedical research report has been compiled and is attached to this email.
            </p>

            <!-- Research Inquiry Card -->
            <div class="inquiry-card">
                <div class="inquiry-label">Original Clinical Research Question</div>
                <div class="inquiry-query">{escaped_query}</div>
                <div style="margin-top: 10px; font-size: 11px; color: #6B5F69;">
                    <strong>Report Date:</strong> {generation_date_str} &nbsp;|&nbsp;
                    <strong>Recipient:</strong> {escaped_recipient}
                </div>
            </div>

            <!-- Attachment Notice -->
            <div class="attachment-card">
                <div class="attachment-header">
                    📎 Attached Dossier: {ATTACHMENT_FILENAME}
                </div>
                <div class="attachment-desc">
                    <strong>Format:</strong> Adobe Portable Document Format (.pdf) &nbsp;|&nbsp;
                    <strong>Size:</strong> ~{pdf_size_kb} KB<br>
                    The complete systematic evidence synthesis, PICO parameter extraction matrices,
                    and original peer-reviewed publication records are preserved in full within the attached document.
                </div>
            </div>

            <!-- About Medpedia (Exact Purpose Introduction) -->
            <div class="section-title">About Medpedia</div>
            <p class="about-text">
                Medpedia is an open biomedical discovery and research platform designed to streamline evidence synthesis
                for clinicians, medical researchers, academics, and healthcare students. Formulating clinical research
                inquiries across extensive biomedical literature typically requires navigating disparate repositories
                and reviewing dozens of heterogeneous publications.
            </p>
            <p class="about-text">
                Medpedia solves this by retrieving peer-reviewed literature directly from authoritative repositories,
                including MEDLINE and PubMed Central (PMC). It automatically extracts structured PICO parameters
                (Population, Intervention, Comparator, and Outcomes), compares study methodologies, and presents
                coherent evidence summaries alongside detailed publication citations. Every synthesis directly links to
                original publication records, allowing clinicians and researchers to verify primary citations and explore
                high-certainty biomedical evidence efficiently.
            </p>
            <p style="margin-top: 14px;">
                <a href="{escaped_url}" class="portal-btn">Access Medpedia Research Platform &rarr;</a>
            </p>
        </div>

        <!-- Medical Disclaimer (Email Only) -->
        <div class="disclaimer-section">
            {MANDATORY_MEDICAL_DISCLAIMER}
        </div>

        <!-- Footer -->
        <div class="footer">
            <p style="margin: 0 0 6px 0; font-weight: 600; color: #3A0F34;">
                Medpedia &bull; Biomedical Literature Synthesis Platform
            </p>
            <p style="margin: 0 0 6px 0;">
                Platform: <a href="{escaped_url}">{escaped_url}</a> &nbsp;|&nbsp; Contact: <a href="mailto:{escaped_contact}">{escaped_contact}</a>
            </p>
            <p style="margin: 0; color: #8A7E88;">
                &copy; {current_year} Medpedia. All rights reserved.
            </p>
        </div>
    </div>
</body>
</html>"""


def build_medpedia_plain_text(
    query: str,
    recipient_email: str,
    generation_date_str: str,
    public_url: str,
    contact_email: str,
) -> str:
    """Builds clean, professional plain-text fallback email representation."""
    return (
        f"Medpedia — Medical Research Evidence Report\n"
        f"{'='*60}\n\n"
        f"Hello,\n\n"
        f"Your requested biomedical research report has been compiled and is attached to this email.\n\n"
        f"CLINICAL RESEARCH QUESTION:\n"
        f"{query}\n\n"
        f"REPORT DETAILS:\n"
        f"- Date: {generation_date_str}\n"
        f"- Recipient: {recipient_email}\n"
        f"- Attached Document: {ATTACHMENT_FILENAME}\n\n"
        f"{'-'*60}\n"
        f"ABOUT MEDPEDIA\n"
        f"{'-'*60}\n"
        f"Medpedia is an open biomedical discovery and research platform designed to\n"
        f"streamline evidence synthesis for clinicians, researchers, academics, and students.\n"
        f"It retrieves peer-reviewed literature from authoritative repositories like MEDLINE\n"
        f"and PubMed Central (PMC), extracts clinical PICO parameters, and organizes findings\n"
        f"into structured evidence dossiers with verifiable primary citations.\n\n"
        f"Platform: {public_url}\n"
        f"Contact: {contact_email}\n\n"
        f"{'-'*60}\n"
        f"{MANDATORY_MEDICAL_DISCLAIMER}\n"
        f"{'='*60}\n"
    )


# ──────────────────────────────────────────────────────────────────────────────
# Dispatcher 1: Google Gmail REST API (HTTPS Port 443 — Primary, 35MB PDFs)
# ──────────────────────────────────────────────────────────────────────────────
def _get_gmail_access_token(
    client_id: str,
    client_secret: str,
    refresh_token: str,
    timeout: float = 10.0,
) -> Tuple[bool, str]:
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
    pdf_bytes: bytes | None,
    client_id: str,
    client_secret: str,
    refresh_token: str,
    timeout: float = 25.0,
) -> Tuple[bool, str]:
    """Sends an RFC 2822 multipart email with PDF attachment directly through
    Google's official Gmail REST API over HTTPS Port 443.
    Supports up to 35 MB per message with zero intermediary services.
    """
    ok, token_or_err = _get_gmail_access_token(client_id, client_secret, refresh_token, timeout=timeout)
    if not ok:
        return False, token_or_err
    access_token = token_or_err

    # Build standard MIME message
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = formataddr(("Medpedia", sender_email))
    msg["To"] = recipient_email

    alt_body = MIMEMultipart("alternative")
    alt_body.attach(MIMEText(plain_text, "plain", "utf-8"))
    alt_body.attach(MIMEText(html_body, "html", "utf-8"))
    msg.attach(alt_body)

    if pdf_bytes:
        pdf_part = MIMEApplication(pdf_bytes, _subtype="pdf", Name=ATTACHMENT_FILENAME)
        pdf_part["Content-Disposition"] = f'attachment; filename="{ATTACHMENT_FILENAME}"'
        msg.attach(pdf_part)

    raw_b64 = base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")

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
            return True, "Email sent successfully."
        return False, f"Gmail API error ({resp.status_code}): {resp.text}"
    except Exception as exc:
        return False, f"Network error sending via Gmail API: {exc}"


# ──────────────────────────────────────────────────────────────────────────────
# Dispatcher 2: Direct Gmail SMTP Fallback (Port 587 STARTTLS)
# ──────────────────────────────────────────────────────────────────────────────
def _dispatch_via_smtp(
    smtp_user: str,
    smtp_password: str,
    smtp_host: str,
    smtp_port: int,
    smtp_timeout: float,
    recipient_email: str,
    subject: str,
    plain_text: str,
    html_body: str,
    pdf_bytes: bytes | None,
) -> Tuple[bool, str]:
    """Dispatches message via standard SMTP for local development."""
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = formataddr(("Medpedia", smtp_user))
    msg["To"] = recipient_email

    alt_body = MIMEMultipart("alternative")
    alt_body.attach(MIMEText(plain_text, "plain", "utf-8"))
    alt_body.attach(MIMEText(html_body, "html", "utf-8"))
    msg.attach(alt_body)

    if pdf_bytes:
        pdf_part = MIMEApplication(pdf_bytes, _subtype="pdf", Name=ATTACHMENT_FILENAME)
        pdf_part["Content-Disposition"] = f'attachment; filename="{ATTACHMENT_FILENAME}"'
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
        return True, "Email sent successfully."
    except smtplib.SMTPAuthenticationError:
        return False, "Gmail SMTP authentication failed. Check your SMTP_USER and Google App Password."
    except smtplib.SMTPRecipientsRefused:
        return False, f"Recipient address '{recipient_email}' was refused by the SMTP server."
    except smtplib.SMTPSenderRefused:
        return False, "Sender address was refused by the SMTP server."
    except smtplib.SMTPDataError as exc:
        err_msg = exc.smtp_error.decode("utf-8", errors="replace") if hasattr(exc, "smtp_error") and isinstance(exc.smtp_error, bytes) else str(exc)
        return False, f"SMTP server refused message data: {err_msg}"
    except TimeoutError:
        return False, f"SMTP connection timed out after {smtp_timeout}s. Outbound SMTP may be blocked on this host."
    except OSError as exc:
        if getattr(exc, "errno", None) == 101 or "unreachable" in str(exc).lower():
            return False, "Outbound SMTP port blocked on hosting provider (Errno 101). Use HTTPS over Port 443."
        return False, f"Network OS error ({getattr(exc, 'errno', 'unknown')}): {exc}"
    except Exception as exc:
        return False, f"SMTP error: {exc}"


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
    """Composes and delivers the complete research evidence package as a
    professional Medpedia email with the complete research dossier PDF attached.

    Primary transport: Google Cloud Gmail REST API over HTTPS Port 443 (supports up to 35MB attachments).
    Secondary / Local fallback: Direct Gmail SMTP (Port 587 STARTTLS).

    Args:
        evidence_report: Synthesized evidence report Markdown.
        recipient_email: Target clinician or researcher email.
        articles_list:   Retrieved literature citations and abstracts.
        query:           Original clinical research inquiry.

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

    now_dt = datetime.now(timezone.utc)
    date_display = now_dt.strftime("%B %d, %Y")
    subject = "Your Medpedia Research Evidence Report is Ready"

    # Environment configuration
    public_url = (os.getenv("MEDPEDIA_PUBLIC_URL") or "https://medpedia-smr.vercel.app").strip()
    logo_url = (os.getenv("MEDPEDIA_LOGO_URL") or f"{public_url}/favicon.svg").strip()
    contact_email = (os.getenv("MEDPEDIA_CONTACT_EMAIL") or "hello051507@gmail.com").strip()

    # 3. Generate Complete Research PDF Dossier
    try:
        pdf_bytes = generate_research_pdf(
            evidence_report=evidence_report,
            articles_list=articles_list,
            query=query,
            recipient_email=target_recipient,
            session_id=f"MED-{now_dt.strftime('%Y%m%d%H%M')}",
            timestamp=now_dt,
        )
    except Exception as exc:
        return f"Error: PDF generation failed: {exc}"

    if not pdf_bytes or len(pdf_bytes) < 100:
        return "Error: Generated PDF is empty or invalid."

    # 4. Construct Professional Email Body (HTML & Plain Text)
    html_body = build_medpedia_email_html(
        query=query,
        recipient_email=target_recipient,
        pdf_size_bytes=len(pdf_bytes),
        generation_date_str=date_display,
        public_url=public_url,
        logo_url=logo_url,
        contact_email=contact_email,
    )
    plain_text = build_medpedia_plain_text(
        query=query,
        recipient_email=target_recipient,
        generation_date_str=date_display,
        public_url=public_url,
        contact_email=contact_email,
    )

    # 5. Dispatch Transport Selection
    # Transport A: Google Gmail REST API (Primary Cloud Dispatch over HTTPS Port 443 — Render Free Tier compatible)
    gmail_client_id = (os.getenv("GMAIL_CLIENT_ID") or "").strip()
    gmail_client_secret = (os.getenv("GMAIL_CLIENT_SECRET") or "").strip()
    gmail_refresh_token = (os.getenv("GMAIL_REFRESH_TOKEN") or "").strip()
    gmail_sender = (os.getenv("GMAIL_SENDER_EMAIL") or os.getenv("SMTP_USER") or "hello051507@gmail.com").strip()

    gmail_configured = bool(gmail_client_id and gmail_client_secret and gmail_refresh_token)
    gmail_err_msg = ""
    if gmail_configured:
        ok, res_msg = _dispatch_via_gmail_api(
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
        if ok:
            return "Email sent successfully."
        gmail_err_msg = res_msg

    # Transport B: Direct Gmail SMTP (Secondary / Local Fallback via Port 587 STARTTLS)
    smtp_user = (os.getenv("SMTP_USER") or "").strip()
    smtp_password = (os.getenv("SMTP_PASSWORD") or "").strip()
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
    try:
        smtp_port = int(os.getenv("SMTP_PORT", "587").strip())
    except ValueError:
        smtp_port = 587
    try:
        smtp_timeout = float(os.getenv("SMTP_TIMEOUT", "15").strip())
    except ValueError:
        smtp_timeout = 15.0

    if smtp_user and smtp_password:
        ok, smtp_res_msg = _dispatch_via_smtp(
            smtp_user=smtp_user,
            smtp_password=smtp_password,
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_timeout=smtp_timeout,
            recipient_email=target_recipient,
            subject=subject,
            plain_text=plain_text,
            html_body=html_body,
            pdf_bytes=pdf_bytes,
        )
        if ok:
            return "Email sent successfully."
        if gmail_configured:
            return f"Error: Both Google Cloud Gmail API ({gmail_err_msg}) and SMTP ({smtp_res_msg}) failed."
        return f"Error: Dispatch failed: {smtp_res_msg}"

    if gmail_configured:
        return f"Error: Google Cloud Gmail API dispatch failed: {gmail_err_msg}"

    return "Error: Missing email dispatch credentials. Please configure GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN, and GMAIL_SENDER_EMAIL (or SMTP_* fallback)."
