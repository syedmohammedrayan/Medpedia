"""
test_send_email_tool.py
───────────────────────
Comprehensive unit test suite for Medpedia's email delivery system,
including Google Gmail REST API (primary HTTPS dispatch),
SMTP fallback, address validation, PDF attachment verification,
content governance, and LangGraph dispatcher node integration.
"""

import os
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from agent.graph import med_email_dispatcher_node
from tools.send_email_tool import (
    ATTACHMENT_FILENAME,
    _validate_recipient_email,
    build_medpedia_email_html,
    send_email,
)

SAMPLE_EVIDENCE = """
## 1. Executive Summary
Controlled trials demonstrate significant therapeutic efficacy for SGLT2 inhibitors.

- Reduced cardiovascular mortality by 26%.
- Consistent renal protective benefits across cohorts.
"""

SAMPLE_ARTICLES = """
### Article #1
**Title:** SGLT2 Inhibitors in Heart Failure
**Authors:** McMurray JJV, et al.
**Journal:** NEJM
**Summary:** [OBJECTIVE] Test efficacy. [RESULTS] Hazard ratio 0.74. [CONCLUSIONS] Favorable outcomes.
**Links:**
- [PubMed](https://pubmed.ncbi.nlm.nih.gov/31535829/)
---
"""


# ── Test 1: Email HTML Contains About Medpedia (Section 1B, 2) ───────────────
def test_email_html_contains_about_medpedia():
    """Verify that recipient-facing email body contains the comprehensive About Medpedia section."""
    html = build_medpedia_email_html(
        query="SGLT2i in heart failure",
        recipient_email="clinician@hospital.edu",
        pdf_size_bytes=15000,
        generation_date_str="November 01, 2026",
        public_url="https://medpedia-smr.vercel.app",
        logo_url="https://medpedia-smr.vercel.app/favicon.svg",
        contact_email="support@medpedia-smr.vercel.app",
    )

    assert "About Medpedia" in html
    assert "biomedical discovery and research platform" in html
    assert "MEDLINE" in html
    assert "PubMed Central" in html
    assert "PICO parameters" in html
    assert "verify primary citations" in html


# ── Test 2: Email HTML Contains Medical Disclaimer (Section 1B) ───────────────
def test_email_html_contains_medical_disclaimer():
    """Verify that recipient-facing email body contains the mandatory disclaimer."""
    html = build_medpedia_email_html(
        query="Heart failure therapy",
        recipient_email="clinician@hospital.edu",
        pdf_size_bytes=15000,
        generation_date_str="November 01, 2026",
        public_url="https://medpedia-smr.vercel.app",
        logo_url="https://medpedia-smr.vercel.app/favicon.svg",
        contact_email="support@medpedia-smr.vercel.app",
    )

    assert "Medical Disclaimer:" in html
    assert "AI-generated and may contain inaccuracies" in html
    assert "do not constitute medical advice, diagnosis or treatment recommendations" in html


# ── Test 3: Email HTML Contains Correct Website Link & Attachment Info ────────
def test_email_html_contains_website_link_and_attachment_info():
    """Verify email contains the explicitly configured production website link and attachment details."""
    html = build_medpedia_email_html(
        query="Cardiorenal outcomes",
        recipient_email="doctor@clinic.org",
        pdf_size_bytes=24576,
        generation_date_str="November 01, 2026",
        public_url="https://medpedia-production.org",
        logo_url="https://medpedia-production.org/favicon.svg",
        contact_email="hello@medpedia-production.org",
    )

    assert "https://medpedia-production.org" in html
    assert ATTACHMENT_FILENAME in html
    assert "~24 KB" in html or "~25 KB" in html


# ── Test 4: Email HTML Strictly Excludes Tech Stack & GitHub ──────────────────
def test_email_html_excludes_tech_stack_and_github():
    """Verify email body does NOT mention internal frameworks, APIs, languages or GitHub."""
    html = build_medpedia_email_html(
        query="Oncology trials",
        recipient_email="oncologist@hospital.edu",
        pdf_size_bytes=18000,
        generation_date_str="November 01, 2026",
        public_url="https://medpedia-smr.vercel.app",
        logo_url="",
        contact_email="contact@medpedia.org",
    )

    assert "github.com" not in html
    assert "FastAPI" not in html
    assert "React" not in html
    assert "LangGraph" not in html
    assert "Python" not in html
    assert "EmailJS" not in html
    assert "Render" not in html


# ── Test 5: Dynamic Recipient Validation ──────────────────────────────────────
@pytest.mark.parametrize("recipient", [
    "clinician@hospital.edu",
    "researcher@university.ac.uk",
    "dr.smith+cardio@clinic.med.org",
    "student@health.gov",
])
def test_dynamic_recipient_accepted(recipient: str):
    """Verify dynamic recipient addresses are properly validated and accepted."""
    ok, cleaned = _validate_recipient_email(recipient)
    assert ok is True
    assert cleaned == recipient


@pytest.mark.parametrize("invalid_email", [
    "",
    "   ",
    "not-an-email",
    "test\nuser@hospital.edu",
    "user1@test.com, user2@test.com",
    "@missing-username.com",
])
def test_invalid_recipient_rejected(invalid_email: str):
    """Verify invalid addresses and header injection attempts are safely rejected."""
    ok, err = _validate_recipient_email(invalid_email)
    assert ok is False
    assert "Error:" in err


# ── Test 6: Google Gmail REST API Dispatch (Primary HTTPS) ────────────────────
def test_gmail_api_dispatch_success():
    """Verify primary Google Gmail REST API dispatch over HTTPS Port 443 with binary PDF attachment."""
    env = {
        "GMAIL_CLIENT_ID": "mock-client-id",
        "GMAIL_CLIENT_SECRET": "mock-client-secret",
        "GMAIL_REFRESH_TOKEN": "mock-refresh-token",
        "GMAIL_SENDER_EMAIL": "hello051507@gmail.com",
    }
    with patch.dict(os.environ, env, clear=True):
        with patch("requests.post") as mock_post:
            token_resp = MagicMock()
            token_resp.status_code = 200
            token_resp.json.return_value = {"access_token": "mock-access-token-123"}

            send_resp = MagicMock()
            send_resp.status_code = 200
            send_resp.json.return_value = {"id": "msg_999"}

            mock_post.side_effect = [token_resp, send_resp]

            result = send_email.invoke({
                "evidence_report": SAMPLE_EVIDENCE,
                "articles_list": SAMPLE_ARTICLES,
                "recipient_email": "doctor@hospital.edu",
                "query": "Cardiorenal trials",
            })

            assert result == "Email sent successfully."
            assert mock_post.call_count == 2
            # First call: OAuth token refresh
            assert mock_post.call_args_list[0][0][0] == "https://oauth2.googleapis.com/token"
            assert mock_post.call_args_list[0][1]["data"]["grant_type"] == "refresh_token"
            # Second call: Gmail message send
            assert mock_post.call_args_list[1][0][0] == "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
            assert mock_post.call_args_list[1][1]["headers"]["Authorization"] == "Bearer mock-access-token-123"
            assert "raw" in mock_post.call_args_list[1][1]["json"]


# ── Test 7: Google Gmail REST API Token Failure Propagated ────────────────────
def test_gmail_api_token_failure_propagates_error():
    """Verify that if Google OAuth token refresh fails and no fallback is available, accurate error is returned."""
    env = {
        "GMAIL_CLIENT_ID": "mock-client-id",
        "GMAIL_CLIENT_SECRET": "mock-client-secret",
        "GMAIL_REFRESH_TOKEN": "invalid-token",
        "GMAIL_SENDER_EMAIL": "hello051507@gmail.com",
    }
    with patch.dict(os.environ, env, clear=True):
        with patch("requests.post") as mock_post:
            token_resp = MagicMock()
            token_resp.status_code = 400
            token_resp.text = "invalid_grant"
            mock_post.return_value = token_resp

            result = send_email.invoke({
                "evidence_report": SAMPLE_EVIDENCE,
                "recipient_email": "clinician@hospital.edu",
            })

            assert "Google Cloud Gmail API dispatch failed:" in result
            assert "Google OAuth token refresh failed (400)" in result


# ── Test 8: Google Gmail REST API Failure Falls Back to SMTP ──────────────────
def test_gmail_api_failure_falls_back_to_smtp():
    """Verify that if Google Gmail REST API fails, system gracefully falls back to SMTP if configured."""
    env = {
        "GMAIL_CLIENT_ID": "mock-client-id",
        "GMAIL_CLIENT_SECRET": "mock-client-secret",
        "GMAIL_REFRESH_TOKEN": "bad-token",
        "GMAIL_SENDER_EMAIL": "hello051507@gmail.com",
        "SMTP_HOST": "smtp.gmail.com",
        "SMTP_PORT": "587",
        "SMTP_USER": "syedmohammedrayan2007@gmail.com",
        "SMTP_PASSWORD": "mock_app_password",
    }
    with patch.dict(os.environ, env, clear=True):
        with patch("requests.post") as mock_post, patch("smtplib.SMTP") as mock_smtp, patch("ssl.create_default_context"):
            token_resp = MagicMock()
            token_resp.status_code = 401
            token_resp.text = "unauthorized"
            mock_post.return_value = token_resp

            server_instance = MagicMock()
            mock_smtp.return_value.__enter__.return_value = server_instance

            result = send_email.invoke({
                "evidence_report": SAMPLE_EVIDENCE,
                "recipient_email": "clinician@hospital.edu",
            })

            assert result == "Email sent successfully."
            server_instance.send_message.assert_called_once()


# ── Test 9: SMTP Dispatch Protocol Sequence & Attachment ──────────────────────
def test_smtp_dispatch_protocol_and_attachment():
    """Verify SMTP fallback dispatches mixed multipart with application/pdf attachment."""
    env = {
        "SMTP_HOST": "smtp.gmail.com",
        "SMTP_PORT": "587",
        "SMTP_USER": "syedmohammedrayan2007@gmail.com",
        "SMTP_PASSWORD": "mock_app_password",
        "SMTP_TIMEOUT": "20",
    }
    with patch.dict(os.environ, env, clear=True):
        with patch("smtplib.SMTP") as mock_smtp, patch("ssl.create_default_context"):
            server_instance = MagicMock()
            mock_smtp.return_value.__enter__.return_value = server_instance

            result = send_email.invoke({
                "evidence_report": SAMPLE_EVIDENCE,
                "articles_list": SAMPLE_ARTICLES,
                "recipient_email": "clinician@hospital.edu",
                "query": "Inquiry on diabetes",
            })

            assert result == "Email sent successfully."
            server_instance.starttls.assert_called_once()
            server_instance.login.assert_called_once_with("syedmohammedrayan2007@gmail.com", "mock_app_password")
            server_instance.send_message.assert_called_once()

            # Check that message contains attachment
            sent_msg = server_instance.send_message.call_args[0][0]
            assert sent_msg.is_multipart()
            parts = sent_msg.get_payload()
            assert any(p.get_content_type() == "application/pdf" for p in parts)


# ── Test 10: LangGraph Dispatcher Node Integration ────────────────────────────
def test_langgraph_med_email_dispatcher_node_integration():
    """Verify LangGraph dispatcher node passes required parameters and sets status."""
    state = {
        "messages": [HumanMessage(content="What are the treatments for heart failure?")],
        "evidence_report": SAMPLE_EVIDENCE,
        "articles_report": SAMPLE_ARTICLES,
        "recipient_email": "clinician@hospital.edu",
    }

    with patch("agent.graph.send_email") as mock_tool:
        mock_tool.invoke.return_value = "Email sent successfully."

        out = med_email_dispatcher_node(state)

        assert "email_status" in out
        assert "Email sent successfully." in out["email_status"]
        assert isinstance(out["messages"][0], AIMessage)

        mock_tool.invoke.assert_called_once_with({
            "evidence_report": SAMPLE_EVIDENCE,
            "recipient_email": "clinician@hospital.edu",
            "articles_list": SAMPLE_ARTICLES,
            "query": "What are the treatments for heart failure?",
        })
