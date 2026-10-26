# Main entry point for the FastAPI backend.
# Initializes the API server that the React frontend communicates with.
import os
import sys

# Ensure UTF-8 output encoding across platforms, particularly on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure the src directory is in the path so imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.routers.research_router import router as research_router

app = FastAPI(
    title="Medical Research Assistant API",
    description="API for the Multi-Agent Medical Research Pipeline",
    version="1.0.0"
) 
 
# Enable CORS for frontend integration
# Allows the React frontend (running on a different port) to make API requests to this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(research_router)

@app.get("/")
async def root():
    return {"message": "Medical Research Assistant API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
