from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from core.database import supabase, get_user_from_token

router = APIRouter()

class CitationMetadata(BaseModel):
    title: str
    authors: List[str]
    year: str
    journal: str
    volume: str
    issue: str
    pages: str
    doi: str

class CitationRequest(BaseModel):
    metadata: CitationMetadata
    style: str = "apa"

class CitationResponse(BaseModel):
    formatted: str
    bibtex: str

@router.post("/generate", response_model=CitationResponse)
async def generate_citation(
    request: CitationRequest,
    token: str = None
):
    """Generate citation in specified style"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Generate formatted citation
    formatted = format_citation(request.metadata, request.style)
    
    # Generate BibTeX
    bibtex = generate_bibtex(request.metadata)
    
    # Save to database
    await save_citation(user['id'], request.metadata, request.style, formatted, bibtex)
    
    return CitationResponse(formatted=formatted, bibtex=bibtex)

@router.post("/batch-generate")
async def batch_generate_citations(
    papers: List[CitationMetadata],
    style: str = "apa",
    token: str = None
):
    """Generate multiple citations"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    results = []
    for paper in papers:
        formatted = format_citation(paper, style)
        bibtex = generate_bibtex(paper)
        results.append({"formatted": formatted, "bibtex": bibtex})
        
        # Save each citation
        await save_citation(user['id'], paper, style, formatted, bibtex)
    
    return {"citations": results}

def format_citation(metadata: CitationMetadata, style: str) -> str:
    """Format citation in specified style"""
    # TODO: Implement full CSL support
    # Placeholder implementation for common styles
    
    authors_text = ", ".join(metadata.authors[:3])
    if len(metadata.authors) > 3:
        authors_text += ", et al."
    
    if style.lower() == "apa":
        return f"{authors_text} ({metadata.year}). {metadata.title}. {metadata.journal}, {metadata.volume}({metadata.issue}), {metadata.pages}. https://doi.org/{metadata.doi}"
    elif style.lower() == "mla":
        return f"{authors_text}. "{metadata.title}." {metadata.journal}, vol. {metadata.volume}, no. {metadata.issue}, {metadata.pages}, {metadata.year}."
    elif style.lower() == "chicago":
        return f"{authors_text}. {metadata.year}. \"{metadata.title}.\" {metadata.journal} {metadata.volume}, no. {metadata.issue}: {metadata.pages}."
    else:
        # Default to APA
        return format_citation(metadata, "apa")

def generate_bibtex(metadata: CitationMetadata) -> str:
    """Generate BibTeX citation"""
    first_author = metadata.authors[0].split()[-1] if metadata.authors else "Unknown"
    cite_key = f"{first_author}{metadata.year}"
    
    bibtex = f"@article{{{cite_key},\n"
    bibtex += f"  author = {{{', '.join(metadata.authors)}}},\n"
    bibtex += f"  title = {{{metadata.title}}},\n"
    bibtex += f"  journal = {{{metadata.journal}}},\n"
    bibtex += f"  year = {{{metadata.year}}},\n"
    bibtex += f"  volume = {{{metadata.volume}}},\n"
    bibtex += f"  number = {{{metadata.issue}}},\n"
    bibtex += f"  pages = {{{metadata.pages}}},\n"
    bibtex += f"  doi = {{{metadata.doi}}}\n"
    bibtex += "}"
    
    return bibtex

async def save_citation(user_id: str, metadata: CitationMetadata, style: str, formatted: str, bibtex: str):
    """Save citation to database"""
    try:
        citation_data = {
            'user_id': user_id,
            'metadata': metadata.dict(),
            'style': style,
            'formatted': formatted
        }
        supabase.table('citations').insert(citation_data).execute()
    except Exception as e:
        print(f"Error saving citation: {e}")
