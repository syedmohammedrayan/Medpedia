"""
test_research_router.py
───────────────────────
Unit tests for the FastAPI research endpoints:
- GET  /research/download-pdf
- POST /research/dispatch-email
- POST /research/start
- POST /research/resume-email
"""

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient
from langchain_core.messages import HumanMessage

from main import app

client = TestClient(app)


# ── Test 1: Download PDF Endpoint 404 on Missing Session ─────────────────────
def test_download_pdf_not_found():
    """Verify download_pdf returns 404 when no session exists for thread_id."""
    with patch("agent.graph.graph.aget_state", new_callable=AsyncMock) as mock_get_state:
        mock_get_state.return_value = None

        response = client.get("/research/download-pdf?thread_id=nonexistent-thread")
        assert response.status_code == 404
        assert "No active research session" in response.json()["detail"]


# ── Test 2: Download PDF Endpoint Success ─────────────────────────────────────
def test_download_pdf_success():
    """Verify download_pdf returns application/pdf with correct filename and content."""
    mock_state = MagicMock()
    mock_state.values = {
        "evidence_report": "## Executive Summary\nTherapeutic efficacy corroborated.",
        "articles_report": "### Article #1\n**Title:** Test Article\n**Links:**\n- [PubMed](https://pubmed.ncbi.nlm.nih.gov/123/)",
        "recipient_email": "clinician@hospital.edu",
        "messages": [HumanMessage(content="Heart failure therapy")],
    }

    with patch("agent.graph.graph.aget_state", new_callable=AsyncMock) as mock_get_state:
        mock_get_state.return_value = mock_state

        response = client.get("/research/download-pdf?thread_id=active-session-123")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert 'filename="Medpedia_Comprehensive_Evidence_Report.pdf"' in response.headers["content-disposition"]
        assert len(response.content) > 1000
        assert response.content.startswith(b"%PDF-")


# ── Test 3: Dispatch Email Endpoint Success ───────────────────────────────────
def test_dispatch_email_endpoint_success():
    """Verify POST /research/dispatch-email dispatches using session state."""
    mock_state = MagicMock()
    mock_state.values = {
        "evidence_report": "## Evidence Synthesis\nFindings confirmed.",
        "articles_report": "Articles list content",
        "messages": [HumanMessage(content="What are the treatments?")],
    }

    with patch("agent.graph.graph.aget_state", new_callable=AsyncMock) as mock_get_state:
        mock_get_state.return_value = mock_state
        with patch("api.routers.research_router.send_email") as mock_send:
            mock_send.invoke.return_value = "Email sent successfully."

            payload = {
                "email": "doctor@hospital.org",
                "thread_id": "session-456",
            }
            response = client.post("/research/dispatch-email", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Email sent successfully."
            assert data["recipient"] == "doctor@hospital.org"


# ── Test 4: Dispatch Email Endpoint Error Feedback ────────────────────────────
def test_dispatch_email_endpoint_error_feedback():
    """Verify POST /research/dispatch-email propagates meaningful error on failure."""
    mock_state = MagicMock()
    mock_state.values = {
        "evidence_report": "Report content",
        "articles_report": "Articles content",
        "messages": [HumanMessage(content="Inquiry")],
    }

    with patch("agent.graph.graph.aget_state", new_callable=AsyncMock) as mock_get_state:
        mock_get_state.return_value = mock_state
        with patch("api.routers.research_router.send_email") as mock_send:
            mock_send.invoke.return_value = "Error: Invalid recipient email address format: 'bad-email'."

            payload = {
                "email": "bad-email",
                "thread_id": "session-456",
            }
            response = client.post("/research/dispatch-email", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert "Invalid recipient" in data["error"]
