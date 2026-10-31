# Defines the API endpoints for the research workflow.
# Receives requests from the frontend and passes them to the ResearchController.
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from api.controllers.research_controller import ResearchController
from tools.pdf_generator import generate_research_pdf
from tools.send_email_tool import send_email

router = APIRouter(prefix="/research", tags=["Research"])

class ResearchRequest(BaseModel):
    query: str
    thread_id: str = "default-user"

class ResumeRequest(BaseModel):
    email: str
    thread_id: str
    evidence_report: str | None = None
    query: str | None = None

@router.post("/start")
async def start_research(request: ResearchRequest):
    # Starts the LangGraph research workflow and returns a streaming response.
    # This allows the frontend to receive real-time updates as the LLM generates tokens.
    try:
        return StreamingResponse(
            ResearchController.astream_research(request.query, request.thread_id),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resume-email")
async def resume_email(request: ResumeRequest):
    # Resumes the paused LangGraph workflow with the collected email address.
    # Returns a stream for the final email dispatch step.
    try:
        return StreamingResponse(
            ResearchController.astream_resume(
                email=request.email,
                thread_id=request.thread_id,
                fallback_evidence=request.evidence_report,
                fallback_query=request.query,
            ),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download-pdf")
async def download_pdf(thread_id: str = "default-user"):
    """Generates and returns the full clinical evidence dossier PDF for a research thread.
    Contains Executive Summary, all retrieved articles, links, and complete PICO matrices.
    Strictly follows research-only content rules (no website URL, no disclaimer in PDF).
    """
    from agent.graph import graph

    config = {"configurable": {"thread_id": thread_id}}
    state = await graph.aget_state(config)
    if not state or not state.values:
        raise HTTPException(status_code=404, detail="No active research session found for thread_id.")

    evidence_report = state.values.get("evidence_report", "No evidence report available.")
    articles_list = state.values.get("articles_report", "")
    recipient_email = state.values.get("recipient_email", "")

    # Retrieve initial clinical question safely
    query = ""
    messages = state.values.get("messages", [])
    for msg in messages:
        if getattr(msg, "type", None) == "human" or (isinstance(msg, dict) and msg.get("role") == "user"):
            query = str(msg.content if hasattr(msg, "content") else msg.get("content", ""))
            break
    if not query and messages:
        first = messages[0]
        query = str(first.content if hasattr(first, "content") else (first.get("content", "") if isinstance(first, dict) else ""))

    try:
        pdf_bytes = generate_research_pdf(
            evidence_report=evidence_report,
            articles_list=articles_list,
            query=query,
            recipient_email=recipient_email,
            session_id=thread_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {exc}")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="Medpedia_Comprehensive_Evidence_Report.pdf"'
        },
    )


@router.post("/dispatch-email")
async def dispatch_email(request: ResumeRequest):
    """Directly generates and dispatches the complete research evidence package
    with the attached PDF dossier to the provided recipient address for an active thread.
    Returns real dispatch results from the backend email dispatch engine.
    """
    from agent.graph import graph

    config = {"configurable": {"thread_id": request.thread_id}}
    state = await graph.aget_state(config)

    evidence_report = (state.values.get("evidence_report") if state and state.values else None) or request.evidence_report
    if not evidence_report:
        raise HTTPException(status_code=404, detail="No active research session or evidence report found for thread_id.")

    articles_list = (state.values.get("articles_report") if state and state.values else "") or ""

    query = request.query or ""
    if not query and state and state.values:
        messages = state.values.get("messages", [])
        for msg in messages:
            if getattr(msg, "type", None) == "human" or (isinstance(msg, dict) and msg.get("role") == "user"):
                query = str(msg.content if hasattr(msg, "content") else msg.get("content", ""))
                break
        if not query and messages:
            first = messages[0]
            query = str(first.content if hasattr(first, "content") else (first.get("content", "") if isinstance(first, dict) else ""))

    try:
        result = send_email.invoke({
            "evidence_report": evidence_report,
            "recipient_email": request.email,
            "articles_list": articles_list,
            "query": query,
        })
        if "successfully" in str(result).lower():
            return {
                "success": True,
                "message": result,
                "recipient": request.email,
            }
        else:
            return {
                "success": False,
                "error": result,
                "recipient": request.email,
            }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "recipient": request.email,
        }

