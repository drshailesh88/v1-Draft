from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from core.database import supabase, get_user_from_token

router = APIRouter()


class LiteratureSearchRequest(BaseModel):
    query: str
    sources: List[str] = ["pubmed", "arxiv", "scholar", "semantic_scholar"]
    max_results: int = 20
    year_start: Optional[int] = None
    year_end: Optional[int] = None


class Paper(BaseModel):
    title: str
    authors: List[str]
    year: str
    journal: Optional[str]
    doi: Optional[str]
    abstract: Optional[str]
    source: str
    url: Optional[str]


class LiteratureSearchResponse(BaseModel):
    papers: List[Paper]
    total: int


@router.post("/search", response_model=LiteratureSearchResponse)
async def search_literature(request: LiteratureSearchRequest, token: str = None):
    """Search across multiple academic databases"""
    # Get user from token
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    all_papers = []

    # Search each source
    for source in request.sources:
        papers = await search_source(
            source=source,
            query=request.query,
            max_results=request.max_results,
            year_start=request.year_start,
            year_end=request.year_end,
        )
        all_papers.extend(papers)

    # Deduplicate results
    deduplicated = deduplicate_papers(all_papers)

    # Save search history
    await save_search_history(user["id"], request.query, request.sources, deduplicated)

    return LiteratureSearchResponse(
        papers=deduplicated[: request.max_results], total=len(deduplicated)
    )


async def search_source(
    source: str,
    query: str,
    max_results: int,
    year_start: Optional[int],
    year_end: Optional[int],
) -> List[Paper]:
    """Search specific academic database"""
    # TODO: Integrate paper-search-mcp and pubmed-mcp-server
    # Placeholder implementation

    if source == "pubmed":
        return await search_pubmed(query, max_results)
    elif source == "arxiv":
        return await search_arxiv(query, max_results)
    elif source == "scholar":
        return await search_scholar(query, max_results)
    elif source == "semantic_scholar":
        return await search_semantic_scholar(query, max_results)
    else:
        return []


async def search_pubmed(query: str, max_results: int) -> List[Paper]:
    """Search PubMed database"""
    # TODO: Implement pubmed-mcp-server integration
    return []


async def search_arxiv(query: str, max_results: int) -> List[Paper]:
    """Search arXiv database"""
    # TODO: Implement paper-search-mcp integration
    return []


async def search_scholar(query: str, max_results: int) -> List[Paper]:
    """Search Google Scholar"""
    # TODO: Implement paper-search-mcp integration
    return []


async def search_semantic_scholar(query: str, max_results: int) -> List[Paper]:
    """Search Semantic Scholar"""
    # TODO: Implement paper-search-mcp integration
    return []


def deduplicate_papers(papers: List[Paper]) -> List[Paper]:
    """Deduplicate papers by DOI and title"""
    seen = set()
    deduplicated = []

    for paper in papers:
        # Create unique key
        key = f"{paper.doi or ''}_{paper.title.lower()}"

        if key not in seen:
            seen.add(key)
            deduplicated.append(paper)

    return deduplicated


async def save_search_history(
    user_id: str, query: str, sources: List[str], papers: List[Paper]
):
    """Save search to database"""
    try:
        search_data = {
            "user_id": user_id,
            "query": query,
            "sources": sources,
            "results": [paper.dict() for paper in papers],
        }
        supabase.table("literature_searches").insert(search_data).execute()
    except Exception as e:
        print(f"Error saving search history: {e}")


@router.post("/save-paper")
async def save_paper(paper: Paper, token: str = None):
    """Save paper to user's library"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    paper_data = {
        "user_id": user["id"],
        "title": paper.title,
        "authors": paper.authors,
        "year": paper.year,
        "journal": paper.journal,
        "doi": paper.doi,
        "abstract": paper.abstract,
        "source": paper.source,
        "metadata": {"url": paper.url},
    }

    supabase.table("saved_papers").insert(paper_data).execute()

    return {"status": "success"}


@router.get("/saved-papers")
async def get_saved_papers(token: str = None):
    """Get user's saved papers"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    response = (
        supabase.table("saved_papers")
        .select("*")
        .eq("user_id", user["id"])
        .order("created_at", desc=True)
        .execute()
    )

    return {"papers": response.data if response.data else []}


@router.get("/export/{format}")
async def export_citations(format: str, paper_ids: List[str], token: str = None):
    """Export papers in specified format"""
    # TODO: Implement citation export (BibTeX, RIS, APA, MLA)
    return {"status": "not_implemented"}
