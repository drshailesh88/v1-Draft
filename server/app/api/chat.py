"""
Chat with PDF API Module
Implements the complete Chat with PDF feature for the Sci-Space Clone platform.

Features:
- PDF upload endpoint (multipart/form-data)
- PDF processing (text extraction with page numbers)
- Text chunking (500-1000 tokens with overlap)
- Embedding generation (OpenAI text-embedding-3-small)
- Vector storage (Supabase pgvector)
- RAG chain for chat responses
- Source citations with page numbers
"""

import os
import sys
import uuid
import math
import re
import tempfile
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Query
from pydantic import BaseModel, Field

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.database import supabase, supabase_admin
from core.openai_client import generate_embedding, generate_embedding_batch
from pdf_processor import extract_text_with_pages, get_pdf_metadata
from langchain_chains import rag_chain, conversational_rag_chain


router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    query: str = Field(..., min_length=1, max_length=2000, description="User's question")
    document_id: str = Field(..., description="ID of the document to chat with")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    answer: str = Field(..., description="AI-generated answer")
    sources: List[int] = Field(default_factory=list, description="Page numbers used as sources")
    document_id: str = Field(..., description="Document ID")
    chunk_count: int = Field(default=0, description="Number of chunks used for context")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for follow-up")


class DocumentUploadResponse(BaseModel):
    """Response model for document upload"""
    status: str
    document_id: str
    message: str
    filename: str
    total_pages: int
    total_chunks: int


class DocumentInfo(BaseModel):
    """Document information model"""
    id: str
    title: str
    filename: str
    status: str
    total_pages: int
    created_at: str


class DocumentListResponse(BaseModel):
    """Response model for listing documents"""
    documents: List[DocumentInfo]
    total: int


class SearchResult(BaseModel):
    """Search result model"""
    content: str
    page_number: int
    similarity: float
    chunk_index: int


class SearchResponse(BaseModel):
    """Response model for semantic search"""
    query: str
    document_id: str
    results: List[SearchResult]
    count: int


# =============================================================================
# Text Chunking with Page Tracking
# =============================================================================

def chunk_text_with_pages(
    pages_data: List[Dict[str, Any]],
    chunk_size: int = 800,
    chunk_overlap: int = 200
) -> List[Dict[str, Any]]:
    """
    Chunk text from pages while preserving page number information.

    This function implements intelligent text chunking that:
    - Preserves page number information for citations
    - Splits on sentence boundaries when possible
    - Maintains overlap between chunks for context continuity
    - Targets 500-1000 tokens per chunk (at ~1.5 chars/token)

    Args:
        pages_data: List of dicts with 'text' and 'page_number'
        chunk_size: Target chunk size in characters (roughly 500-1000 tokens at ~1.5 chars/token)
        chunk_overlap: Overlap between consecutive chunks

    Returns:
        List of chunks with 'text', 'page_number', and 'chunk_index'
    """
    chunks = []
    chunk_index = 0

    for page_data in pages_data:
        page_text = page_data["text"]
        page_number = page_data["page_number"]

        # Skip empty pages
        if not page_text or not page_text.strip():
            continue

        # Clean the text - normalize whitespace
        page_text = " ".join(page_text.split())

        # If page text is smaller than chunk_size, add as single chunk
        if len(page_text) <= chunk_size:
            chunks.append({
                "text": page_text,
                "page_number": page_number,
                "chunk_index": chunk_index
            })
            chunk_index += 1
            continue

        # Split larger pages into multiple chunks
        # Try to split on sentence boundaries
        sentences = _split_into_sentences(page_text)
        current_chunk = ""

        for sentence in sentences:
            # If adding this sentence exceeds chunk_size, save current chunk
            if current_chunk and len(current_chunk) + len(sentence) > chunk_size:
                chunks.append({
                    "text": current_chunk.strip(),
                    "page_number": page_number,
                    "chunk_index": chunk_index
                })
                chunk_index += 1

                # Start new chunk with overlap from previous
                overlap_text = current_chunk[-chunk_overlap:] if len(current_chunk) > chunk_overlap else current_chunk
                current_chunk = overlap_text + " " + sentence
            else:
                current_chunk = current_chunk + " " + sentence if current_chunk else sentence

        # Don't forget the last chunk
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "page_number": page_number,
                "chunk_index": chunk_index
            })
            chunk_index += 1

    return chunks


def _split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences for better chunking.

    Uses regex to handle common sentence endings while being careful
    about abbreviations and decimal numbers.

    Args:
        text: Input text

    Returns:
        List of sentences
    """
    # Split on common sentence endings
    # Handle abbreviations and decimal numbers better
    sentence_endings = r'(?<=[.!?])\s+(?=[A-Z])'
    sentences = re.split(sentence_endings, text)

    # Filter out empty sentences
    return [s.strip() for s in sentences if s.strip()]


# =============================================================================
# Vector Search Functions
# =============================================================================

def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Cosine similarity score (0-1)
    """
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


async def search_relevant_chunks(
    query: str,
    document_id: str,
    k: int = 5,
    similarity_threshold: float = 0.3
) -> List[Dict[str, Any]]:
    """
    Search for relevant chunks using vector similarity in Supabase pgvector.

    This function:
    1. Generates an embedding for the query using OpenAI
    2. Attempts to use the optimized RPC function for vector search
    3. Falls back to manual similarity calculation if RPC is unavailable

    Args:
        query: User's search query
        document_id: ID of the document to search within
        k: Number of top results to return
        similarity_threshold: Minimum similarity score (0-1)

    Returns:
        List of relevant chunks with content, page_number, and similarity score
    """
    try:
        # Generate embedding for the query
        query_embedding = await generate_embedding(query)

        # Try using the RPC function first (if it exists)
        try:
            response = supabase_admin.rpc(
                "match_document_chunks",
                {
                    "query_embedding": query_embedding,
                    "target_document_id": document_id,
                    "match_threshold": similarity_threshold,
                    "match_count": k
                }
            ).execute()

            if response.data:
                return response.data

        except Exception as rpc_error:
            # RPC function not available, use fallback
            print(f"RPC function not available, using fallback: {rpc_error}")

        # Fallback: Direct query with manual similarity calculation
        # This is less efficient but works without the RPC function
        response = supabase_admin.table("document_chunks") \
            .select("id, content, page_number, embedding, chunk_index") \
            .eq("document_id", document_id) \
            .execute()

        if not response.data:
            return []

        # Calculate cosine similarity manually
        chunks_with_similarity = []
        for chunk in response.data:
            if chunk.get("embedding"):
                similarity = _cosine_similarity(query_embedding, chunk["embedding"])
                if similarity >= similarity_threshold:
                    chunks_with_similarity.append({
                        "id": chunk["id"],
                        "content": chunk["content"],
                        "page_number": chunk["page_number"],
                        "chunk_index": chunk["chunk_index"],
                        "similarity": similarity
                    })

        # Sort by similarity and return top k
        chunks_with_similarity.sort(key=lambda x: x["similarity"], reverse=True)
        return chunks_with_similarity[:k]

    except Exception as e:
        print(f"Error searching chunks: {e}")
        return []


# =============================================================================
# Conversation Management
# =============================================================================

# In-memory conversation store (for dev mode - use Redis/DB in production)
_conversation_store: Dict[str, Dict[str, Any]] = {}


def get_or_create_conversation(conversation_id: Optional[str], document_id: str) -> tuple:
    """
    Get or create a conversation context.

    Args:
        conversation_id: Optional existing conversation ID
        document_id: Document ID for this conversation

    Returns:
        Tuple of (conversation_id, conversation_data)
    """
    if conversation_id and conversation_id in _conversation_store:
        return conversation_id, _conversation_store[conversation_id]

    new_id = str(uuid.uuid4())
    _conversation_store[new_id] = {
        "document_id": document_id,
        "history": [],
        "created_at": datetime.utcnow().isoformat()
    }
    return new_id, _conversation_store[new_id]


def update_conversation_history(conversation_id: str, query: str, answer: str):
    """Update conversation history with new exchange."""
    if conversation_id in _conversation_store:
        _conversation_store[conversation_id]["history"].append({
            "query": query,
            "answer": answer,
            "timestamp": datetime.utcnow().isoformat()
        })
        # Keep only last 10 exchanges
        _conversation_store[conversation_id]["history"] = \
            _conversation_store[conversation_id]["history"][-10:]


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(..., description="PDF file to upload"),
    title: Optional[str] = Form(None, description="Optional document title"),
    user_id: Optional[str] = Form(None, description="Optional user ID (dev mode)")
):
    """
    Upload and process a PDF document.

    This endpoint:
    1. Accepts PDF upload (multipart/form-data)
    2. Extracts text with page numbers using pypdf
    3. Chunks text (500-1000 tokens with overlap)
    4. Generates embeddings using OpenAI text-embedding-3-small
    5. Stores vectors in Supabase pgvector

    Development mode: No authentication required.

    **Request:**
    - file: PDF file (max 50MB)
    - title: Optional custom title
    - user_id: Optional user ID for tracking

    **Response:**
    - document_id: Unique ID for the uploaded document
    - total_pages: Number of pages in the PDF
    - total_chunks: Number of text chunks created
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Check file size (max 50MB)
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 50MB limit")

    # Reset file position
    await file.seek(0)

    # Save to temporary file
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        # Extract text with page numbers
        pages_data = await extract_text_with_pages(tmp_path)

        if not pages_data:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF. The file may be empty, scanned, or corrupted."
            )

        # Get PDF metadata
        metadata = get_pdf_metadata(tmp_path)

        # Chunk text with page tracking
        chunks = chunk_text_with_pages(pages_data, chunk_size=800, chunk_overlap=200)

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="Could not create text chunks from PDF content"
            )

        # Generate document ID
        document_id = str(uuid.uuid4())

        # Determine document title
        doc_title = title or metadata.get("title") or file.filename or "Untitled Document"

        # Create document record in database
        doc_data = {
            "id": document_id,
            "title": doc_title,
            "filename": file.filename,
            "status": "processing",
            "total_pages": metadata.get("total_pages", len(pages_data)),
            "metadata": {
                "author": metadata.get("author"),
                "subject": metadata.get("subject"),
                "creator": metadata.get("creator"),
                "file_size": len(content)
            }
        }

        # Add user_id if provided (dev mode)
        if user_id:
            doc_data["user_id"] = user_id

        # Insert document record
        doc_response = supabase_admin.table("documents").insert(doc_data).execute()

        if not doc_response.data:
            raise HTTPException(status_code=500, detail="Failed to create document record")

        # Generate embeddings for all chunks
        # Process in batches to avoid API limits
        chunk_texts = [chunk["text"] for chunk in chunks]
        batch_size = 100
        all_embeddings = []

        for i in range(0, len(chunk_texts), batch_size):
            batch = chunk_texts[i:i + batch_size]
            embeddings = await generate_embedding_batch(batch)
            all_embeddings.extend(embeddings)

        # Prepare chunk data for insertion
        chunk_records = []
        for i, (chunk, embedding) in enumerate(zip(chunks, all_embeddings)):
            chunk_records.append({
                "document_id": document_id,
                "chunk_index": chunk["chunk_index"],
                "content": chunk["text"],
                "page_number": chunk["page_number"],
                "embedding": embedding
            })

        # Insert chunks with embeddings
        # Process in batches for large documents
        for i in range(0, len(chunk_records), 50):
            batch = chunk_records[i:i + 50]
            supabase_admin.table("document_chunks").insert(batch).execute()

        # Update document status to completed
        supabase_admin.table("documents").update({
            "status": "completed",
            "total_chunks": len(chunks),
            "processed_at": datetime.utcnow().isoformat()
        }).eq("id", document_id).execute()

        return DocumentUploadResponse(
            status="success",
            document_id=document_id,
            message="Document processed successfully",
            filename=file.filename,
            total_pages=metadata.get("total_pages", len(pages_data)),
            total_chunks=len(chunks)
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing document: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )
    finally:
        # Cleanup temporary file
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.post("/chat", response_model=ChatResponse)
async def chat_with_document(request: ChatRequest):
    """
    Chat with an uploaded document using RAG (Retrieval-Augmented Generation).

    This endpoint:
    1. Generates embedding for the user's query
    2. Searches for relevant chunks using vector similarity
    3. Uses LangChain RAG chain to generate an answer
    4. Returns the answer with source page citations

    Development mode: No authentication required.

    **Request:**
    - query: The user's question (max 2000 chars)
    - document_id: ID of the document to chat with
    - conversation_id: Optional ID for maintaining conversation context

    **Response:**
    - answer: AI-generated response with inline citations
    - sources: List of page numbers referenced
    - chunk_count: Number of relevant chunks used
    - conversation_id: ID for follow-up questions
    """
    # Validate document exists
    doc_response = supabase_admin.table("documents") \
        .select("id, status, title") \
        .eq("id", request.document_id) \
        .execute()

    if not doc_response.data:
        raise HTTPException(status_code=404, detail="Document not found")

    document = doc_response.data[0]

    if document["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Document is still being processed (status: {document['status']})"
        )

    # Get or create conversation context
    conv_id, conv_data = get_or_create_conversation(
        request.conversation_id,
        request.document_id
    )

    # Search for relevant chunks
    relevant_chunks = await search_relevant_chunks(
        query=request.query,
        document_id=request.document_id,
        k=5,
        similarity_threshold=0.3
    )

    if not relevant_chunks:
        return ChatResponse(
            answer="I couldn't find any relevant information in this document to answer your question. Please try rephrasing your question or asking about a different topic covered in the document.",
            sources=[],
            document_id=request.document_id,
            chunk_count=0,
            conversation_id=conv_id
        )

    # Generate answer using RAG chain
    answer = await rag_chain.generate_answer(
        query=request.query,
        relevant_chunks=relevant_chunks
    )

    # Update conversation history
    update_conversation_history(conv_id, request.query, answer)

    # Extract unique page numbers from sources
    sources = list(set(
        chunk["page_number"]
        for chunk in relevant_chunks
        if chunk.get("page_number")
    ))
    sources.sort()

    return ChatResponse(
        answer=answer,
        sources=sources,
        document_id=request.document_id,
        chunk_count=len(relevant_chunks),
        conversation_id=conv_id
    )


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100, description="Number of documents to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    List uploaded documents.

    Development mode: Returns all documents or filters by user_id if provided.

    **Query Parameters:**
    - user_id: Filter documents by user
    - status: Filter by status (processing, completed, failed)
    - limit: Number of results (1-100, default 20)
    - offset: Pagination offset
    """
    query = supabase_admin.table("documents") \
        .select("id, title, filename, status, total_pages, created_at")

    if user_id:
        query = query.eq("user_id", user_id)

    if status:
        query = query.eq("status", status)

    response = query.order("created_at", desc=True) \
        .range(offset, offset + limit - 1) \
        .execute()

    documents = [
        DocumentInfo(
            id=doc["id"],
            title=doc["title"],
            filename=doc["filename"],
            status=doc["status"],
            total_pages=doc.get("total_pages", 0),
            created_at=doc["created_at"]
        )
        for doc in (response.data or [])
    ]

    return DocumentListResponse(
        documents=documents,
        total=len(documents)
    )


@router.get("/documents/{document_id}")
async def get_document(document_id: str):
    """
    Get document details by ID.

    Development mode: No authentication required.

    **Path Parameters:**
    - document_id: UUID of the document

    **Response:**
    Complete document information including metadata
    """
    response = supabase_admin.table("documents") \
        .select("*") \
        .eq("id", document_id) \
        .execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Document not found")

    return response.data[0]


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document and all its chunks.

    Development mode: No authentication required.

    **Path Parameters:**
    - document_id: UUID of the document to delete

    **Response:**
    Confirmation of deletion
    """
    # Verify document exists
    doc_response = supabase_admin.table("documents") \
        .select("id") \
        .eq("id", document_id) \
        .execute()

    if not doc_response.data:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete chunks first (foreign key constraint)
    supabase_admin.table("document_chunks") \
        .delete() \
        .eq("document_id", document_id) \
        .execute()

    # Delete document
    supabase_admin.table("documents") \
        .delete() \
        .eq("id", document_id) \
        .execute()

    # Clean up any conversations for this document
    for conv_id, conv_data in list(_conversation_store.items()):
        if conv_data.get("document_id") == document_id:
            del _conversation_store[conv_id]

    return {"status": "success", "message": "Document deleted successfully"}


@router.get("/documents/{document_id}/chunks")
async def get_document_chunks(
    document_id: str,
    page_number: Optional[int] = Query(None, description="Filter by page number"),
    limit: int = Query(50, ge=1, le=200, description="Number of chunks to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Get chunks for a specific document.

    Development mode: No authentication required.

    **Path Parameters:**
    - document_id: UUID of the document

    **Query Parameters:**
    - page_number: Filter chunks by page
    - limit: Number of results (1-200, default 50)
    - offset: Pagination offset
    """
    query = supabase_admin.table("document_chunks") \
        .select("id, chunk_index, content, page_number") \
        .eq("document_id", document_id)

    if page_number is not None:
        query = query.eq("page_number", page_number)

    response = query.order("chunk_index") \
        .range(offset, offset + limit - 1) \
        .execute()

    return {
        "document_id": document_id,
        "chunks": response.data or [],
        "count": len(response.data or [])
    }


@router.post("/search", response_model=SearchResponse)
async def semantic_search(
    query: str = Form(..., description="Search query"),
    document_id: str = Form(..., description="Document ID to search within"),
    k: int = Form(5, ge=1, le=20, description="Number of results"),
    threshold: float = Form(0.3, ge=0.0, le=1.0, description="Similarity threshold")
):
    """
    Perform semantic search within a document.

    This returns the most relevant chunks without generating an AI response.
    Useful for exploring document content and finding specific passages.

    **Form Parameters:**
    - query: Search query text
    - document_id: UUID of the document to search
    - k: Number of results to return (1-20, default 5)
    - threshold: Minimum similarity score (0-1, default 0.3)

    **Response:**
    - results: List of matching chunks with content, page number, and similarity score
    """
    # Validate document exists
    doc_response = supabase_admin.table("documents") \
        .select("id, status") \
        .eq("id", document_id) \
        .execute()

    if not doc_response.data:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc_response.data[0]["status"] != "completed":
        raise HTTPException(status_code=400, detail="Document is still being processed")

    # Search for relevant chunks
    results = await search_relevant_chunks(
        query=query,
        document_id=document_id,
        k=k,
        similarity_threshold=threshold
    )

    # Convert to response model
    search_results = [
        SearchResult(
            content=r["content"],
            page_number=r["page_number"],
            similarity=r["similarity"],
            chunk_index=r["chunk_index"]
        )
        for r in results
    ]

    return SearchResponse(
        query=query,
        document_id=document_id,
        results=search_results,
        count=len(search_results)
    )


@router.get("/conversations/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    """
    Get conversation history for a chat session.

    **Path Parameters:**
    - conversation_id: UUID of the conversation

    **Response:**
    - Conversation history including all exchanges
    """
    if conversation_id not in _conversation_store:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv = _conversation_store[conversation_id]
    return {
        "conversation_id": conversation_id,
        "document_id": conv["document_id"],
        "history": conv["history"],
        "created_at": conv["created_at"]
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Delete a conversation and its history.

    **Path Parameters:**
    - conversation_id: UUID of the conversation to delete
    """
    if conversation_id not in _conversation_store:
        raise HTTPException(status_code=404, detail="Conversation not found")

    del _conversation_store[conversation_id]
    return {"status": "success", "message": "Conversation deleted successfully"}


@router.get("/health")
async def health_check():
    """
    Health check endpoint for the chat API.

    Returns status of the chat service including database connectivity.
    """
    try:
        # Test database connectivity
        response = supabase_admin.table("documents").select("id").limit(1).execute()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "service": "chat-with-pdf",
        "database": db_status,
        "active_conversations": len(_conversation_store)
    }
