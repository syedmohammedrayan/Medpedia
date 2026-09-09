# Defines the API endpoints for the research workflow.
# Receives requests from the frontend and passes them to the ResearchController.
from fastapi import APIRouter, HTTPException
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
