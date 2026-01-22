"""
Literature Search API - Agent B
Searches across multiple academic databases: PubMed, arXiv, Semantic Scholar
"""

import os
import asyncio
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
import httpx

# PubMed imports
from Bio import Entrez, Medline

# arXiv imports
import arxiv

from core.database import supabase

router = APIRouter()

# Configure Entrez for PubMed
Entrez.email = os.getenv("PUBMED_EMAIL", "researcher@scispace.com")


# === Pydantic Models ===


class Paper(BaseModel):
    """Paper model for search results"""

    title: str
    authors: List[str]
    year: str
    journal: Optional[str] = None
    doi: Optional[str] = None
    abstract: Optional[str] = None
    source: str
    url: Optional[str] = None
    pmid: Optional[str] = None
    arxiv_id: Optional[str] = None
    citation_count: Optional[int] = None


class LiteratureSearchRequest(BaseModel):
    """Request model for literature search"""

    query: str = Field(..., min_length=1, description="Search query")
    sources: List[str] = Field(
        default=["pubmed", "arxiv", "semantic_scholar"],
        description="Sources to search",
    )
    max_results: int = Field(default=20, ge=1, le=100)
    year_start: Optional[int] = Field(default=None, ge=1900, le=2100)
    year_end: Optional[int] = Field(default=None, ge=1900, le=2100)


class LiteratureSearchResponse(BaseModel):
    """Response model for literature search"""

    papers: List[Paper]
    total: int
    sources_searched: List[str]


class CitationExportRequest(BaseModel):
    """Request model for citation export"""

    paper_ids: List[str] = Field(default=[], description="IDs of saved papers to export")
    papers: List[Paper] = Field(default=[], description="Papers to export directly")
    format: str = Field(default="bibtex", description="Export format")


# === Search Implementations ===


async def search_pubmed(
    query: str,
    max_results: int = 20,
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
) -> List[Paper]:
    """Search PubMed database using Entrez API"""
    try:
        # Build date filter
        date_filter = ""
        if year_start and year_end:
            date_filter = f" AND {year_start}:{year_end}[dp]"
        elif year_start:
            date_filter = f" AND {year_start}:3000[dp]"
        elif year_end:
            date_filter = f" AND 1900:{year_end}[dp]"

        search_query = f"{query}{date_filter}"

        # Run in thread pool since Entrez is synchronous
        loop = asyncio.get_event_loop()

        def _search():
            # Search for IDs
            handle = Entrez.esearch(
                db="pubmed", term=search_query, retmax=max_results, sort="relevance"
            )
            record = Entrez.read(handle)
            handle.close()
            return record.get("IdList", [])

        ids = await loop.run_in_executor(None, _search)

        if not ids:
            return []

        def _fetch():
            # Fetch paper details
            handle = Entrez.efetch(
                db="pubmed", id=",".join(ids), rettype="medline", retmode="text"
            )
            records = list(Medline.parse(handle))
            handle.close()
            return records

        records = await loop.run_in_executor(None, _fetch)

        papers = []
        for record in records:
            # Extract year from date
            pub_date = record.get("DP", "")
            year = pub_date[:4] if pub_date else ""

            # Extract DOI
            doi = None
            aid = record.get("AID", [])
            for identifier in aid:
                if "[doi]" in identifier:
                    doi = identifier.replace(" [doi]", "")
                    break

            paper = Paper(
                title=record.get("TI", "No title"),
                authors=record.get("AU", []),
                year=year,
                journal=record.get("JT", record.get("TA", "")),
                doi=doi,
                abstract=record.get("AB", ""),
                source="pubmed",
                url=f"https://pubmed.ncbi.nlm.nih.gov/{record.get('PMID', '')}/",
                pmid=record.get("PMID", ""),
            )
            papers.append(paper)

        return papers

    except Exception as e:
        print(f"PubMed search error: {e}")
        return []


async def search_arxiv(
    query: str,
    max_results: int = 20,
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
) -> List[Paper]:
    """Search arXiv database"""
    try:
        # Build search
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )

        # Run in thread pool since arxiv library is synchronous
        loop = asyncio.get_event_loop()

        def _search():
            client = arxiv.Client()
            return list(client.results(search))

        results = await loop.run_in_executor(None, _search)

        papers = []
        for result in results:
            pub_year = result.published.year if result.published else None

            # Apply year filter
            if year_start and pub_year and pub_year < year_start:
                continue
            if year_end and pub_year and pub_year > year_end:
                continue

            arxiv_id = result.entry_id.split("/")[-1] if result.entry_id else ""

            paper = Paper(
                title=result.title,
                authors=[author.name for author in result.authors],
                year=str(pub_year) if pub_year else "",
                journal="arXiv",
                doi=result.doi if hasattr(result, "doi") else None,
                abstract=result.summary,
                source="arxiv",
                url=result.entry_id,
                arxiv_id=arxiv_id,
            )
            papers.append(paper)

        return papers

    except Exception as e:
        print(f"arXiv search error: {e}")
        return []


async def search_semantic_scholar(
    query: str,
    max_results: int = 20,
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
) -> List[Paper]:
    """Search Semantic Scholar API"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Build URL with parameters
            params = {
                "query": query,
                "limit": max_results,
                "fields": "title,authors,year,venue,externalIds,abstract,citationCount,url",
            }

            # Add year filter
            if year_start and year_end:
                params["year"] = f"{year_start}-{year_end}"
            elif year_start:
                params["year"] = f"{year_start}-"
            elif year_end:
                params["year"] = f"-{year_end}"

            response = await client.get(
                "https://api.semanticscholar.org/graph/v1/paper/search",
                params=params,
                headers={"Accept": "application/json"},
            )

            if response.status_code != 200:
                print(f"Semantic Scholar API error: {response.status_code}")
                return []

            data = response.json()
            results = data.get("data", [])

            papers = []
            for result in results:
                # Extract DOI from externalIds
                external_ids = result.get("externalIds", {}) or {}
                doi = external_ids.get("DOI")

                # Get authors
                authors = [
                    author.get("name", "") for author in result.get("authors", [])
                ]

                paper = Paper(
                    title=result.get("title", "No title"),
                    authors=authors,
                    year=str(result.get("year", "")),
                    journal=result.get("venue", ""),
                    doi=doi,
                    abstract=result.get("abstract", ""),
                    source="semantic_scholar",
                    url=result.get("url", ""),
                    citation_count=result.get("citationCount"),
                )
                papers.append(paper)

            return papers

    except Exception as e:
        print(f"Semantic Scholar search error: {e}")
        return []


def deduplicate_papers(papers: List[Paper]) -> List[Paper]:
    """Deduplicate papers by DOI and normalized title"""
    seen_dois = set()
    seen_titles = set()
    deduplicated = []

    for paper in papers:
        # Check DOI first (most reliable)
        if paper.doi:
            doi_lower = paper.doi.lower()
            if doi_lower in seen_dois:
                continue
            seen_dois.add(doi_lower)

        # Check normalized title
        title_normalized = paper.title.lower().strip()
        # Remove common punctuation for comparison
        title_key = "".join(c for c in title_normalized if c.isalnum() or c.isspace())

        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)

        deduplicated.append(paper)

    return deduplicated


# === Citation Export Functions ===


def generate_bibtex(paper: Paper) -> str:
    """Generate BibTeX citation"""
    # Create citation key
    first_author = paper.authors[0].split()[-1] if paper.authors else "Unknown"
    year = paper.year or "XXXX"
    key = f"{first_author}{year}"

    # Determine entry type
    if paper.source == "arxiv":
        entry_type = "article"
    else:
        entry_type = "article"

    lines = [f"@{entry_type}{{{key},"]
    lines.append(f'  author = {{{" and ".join(paper.authors)}}},')
    lines.append(f"  title = {{{paper.title}}},")

    if paper.journal:
        lines.append(f"  journal = {{{paper.journal}}},")
    if paper.year:
        lines.append(f"  year = {{{paper.year}}},")
    if paper.doi:
        lines.append(f"  doi = {{{paper.doi}}},")
    if paper.url:
        lines.append(f"  url = {{{paper.url}}},")
    if paper.pmid:
        lines.append(f"  pmid = {{{paper.pmid}}},")
    if paper.arxiv_id:
        lines.append(f"  eprint = {{{paper.arxiv_id}}},")
        lines.append("  archiveprefix = {arXiv},")

    lines.append("}")
    return "\n".join(lines)


def generate_ris(paper: Paper) -> str:
    """Generate RIS citation"""
    lines = ["TY  - JOUR"]
    lines.append(f"TI  - {paper.title}")

    for author in paper.authors:
        lines.append(f"AU  - {author}")

    if paper.year:
        lines.append(f"PY  - {paper.year}")
    if paper.journal:
        lines.append(f"JO  - {paper.journal}")
    if paper.doi:
        lines.append(f"DO  - {paper.doi}")
    if paper.url:
        lines.append(f"UR  - {paper.url}")
    if paper.abstract:
        lines.append(f"AB  - {paper.abstract}")

    lines.append("ER  - ")
    return "\n".join(lines)


def generate_apa(paper: Paper) -> str:
    """Generate APA 7th edition citation"""
    # Format authors
    if len(paper.authors) == 0:
        authors_str = "Unknown"
    elif len(paper.authors) == 1:
        parts = paper.authors[0].split()
        if len(parts) >= 2:
            authors_str = f"{parts[-1]}, {parts[0][0]}."
        else:
            authors_str = paper.authors[0]
    elif len(paper.authors) == 2:
        formatted = []
        for author in paper.authors:
            parts = author.split()
            if len(parts) >= 2:
                formatted.append(f"{parts[-1]}, {parts[0][0]}.")
            else:
                formatted.append(author)
        authors_str = " & ".join(formatted)
    else:
        formatted = []
        for i, author in enumerate(paper.authors[:19]):  # APA shows up to 20 authors
            parts = author.split()
            if len(parts) >= 2:
                formatted.append(f"{parts[-1]}, {parts[0][0]}.")
            else:
                formatted.append(author)

        if len(paper.authors) > 20:
            authors_str = ", ".join(formatted[:19]) + ", ... " + formatted[-1]
        else:
            authors_str = ", ".join(formatted[:-1]) + ", & " + formatted[-1]

    year = f"({paper.year})" if paper.year else "(n.d.)"
    title = paper.title

    journal = paper.journal or ""
    doi_str = f"https://doi.org/{paper.doi}" if paper.doi else ""

    citation = f"{authors_str} {year}. {title}."
    if journal:
        citation += f" {journal}."
    if doi_str:
        citation += f" {doi_str}"

    return citation


def generate_mla(paper: Paper) -> str:
    """Generate MLA 9th edition citation"""
    # Format authors
    if len(paper.authors) == 0:
        authors_str = "Unknown"
    elif len(paper.authors) == 1:
        parts = paper.authors[0].split()
        if len(parts) >= 2:
            authors_str = f"{parts[-1]}, {' '.join(parts[:-1])}"
        else:
            authors_str = paper.authors[0]
    elif len(paper.authors) == 2:
        first = paper.authors[0].split()
        if len(first) >= 2:
            first_str = f"{first[-1]}, {' '.join(first[:-1])}"
        else:
            first_str = paper.authors[0]
        authors_str = f"{first_str}, and {paper.authors[1]}"
    else:
        first = paper.authors[0].split()
        if len(first) >= 2:
            first_str = f"{first[-1]}, {' '.join(first[:-1])}"
        else:
            first_str = paper.authors[0]
        authors_str = f"{first_str}, et al."

    title = f'"{paper.title}."'
    journal = f"*{paper.journal}*," if paper.journal else ""
    year = f"{paper.year}," if paper.year else ""
    doi_str = f"doi:{paper.doi}." if paper.doi else ""

    parts = [p for p in [authors_str, title, journal, year, doi_str] if p]
    return " ".join(parts)


# === API Endpoints ===


@router.post("/search", response_model=LiteratureSearchResponse)
async def search_literature(request: LiteratureSearchRequest):
    """
    Search across multiple academic databases.

    Supported sources: pubmed, arxiv, semantic_scholar
    """
    all_papers = []
    searched_sources = []

    # Search each source concurrently
    tasks = []

    if "pubmed" in request.sources:
        tasks.append(
            (
                "pubmed",
                search_pubmed(
                    request.query,
                    request.max_results,
                    request.year_start,
                    request.year_end,
                ),
            )
        )

    if "arxiv" in request.sources:
        tasks.append(
            (
                "arxiv",
                search_arxiv(
                    request.query,
                    request.max_results,
                    request.year_start,
                    request.year_end,
                ),
            )
        )

    if "semantic_scholar" in request.sources:
        tasks.append(
            (
                "semantic_scholar",
                search_semantic_scholar(
                    request.query,
                    request.max_results,
                    request.year_start,
                    request.year_end,
                ),
            )
        )

    # Execute all searches concurrently
    if tasks:
        results = await asyncio.gather(*[task[1] for task in tasks])

        for i, (source_name, _) in enumerate(tasks):
            searched_sources.append(source_name)
            all_papers.extend(results[i])

    # Deduplicate results
    deduplicated = deduplicate_papers(all_papers)

    # Limit to max_results
    final_papers = deduplicated[: request.max_results]

    return LiteratureSearchResponse(
        papers=final_papers, total=len(deduplicated), sources_searched=searched_sources
    )


@router.post("/save-paper")
async def save_paper(paper: Paper, user_id: Optional[str] = None):
    """Save paper to user's library"""
    if not user_id:
        # For development, use a default user ID
        user_id = "dev-user"

    try:
        paper_data = {
            "user_id": user_id,
            "title": paper.title,
            "authors": paper.authors,
            "year": paper.year,
            "journal": paper.journal,
            "doi": paper.doi,
            "abstract": paper.abstract,
            "source": paper.source,
            "metadata": {
                "url": paper.url,
                "pmid": paper.pmid,
                "arxiv_id": paper.arxiv_id,
                "citation_count": paper.citation_count,
            },
        }

        result = supabase.table("saved_papers").insert(paper_data).execute()

        return {"status": "success", "paper_id": result.data[0]["id"] if result.data else None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save paper: {str(e)}")


@router.get("/saved-papers")
async def get_saved_papers(user_id: Optional[str] = None, limit: int = 50):
    """Get user's saved papers"""
    if not user_id:
        user_id = "dev-user"

    try:
        response = (
            supabase.table("saved_papers")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        return {"papers": response.data if response.data else [], "total": len(response.data) if response.data else 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get papers: {str(e)}")


@router.post("/export")
async def export_citations(request: CitationExportRequest):
    """
    Export citations in specified format.

    Supported formats: bibtex, ris, apa, mla
    """
    papers_to_export = request.papers

    # If paper_ids provided, fetch from database
    if request.paper_ids and not papers_to_export:
        try:
            response = (
                supabase.table("saved_papers")
                .select("*")
                .in_("id", request.paper_ids)
                .execute()
            )

            for row in response.data or []:
                paper = Paper(
                    title=row.get("title", ""),
                    authors=row.get("authors", []),
                    year=row.get("year", ""),
                    journal=row.get("journal"),
                    doi=row.get("doi"),
                    abstract=row.get("abstract"),
                    source=row.get("source", ""),
                    url=row.get("metadata", {}).get("url") if row.get("metadata") else None,
                    pmid=row.get("metadata", {}).get("pmid") if row.get("metadata") else None,
                    arxiv_id=row.get("metadata", {}).get("arxiv_id") if row.get("metadata") else None,
                )
                papers_to_export.append(paper)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch papers: {str(e)}")

    if not papers_to_export:
        raise HTTPException(status_code=400, detail="No papers to export")

    # Generate citations
    format_lower = request.format.lower()
    citations = []

    for paper in papers_to_export:
        if format_lower == "bibtex":
            citations.append(generate_bibtex(paper))
        elif format_lower == "ris":
            citations.append(generate_ris(paper))
        elif format_lower == "apa":
            citations.append(generate_apa(paper))
        elif format_lower == "mla":
            citations.append(generate_mla(paper))
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format: {request.format}. Supported: bibtex, ris, apa, mla",
            )

    # Join citations
    separator = "\n\n" if format_lower in ["bibtex", "ris"] else "\n"
    output = separator.join(citations)

    return {
        "format": request.format,
        "count": len(citations),
        "citations": output,
    }


@router.get("/search-history")
async def get_search_history(user_id: Optional[str] = None, limit: int = 20):
    """Get user's search history"""
    if not user_id:
        user_id = "dev-user"

    try:
        response = (
            supabase.table("literature_searches")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        return {"searches": response.data if response.data else []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")
