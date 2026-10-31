"""
test_send_email_tool.py
───────────────────────
Comprehensive unit test suite for Gmail SMTP email dispatch,
address validation, error handling, HTML/plain-text generation,
and LangGraph dispatcher integration.
"""

import os
import smtplib
import socket
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage

from agent.graph import med_email_dispatcher_node
from tools.send_email_tool import (
    _markdown_to_html,
    _validate_recipient_email,
    send_email,
)


# ── Test 1: SMTP Configuration ───────────────────────────────────────────────
def test_smtp_configuration_custom_values():
    """Verify that SMTP configuration reads custom environment variables."""
    custom_env = {
        "SMTP_HOST": "mail.example.org",
        "SMTP_PORT": "2525",
        "SMTP_USER": "sender@example.org",
        "SMTP_PASSWORD": "custom_password",
        "SMTP_TIMEOUT": "25",
    }
    with patch.dict(os.environ, custom_env, clear=True):
        with patch("smtplib.SMTP") as mock_smtp:
            server_instance = MagicMock()
            mock_smtp.return_value.__enter__.return_value = server_instance

            result = send_email.invoke({
                "evidence_report": "Valid report content",
                "recipient_email": "clinician@hospital.edu",
            })

            assert result == "Email sent successfully."
            mock_smtp.assert_called_once_with("mail.example.org", 2525, timeout=25.0)
            server_instance.login.assert_called_once_with("sender@example.org", "custom_password")


# ── Test 2: SMTP Connection & Protocol Sequence ─────────────────────────────
def test_smtp_connection_protocol_sequence():
    """Verify SMTP connection sequence: connect, EHLO, STARTTLS, EHLO, login, send_message."""
    env = {
        "SMTP_HOST": "smtp.gmail.com",
        "SMTP_PORT": "587",
        "SMTP_USER": "syedmohammedrayan2007@gmail.com",
        "SMTP_PASSWORD": "mock_app_password",
    }
    with patch.dict(os.environ, env, clear=True):
        with patch("smtplib.SMTP") as mock_smtp, patch("ssl.create_default_context") as mock_ssl:
            server_instance = MagicMock()
            mock_smtp.return_value.__enter__.return_value = server_instance
            mock_context = MagicMock()
            mock_ssl.return_value = mock_context

            result = send_email.invoke({
                "evidence_report": "Test report content",
                "recipient_email": "colleague@university.org",
            })

            assert result == "Email sent successfully."
            mock_smtp.assert_called_once_with("smtp.gmail.com", 587, timeout=15.0)

            # Verify protocol sequence
            assert server_instance.ehlo.call_count == 2
            server_instance.starttls.assert_called_once_with(context=mock_context)
            server_instance.login.assert_called_once_with("syedmohammedrayan2007@gmail.com", "mock_app_password")
            server_instance.send_message.assert_called_once()


# ── Test 3: Dynamic Recipient Handling ───────────────────────────────────────
@pytest.mark.parametrize("recipient", [
    "testuser@gmail.com",
    "testuser@outlook.com",
    "testuser@yahoo.com",
    "researcher@example.org",
    "student@university.edu",
    "doctor.smith+pediatrics@clinic.med.uk",
])
def test_dynamic_recipient_accepted(recipient: str):
    """Verify that ANY valid recipient email address is accepted and addressed."""
    env = {
        "SMTP_USER": "syedmohammedrayan2007@gmail.com",
        "SMTP_PASSWORD": "mock_app_password",
    }
    with patch.dict(os.environ, env, clear=True):
        with patch("smtplib.SMTP") as mock_smtp:
            server_instance = MagicMock()
            mock_smtp.return_value.__enter__.return_value = server_instance

            result = send_email.invoke({
                "evidence_report": "Report content",
                "recipient_email": recipient,
            })

            assert result == "Email sent successfully."
            sent_msg = server_instance.send_message.call_args[0][0]
            assert sent_msg["To"] == recipient


# ── Test 4: Sender Address Integrity ─────────────────────────────────────────
def test_sender_address_uses_authenticated_user():
    """Verify that From header uses the authenticated Gmail account."""
    env = {
        "SMTP_USER": "syedmohammedrayan2007@gmail.com",
        "SMTP_PASSWORD": "mock_app_password",
    }
    with patch.dict(os.environ, env, clear=True):
        with patch("smtplib.SMTP") as mock_smtp:
            server_instance = MagicMock()
            mock_smtp.return_value.__enter__.return_value = server_instance

            send_email.invoke({
                "evidence_report": "Report content",
                "recipient_email": "external.user@example.com",
            })

            sent_msg = server_instance.send_message.call_args[0][0]
            assert sent_msg["From"] == "Medpedia <syedmohammedrayan2007@gmail.com>"


# ── Test 5: Error Handling ───────────────────────────────────────────────────
def test_missing_smtp_credentials():
    with patch.dict(os.environ, {}, clear=True):
        result = send_email.invoke({
            "evidence_report": "Some report",
            "recipient_email": "user@example.com",
        })
        assert "Missing email credentials" in result


# ── Test 5b: Google Gmail REST API Dispatch (HTTPS Port 443) ────────────────
def test_gmail_api_dispatch_success():
    """Verify that Google Gmail REST API dispatch succeeds with OAuth token exchange and PDF."""
    env = {
        "GMAIL_CLIENT_ID": "mock_client_id.apps.googleusercontent.com",
        "GMAIL_CLIENT_SECRET": "mock_client_secret",
        "GMAIL_REFRESH_TOKEN": "mock_refresh_token",
        "GMAIL_SENDER_EMAIL": "syedmohammedrayan2007@gmail.com",
    }
    with patch.dict(os.environ, env, clear=True):
        with patch("tools.send_email_tool.requests.post") as mock_post:
            token_resp = MagicMock()
            token_resp.status_code = 200
            token_resp.json.return_value = {"access_token": "mock_access_token_123"}

            send_resp = MagicMock()
            send_resp.status_code = 200
            send_resp.json.return_value = {"id": "18c12345678"}

            mock_post.side_effect = [token_resp, send_resp]

            result = send_email.invoke({
                "evidence_report": "## Clinical Evidence\nKey insights here.",
                "recipient_email": "physician@hospital.edu",
            })

            assert result == "Email sent successfully."
            assert mock_post.call_count == 2

            # Verify OAuth token exchange
            token_call = mock_post.call_args_list[0]
            assert token_call[0][0] == "https://oauth2.googleapis.com/token"
            assert token_call[1]["data"]["refresh_token"] == "mock_refresh_token"

            # Verify Gmail API messages.send
            send_call = mock_post.call_args_list[1]
            assert send_call[0][0] == "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
            assert send_call[1]["headers"]["Authorization"] == "Bearer mock_access_token_123"
            assert "raw" in send_call[1]["json"]


def test_gmail_api_failure_falls_back_to_smtp():
    """Verify that when Gmail API token refresh fails, it falls back to direct Gmail SMTP."""
    env = {
        "GMAIL_CLIENT_ID": "client_id",
        "GMAIL_CLIENT_SECRET": "client_secret",
        "GMAIL_REFRESH_TOKEN": "bad_token",
        "SMTP_USER": "syedmohammedrayan2007@gmail.com",
        "SMTP_PASSWORD": "app_password",
    }
    with patch.dict(os.environ, env, clear=True):
        with patch("tools.send_email_tool.requests.post") as mock_post:
            token_resp = MagicMock()
            token_resp.status_code = 400
            token_resp.text = "invalid_grant"
            mock_post.return_value = token_resp

            with patch("smtplib.SMTP") as mock_smtp:
                server = MagicMock()
                mock_smtp.return_value.__enter__.return_value = server

                result = send_email.invoke({
                    "evidence_report": "Report content",
                    "recipient_email": "user@example.com",
                })

                assert result == "Email sent successfully."
                mock_smtp.assert_called_once()



def test_empty_evidence_report():
    env = {"SMTP_USER": "user@gmail.com", "SMTP_PASSWORD": "app_password"}
    with patch.dict(os.environ, env, clear=True):
        result = send_email.invoke({
            "evidence_report": "   ",
            "recipient_email": "user@example.com",
        })
        assert "Evidence report is empty" in result


@pytest.mark.parametrize("invalid_email,expected_keyword", [
    ("", "required"),
    ("   ", "required"),
    ("not-an-email", "Invalid recipient email address format"),
    ("user@domain", "Invalid recipient email address format"),
    ("user@domain..com", "Invalid recipient email address format"),
    ("user1@example.com, user2@example.com", "Only a single recipient"),
    ("user1@example.com; user2@example.com", "Only a single recipient"),
    ("user@example.com\r\nBcc: evil@attacker.com", "newline"),
])
def test_invalid_recipient_emails(invalid_email: str, expected_keyword: str):
    env = {"SMTP_USER": "user@gmail.com", "SMTP_PASSWORD": "app_password"}
    with patch.dict(os.environ, env, clear=True):
        result = send_email.invoke({
            "evidence_report": "Valid report",
            "recipient_email": invalid_email,
        })
        assert expected_keyword.lower() in result.lower()


def test_smtp_authentication_error():
    env = {"SMTP_USER": "user@gmail.com", "SMTP_PASSWORD": "wrong_password"}
    with patch.dict(os.environ, env, clear=True):
        with patch("smtplib.SMTP") as mock_smtp:
            server = MagicMock()
            server.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Authentication failed")
            mock_smtp.return_value.__enter__.return_value = server

            result = send_email.invoke({
                "evidence_report": "Report",
                "recipient_email": "user@example.com",
            })
            assert "Gmail SMTP authentication failed" in result


def test_smtp_connection_timeout():
    env = {"SMTP_USER": "user@gmail.com", "SMTP_PASSWORD": "app_password"}
    with patch.dict(os.environ, env, clear=True):
        with patch("smtplib.SMTP", side_effect=socket.timeout("timed out")):
            result = send_email.invoke({
                "evidence_report": "Report",
                "recipient_email": "user@example.com",
            })
            assert "timed out" in result.lower()


def test_smtp_recipient_refused():
    env = {"SMTP_USER": "user@gmail.com", "SMTP_PASSWORD": "app_password"}
    with patch.dict(os.environ, env, clear=True):
        with patch("smtplib.SMTP") as mock_smtp:
            server = MagicMock()
            server.send_message.side_effect = smtplib.SMTPRecipientsRefused({"rejected@example.com": (550, b"User unknown")})
            mock_smtp.return_value.__enter__.return_value = server

            result = send_email.invoke({
                "evidence_report": "Report",
                "recipient_email": "rejected@example.com",
            })
            assert "was refused by the SMTP server" in result


# ── Test 6: HTML & Plaintext Email Structure ────────────────────────────────
def test_email_payload_contains_required_sections():
    env = {"SMTP_USER": "syedmohammedrayan2007@gmail.com", "SMTP_PASSWORD": "app_password"}
    sample_report = (
        "## 🧪 Executive Evidence Summary\n\n"
        "Key findings regarding immunotherapy.\n\n"
        "### Article #1: Clinical Trial\n"
        "- [PubMed Link](https://pubmed.ncbi.nlm.nih.gov/12345/)\n"
        "- **STUDY TYPE:** Randomized Controlled Trial\n"
        "- **EVIDENCE CERTAINTY:** High\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "## 📚 Source Articles (Search Results)\n\n"
        "Article details here."
    )
    with patch.dict(os.environ, env, clear=True):
        with patch("smtplib.SMTP") as mock_smtp:
            server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = server

            send_email.invoke({
                "evidence_report": sample_report,
                "recipient_email": "doctor@hospital.org",
            })

            sent_msg = server.send_message.call_args[0][0]
            assert sent_msg.is_multipart()

            # Retrieve text and html parts (filtering for text content type)
            parts = {
                part.get_content_type(): part.get_payload(decode=True).decode("utf-8")
                for part in sent_msg.walk()
                if not part.is_multipart() and part.get_content_type().startswith("text/")
            }

            assert "text/plain" in parts
            assert "text/html" in parts

            # Verify PDF attachment is also attached
            pdf_parts = [
                part for part in sent_msg.walk()
                if part.get_content_type() == "application/pdf"
            ]
            assert len(pdf_parts) == 1
            assert pdf_parts[0].get_filename() == "Medpedia_Evidence_Report.pdf"

            html_content = parts["text/html"]
            assert "🔬 Medical Research Insights" in html_content
            assert "Executive Evidence Summary" in html_content
            assert "Source Articles" in html_content
            assert "https://pubmed.ncbi.nlm.nih.gov/12345/" in html_content
            assert "Medical Disclaimer" in html_content
            assert "Medpedia" in html_content


def test_markdown_to_html_escaping_prevents_xss():
    malicious_md = "Testing <script>alert('xss')</script> in report"
    html_output = _markdown_to_html(malicious_md)
    assert "<script>" not in html_output
    assert "&lt;script&gt;" in html_output


# ── Test 7: LangGraph Workflow Node Integration ──────────────────────────────
def test_med_email_dispatcher_node_integration():
    """Verify that med_email_dispatcher_node extracts recipient and report, invokes send_email, and updates email_status."""
    env = {"SMTP_USER": "syedmohammedrayan2007@gmail.com", "SMTP_PASSWORD": "app_password"}
    state = {
        "messages": [],
        "evidence_report": "Synthesized evidence brief.",
        "articles_report": "List of retrieved articles.",
        "recipient_email": "clinician@research.org",
    }
    with patch.dict(os.environ, env, clear=True):
        with patch("tools.send_email_tool.smtplib.SMTP") as mock_smtp:
            server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = server

            node_output = med_email_dispatcher_node(state)

            assert "email_status" in node_output
            assert "Email sent successfully." in node_output["email_status"]
            assert isinstance(node_output["messages"][0], AIMessage)
            sent_msg = server.send_message.call_args[0][0]
            assert sent_msg["To"] == "clinician@research.org"


# ── Test 8: Frontend Feedback / Controller SSE Stream ─────────────────────────
@pytest.mark.anyio
async def test_astream_resume_emits_email_status_to_frontend():
    """Verify that ResearchController.astream_resume yields the dispatcher output to SSE."""
    from api.controllers.research_controller import ResearchController

    mock_state = MagicMock()
    mock_state.values = {"recipient_email": "clinician@research.org"}
    mock_state.next = ("email_collector",)

    async def mock_events(*args, **kwargs):
        yield {
            "event": "on_chain_end",
            "metadata": {"langgraph_node": "med_email_dispatcher"},
            "data": {
                "output": {
                    "email_status": "✅ **Email dispatch result:** Email sent successfully."
                }
            },
        }

    with patch("api.controllers.research_controller.graph.aget_state", return_value=mock_state):
        with patch("api.controllers.research_controller.graph.astream_events", side_effect=mock_events):
            stream_chunks = []
            async for chunk in ResearchController.astream_resume("clinician@research.org", "test_thread"):
                stream_chunks.append(chunk)

            joined_stream = "".join(stream_chunks)
            assert "data: [DONE]" in joined_stream
            assert "Email sent successfully." in joined_stream
            assert '"type": "token"' in joined_stream

