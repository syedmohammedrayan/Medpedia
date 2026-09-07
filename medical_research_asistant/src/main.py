import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Ensure the src directory is in the path so imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.routers.research_router import router as research_router

app = FastAPI(
    title="Medical Research Assistant API",
    description="API for the Multi-Agent Medical Research Pipeline",
    version="1.0.0"
) 
 
# Enable CORS for frontend integration
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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
