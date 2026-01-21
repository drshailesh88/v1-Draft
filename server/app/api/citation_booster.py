from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from core.database import supabase, get_user_from_token
import httpx
import json
import os
from datetime import datetime
import re

router = APIRouter()

API_URL = os.getenv("NEXT_PUBLIC_API_URL", "http://localhost:3000")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class CitationAnalyzeRequest(BaseModel):
    text: str


class CitationGap(BaseModel):
    section: str
    position: int
    gap_type: str
    description: str
    suggested_topics: List[str]


class SuggestedPaper(BaseModel):
    title: str
    authors: List[str]
    year: str
    journal: str
    doi: str
    abstract: str
    source: str
    url: str
    relevance_score: float
    reason: str


class CitationAnalyzeResponse(BaseModel):
    missing_citations: List[CitationGap]
    suggested_papers: List[SuggestedPaper]
    gap_analysis: str
    original_text: str


class AddCitationRequest(BaseModel):
    text: str
    paper: dict
    position: int


class AddCitationResponse(BaseModel):
    updated_text: str
    citation_added: str


@router.post("/analyze", response_model=CitationAnalyzeResponse)
async def analyze_citations(request: CitationAnalyzeRequest, token: str = None):
    """Analyze text for citation gaps and suggest relevant papers"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        text = request.text
        if not text or len(text) < 100:
            raise HTTPException(status_code=400, detail="Text too short for analysis")

        # Analyze gaps using OpenAI
        gap_analysis_result = await analyze_gaps_with_openai(text)

        # Extract topics from gaps to search for papers
        all_topics = []
        for gap in gap_analysis_result.get("gaps", []):
            all_topics.extend(gap.get("suggested_topics", []))

        # Search for relevant papers
        suggested_papers = []
        if all_topics:
            search_results = await search_relevant_papers(all_topics)
            # Calculate relevance scores
            suggested_papers = await rank_papers_relevance(text, search_results)

        # Save to database
        boost_data = {
            "user_id": user.get("id") if user else None,
            "original_text": text,
            "gap_analysis": gap_analysis_result.get("overall_analysis", ""),
            "created_at": datetime.now().isoformat(),
        }
        boost_response = supabase.table("citation_boosts").insert(boost_data).execute()

        boost_id = boost_response.data[0]["id"] if boost_response.data else None

        # Save boosted citations
        if boost_id and suggested_papers:
            citations_data = []
            for i, paper in enumerate(suggested_papers[:10]):
                citations_data.append(
                    {
                        "boost_id": boost_id,
                        "paper_id": paper.get("doi", f"paper_{i}"),
                        "position_in_text": i,
                        "relevance_score": paper.get("relevance_score", 0.0),
                        "paper_metadata": paper,
                    }
                )
            if citations_data:
                supabase.table("boosted_citations").insert(citations_data).execute()

        return CitationAnalyzeResponse(
            missing_citations=[
                CitationGap(
                    section=gap.get("section", ""),
                    position=gap.get("position", 0),
                    gap_type=gap.get("gap_type", ""),
                    description=gap.get("description", ""),
                    suggested_topics=gap.get("suggested_topics", []),
                )
                for gap in gap_analysis_result.get("gaps", [])
            ],
            suggested_papers=[
                SuggestedPaper(
                    title=paper.get("title", ""),
                    authors=paper.get("authors", []),
                    year=paper.get("year", ""),
                    journal=paper.get("journal", ""),
                    doi=paper.get("doi", ""),
                    abstract=paper.get("abstract", ""),
                    source=paper.get("source", ""),
                    url=paper.get("url", ""),
                    relevance_score=paper.get("relevance_score", 0.0),
                    reason=paper.get("reason", ""),
                )
                for paper in suggested_papers
            ],
            gap_analysis=gap_analysis_result.get("overall_analysis", ""),
            original_text=text,
        )

    except Exception as e:
        print(f"Error analyzing citations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def analyze_gaps_with_openai(text: str) -> dict:
    """Use OpenAI GPT-4 to analyze text for citation gaps"""
    try:
        prompt = f"""Analyze the following academic text for citation gaps. Identify:

1. Sections that need citations (e.g., claims without evidence, referenced but not cited)
2. Types of gaps (missing evidence, outdated sources, lack of foundational support)
3. Description of why each gap exists
4. Suggested topics/research areas to search for relevant papers

Text to analyze:
{text[:4000]}

Return your response in this exact JSON format:
{{
  "overall_analysis": "Brief summary of citation quality and major gaps",
  "gaps": [
    {{
      "section": "Introduction/methods/etc",
      "position": 0,
      "gap_type": "missing_evidence/outdated/lack_support",
      "description": "Specific explanation",
      "suggested_topics": ["topic1", "topic2"]
    }}
  ]
}}"""

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
            )
            response.raise_for_status()
            result = response.json()

            content = result["choices"][0]["message"]["content"]
            return json.loads(content)

    except Exception as e:
        print(f"OpenAI analysis error: {e}")
        return {
            "overall_analysis": "Unable to perform detailed analysis. Please try again.",
            "gaps": [],
        }


async def search_relevant_papers(topics: List[str]) -> List[dict]:
    """Search literature API for papers on suggested topics"""
    all_papers = []

    try:
        for topic in topics[:5]:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{API_URL}/api/literature/search",
                    json={
                        "query": topic,
                        "sources": ["pubmed", "arxiv", "semantic_scholar"],
                        "max_results": 5,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    all_papers.extend(data.get("papers", []))

    except Exception as e:
        print(f"Error searching literature: {e}")

    return all_papers


async def rank_papers_relevance(text: str, papers: List[dict]) -> List[dict]:
    """Calculate relevance scores for suggested papers"""
    if not papers:
        return []

    try:
        prompt = f"""Rate the relevance of each paper to the text below. Consider:

1. How well the paper supports claims in the text
2. Recency (prefer newer papers for current research)
3. Authority (journal impact, well-known authors)
4. Direct relevance to the research topic

Text excerpt:
{text[:2000]}

Papers to rate:
{json.dumps([{"title": p.get("title", ""), "abstract": p.get("abstract", "")} for p in papers[:15]], indent=2)}

Return your response in this exact JSON format:
{{
  "papers": [
    {{
      "index": 0,
      "relevance_score": 0.85,
      "reason": "Brief explanation of why this paper is relevant"
    }}
  ]
}}

Relevance scores should be between 0.0 and 1.0."""

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
            )
            response.raise_for_status()
            result = response.json()

            content = result["choices"][0]["message"]["content"]
            ratings = json.loads(content)

            # Merge ratings with paper data
            for rating in ratings.get("papers", []):
                idx = rating.get("index", 0)
                if idx < len(papers):
                    papers[idx]["relevance_score"] = rating.get("relevance_score", 0.5)
                    papers[idx]["reason"] = rating.get("reason", "")

            # Sort by relevance score
            papers.sort(key=lambda x: x.get("relevance_score", 0.0), reverse=True)

            return papers[:10]

    except Exception as e:
        print(f"Error ranking papers: {e}")
        # Return papers with default scores
        for paper in papers:
            paper["relevance_score"] = 0.5
            paper["reason"] = "Unable to calculate detailed relevance score"
        return papers[:10]


@router.post("/add-citation", response_model=AddCitationResponse)
async def add_citation(request: AddCitationRequest, token: str = None):
    """Add a citation to the text at specified position"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        text = request.text
        paper = request.paper
        position = request.position

        # Generate citation in common format
        citation = generate_citation_string(paper)

        # Insert citation at position
        if position >= 0 and position <= len(text):
            updated_text = text[:position] + citation + " " + text[position:]
        else:
            updated_text = citation + "\n\n" + text

        return AddCitationResponse(
            updated_text=updated_text,
            citation_added=citation,
        )

    except Exception as e:
        print(f"Error adding citation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def generate_citation_string(paper: dict) -> str:
    """Generate a formatted citation string"""
    title = paper.get("title", "")
    authors = paper.get("authors", [])
    year = paper.get("year", "")
    journal = paper.get("journal", "")
    doi = paper.get("doi", "")

    authors_str = ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")
    citation = f"({authors_str}, {year})"

    return citation


@router.get("/history")
async def get_boost_history(token: str = None):
    """Get user's citation boost history"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        response = (
            supabase.table("citation_boosts")
            .select("*")
            .eq("user_id", user.get("id"))
            .order("created_at", desc=True)
            .execute()
        )

        return {"boosts": response.data if response.data else []}

    except Exception as e:
        print(f"Error fetching boost history: {e}")
        return {"boosts": []}


@router.get("/{boost_id}")
async def get_boost_details(boost_id: str, token: str = None):
    """Get details of a specific citation boost"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        boost_response = (
            supabase.table("citation_boosts")
            .select("*")
            .eq("id", boost_id)
            .single()
            .execute()
        )

        if not boost_response.data:
            raise HTTPException(status_code=404, detail="Boost not found")

        boost = boost_response.data

        if boost.get("user_id") != user.get("id"):
            raise HTTPException(status_code=403, detail="Access denied")

        citations_response = (
            supabase.table("boosted_citations")
            .select("*")
            .eq("boost_id", boost_id)
            .execute()
        )

        return {
            "boost": boost,
            "citations": citations_response.data if citations_response.data else [],
        }

    except Exception as e:
        print(f"Error fetching boost details: {e}")
        raise HTTPException(status_code=500, detail=str(e))
