from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import tempfile
import os
from core.database import get_user_from_token, supabase, supabase_admin
from core.openai_client import generate_embedding, generate_embedding_batch
from pdf_processor import extract_text_from_pdf
from langchain_chains import rag_chain

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    document_id: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[int]


@router.post("/upload")
async def upload_document(file: UploadFile = File(...), token: str = None):
    """Upload and process PDF document"""
    # Get user from token
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Check subscription limits
    if user.get("subscription_tier") == "free":
        # Count user's documents
        response = (
            supabase.table("documents").select("*").eq("user_id", user["id"]).execute()
        )
        doc_count = len(response.data)

        if doc_count >= 5:
            raise HTTPException(
                status_code=400, detail="Free tier limited to 5 documents"
            )

    # Save uploaded file to temp
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Extract text from PDF
        text = await extract_text_from_pdf(tmp_path)

        # Chunk text (500-1000 tokens)
        chunks = chunk_text(text)

        # Create document record
        doc_data = {
            "user_id": user["id"],
            "title": file.filename or "Untitled",
            "filename": file.filename or "untitled.pdf",
            "status": "processing",
        }
        doc_response = supabase.table("documents").insert(doc_data).execute()
        document = doc_response.data[0] if doc_response.data else None

        if not document:
            raise HTTPException(status_code=500, detail="Failed to create document")

        # Generate embeddings for chunks
        embeddings = await generate_embedding_batch([chunk["text"] for chunk in chunks])

        # Save chunks with embeddings
        chunk_data = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_data.append(
                {
                    "document_id": document["id"],
                    "chunk_index": i,
                    "content": chunk["text"],
                    "page_number": chunk["page_number"],
                    "embedding": embedding,
                }
            )

        # Use admin client to insert embeddings
        supabase_admin.table("document_chunks").insert(chunk_data).execute()

        # Update document status
        supabase.table("documents").update(
            {"status": "completed", "processed_at": "NOW()"}
        ).eq("id", document["id"]).execute()

        return {
            "status": "success",
            "document_id": document["id"],
            "message": "Document processed successfully",
        }
    except Exception as e:
        print(f"Error processing document: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error processing document: {str(e)}"
        )
    finally:
        # Cleanup temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.post("/chat", response_model=ChatResponse)
async def chat_with_document(request: ChatRequest, token: str = None):
    """Chat with uploaded document"""
    # Get user from token
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Verify document belongs to user
    doc_response = (
        supabase.table("documents")
        .select("*")
        .eq("id", request.document_id)
        .eq("user_id", user["id"])
        .execute()
    )

    if not doc_response.data:
        raise HTTPException(status_code=404, detail="Document not found")

    # Search for relevant chunks using vector similarity
    relevant_chunks = await search_relevant_chunks(request.query, request.document_id)

    # Generate answer using RAG chain
    answer = await rag_chain.generate_answer(request.query, relevant_chunks)

    # Extract page numbers from sources
    sources = [chunk["page_number"] for chunk in relevant_chunks]

    return ChatResponse(answer=answer, sources=sources)


async def search_relevant_chunks(
    query: str, document_id: str, k: int = 5
) -> List[dict]:
    """Search for relevant chunks using vector similarity"""
    try:
        # Generate embedding for query
        query_embedding = await generate_embedding(query)

        # Search in Supabase pgvector
        response = supabase_admin.rpc(
            "match_document_chunks",
            params={
                "query_embedding": query_embedding,
                "document_id": document_id,
                "match_threshold": 0.7,
                "match_count": k,
            },
        ).execute()

        return response.data if response.data else []
    except Exception as e:
        print(f"Error searching chunks: {e}")
        return []


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[dict]:
    """Chunk text into smaller pieces"""
    # Simple chunking - can be improved
    chunks = []
    words = text.split()

    for i in range(0, len(words), chunk_size):
        chunk_text = " ".join(words[i : i + chunk_size])
        chunks.append(
            {
                "text": chunk_text,
                "page_number": 1,  # TODO: Extract actual page numbers
            }
        )

    return chunks
