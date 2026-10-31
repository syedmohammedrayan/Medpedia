"""
send_email_tool.py
──────────────────
Provides the `send_email` LangChain-compatible tool used by the
med_email_dispatcher node in the LangGraph pipeline.

Sends the full evidence report (evidence cards + synthesis) as a
styled HTML email using Gmail SMTP (STARTTLS on port 587).
"""

import html
import os
import re
import smtplib
import socket
import ssl
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from langchain_core.tools import tool


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
            html_lines.append('<hr style="border: none; border-top: 1px solid #E2E8F0; margin: 30px 0;">')
            continue

        # Handle headings
        if stripped.startswith("### "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            title = html.escape(stripped[4:])
            html_lines.append(f'<h3 style="color: #2D3748; font-size: 18px; margin-top: 24px; margin-bottom: 12px;">{title}</h3>')
        elif stripped.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            title = html.escape(stripped[3:])
            html_lines.append(f'<h2 style="color: #1A365D; font-size: 22px; border-bottom: 2px solid #EBF8FF; padding-bottom: 8px; margin-top: 32px; margin-bottom: 16px;">{title}</h2>')
        elif stripped.startswith("# "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            title = html.escape(stripped[2:])
            html_lines.append(f'<h1 style="color: #2A4365; font-size: 26px; margin-top: 40px; margin-bottom: 20px;">{title}</h1>')

        # Handle lists
        elif stripped.startswith("- "):
            if not in_list:
                html_lines.append('<ul style="padding-left: 20px; color: #4A5568;">')
                in_list = True
            content = html.escape(stripped[2:])
            content = link_re.sub(r'<a href="\2" style="color: #3182CE; text-decoration: none; font-weight: 500;">\1</a>', content)
            content = bold_re.sub(r'<strong style="color: #2D3748;">\1</strong>', content)
            content = italic_re.sub(r'<em style="color: #4A5568;">\1</em>', content)
            html_lines.append(f'<li style="margin-bottom: 8px;">{content}</li>')

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
            processed = link_re.sub(r'<a href="\2" style="color: #3182CE; text-decoration: none; font-weight: 500;">\1</a>', processed)
            processed = bold_re.sub(r'<strong style="color: #2D3748;">\1</strong>', processed)
            processed = italic_re.sub(r'<em style="color: #4A5568;">\1</em>', processed)

            # Special check for article "Cards" header or badges
            if "Article #" in processed or "STUDY TYPE" in processed.upper() or "EVIDENCE" in processed.upper():
                html_lines.append(f'<p style="margin: 10px 0; font-size: 15px; color: #2D3748; background-color: #F7FAFC; padding: 8px 12px; border-left: 4px solid #4299E1; border-radius: 4px;">{processed}</p>')
            else:
                html_lines.append(f'<p style="margin: 8px 0; font-size: 15px; color: #4A5568;">{processed}</p>')

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


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
# LangChain Tool
# ──────────────────────────────────────────────────────────────────────────────

@tool
def send_email(
    evidence_report: str,
    recipient_email: str,
) -> str:
    """
    Composes and sends the full evidence report as a styled HTML email via Gmail SMTP.

    Args:
        evidence_report:  The complete Markdown output from the evidence
                          builder agent (article cards + Overall Evidence
                          Summary). This is rendered as HTML in the email body.
        recipient_email:  Destination email address.

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

    # 3. Read SMTP configuration from environment variables
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
    smtp_port_raw = os.getenv("SMTP_PORT", "587").strip()
    try:
        smtp_port = int(smtp_port_raw)
    except ValueError:
        smtp_port = 587

    smtp_user = (os.getenv("SMTP_USER") or "").strip()
    smtp_password = (os.getenv("SMTP_PASSWORD") or "").strip()

    timeout_raw = os.getenv("SMTP_TIMEOUT", "15").strip()
    try:
        smtp_timeout = float(timeout_raw)
    except ValueError:
        smtp_timeout = 15.0

    # 4. Check for SMTP credentials
    if not smtp_user or not smtp_password:
        return "Error: Missing SMTP credentials. SMTP_USER and SMTP_PASSWORD must be configured in environment variables."

    # 5. Build email message (both text and HTML parts for multipart/alternative)
    now = datetime.now(timezone.utc).strftime("%B %d, %Y")
    report_html = _markdown_to_html(evidence_report)

    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #2D3748;
            background-color: #F8FAFC;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 700px;
            margin: 40px auto;
            background-color: #ffffff;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border: 1px solid #E2E8F0;
        }}
        .header {{
            background: linear-gradient(135deg, #1A365D 0%, #2B6CB0 100%);
            color: white;
            padding: 40px 32px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 700;
            letter-spacing: -0.025em;
        }}
        .header p {{
            margin: 10px 0 0;
            opacity: 0.9;
            font-size: 16px;
        }}
        .content {{
            padding: 32px;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 8px;
        }}
        .footer {{
            background-color: #F7FAFC;
            padding: 24px 32px;
            text-align: center;
            font-size: 13px;
            color: #718096;
            border-top: 1px solid #E2E8F0;
        }}
        .disclaimer {{
            font-style: italic;
            margin-top: 12px;
            display: block;
        }}
        a {{
            color: #3182CE;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
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
            {report_html}
        </div>

        <div class="footer">
            <p>Generated by <strong>Medpedia</strong> Agentic Pipeline</p>
            <span class="disclaimer">
                <strong>Medical Disclaimer:</strong> This report is for informational purposes only and does not constitute medical advice. 
                Always seek the advice of a physician or other qualified health provider with any questions regarding a medical condition.
            </span>
        </div>
    </div>
</body>
</html>"""

    plain_text = (
        f"Medical Research Insights – {now}\n\n"
        f"{evidence_report.strip()}\n\n"
        f"─────────────────────────────────────────────\n"
        f"Generated by Medpedia Agentic Pipeline\n"
        f"Medical Disclaimer: This report is for informational purposes only and does not constitute medical advice. "
        f"Always seek the advice of a physician or other qualified health provider with any questions regarding a medical condition.\n"
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🔬 Medical Research Insights – {now}"
    msg["From"] = formataddr(("Medpedia", smtp_user))
    msg["To"] = target_recipient

    msg.attach(MIMEText(plain_text, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    # 6. Dispatch via Gmail SMTP
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_host, smtp_port, timeout=smtp_timeout) as server:
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
    except Exception as exc:
        return f"Error: Unexpected error while sending email: {exc}"

