"""
Citation Booster API - Agent H
Analyzes text to suggest relevant citations and ensure citation completeness
"""

import asyncio
import re
import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
import numpy as np

from core.database import supabase
from core.openai_client import (
    generate_embedding,
    generate_embedding_batch,
    chat_completion,
    async_client,
)

# Import from literature search module
from app.api.literature import (
    Paper,
    search_pubmed,
    search_arxiv,
    search_semantic_scholar,
    deduplicate_papers,
    generate_bibtex,
    generate_ris,
    generate_apa,
    generate_mla,
)

router = APIRouter()


# === Pydantic Models ===


class TextAnalysisRequest(BaseModel):
    """Request model for text analysis"""

    text: str = Field(..., min_length=10, description="Text to analyze for citations")
    extract_claims: bool = Field(default=True, description="Extract claims that need citations")
    extract_concepts: bool = Field(default=True, description="Extract key concepts")


class Claim(BaseModel):
    """A claim extracted from text that may need citation"""

    text: str
    position: int  # Character position in original text
    confidence: float  # Confidence that this needs a citation (0-1)
    category: str  # e.g., "statistical", "factual", "methodological", "theoretical"
    has_citation: bool = False  # Whether claim already has a citation


class Concept(BaseModel):
    """A key concept extracted from text"""

    term: str
    frequency: int
    importance: float  # 0-1 score
    context: str  # Surrounding context


class TextAnalysisResponse(BaseModel):
    """Response model for text analysis"""

    claims: List[Claim]
    concepts: List[Concept]
    total_claims: int
    uncited_claims: int
    text_length: int


class CitationSuggestion(BaseModel):
    """A suggested citation with relevance scoring"""

    paper: Paper
    relevance_score: float = Field(..., ge=0, le=1)
    matching_claims: List[str]  # Claims this citation supports
    matching_concepts: List[str]  # Concepts this citation relates to
    insertion_context: str  # Suggested context for insertion
    citation_text: Dict[str, str]  # Pre-formatted citations in different styles


class CitationSuggestionRequest(BaseModel):
    """Request model for citation suggestions"""

    text: str = Field(..., min_length=10, description="Text to find citations for")
    max_suggestions: int = Field(default=10, ge=1, le=50)
    sources: List[str] = Field(
        default=["pubmed", "arxiv", "semantic_scholar"],
        description="Academic sources to search",
    )
    year_start: Optional[int] = Field(default=None, ge=1900, le=2100)
    year_end: Optional[int] = Field(default=None, ge=1900, le=2100)
    min_relevance_score: float = Field(default=0.5, ge=0, le=1)


class CitationSuggestionResponse(BaseModel):
    """Response model for citation suggestions"""

    suggestions: List[CitationSuggestion]
    total_found: int
    analysis_summary: Dict[str, Any]


class CitationInsertionRequest(BaseModel):
    """Request model for citation insertion"""

    text: str = Field(..., description="Original text")
    paper: Paper = Field(..., description="Paper to cite")
    position: int = Field(..., ge=0, description="Position to insert citation")
    format: str = Field(default="apa", description="Citation format (apa, mla, bibtex, ris)")
    inline_style: str = Field(
        default="parenthetical",
        description="Inline style: parenthetical, narrative, or footnote",
    )


class CitationInsertionResponse(BaseModel):
    """Response model for citation insertion"""

    modified_text: str
    citation_key: str
    reference_entry: str


class CitationGapRequest(BaseModel):
    """Request for citation gap analysis"""

    text: str = Field(..., min_length=10)
    existing_citations: List[Paper] = Field(default=[])


class CitationGap(BaseModel):
    """An identified gap in citations"""

    claim: Claim
    severity: str  # "critical", "recommended", "optional"
    suggested_search_terms: List[str]
    reason: str


class CitationGapResponse(BaseModel):
    """Response for citation gap analysis"""

    gaps: List[CitationGap]
    coverage_score: float  # 0-1 overall citation coverage
    recommendations: List[str]


class BatchSuggestionRequest(BaseModel):
    """Request for batch citation suggestions on entire document"""

    text: str = Field(..., min_length=50)
    sections: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Optional section breakdown with titles and text",
    )
    max_suggestions_per_section: int = Field(default=5, ge=1, le=20)
    sources: List[str] = Field(default=["pubmed", "arxiv", "semantic_scholar"])


class SectionSuggestions(BaseModel):
    """Suggestions for a document section"""

    section_title: str
    section_text: str
    suggestions: List[CitationSuggestion]
    uncited_claims_count: int


class BatchSuggestionResponse(BaseModel):
    """Response for batch suggestions"""

    sections: List[SectionSuggestions]
    total_suggestions: int
    document_analysis: Dict[str, Any]


class CompletenessReportRequest(BaseModel):
    """Request for citation completeness report"""

    text: str = Field(..., min_length=50)
    existing_citations: List[Paper] = Field(default=[])
    citation_style: str = Field(default="apa")


class CompletenessReport(BaseModel):
    """Comprehensive citation completeness report"""

    overall_score: float  # 0-100
    total_claims: int
    cited_claims: int
    uncited_claims: int
    coverage_by_category: Dict[str, Dict[str, Any]]
    critical_gaps: List[CitationGap]
    suggested_citations: List[CitationSuggestion]
    recommendations: List[str]
    formatted_reference_list: str


# === Helper Functions ===


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    a = np.array(vec1)
    b = np.array(vec2)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


async def extract_claims_from_text(text: str) -> List[Claim]:
    """Use GPT to extract claims that need citations"""
    prompt = f"""Analyze the following academic text and identify claims that should have citations.
For each claim, provide:
1. The exact text of the claim
2. The approximate character position where it starts
3. A confidence score (0-1) for how strongly this claim needs a citation
4. The category: "statistical" (numbers, percentages), "factual" (established facts),
   "methodological" (methods, procedures), or "theoretical" (theories, frameworks)
5. Whether it appears to already have a citation (look for [1], (Author, Year), etc.)

Text to analyze:
{text[:4000]}

Respond in JSON format:
{{
    "claims": [
        {{
            "text": "claim text",
            "position": 0,
            "confidence": 0.9,
            "category": "statistical",
            "has_citation": false
        }}
    ]
}}"""

    try:
        response = await async_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an academic writing assistant that identifies claims needing citations.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)
        claims = []
        for claim_data in result.get("claims", []):
            claims.append(
                Claim(
                    text=claim_data.get("text", ""),
                    position=claim_data.get("position", 0),
                    confidence=claim_data.get("confidence", 0.5),
                    category=claim_data.get("category", "factual"),
                    has_citation=claim_data.get("has_citation", False),
                )
            )
        return claims
    except Exception as e:
        print(f"Error extracting claims: {e}")
        return []


async def extract_concepts_from_text(text: str) -> List[Concept]:
    """Use GPT to extract key concepts from text"""
    prompt = f"""Analyze the following academic text and identify key concepts that could be used
to find relevant citations. Focus on:
- Technical terms
- Methodologies
- Theories or frameworks
- Domain-specific vocabulary

For each concept, provide:
1. The term
2. How many times it appears (frequency)
3. Importance score (0-1) based on how central it is to the text
4. A brief context showing how it's used

Text to analyze:
{text[:4000]}

Respond in JSON format:
{{
    "concepts": [
        {{
            "term": "machine learning",
            "frequency": 5,
            "importance": 0.9,
            "context": "used in the context of..."
        }}
    ]
}}"""

    try:
        response = await async_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an academic concept extraction specialist.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)
        concepts = []
        for concept_data in result.get("concepts", []):
            concepts.append(
                Concept(
                    term=concept_data.get("term", ""),
                    frequency=concept_data.get("frequency", 1),
                    importance=concept_data.get("importance", 0.5),
                    context=concept_data.get("context", ""),
                )
            )
        return concepts
    except Exception as e:
        print(f"Error extracting concepts: {e}")
        return []


async def generate_search_queries(claims: List[Claim], concepts: List[Concept]) -> List[str]:
    """Generate optimal search queries from claims and concepts"""
    # Combine high-confidence claims and important concepts
    query_sources = []

    for claim in claims:
        if claim.confidence > 0.7 and not claim.has_citation:
            query_sources.append(claim.text[:100])

    for concept in concepts:
        if concept.importance > 0.6:
            query_sources.append(concept.term)

    # Deduplicate and limit
    unique_queries = list(set(query_sources))[:5]

    # If we have very few queries, add some based on concepts
    if len(unique_queries) < 3:
        for concept in sorted(concepts, key=lambda c: c.importance, reverse=True):
            if concept.term not in unique_queries:
                unique_queries.append(concept.term)
            if len(unique_queries) >= 3:
                break

    return unique_queries


async def score_paper_relevance(
    paper: Paper,
    text_embedding: List[float],
    claims: List[Claim],
    concepts: List[Concept],
) -> tuple[float, List[str], List[str]]:
    """Score how relevant a paper is to the text, claims, and concepts"""

    # Generate embedding for paper content
    paper_text = f"{paper.title}. {paper.abstract or ''}"
    try:
        paper_embedding = await generate_embedding(paper_text[:2000])
    except Exception:
        # Fallback if embedding fails
        paper_embedding = text_embedding  # Will result in score of 1, needs adjustment

    # Calculate semantic similarity
    semantic_score = cosine_similarity(text_embedding, paper_embedding)

    # Find matching claims (simple text matching)
    matching_claims = []
    paper_text_lower = paper_text.lower()
    for claim in claims:
        claim_words = set(claim.text.lower().split())
        # Check if significant words from claim appear in paper
        matching_words = sum(1 for word in claim_words if len(word) > 4 and word in paper_text_lower)
        if matching_words >= 2:
            matching_claims.append(claim.text[:100])

    # Find matching concepts
    matching_concepts = []
    for concept in concepts:
        if concept.term.lower() in paper_text_lower:
            matching_concepts.append(concept.term)

    # Calculate final score
    # Weight: 50% semantic similarity, 25% claim matches, 25% concept matches
    claim_score = min(len(matching_claims) / max(len(claims), 1), 1.0)
    concept_score = min(len(matching_concepts) / max(len(concepts), 1), 1.0)

    final_score = (0.5 * semantic_score) + (0.25 * claim_score) + (0.25 * concept_score)

    return final_score, matching_claims, matching_concepts


def format_citation_for_paper(paper: Paper) -> Dict[str, str]:
    """Generate all citation formats for a paper"""
    return {
        "apa": generate_apa(paper),
        "mla": generate_mla(paper),
        "bibtex": generate_bibtex(paper),
        "ris": generate_ris(paper),
    }


def generate_inline_citation(paper: Paper, style: str, inline_style: str) -> str:
    """Generate inline citation text"""
    first_author = paper.authors[0].split()[-1] if paper.authors else "Unknown"
    year = paper.year or "n.d."

    if inline_style == "parenthetical":
        if style.lower() == "apa":
            if len(paper.authors) == 1:
                return f"({first_author}, {year})"
            elif len(paper.authors) == 2:
                second_author = paper.authors[1].split()[-1]
                return f"({first_author} & {second_author}, {year})"
            else:
                return f"({first_author} et al., {year})"
        elif style.lower() == "mla":
            return f"({first_author})"
        else:
            return f"[{first_author}{year}]"

    elif inline_style == "narrative":
        if len(paper.authors) == 1:
            return f"{first_author} ({year})"
        elif len(paper.authors) == 2:
            second_author = paper.authors[1].split()[-1]
            return f"{first_author} and {second_author} ({year})"
        else:
            return f"{first_author} et al. ({year})"

    elif inline_style == "footnote":
        return f"[^{first_author}{year}]"

    return f"({first_author}, {year})"


async def identify_citation_gaps(
    claims: List[Claim],
    existing_citations: List[Paper],
) -> List[CitationGap]:
    """Identify gaps in citation coverage"""
    gaps = []

    # Get embeddings for existing citations if any
    citation_texts = []
    for paper in existing_citations:
        citation_texts.append(f"{paper.title}. {paper.abstract or ''}"[:500])

    citation_embeddings = []
    if citation_texts:
        try:
            citation_embeddings = await generate_embedding_batch(citation_texts)
        except Exception:
            pass

    for claim in claims:
        if claim.has_citation:
            continue

        # Determine severity based on confidence and category
        if claim.confidence > 0.8:
            if claim.category == "statistical":
                severity = "critical"
            elif claim.category in ["factual", "methodological"]:
                severity = "critical" if claim.confidence > 0.9 else "recommended"
            else:
                severity = "recommended"
        elif claim.confidence > 0.6:
            severity = "recommended"
        else:
            severity = "optional"

        # Check if any existing citation covers this claim
        if citation_embeddings:
            try:
                claim_embedding = await generate_embedding(claim.text)
                max_similarity = max(
                    cosine_similarity(claim_embedding, ce) for ce in citation_embeddings
                )
                if max_similarity > 0.7:
                    # Claim is likely covered by existing citation
                    continue
            except Exception:
                pass

        # Generate search terms for this gap
        words = claim.text.split()
        search_terms = [
            " ".join(words[i : i + 3])
            for i in range(0, min(len(words), 9), 3)
            if i + 3 <= len(words)
        ]

        gap = CitationGap(
            claim=claim,
            severity=severity,
            suggested_search_terms=search_terms[:3],
            reason=f"Uncited {claim.category} claim with {claim.confidence:.0%} citation need confidence",
        )
        gaps.append(gap)

    return gaps


# === API Endpoints ===


@router.post("/analyze", response_model=TextAnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    """
    Analyze text to extract claims and concepts that need citations.

    This endpoint identifies:
    - Claims that should have citations (statistical, factual, methodological, theoretical)
    - Key concepts that can be used to find relevant literature
    """
    tasks = []

    if request.extract_claims:
        tasks.append(extract_claims_from_text(request.text))
    else:
        tasks.append(asyncio.coroutine(lambda: [])())

    if request.extract_concepts:
        tasks.append(extract_concepts_from_text(request.text))
    else:
        tasks.append(asyncio.coroutine(lambda: [])())

    claims, concepts = await asyncio.gather(*tasks)

    uncited_claims = sum(1 for c in claims if not c.has_citation)

    return TextAnalysisResponse(
        claims=claims,
        concepts=concepts,
        total_claims=len(claims),
        uncited_claims=uncited_claims,
        text_length=len(request.text),
    )


@router.post("/analyze-upload")
async def analyze_uploaded_text(file: UploadFile = File(...)):
    """
    Analyze uploaded text file for citation needs.

    Supports: .txt, .md files
    """
    if not file.filename.endswith((".txt", ".md")):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload .txt or .md files.",
        )

    try:
        content = await file.read()
        text = content.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

    # Analyze the text
    claims, concepts = await asyncio.gather(
        extract_claims_from_text(text),
        extract_concepts_from_text(text),
    )

    uncited_claims = sum(1 for c in claims if not c.has_citation)

    return TextAnalysisResponse(
        claims=claims,
        concepts=concepts,
        total_claims=len(claims),
        uncited_claims=uncited_claims,
        text_length=len(text),
    )


@router.post("/suggest", response_model=CitationSuggestionResponse)
async def suggest_citations(request: CitationSuggestionRequest):
    """
    Suggest relevant citations for the given text.

    Uses semantic similarity and keyword matching to find the most relevant papers
    from multiple academic databases.
    """
    # Step 1: Analyze text
    claims, concepts = await asyncio.gather(
        extract_claims_from_text(request.text),
        extract_concepts_from_text(request.text),
    )

    # Step 2: Generate search queries
    search_queries = await generate_search_queries(claims, concepts)

    if not search_queries:
        # Fallback: use first 100 chars of text as query
        search_queries = [request.text[:100]]

    # Step 3: Search across sources
    all_papers = []
    search_tasks = []

    for query in search_queries[:3]:  # Limit to 3 queries
        if "pubmed" in request.sources:
            search_tasks.append(
                search_pubmed(query, max_results=10, year_start=request.year_start, year_end=request.year_end)
            )
        if "arxiv" in request.sources:
            search_tasks.append(
                search_arxiv(query, max_results=10, year_start=request.year_start, year_end=request.year_end)
            )
        if "semantic_scholar" in request.sources:
            search_tasks.append(
                search_semantic_scholar(query, max_results=10, year_start=request.year_start, year_end=request.year_end)
            )

    if search_tasks:
        results = await asyncio.gather(*search_tasks)
        for paper_list in results:
            all_papers.extend(paper_list)

    # Deduplicate papers
    unique_papers = deduplicate_papers(all_papers)

    if not unique_papers:
        return CitationSuggestionResponse(
            suggestions=[],
            total_found=0,
            analysis_summary={
                "claims_found": len(claims),
                "concepts_found": len(concepts),
                "search_queries": search_queries,
            },
        )

    # Step 4: Generate text embedding for relevance scoring
    try:
        text_embedding = await generate_embedding(request.text[:2000])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate embedding: {str(e)}")

    # Step 5: Score and rank papers
    scored_suggestions = []
    for paper in unique_papers:
        score, matching_claims, matching_concepts = await score_paper_relevance(
            paper, text_embedding, claims, concepts
        )

        if score >= request.min_relevance_score:
            suggestion = CitationSuggestion(
                paper=paper,
                relevance_score=score,
                matching_claims=matching_claims[:3],
                matching_concepts=matching_concepts[:5],
                insertion_context=f"Supports claims about {', '.join(matching_concepts[:2]) if matching_concepts else 'the topic'}",
                citation_text=format_citation_for_paper(paper),
            )
            scored_suggestions.append(suggestion)

    # Sort by relevance and limit
    scored_suggestions.sort(key=lambda s: s.relevance_score, reverse=True)
    final_suggestions = scored_suggestions[: request.max_suggestions]

    return CitationSuggestionResponse(
        suggestions=final_suggestions,
        total_found=len(scored_suggestions),
        analysis_summary={
            "claims_found": len(claims),
            "uncited_claims": sum(1 for c in claims if not c.has_citation),
            "concepts_found": len(concepts),
            "search_queries_used": search_queries,
            "papers_searched": len(unique_papers),
        },
    )


@router.post("/insert", response_model=CitationInsertionResponse)
async def insert_citation(request: CitationInsertionRequest):
    """
    Insert a citation into text with proper formatting.

    Supports multiple citation styles and inline formats.
    """
    # Validate position
    if request.position > len(request.text):
        raise HTTPException(
            status_code=400,
            detail=f"Position {request.position} exceeds text length {len(request.text)}",
        )

    # Generate inline citation
    inline_citation = generate_inline_citation(
        request.paper, request.format, request.inline_style
    )

    # Generate citation key
    first_author = request.paper.authors[0].split()[-1] if request.paper.authors else "Unknown"
    citation_key = f"{first_author}{request.paper.year or 'nd'}"

    # Insert citation at position
    modified_text = (
        request.text[: request.position]
        + " "
        + inline_citation
        + request.text[request.position:]
    )

    # Generate reference entry
    format_lower = request.format.lower()
    if format_lower == "apa":
        reference_entry = generate_apa(request.paper)
    elif format_lower == "mla":
        reference_entry = generate_mla(request.paper)
    elif format_lower == "bibtex":
        reference_entry = generate_bibtex(request.paper)
    elif format_lower == "ris":
        reference_entry = generate_ris(request.paper)
    else:
        reference_entry = generate_apa(request.paper)

    return CitationInsertionResponse(
        modified_text=modified_text,
        citation_key=citation_key,
        reference_entry=reference_entry,
    )


@router.post("/gaps", response_model=CitationGapResponse)
async def analyze_citation_gaps(request: CitationGapRequest):
    """
    Analyze text to identify citation gaps.

    Returns claims that need citations but don't have them,
    along with severity ratings and search suggestions.
    """
    # Extract claims
    claims = await extract_claims_from_text(request.text)

    # Identify gaps
    gaps = await identify_citation_gaps(claims, request.existing_citations)

    # Calculate coverage score
    total_claims = len(claims)
    cited_claims = sum(1 for c in claims if c.has_citation)

    if total_claims > 0:
        # Also consider claims covered by existing_citations
        coverage_score = cited_claims / total_claims
    else:
        coverage_score = 1.0

    # Generate recommendations
    recommendations = []
    critical_count = sum(1 for g in gaps if g.severity == "critical")
    recommended_count = sum(1 for g in gaps if g.severity == "recommended")

    if critical_count > 0:
        recommendations.append(
            f"Add citations for {critical_count} critical claims (statistical/factual statements)"
        )
    if recommended_count > 0:
        recommendations.append(
            f"Consider adding citations for {recommended_count} recommended claims"
        )
    if coverage_score < 0.5:
        recommendations.append(
            "Overall citation coverage is low. Consider a comprehensive literature review."
        )
    elif coverage_score > 0.8:
        recommendations.append("Good citation coverage! Focus on the remaining gaps.")

    return CitationGapResponse(
        gaps=gaps,
        coverage_score=coverage_score,
        recommendations=recommendations,
    )


@router.post("/batch-suggest", response_model=BatchSuggestionResponse)
async def batch_suggest_citations(request: BatchSuggestionRequest):
    """
    Generate citation suggestions for an entire document.

    Can process the document as a whole or by sections.
    """
    sections_to_process = []

    if request.sections:
        # Use provided sections
        for section in request.sections:
            sections_to_process.append({
                "title": section.get("title", "Untitled Section"),
                "text": section.get("text", ""),
            })
    else:
        # Auto-detect sections based on headers or split into chunks
        # Simple approach: split by double newlines or headers
        header_pattern = r"^#{1,6}\s+.+$|^[A-Z][^.!?]*:?\s*$"
        parts = re.split(r"\n\n+", request.text)

        current_section = {"title": "Introduction", "text": ""}

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Check if this looks like a header
            if re.match(header_pattern, part, re.MULTILINE):
                if current_section["text"]:
                    sections_to_process.append(current_section)
                current_section = {"title": part.strip("#").strip(), "text": ""}
            else:
                current_section["text"] += part + "\n\n"

        if current_section["text"]:
            sections_to_process.append(current_section)

    # If no sections detected, treat whole text as one section
    if not sections_to_process:
        sections_to_process = [{"title": "Document", "text": request.text}]

    # Process each section
    section_results = []
    total_suggestions = 0

    for section in sections_to_process:
        if len(section["text"]) < 50:
            continue

        # Get suggestions for this section
        try:
            suggestion_request = CitationSuggestionRequest(
                text=section["text"],
                max_suggestions=request.max_suggestions_per_section,
                sources=request.sources,
            )

            result = await suggest_citations(suggestion_request)

            section_results.append(
                SectionSuggestions(
                    section_title=section["title"],
                    section_text=section["text"][:500] + "..." if len(section["text"]) > 500 else section["text"],
                    suggestions=result.suggestions,
                    uncited_claims_count=result.analysis_summary.get("uncited_claims", 0),
                )
            )
            total_suggestions += len(result.suggestions)

        except Exception as e:
            print(f"Error processing section '{section['title']}': {e}")
            section_results.append(
                SectionSuggestions(
                    section_title=section["title"],
                    section_text=section["text"][:500] + "...",
                    suggestions=[],
                    uncited_claims_count=0,
                )
            )

    # Document-level analysis
    document_analysis = {
        "total_sections": len(section_results),
        "total_suggestions": total_suggestions,
        "sections_needing_citations": sum(
            1 for s in section_results if s.uncited_claims_count > 0
        ),
        "document_length": len(request.text),
    }

    return BatchSuggestionResponse(
        sections=section_results,
        total_suggestions=total_suggestions,
        document_analysis=document_analysis,
    )


@router.post("/completeness-report", response_model=CompletenessReport)
async def generate_completeness_report(request: CompletenessReportRequest):
    """
    Generate a comprehensive citation completeness report.

    Includes overall score, gap analysis, and suggested citations.
    """
    # Extract claims and concepts
    claims, concepts = await asyncio.gather(
        extract_claims_from_text(request.text),
        extract_concepts_from_text(request.text),
    )

    # Analyze gaps
    gaps = await identify_citation_gaps(claims, request.existing_citations)

    # Calculate statistics
    total_claims = len(claims)
    cited_claims = sum(1 for c in claims if c.has_citation)
    uncited_claims = total_claims - cited_claims

    # Coverage by category
    categories = ["statistical", "factual", "methodological", "theoretical"]
    coverage_by_category = {}

    for category in categories:
        category_claims = [c for c in claims if c.category == category]
        category_cited = sum(1 for c in category_claims if c.has_citation)

        coverage_by_category[category] = {
            "total": len(category_claims),
            "cited": category_cited,
            "uncited": len(category_claims) - category_cited,
            "coverage_percent": (
                (category_cited / len(category_claims) * 100)
                if category_claims
                else 100
            ),
        }

    # Calculate overall score (weighted by category importance)
    weights = {"statistical": 1.0, "factual": 0.9, "methodological": 0.8, "theoretical": 0.7}
    weighted_score = 0
    total_weight = 0

    for category, data in coverage_by_category.items():
        weight = weights.get(category, 0.5)
        if data["total"] > 0:
            weighted_score += weight * data["coverage_percent"]
            total_weight += weight

    overall_score = weighted_score / total_weight if total_weight > 0 else 100

    # Get critical gaps
    critical_gaps = [g for g in gaps if g.severity == "critical"]

    # Get citation suggestions for uncited claims
    suggested_citations = []
    if uncited_claims > 0:
        try:
            suggestion_request = CitationSuggestionRequest(
                text=request.text,
                max_suggestions=min(10, uncited_claims),
                min_relevance_score=0.4,
            )
            suggestion_result = await suggest_citations(suggestion_request)
            suggested_citations = suggestion_result.suggestions
        except Exception:
            pass

    # Generate recommendations
    recommendations = []

    if overall_score < 50:
        recommendations.append(
            "Citation coverage is significantly below standards. Prioritize adding citations for statistical and factual claims."
        )
    elif overall_score < 75:
        recommendations.append(
            "Citation coverage needs improvement. Focus on uncited claims marked as critical."
        )
    else:
        recommendations.append(
            "Good citation coverage. Review remaining gaps for completeness."
        )

    if coverage_by_category["statistical"]["uncited"] > 0:
        recommendations.append(
            f"Add citations for {coverage_by_category['statistical']['uncited']} statistical claims (numbers, percentages)."
        )

    if coverage_by_category["factual"]["uncited"] > 0:
        recommendations.append(
            f"Add citations for {coverage_by_category['factual']['uncited']} factual claims."
        )

    if len(request.existing_citations) < 5 and total_claims > 10:
        recommendations.append(
            "Consider expanding your reference list. The document has many claims but few citations."
        )

    # Format reference list from existing citations
    reference_list_entries = []
    for paper in request.existing_citations:
        if request.citation_style.lower() == "apa":
            reference_list_entries.append(generate_apa(paper))
        elif request.citation_style.lower() == "mla":
            reference_list_entries.append(generate_mla(paper))
        elif request.citation_style.lower() == "bibtex":
            reference_list_entries.append(generate_bibtex(paper))
        else:
            reference_list_entries.append(generate_apa(paper))

    # Sort alphabetically by first author
    reference_list_entries.sort()
    formatted_reference_list = "\n\n".join(reference_list_entries)

    return CompletenessReport(
        overall_score=round(overall_score, 1),
        total_claims=total_claims,
        cited_claims=cited_claims,
        uncited_claims=uncited_claims,
        coverage_by_category=coverage_by_category,
        critical_gaps=critical_gaps[:10],
        suggested_citations=suggested_citations,
        recommendations=recommendations,
        formatted_reference_list=formatted_reference_list,
    )


@router.get("/formats")
async def get_supported_formats():
    """Get list of supported citation formats"""
    return {
        "citation_formats": ["apa", "mla", "bibtex", "ris"],
        "inline_styles": ["parenthetical", "narrative", "footnote"],
        "descriptions": {
            "apa": "APA 7th Edition - Author-date format commonly used in social sciences",
            "mla": "MLA 9th Edition - Author-page format commonly used in humanities",
            "bibtex": "BibTeX - LaTeX bibliography format for technical documents",
            "ris": "RIS - Research Information Systems format for reference managers",
        },
    }


@router.post("/quick-cite")
async def quick_cite(
    text: str = Form(..., description="Text passage to cite"),
    query: Optional[str] = Form(None, description="Optional specific search query"),
    format: str = Form("apa", description="Citation format"),
    max_results: int = Form(5, ge=1, le=20),
):
    """
    Quick citation endpoint - find and format citations in one step.

    Analyzes text and returns ready-to-use citations.
    """
    # Use query if provided, otherwise extract from text
    search_query = query or text[:100]

    # Search for papers
    papers = []
    search_tasks = [
        search_pubmed(search_query, max_results=max_results),
        search_semantic_scholar(search_query, max_results=max_results),
    ]

    results = await asyncio.gather(*search_tasks)
    for result in results:
        papers.extend(result)

    # Deduplicate
    unique_papers = deduplicate_papers(papers)[:max_results]

    # Format citations
    formatted_citations = []
    for paper in unique_papers:
        citation_formats = format_citation_for_paper(paper)
        inline_citation = generate_inline_citation(paper, format, "parenthetical")

        formatted_citations.append({
            "paper": {
                "title": paper.title,
                "authors": paper.authors,
                "year": paper.year,
                "journal": paper.journal,
                "doi": paper.doi,
            },
            "inline_citation": inline_citation,
            "reference_entry": citation_formats.get(format.lower(), citation_formats["apa"]),
            "all_formats": citation_formats,
        })

    return {
        "query_used": search_query,
        "citations": formatted_citations,
        "count": len(formatted_citations),
    }
