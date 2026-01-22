"""
Paraphraser API - Text paraphrasing with multiple modes for academic research.
Provides sentence-level, paragraph-level, and batch paraphrasing with plagiarism-safe output.
"""

import uuid
import json
import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field

from core.database import supabase
from core.openai_client import async_client

router = APIRouter()

# === Database Schema (for reference) ===
"""
-- Paraphrase History Table
CREATE TABLE paraphrase_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL DEFAULT 'dev-user',
    original_text TEXT NOT NULL,
    paraphrased_text TEXT NOT NULL,
    mode TEXT NOT NULL,
    level TEXT NOT NULL,
    preserve_word_count BOOLEAN DEFAULT FALSE,
    word_count_original INTEGER,
    word_count_result INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Batch Paraphrase Sessions Table
CREATE TABLE batch_paraphrase_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL DEFAULT 'dev-user',
    total_paragraphs INTEGER NOT NULL,
    completed_paragraphs INTEGER DEFAULT 0,
    mode TEXT NOT NULL,
    status TEXT DEFAULT 'processing',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Batch Paraphrase Items Table
CREATE TABLE batch_paraphrase_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES batch_paraphrase_sessions(id) ON DELETE CASCADE,
    original_text TEXT NOT NULL,
    paraphrased_text TEXT,
    paragraph_index INTEGER NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_paraphrase_history_user ON paraphrase_history(user_id);
CREATE INDEX idx_paraphrase_history_created ON paraphrase_history(created_at DESC);
CREATE INDEX idx_batch_items_session ON batch_paraphrase_items(session_id);
"""


# === Enums and Constants ===

class ParaphraseMode(str, Enum):
    STANDARD = "standard"
    ACADEMIC = "academic"
    SIMPLIFIED = "simplified"
    FORMAL = "formal"
    CREATIVE = "creative"


class ParaphraseLevel(str, Enum):
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"


class BatchStatus(str, Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Mode-specific system prompts for paraphrasing
MODE_PROMPTS = {
    ParaphraseMode.STANDARD: """You are an expert paraphraser. Rewrite the given text while:
- Preserving the original meaning completely
- Changing sentence structure and word choice significantly
- Maintaining the same level of formality
- Ensuring the output is plagiarism-safe with substantial structural changes
- Using synonyms and alternative phrasings
Do not add new information or remove existing information.""",

    ParaphraseMode.ACADEMIC: """You are an expert academic writer and paraphraser. Rewrite the given text while:
- Preserving the original meaning completely
- Using formal academic language and terminology
- Employing appropriate hedging language (e.g., "suggests", "indicates", "may")
- Using passive voice where appropriate for scientific writing
- Maintaining objectivity and precision
- Ensuring the output is suitable for academic publication
- Making significant structural changes for plagiarism safety
Do not add new information or remove existing information.""",

    ParaphraseMode.SIMPLIFIED: """You are an expert at simplifying complex text. Rewrite the given text while:
- Preserving the original meaning completely
- Using simpler vocabulary and shorter sentences
- Breaking down complex ideas into easier-to-understand concepts
- Avoiding jargon and technical terms (or explaining them if necessary)
- Making the text accessible to a general audience
- Ensuring clarity and readability
Do not add new information or remove existing information.""",

    ParaphraseMode.FORMAL: """You are an expert at formal writing. Rewrite the given text while:
- Preserving the original meaning completely
- Using highly formal and professional language
- Avoiding contractions, colloquialisms, and casual expressions
- Employing sophisticated vocabulary appropriately
- Maintaining a professional and authoritative tone
- Ensuring the output is suitable for formal documents
Do not add new information or remove existing information.""",

    ParaphraseMode.CREATIVE: """You are a creative writer and paraphraser. Rewrite the given text while:
- Preserving the original meaning completely
- Using creative and engaging language
- Employing varied sentence structures and literary devices
- Making the text more interesting and compelling to read
- Adding stylistic flair without changing the core message
- Ensuring significant structural changes for uniqueness
Do not add new information or remove existing information.""",
}


# === Pydantic Models ===

class ParaphraseRequest(BaseModel):
    """Request model for single text paraphrasing"""
    text: str = Field(..., min_length=10, max_length=10000, description="Text to paraphrase")
    mode: ParaphraseMode = Field(default=ParaphraseMode.STANDARD, description="Paraphrasing mode")
    level: ParaphraseLevel = Field(default=ParaphraseLevel.PARAGRAPH, description="Paraphrase level")
    preserve_word_count: bool = Field(default=False, description="Try to maintain similar word count")
    num_variations: int = Field(default=1, ge=1, le=5, description="Number of paraphrase variations to generate")
    save_history: bool = Field(default=True, description="Save to paraphrase history")


class ParaphraseVariation(BaseModel):
    """Single paraphrase variation"""
    text: str
    word_count: int
    structural_change_score: float = Field(description="Score indicating how different the structure is (0-1)")


class ParaphraseResponse(BaseModel):
    """Response model for paraphrasing"""
    original_text: str
    original_word_count: int
    mode: str
    level: str
    variations: List[ParaphraseVariation]
    preserve_word_count: bool
    history_id: Optional[str] = None


class MultipleVariationsRequest(BaseModel):
    """Request model for generating multiple variations"""
    text: str = Field(..., min_length=10, max_length=10000, description="Text to paraphrase")
    mode: ParaphraseMode = Field(default=ParaphraseMode.STANDARD, description="Paraphrasing mode")
    num_variations: int = Field(default=3, ge=3, le=5, description="Number of variations (3-5)")
    preserve_word_count: bool = Field(default=False, description="Try to maintain similar word count")


class SentenceParaphraseRequest(BaseModel):
    """Request model for sentence-level paraphrasing"""
    text: str = Field(..., min_length=5, max_length=5000, description="Text containing sentences to paraphrase")
    mode: ParaphraseMode = Field(default=ParaphraseMode.STANDARD, description="Paraphrasing mode")
    preserve_word_count: bool = Field(default=False, description="Try to maintain similar word count per sentence")


class SentenceResult(BaseModel):
    """Result for a single sentence"""
    original: str
    paraphrased: str
    original_word_count: int
    paraphrased_word_count: int


class SentenceParaphraseResponse(BaseModel):
    """Response model for sentence-level paraphrasing"""
    mode: str
    total_sentences: int
    sentences: List[SentenceResult]
    combined_text: str


class BatchParaphraseRequest(BaseModel):
    """Request model for batch paraphrasing"""
    paragraphs: List[str] = Field(..., min_items=1, max_items=50, description="List of paragraphs to paraphrase")
    mode: ParaphraseMode = Field(default=ParaphraseMode.STANDARD, description="Paraphrasing mode")
    preserve_word_count: bool = Field(default=False, description="Try to maintain similar word count")


class BatchParagraphResult(BaseModel):
    """Result for a single paragraph in batch"""
    index: int
    original_text: str
    paraphrased_text: str
    original_word_count: int
    paraphrased_word_count: int
    status: str


class BatchParaphraseResponse(BaseModel):
    """Response model for batch paraphrasing"""
    session_id: str
    mode: str
    total_paragraphs: int
    completed_paragraphs: int
    status: str
    results: List[BatchParagraphResult]


class HistoryItem(BaseModel):
    """History item model"""
    id: str
    original_text: str
    paraphrased_text: str
    mode: str
    level: str
    preserve_word_count: bool
    word_count_original: int
    word_count_result: int
    created_at: str


class HistoryResponse(BaseModel):
    """Response model for history listing"""
    items: List[HistoryItem]
    total: int
    page: int
    page_size: int


# === Helper Functions ===

def count_words(text: str) -> int:
    """Count words in text"""
    if not text:
        return 0
    return len(text.split())


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences"""
    # Use regex to split on sentence-ending punctuation
    sentence_pattern = r'(?<=[.!?])\s+'
    sentences = re.split(sentence_pattern, text.strip())
    # Filter out empty sentences
    return [s.strip() for s in sentences if s.strip()]


def calculate_structural_change_score(original: str, paraphrased: str) -> float:
    """
    Calculate a score indicating how different the structure is.
    Higher score means more structural change (better for plagiarism avoidance).
    """
    original_words = set(original.lower().split())
    paraphrased_words = set(paraphrased.lower().split())

    if not original_words:
        return 0.0

    # Calculate Jaccard distance (1 - similarity)
    intersection = len(original_words & paraphrased_words)
    union = len(original_words | paraphrased_words)

    if union == 0:
        return 0.0

    similarity = intersection / union
    change_score = 1 - similarity

    # Also consider sentence structure differences
    original_sentences = len(split_into_sentences(original))
    paraphrased_sentences = len(split_into_sentences(paraphrased))

    structure_diff = abs(original_sentences - paraphrased_sentences) / max(original_sentences, 1)

    # Combine word change and structure change
    final_score = (change_score * 0.7) + (min(structure_diff, 0.3) * 0.3)

    return round(min(final_score, 1.0), 2)


async def generate_paraphrase(
    text: str,
    mode: ParaphraseMode,
    preserve_word_count: bool = False,
    num_variations: int = 1,
) -> List[str]:
    """Generate paraphrased versions of text using GPT-4"""
    system_prompt = MODE_PROMPTS[mode]

    word_count_instruction = ""
    if preserve_word_count:
        original_count = count_words(text)
        word_count_instruction = f"\n\nIMPORTANT: Keep the word count approximately the same as the original ({original_count} words). Aim for {original_count - 10} to {original_count + 10} words."

    if num_variations > 1:
        user_prompt = f"""Paraphrase the following text {num_variations} different ways. Each version should be distinctly different in structure and word choice while preserving the exact same meaning.
{word_count_instruction}

Text to paraphrase:
\"\"\"
{text}
\"\"\"

Provide exactly {num_variations} different paraphrased versions. Format your response as a JSON array of strings:
["version 1", "version 2", ...]"""
    else:
        user_prompt = f"""Paraphrase the following text.
{word_count_instruction}

Text to paraphrase:
\"\"\"
{text}
\"\"\"

Provide only the paraphrased text, nothing else."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    try:
        response = await async_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7 if num_variations > 1 else 0.5,
            max_tokens=4000,
        )

        result_text = response.choices[0].message.content.strip()

        if num_variations > 1:
            # Parse JSON array response
            try:
                # Try to find JSON array in the response
                json_match = re.search(r'\[.*\]', result_text, re.DOTALL)
                if json_match:
                    variations = json.loads(json_match.group())
                else:
                    # Fallback: try to parse the whole response
                    variations = json.loads(result_text)

                # Ensure we have the right number
                if len(variations) < num_variations:
                    # Generate more if needed
                    additional = await generate_paraphrase(text, mode, preserve_word_count, num_variations - len(variations))
                    variations.extend(additional)

                return variations[:num_variations]
            except json.JSONDecodeError:
                # If JSON parsing fails, return the text as a single variation
                return [result_text]
        else:
            return [result_text]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate paraphrase: {str(e)}")


async def save_to_history(
    user_id: str,
    original_text: str,
    paraphrased_text: str,
    mode: str,
    level: str,
    preserve_word_count: bool,
) -> str:
    """Save paraphrase to history and return the history ID"""
    try:
        history_data = {
            "user_id": user_id,
            "original_text": original_text,
            "paraphrased_text": paraphrased_text,
            "mode": mode,
            "level": level,
            "preserve_word_count": preserve_word_count,
            "word_count_original": count_words(original_text),
            "word_count_result": count_words(paraphrased_text),
        }

        result = supabase.table("paraphrase_history").insert(history_data).execute()

        if result.data:
            return result.data[0]["id"]
        return None
    except Exception as e:
        print(f"Error saving to history: {e}")
        return None


# === API Endpoints ===

@router.post("/paraphrase", response_model=ParaphraseResponse)
async def paraphrase_text(request: ParaphraseRequest, user_id: Optional[str] = None):
    """
    Paraphrase text with specified mode and options.

    Modes:
    - standard: General-purpose paraphrasing
    - academic: Formal academic language with hedging
    - simplified: Easier vocabulary and shorter sentences
    - formal: Highly professional and formal language
    - creative: Engaging and stylistically varied

    Levels:
    - sentence: Process each sentence individually
    - paragraph: Process the entire text as a unit
    """
    if not user_id:
        user_id = "dev-user"

    try:
        # Generate paraphrase variations
        variations_text = await generate_paraphrase(
            text=request.text,
            mode=request.mode,
            preserve_word_count=request.preserve_word_count,
            num_variations=request.num_variations,
        )

        # Build variation objects with scores
        variations = []
        for var_text in variations_text:
            variations.append(ParaphraseVariation(
                text=var_text,
                word_count=count_words(var_text),
                structural_change_score=calculate_structural_change_score(request.text, var_text),
            ))

        # Save to history if requested
        history_id = None
        if request.save_history and variations:
            history_id = await save_to_history(
                user_id=user_id,
                original_text=request.text,
                paraphrased_text=variations[0].text,
                mode=request.mode.value,
                level=request.level.value,
                preserve_word_count=request.preserve_word_count,
            )

        return ParaphraseResponse(
            original_text=request.text,
            original_word_count=count_words(request.text),
            mode=request.mode.value,
            level=request.level.value,
            variations=variations,
            preserve_word_count=request.preserve_word_count,
            history_id=history_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Paraphrasing failed: {str(e)}")


@router.post("/variations", response_model=ParaphraseResponse)
async def generate_multiple_variations(request: MultipleVariationsRequest, user_id: Optional[str] = None):
    """
    Generate 3-5 different paraphrase variations of the input text.
    Each variation will have distinct structure and word choice while preserving meaning.
    Useful for choosing the best alternative or avoiding plagiarism detection.
    """
    if not user_id:
        user_id = "dev-user"

    try:
        variations_text = await generate_paraphrase(
            text=request.text,
            mode=request.mode,
            preserve_word_count=request.preserve_word_count,
            num_variations=request.num_variations,
        )

        variations = []
        for var_text in variations_text:
            variations.append(ParaphraseVariation(
                text=var_text,
                word_count=count_words(var_text),
                structural_change_score=calculate_structural_change_score(request.text, var_text),
            ))

        # Sort by structural change score (highest first - most different)
        variations.sort(key=lambda x: x.structural_change_score, reverse=True)

        return ParaphraseResponse(
            original_text=request.text,
            original_word_count=count_words(request.text),
            mode=request.mode.value,
            level=ParaphraseLevel.PARAGRAPH.value,
            variations=variations,
            preserve_word_count=request.preserve_word_count,
            history_id=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate variations: {str(e)}")


@router.post("/sentence-level", response_model=SentenceParaphraseResponse)
async def paraphrase_sentence_level(request: SentenceParaphraseRequest, user_id: Optional[str] = None):
    """
    Paraphrase text at the sentence level.
    Each sentence is processed individually for fine-grained control.
    Returns both individual sentence results and combined text.
    """
    if not user_id:
        user_id = "dev-user"

    try:
        sentences = split_into_sentences(request.text)

        if not sentences:
            raise HTTPException(status_code=400, detail="No valid sentences found in the text")

        # Generate paraphrases for all sentences using a single API call for efficiency
        system_prompt = MODE_PROMPTS[request.mode]

        word_count_instruction = ""
        if request.preserve_word_count:
            word_count_instruction = "\nIMPORTANT: Keep each paraphrased sentence approximately the same word count as its original."

        sentences_numbered = "\n".join([f"{i+1}. {s}" for i, s in enumerate(sentences)])

        user_prompt = f"""Paraphrase each of the following sentences individually. Maintain the same numbering.
{word_count_instruction}

Sentences:
{sentences_numbered}

Provide your response as a JSON array where each element is the paraphrased version of the corresponding sentence:
["paraphrased sentence 1", "paraphrased sentence 2", ...]"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = await async_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.5,
            max_tokens=4000,
        )

        result_text = response.choices[0].message.content.strip()

        # Parse the JSON response
        try:
            json_match = re.search(r'\[.*\]', result_text, re.DOTALL)
            if json_match:
                paraphrased_sentences = json.loads(json_match.group())
            else:
                paraphrased_sentences = json.loads(result_text)
        except json.JSONDecodeError:
            # Fallback: process each sentence individually
            paraphrased_sentences = []
            for sentence in sentences:
                result = await generate_paraphrase(sentence, request.mode, request.preserve_word_count, 1)
                paraphrased_sentences.append(result[0] if result else sentence)

        # Build sentence results
        sentence_results = []
        for i, (orig, para) in enumerate(zip(sentences, paraphrased_sentences)):
            sentence_results.append(SentenceResult(
                original=orig,
                paraphrased=para,
                original_word_count=count_words(orig),
                paraphrased_word_count=count_words(para),
            ))

        # Combine paraphrased sentences
        combined_text = " ".join(paraphrased_sentences)

        return SentenceParaphraseResponse(
            mode=request.mode.value,
            total_sentences=len(sentences),
            sentences=sentence_results,
            combined_text=combined_text,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentence-level paraphrasing failed: {str(e)}")


@router.post("/paragraph-level", response_model=ParaphraseResponse)
async def paraphrase_paragraph_level(request: ParaphraseRequest, user_id: Optional[str] = None):
    """
    Paraphrase text at the paragraph level.
    The entire text is processed as a single unit for coherent output.
    Alias for the main /paraphrase endpoint with level=paragraph.
    """
    request.level = ParaphraseLevel.PARAGRAPH
    return await paraphrase_text(request, user_id)


@router.post("/batch", response_model=BatchParaphraseResponse)
async def batch_paraphrase(request: BatchParaphraseRequest, user_id: Optional[str] = None):
    """
    Paraphrase multiple paragraphs in a single request.
    Useful for processing entire documents or multiple text sections.
    Each paragraph is processed independently and results are returned together.
    """
    if not user_id:
        user_id = "dev-user"

    try:
        session_id = str(uuid.uuid4())

        # Create batch session record
        try:
            session_data = {
                "id": session_id,
                "user_id": user_id,
                "total_paragraphs": len(request.paragraphs),
                "completed_paragraphs": 0,
                "mode": request.mode.value,
                "status": BatchStatus.PROCESSING.value,
            }
            supabase.table("batch_paraphrase_sessions").insert(session_data).execute()
        except Exception:
            pass  # Continue even if session save fails

        results = []
        completed_count = 0

        for i, paragraph in enumerate(request.paragraphs):
            try:
                # Generate paraphrase for this paragraph
                paraphrased_list = await generate_paraphrase(
                    text=paragraph,
                    mode=request.mode,
                    preserve_word_count=request.preserve_word_count,
                    num_variations=1,
                )

                paraphrased_text = paraphrased_list[0] if paraphrased_list else paragraph
                status = "completed"
                completed_count += 1

            except Exception as e:
                paraphrased_text = f"Error: {str(e)}"
                status = "failed"

            results.append(BatchParagraphResult(
                index=i,
                original_text=paragraph,
                paraphrased_text=paraphrased_text,
                original_word_count=count_words(paragraph),
                paraphrased_word_count=count_words(paraphrased_text) if status == "completed" else 0,
                status=status,
            ))

            # Save batch item
            try:
                item_data = {
                    "session_id": session_id,
                    "original_text": paragraph,
                    "paraphrased_text": paraphrased_text if status == "completed" else None,
                    "paragraph_index": i,
                    "status": status,
                }
                supabase.table("batch_paraphrase_items").insert(item_data).execute()
            except Exception:
                pass

        # Update session status
        final_status = BatchStatus.COMPLETED.value if completed_count == len(request.paragraphs) else BatchStatus.FAILED.value

        try:
            supabase.table("batch_paraphrase_sessions").update({
                "completed_paragraphs": completed_count,
                "status": final_status,
                "completed_at": datetime.utcnow().isoformat(),
            }).eq("id", session_id).execute()
        except Exception:
            pass

        return BatchParaphraseResponse(
            session_id=session_id,
            mode=request.mode.value,
            total_paragraphs=len(request.paragraphs),
            completed_paragraphs=completed_count,
            status=final_status,
            results=results,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch paraphrasing failed: {str(e)}")


@router.get("/batch/{session_id}", response_model=BatchParaphraseResponse)
async def get_batch_status(session_id: str):
    """
    Get the status and results of a batch paraphrase session.
    """
    try:
        # Get session
        session_resp = (
            supabase.table("batch_paraphrase_sessions")
            .select("*")
            .eq("id", session_id)
            .execute()
        )

        if not session_resp.data:
            raise HTTPException(status_code=404, detail="Batch session not found")

        session = session_resp.data[0]

        # Get items
        items_resp = (
            supabase.table("batch_paraphrase_items")
            .select("*")
            .eq("session_id", session_id)
            .order("paragraph_index")
            .execute()
        )

        results = []
        for item in items_resp.data or []:
            results.append(BatchParagraphResult(
                index=item["paragraph_index"],
                original_text=item["original_text"],
                paraphrased_text=item.get("paraphrased_text", ""),
                original_word_count=count_words(item["original_text"]),
                paraphrased_word_count=count_words(item.get("paraphrased_text", "")),
                status=item["status"],
            ))

        return BatchParaphraseResponse(
            session_id=session_id,
            mode=session["mode"],
            total_paragraphs=session["total_paragraphs"],
            completed_paragraphs=session["completed_paragraphs"],
            status=session["status"],
            results=results,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get batch status: {str(e)}")


@router.post("/academic", response_model=ParaphraseResponse)
async def paraphrase_academic(
    text: str = Query(..., min_length=10, max_length=10000, description="Text to paraphrase"),
    preserve_word_count: bool = Query(default=False, description="Try to maintain similar word count"),
    num_variations: int = Query(default=1, ge=1, le=5, description="Number of variations"),
    user_id: Optional[str] = None,
):
    """
    Paraphrase text with academic tone enforcement.
    Shortcut endpoint for academic mode paraphrasing.
    Uses formal academic language with appropriate hedging and passive voice.
    """
    request = ParaphraseRequest(
        text=text,
        mode=ParaphraseMode.ACADEMIC,
        level=ParaphraseLevel.PARAGRAPH,
        preserve_word_count=preserve_word_count,
        num_variations=num_variations,
        save_history=True,
    )
    return await paraphrase_text(request, user_id)


@router.post("/plagiarism-safe", response_model=ParaphraseResponse)
async def paraphrase_plagiarism_safe(
    text: str = Query(..., min_length=10, max_length=10000, description="Text to paraphrase"),
    mode: ParaphraseMode = Query(default=ParaphraseMode.STANDARD, description="Paraphrasing mode"),
    user_id: Optional[str] = None,
):
    """
    Generate plagiarism-safe paraphrases with maximum structural changes.
    Returns multiple variations sorted by structural change score.
    Higher scores indicate more significant changes from the original.
    """
    if not user_id:
        user_id = "dev-user"

    try:
        # Generate 5 variations for maximum diversity
        variations_text = await generate_paraphrase(
            text=text,
            mode=mode,
            preserve_word_count=False,  # Allow flexibility for maximum change
            num_variations=5,
        )

        variations = []
        for var_text in variations_text:
            score = calculate_structural_change_score(text, var_text)
            variations.append(ParaphraseVariation(
                text=var_text,
                word_count=count_words(var_text),
                structural_change_score=score,
            ))

        # Sort by structural change score (highest first)
        variations.sort(key=lambda x: x.structural_change_score, reverse=True)

        # Return top 3 most different variations
        return ParaphraseResponse(
            original_text=text,
            original_word_count=count_words(text),
            mode=mode.value,
            level=ParaphraseLevel.PARAGRAPH.value,
            variations=variations[:3],
            preserve_word_count=False,
            history_id=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plagiarism-safe paraphrasing failed: {str(e)}")


# === History Endpoints ===

@router.get("/history", response_model=HistoryResponse)
async def get_paraphrase_history(
    user_id: Optional[str] = None,
    mode: Optional[ParaphraseMode] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    """
    Get paraphrase history for a user.
    Supports filtering by mode and pagination.
    """
    if not user_id:
        user_id = "dev-user"

    try:
        offset = (page - 1) * page_size

        query = (
            supabase.table("paraphrase_history")
            .select("*")
            .eq("user_id", user_id)
        )

        if mode:
            query = query.eq("mode", mode.value)

        response = (
            query
            .order("created_at", desc=True)
            .range(offset, offset + page_size - 1)
            .execute()
        )

        # Get total count
        count_query = (
            supabase.table("paraphrase_history")
            .select("id", count="exact")
            .eq("user_id", user_id)
        )
        if mode:
            count_query = count_query.eq("mode", mode.value)
        count_response = count_query.execute()

        total = count_response.count if hasattr(count_response, 'count') else len(response.data or [])

        items = []
        for item in response.data or []:
            items.append(HistoryItem(
                id=item["id"],
                original_text=item["original_text"],
                paraphrased_text=item["paraphrased_text"],
                mode=item["mode"],
                level=item["level"],
                preserve_word_count=item.get("preserve_word_count", False),
                word_count_original=item.get("word_count_original", 0),
                word_count_result=item.get("word_count_result", 0),
                created_at=item["created_at"],
            ))

        return HistoryResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@router.get("/history/{history_id}", response_model=HistoryItem)
async def get_history_item(history_id: str, user_id: Optional[str] = None):
    """
    Get a specific paraphrase history item.
    """
    if not user_id:
        user_id = "dev-user"

    try:
        response = (
            supabase.table("paraphrase_history")
            .select("*")
            .eq("id", history_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="History item not found")

        item = response.data[0]

        return HistoryItem(
            id=item["id"],
            original_text=item["original_text"],
            paraphrased_text=item["paraphrased_text"],
            mode=item["mode"],
            level=item["level"],
            preserve_word_count=item.get("preserve_word_count", False),
            word_count_original=item.get("word_count_original", 0),
            word_count_result=item.get("word_count_result", 0),
            created_at=item["created_at"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history item: {str(e)}")


@router.delete("/history/{history_id}")
async def delete_history_item(history_id: str, user_id: Optional[str] = None):
    """
    Delete a specific paraphrase history item.
    """
    if not user_id:
        user_id = "dev-user"

    try:
        result = (
            supabase.table("paraphrase_history")
            .delete()
            .eq("id", history_id)
            .eq("user_id", user_id)
            .execute()
        )

        return {"status": "success", "message": "History item deleted"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete history item: {str(e)}")


@router.delete("/history")
async def clear_history(user_id: Optional[str] = None, mode: Optional[ParaphraseMode] = None):
    """
    Clear paraphrase history for a user.
    Optionally filter by mode to clear only specific mode history.
    """
    if not user_id:
        user_id = "dev-user"

    try:
        query = (
            supabase.table("paraphrase_history")
            .delete()
            .eq("user_id", user_id)
        )

        if mode:
            query = query.eq("mode", mode.value)

        query.execute()

        return {"status": "success", "message": "History cleared"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear history: {str(e)}")


# === Utility Endpoints ===

@router.get("/modes")
async def list_paraphrase_modes():
    """
    List all available paraphrase modes with descriptions.
    """
    return {
        "modes": [
            {
                "name": ParaphraseMode.STANDARD.value,
                "description": "General-purpose paraphrasing with balanced word choice and structure changes",
            },
            {
                "name": ParaphraseMode.ACADEMIC.value,
                "description": "Formal academic language with hedging, passive voice, and scholarly tone",
            },
            {
                "name": ParaphraseMode.SIMPLIFIED.value,
                "description": "Simpler vocabulary and shorter sentences for general audience accessibility",
            },
            {
                "name": ParaphraseMode.FORMAL.value,
                "description": "Highly professional language suitable for formal documents",
            },
            {
                "name": ParaphraseMode.CREATIVE.value,
                "description": "Engaging and stylistically varied language with literary flair",
            },
        ]
    }


@router.post("/analyze-structure")
async def analyze_text_structure(
    original: str = Query(..., min_length=10, description="Original text"),
    paraphrased: str = Query(..., min_length=10, description="Paraphrased text"),
):
    """
    Analyze the structural differences between original and paraphrased text.
    Returns metrics useful for plagiarism avoidance assessment.
    """
    original_words = count_words(original)
    paraphrased_words = count_words(paraphrased)
    original_sentences = len(split_into_sentences(original))
    paraphrased_sentences = len(split_into_sentences(paraphrased))

    structural_change_score = calculate_structural_change_score(original, paraphrased)

    # Calculate word overlap
    original_word_set = set(original.lower().split())
    paraphrased_word_set = set(paraphrased.lower().split())
    common_words = original_word_set & paraphrased_word_set
    word_overlap_ratio = len(common_words) / len(original_word_set) if original_word_set else 0

    return {
        "original": {
            "word_count": original_words,
            "sentence_count": original_sentences,
        },
        "paraphrased": {
            "word_count": paraphrased_words,
            "sentence_count": paraphrased_sentences,
        },
        "comparison": {
            "word_count_difference": paraphrased_words - original_words,
            "word_count_change_percent": round((paraphrased_words - original_words) / original_words * 100, 1) if original_words else 0,
            "sentence_count_difference": paraphrased_sentences - original_sentences,
            "word_overlap_ratio": round(word_overlap_ratio, 2),
            "structural_change_score": structural_change_score,
            "plagiarism_safety": "high" if structural_change_score >= 0.5 else "medium" if structural_change_score >= 0.3 else "low",
        },
    }
