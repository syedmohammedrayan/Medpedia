# Defines the API endpoints for the research workflow.
# Receives requests from the frontend and passes them to the ResearchController.
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from api.controllers.research_controller import ResearchController

router = APIRouter(prefix="/research", tags=["Research"])

class ResearchRequest(BaseModel):
    query: str
    thread_id: str = "default-user"

class ResumeRequest(BaseModel):
    email: str
    thread_id: str

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
            ResearchController.astream_resume(request.email, request.thread_id),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download-pdf")
async def download_pdf(thread_id: str = "default-user"):
    """
    Generates and returns the full clinical evidence dossier PDF for a research thread.
    Contains Executive Summary, all retrieved articles, links, websites, and medical disclaimers.
    """
    from agent.graph import graph
    from tools.pdf_generator import generate_research_pdf

    config = {"configurable": {"thread_id": thread_id}}
    state = await graph.aget_state(config)
    if not state or not state.values:
        raise HTTPException(status_code=404, detail="No active research session found for thread_id.")

    evidence_report = state.values.get("evidence_report", "No evidence report available.")
    articles_list = state.values.get("articles_report", "")
    recipient_email = state.values.get("recipient_email", "")

    # Retrieve initial clinical question
    query = ""
    messages = state.values.get("messages", [])
    for msg in messages:
        if getattr(msg, "type", None) == "human" or hasattr(msg, "content"):
            query = str(msg.content)
            break

    pdf_bytes = generate_research_pdf(
        evidence_report=evidence_report,
        articles_list=articles_list,
        query=query,
        recipient_email=recipient_email,
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="Medpedia_Evidence_Report.pdf"'
        },
    )

