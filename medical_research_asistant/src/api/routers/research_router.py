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
    try:
        return StreamingResponse(
            ResearchController.astream_research(request.query, request.thread_id),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resume-email")
async def resume_email(request: ResumeRequest):
    try:
        return StreamingResponse(
            ResearchController.astream_resume(request.email, request.thread_id),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
