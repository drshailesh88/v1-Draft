from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from core.database import supabase, get_user_from_token
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
import os

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
async def search_literature(
    request: LiteratureSearchRequest, token: Optional[str] = None
):
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
    """Search PubMed database using pubmed-mcp-server"""
    try:
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@execution-developers/pubmed-mcp-server"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                result = await session.call_tool(
                    "search_pubmed", {"query": query, "max_results": max_results}
                )

                papers = []
                for item in result.content:
                    if hasattr(item, "text"):
                        import json

                        data = json.loads(item.text)
                        if isinstance(data, list):
                            for paper in data:
                                authors = []
                                if isinstance(paper.get("authors"), list):
                                    authors = [
                                        a.get("name", "")
                                        for a in paper.get("authors", [])[:10]
                                    ]

                                papers.append(
                                    Paper(
                                        title=paper.get("title", ""),
                                        authors=authors,
                                        year=str(paper.get("year", "")),
                                        journal=paper.get("journal", ""),
                                        doi=paper.get("doi", ""),
                                        abstract=paper.get("abstract", ""),
                                        source="pubmed",
                                        url=paper.get(
                                            "url",
                                            f"https://pubmed.ncbi.nlm.nih.gov/{paper.get('pmid', '')}",
                                        ),
                                    )
                                )

                return papers

    except ConnectionError as e:
        print(f"PubMed MCP connection error: {e}")
        return []
    except TimeoutError as e:
        print(f"PubMed MCP timeout error: {e}")
        return []
    except Exception as e:
        print(f"PubMed MCP search error: {e}")
        return []


async def search_arxiv(query: str, max_results: int) -> List[Paper]:
    """Search arXiv database using paper-search-mcp"""
    try:
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@paper-search-mcp/paper-search-mcp"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                result = await session.call_tool(
                    "search_papers",
                    {"query": query, "source": "arxiv", "max_results": max_results},
                )

                papers = []
                for item in result.content:
                    if hasattr(item, "text"):
                        import json

                        data = json.loads(item.text)
                        if isinstance(data, list):
                            for paper in data:
                                authors = []
                                if isinstance(paper.get("authors"), list):
                                    authors = [
                                        a.get("name", "")
                                        for a in paper.get("authors", [])[:10]
                                    ]
                                elif isinstance(paper.get("authors"), str):
                                    authors = paper.get("authors", "").split(",")[:10]

                                papers.append(
                                    Paper(
                                        title=paper.get("title", ""),
                                        authors=authors,
                                        year=str(paper.get("year", "")),
                                        journal="arXiv",
                                        doi=paper.get("doi", ""),
                                        abstract=paper.get("abstract", ""),
                                        source="arxiv",
                                        url=paper.get("url", ""),
                                    )
                                )

                return papers

    except ConnectionError as e:
        print(f"arXiv MCP connection error: {e}")
        return []
    except TimeoutError as e:
        print(f"arXiv MCP timeout error: {e}")
        return []
    except Exception as e:
        print(f"arXiv MCP search error: {e}")
        return []


async def search_scholar(query: str, max_results: int) -> List[Paper]:
    """Search Google Scholar using paper-search-mcp"""
    try:
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@paper-search-mcp/paper-search-mcp"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                result = await session.call_tool(
                    "search_papers",
                    {
                        "query": query,
                        "source": "google_scholar",
                        "max_results": max_results,
                    },
                )

                papers = []
                for item in result.content:
                    if hasattr(item, "text"):
                        import json

                        data = json.loads(item.text)
                        if isinstance(data, list):
                            for paper in data:
                                authors = []
                                if isinstance(paper.get("authors"), list):
                                    authors = [
                                        a.get("name", "")
                                        for a in paper.get("authors", [])[:10]
                                    ]
                                elif isinstance(paper.get("authors"), str):
                                    authors = paper.get("authors", "").split(",")[:10]

                                journal_name = ""
                                if isinstance(paper.get("journal"), dict):
                                    journal_name = paper.get("journal", {}).get(
                                        "name", ""
                                    )
                                elif isinstance(paper.get("journal"), str):
                                    journal_name = paper.get("journal", "")

                                papers.append(
                                    Paper(
                                        title=paper.get("title", ""),
                                        authors=authors,
                                        year=str(paper.get("year", "")),
                                        journal=journal_name,
                                        doi=paper.get("doi", ""),
                                        abstract=paper.get("abstract", ""),
                                        source="google_scholar",
                                        url=paper.get("url", ""),
                                    )
                                )

                return papers

    except ConnectionError as e:
        print(f"Google Scholar MCP connection error: {e}")
        return []
    except TimeoutError as e:
        print(f"Google Scholar MCP timeout error: {e}")
        return []
    except Exception as e:
        print(f"Google Scholar MCP search error: {e}")
        return []


async def search_semantic_scholar(query: str, max_results: int) -> List[Paper]:
    """Search Semantic Scholar using paper-search-mcp"""
    try:
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@paper-search-mcp/paper-search-mcp"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                result = await session.call_tool(
                    "search_papers",
                    {
                        "query": query,
                        "source": "semantic_scholar",
                        "max_results": max_results,
                    },
                )

                papers = []
                for item in result.content:
                    if hasattr(item, "text"):
                        import json

                        data = json.loads(item.text)
                        if isinstance(data, list):
                            for paper in data:
                                authors = []
                                if isinstance(paper.get("authors"), list):
                                    authors = [
                                        a.get("name", "")
                                        for a in paper.get("authors", [])[:10]
                                    ]
                                elif isinstance(paper.get("authors"), str):
                                    authors = paper.get("authors", "").split(",")[:10]

                                journal_name = ""
                                if isinstance(paper.get("journal"), dict):
                                    journal_name = paper.get("journal", {}).get(
                                        "name", ""
                                    )
                                elif isinstance(paper.get("journal"), str):
                                    journal_name = paper.get("journal", "")

                                papers.append(
                                    Paper(
                                        title=paper.get("title", ""),
                                        authors=authors,
                                        year=str(paper.get("year", "")),
                                        journal=journal_name,
                                        doi=paper.get("doi", ""),
                                        abstract=paper.get("abstract", ""),
                                        source="semantic_scholar",
                                        url=paper.get("url", ""),
                                    )
                                )

                return papers

    except ConnectionError as e:
        print(f"Semantic Scholar MCP connection error: {e}")
        return []
    except TimeoutError as e:
        print(f"Semantic Scholar MCP timeout error: {e}")
        return []
    except Exception as e:
        print(f"Semantic Scholar MCP search error: {e}")
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
            "results": [paper.model_dump() for paper in papers],
        }
        supabase.table("literature_searches").insert(search_data).execute()
    except Exception as e:
        print(f"Error saving search history: {e}")


@router.post("/save-paper")
async def save_paper(paper: Paper, token: Optional[str] = None):
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
async def get_saved_papers(token: Optional[str] = None):
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
async def export_citations(
    format: str, paper_ids: List[str], token: Optional[str] = None
):
    """Export papers in specified format"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        response = (
            supabase.table("saved_papers")
            .select("*")
            .eq("user_id", user["id"])
            .in_("id", paper_ids)
            .execute()
        )

        papers = response.data if response.data else []

        if format.lower() == "bibtex":
            return {"format": "bibtex", "content": format_bibtex(papers)}
        elif format.lower() == "ris":
            return {"format": "ris", "content": format_ris(papers)}
        elif format.lower() == "apa":
            return {"format": "apa", "content": format_apa(papers)}
        elif format.lower() == "mla":
            return {"format": "mla", "content": format_mla(papers)}
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")

    except Exception as e:
        print(f"Error exporting citations: {e}")
        raise HTTPException(status_code=500, detail="Failed to export citations")


def format_bibtex(papers: List) -> str:
    """Format papers in BibTeX format"""
    bibtex = []
    for paper in papers:
        key = paper["title"].lower().replace(" ", "_")[:20]
        authors = " and ".join(paper["authors"])
        bibtex.append(
            f"@article{{{key},\n"
            f'  title = "{{{paper["title"]}}}",\n'
            f'  author = "{{{authors}}}",\n'
            f'  journal = "{{{paper["journal"]}}}",\n'
            f'  year = "{{{paper["year"]}}}",\n'
            f'  doi = "{{{paper["doi"]}}}"\n'
            f"}}\n"
        )
    return "\n".join(bibtex)


def format_ris(papers: List) -> str:
    """Format papers in RIS format"""
    ris = []
    for paper in papers:
        ris.append(f"TY - JOUR\n")
        ris.append(f"TI - {paper['title']}\n")
        for author in paper["authors"]:
            ris.append(f"AU - {author}\n")
        ris.append(f"JO - {paper['journal']}\n")
        ris.append(f"PY - {paper['year']}\n")
        ris.append(f"DO - {paper['doi']}\n")
        ris.append(f"ER - \n")
    return "".join(ris)


def format_apa(papers: List) -> str:
    """Format papers in APA style"""
    citations = []
    for paper in papers:
        authors = ", ".join(paper["authors"])
        citations.append(
            f"{authors} ({paper['year']}). {paper['title']}. {paper['journal']}. https://doi.org/{paper['doi']}"
        )
    return "\n".join(citations)


def format_mla(papers: List) -> str:
    """Format papers in MLA style"""
    citations = []
    for paper in papers:
        authors = paper["authors"][0] if paper["authors"] else "Unknown"
        citations.append(
            f'{authors}. "{paper["title"]}". {paper["journal"]}, {paper["year"]}, doi:{paper["doi"]}.'
        )
    return "\n".join(citations)
