import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting FastAPI server...")
    yield
    # Shutdown
    print("👋 Shutting down FastAPI server...")


app = FastAPI(
    title="Sci-Space Clone API",
    description="Academic research platform API - 5 parallel features",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Sci-Space Clone API",
        "version": "1.0.0",
        "features": [
            "Chat with PDF",
            "Literature Search",
            "Citation Generator",
            "Data Extraction",
            "AI Detector",
        ],
        "status": "running",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


# Include routers for all 5 parallel features
from app.api import chat, literature, citations, data_extraction, ai_detector

app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(literature.router, prefix="/api/literature", tags=["literature"])
app.include_router(citations.router, prefix="/api/citations", tags=["citations"])
app.include_router(
    data_extraction.router, prefix="/api/data-extraction", tags=["data-extraction"]
)
app.include_router(ai_detector.router, prefix="/api/ai-detector", tags=["ai-detector"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
