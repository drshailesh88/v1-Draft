import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting FastAPI server...")
    yield
    print("👋 Shutting down FastAPI server...")


app = FastAPI(
    title="V1 Draft API",
    description="Academic research platform API - 5 parallel features",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "V1 Draft API",
        "version": "1.0.0",
        "features": [
            "Chat with PDF",
            "Literature Search",
            "Citation Generator",
            "Data Extraction",
            "AI Detector",
            "Find Topics",
            "Paraphraser",
            "AI Writer",
            "Systematic Review",
            "Citation Booster",
            "Deep Review",
            "Payments & Subscriptions",
        ],
        "status": "running",
        "environment": os.getenv("RAILWAY_ENV", "development"),
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


from app.api import chat, literature, citations, data_extraction, ai_detector

app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
from app.api import (
    literature,
    topics,
    paraphraser,
    ai_writer,
    systematic_review,
    citation_booster,
    deep_review,
    payments,
)

app.include_router(literature.router, prefix="/api/literature", tags=["literature"])
app.include_router(citations.router, prefix="/api/citations", tags=["citations"])
app.include_router(
    data_extraction.router, prefix="/api/data-extraction", tags=["data-extraction"]
)
app.include_router(ai_detector.router, prefix="/api/ai-detector", tags=["ai-detector"])
app.include_router(topics.router, prefix="/api/topics", tags=["topics"])
app.include_router(paraphraser.router, prefix="/api/paraphraser", tags=["paraphraser"])
app.include_router(ai_writer.router, prefix="/api/ai-writer", tags=["ai-writer"])
app.include_router(
    systematic_review.router,
    prefix="/api/systematic-review",
    tags=["systematic-review"],
)
app.include_router(
    citation_booster.router, prefix="/api/citation-booster", tags=["citation-booster"]
)
app.include_router(deep_review.router, prefix="/api/deep-review", tags=["deep-review"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
