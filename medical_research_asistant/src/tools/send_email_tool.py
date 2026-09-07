"""
send_email_tool.py
──────────────────
Provides the `send_email` LangChain-compatible tool used by the
med_email_dispatcher node in the LangGraph pipeline.

Sends the full evidence report (evidence cards + synthesis) as a
styled HTML email. No CSV attachment is needed.
"""

import os
import re
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from langchain_core.tools import tool


# ──────────────────────────────────────────────────────────────────────────────
# Helper — convert Markdown to styled HTML
# ──────────────────────────────────────────────────────────────────────────────

def _markdown_to_html(md: str) -> str:
    """
    Enhanced Markdown → HTML converter for the evidence report.
    """
    link_re   = re.compile(r'\[([^\]]+)\]\((https?://[^\s)]+)\)')
    bold_re   = re.compile(r'\*\*(.+?)\*\*')
    italic_re = re.compile(r'\*(.+?)\*')

    html_lines: list[str] = []
    in_list = False

    for line in md.splitlines():
        stripped = line.strip()

        # Handle separators
        if stripped in ("---", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                          "─────────────────────────────────────────────",
                          "──────────────────"):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append('<hr style="border: none; border-top: 1px solid #E2E8F0; margin: 30px 0;">')
            continue

        # Handle headings
        if stripped.startswith("### "):
            if in_list: html_lines.append("</ul>"); in_list = False
            html_lines.append(f'<h3 style="color: #2D3748; font-size: 18px; margin-top: 24px; margin-bottom: 12px;">{stripped[4:]}</h3>')
        elif stripped.startswith("## "):
            if in_list: html_lines.append("</ul>"); in_list = False
            html_lines.append(f'<h2 style="color: #1A365D; font-size: 22px; border-bottom: 2px solid #EBF8FF; padding-bottom: 8px; margin-top: 32px; margin-bottom: 16px;">{stripped[3:]}</h2>')
        elif stripped.startswith("# "):
            if in_list: html_lines.append("</ul>"); in_list = False
            html_lines.append(f'<h1 style="color: #2A4365; font-size: 26px; margin-top: 40px; margin-bottom: 20px;">{stripped[2:]}</h1>')
        
        # Handle lists
        elif stripped.startswith("- "):
            if not in_list:
                html_lines.append('<ul style="padding-left: 20px; color: #4A5568;">')
                in_list = True
            content = stripped[2:]
            content = link_re.sub(r'<a href="\2" style="color: #3182CE; text-decoration: none; font-weight: 500;">\1</a>', content)
            content = bold_re.sub(r'<strong style="color: #2D3748;">\1</strong>', content)
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
            processed = link_re.sub(r'<a href="\2" style="color: #3182CE; text-decoration: none; font-weight: 500;">\1</a>', stripped)
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
# LangChain Tool
# ──────────────────────────────────────────────────────────────────────────────

@tool
def send_email(
    evidence_report: str,
    recipient_email: str,
) -> str:
    """
    Composes and sends the full evidence report as a styled HTML email.

    Args:
        evidence_report:  The complete Markdown output from the evidence
                          builder agent (article cards + Overall Evidence
                          Summary). This is rendered as HTML in the email body.
        recipient_email:  Destination email address.

    Returns:
        "Email sent successfully." on success, or an error description.
    """
    smtp_user     = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_host     = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port     = int(os.getenv("SMTP_PORT", 587))

    if not smtp_user or not smtp_password:
        return "Error: SMTP_USER and SMTP_PASSWORD must be set in environment variables."

    # Build message headers
    now = datetime.now(timezone.utc).strftime("%B %d, %Y")
    msg = MIMEMultipart()
    msg["Subject"] = f"🔬 Medical Research Insights – {now}"
    msg["From"]    = f"Medical Research Assistant <{smtp_user}>"
    msg["To"]      = recipient_email

    # Render the evidence report as HTML
    report_html = _markdown_to_html(evidence_report or "No evidence report provided.")

    html_body = f"""
    <!DOCTYPE html>
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
                <p>Generated by <strong>Medical Research Pro</strong> Agentic Pipeline</p>
                <span class="disclaimer">
                    <strong>Medical Disclaimer:</strong> This report is for informational purposes only and does not constitute medical advice. 
                    Always seek the advice of a physician or other qualified health provider with any questions regarding a medical condition.
                </span>
            </div>
        </div>
    </body>
    </html>
    """
    msg.attach(MIMEText(html_body, "html"))

    # Send via SMTP
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        return "Email sent successfully."
    except Exception as exc:
        return f"Error: {exc}"
