from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from core.database import supabase, get_user_from_token
import requests
import json

router = APIRouter()


class CreateReviewRequest(BaseModel):
    research_question: str
    databases: List[str]
    search_terms: str
    inclusion_criteria: str
    exclusion_criteria: str


class ScreeningRecordRequest(BaseModel):
    review_id: str
    paper_id: str
    title: str
    authors: List[str]
    year: str
    doi: str
    status: str
    reason: str
    stage: str


class CreateReviewResponse(BaseModel):
    id: str
    research_question: str
    databases: List[str]
    search_terms: str
    inclusion_criteria: str
    exclusion_criteria: str
    created_at: str
    screening_counts: Dict[str, int]


@router.post("/create-review", response_model=CreateReviewResponse)
async def create_review(request: CreateReviewRequest, token: str = None):
    """Create a new systematic review"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    review_data = {
        "user_id": user["id"],
        "research_question": request.research_question,
        "databases": request.databases,
        "search_terms": request.search_terms,
        "inclusion_criteria": request.inclusion_criteria,
        "exclusion_criteria": request.exclusion_criteria,
        "screening_counts": {
            "identification": 0,
            "screening": 0,
            "eligibility": 0,
            "included": 0,
            "excluded": 0,
        },
    }

    try:
        response = supabase.table("systematic_reviews").insert(review_data).execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create review")

        review = response.data[0]

        return CreateReviewResponse(
            id=review["id"],
            research_question=review["research_question"],
            databases=review["databases"],
            search_terms=review["search_terms"],
            inclusion_criteria=review["inclusion_criteria"],
            exclusion_criteria=review["exclusion_criteria"],
            created_at=review["created_at"],
            screening_counts=review["screening_counts"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/review/{review_id}")
async def get_review(review_id: str, token: str = None):
    """Get full systematic review details"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        response = (
            supabase.table("systematic_reviews")
            .select("*")
            .eq("id", review_id)
            .eq("user_id", user["id"])
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Review not found")

        review = response.data[0]

        screening_records_response = (
            supabase.table("screening_records")
            .select("*")
            .eq("review_id", review_id)
            .execute()
        )

        return {
            "review": review,
            "screening_records": screening_records_response.data or [],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user-reviews")
async def get_user_reviews(token: str = None):
    """Get all systematic reviews for user"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        response = (
            supabase.table("systematic_reviews")
            .select("*")
            .eq("user_id", user["id"])
            .order("created_at", desc=True)
            .execute()
        )

        return {"reviews": response.data or []}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/record-screening")
async def record_screening(request: ScreeningRecordRequest, token: str = None):
    """Record screening decision for a paper"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        record_data = {
            "review_id": request.review_id,
            "paper_id": request.paper_id,
            "title": request.title,
            "authors": request.authors,
            "year": request.year,
            "doi": request.doi,
            "status": request.status,
            "reason": request.reason,
            "stage": request.stage,
        }

        response = supabase.table("screening_records").insert(record_data).execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to record screening")

        screening_record = response.data[0]

        update_screening_counts(request.review_id, request.status, request.stage)

        return {"status": "success", "record": screening_record}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def update_screening_counts(review_id: str, status: str, stage: str):
    """Update screening counts for review"""
    try:
        review_response = (
            supabase.table("systematic_reviews")
            .select("*")
            .eq("id", review_id)
            .execute()
        )

        if not review_response.data:
            return

        review = review_response.data[0]
        counts = review.get("screening_counts", {})

        if stage == "identification":
            counts["identification"] = counts.get("identification", 0) + 1
        elif stage == "screening":
            counts["screening"] = counts.get("screening", 0) + 1
        elif stage == "eligibility":
            counts["eligibility"] = counts.get("eligibility", 0) + 1

        if status == "included":
            counts["included"] = counts.get("included", 0) + 1
        elif status == "excluded":
            counts["excluded"] = counts.get("excluded", 0) + 1

        supabase.table("systematic_reviews").update({"screening_counts": counts}).eq(
            "id", review_id
        ).execute()

    except Exception as e:
        print(f"Error updating screening counts: {e}")


@router.get("/search-literature")
async def search_literature_for_review(
    query: str,
    sources: str = "pubmed,arxiv,semantic_scholar",
    max_results: int = 50,
    token: str = None,
):
    """Search literature for systematic review using existing literature API"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        sources_list = sources.split(",")

        search_data = {
            "query": query,
            "sources": sources_list,
            "max_results": max_results,
        }

        response = await search_literature_internal(search_data)

        return {"papers": response["papers"], "total": response["total"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def search_literature_internal(search_data: dict):
    """Internal literature search using existing API logic"""
    from app.api.literature import search_source, deduplicate_papers, Paper

    all_papers = []

    for source in search_data["sources"]:
        papers = await search_source(
            source=source,
            query=search_data["query"],
            max_results=search_data["max_results"],
            year_start=None,
            year_end=None,
        )
        all_papers.extend(papers)

    deduplicated = deduplicate_papers(all_papers)

    return {"papers": [p.dict() for p in deduplicated], "total": len(deduplicated)}


@router.post("/generate-prisma-diagram")
async def generate_prisma_diagram(review_id: str, token: str = None):
    """Generate PRISMA flow diagram SVG"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        response = (
            supabase.table("systematic_reviews")
            .select("*")
            .eq("id", review_id)
            .eq("user_id", user["id"])
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Review not found")

        review = response.data[0]
        counts = review.get("screening_counts", {})

        svg = generate_prisma_svg(counts, review["research_question"])

        return {
            "svg": svg,
            "counts": counts,
            "research_question": review["research_question"],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def generate_prisma_svg(counts: dict, research_question: str):
    """Generate PRISMA flow diagram as SVG"""
    identified = counts.get("identification", 0)
    screened = counts.get("screening", 0)
    eligibility = counts.get("eligibility", 0)
    included = counts.get("included", 0)
    excluded = counts.get("excluded", 0)

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 900" width="600" height="900">
  <style>
    .box {{ fill: #f8fafc; stroke: #334155; stroke-width: 2; }}
    .arrow {{ stroke: #334155; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }}
    .text {{ font-family: Arial, sans-serif; font-size: 12px; fill: #1e293b; text-anchor: middle; }}
    .count {{ font-weight: bold; font-size: 14px; }}
    .title {{ font-size: 16px; font-weight: bold; }}
  </style>
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#334155" />
    </marker>
  </defs>
  
  <text x="300" y="30" class="text title">PRISMA Flow Diagram</text>
  <text x="300" y="50" class="text" font-size="11">{research_question[:60]}...</text>

  <rect x="200" y="80" width="200" height="50" class="box" />
  <text x="300" y="100" class="text">Identification</text>
  <text x="300" y="120" class="text count">Records identified</text>
  <text x="410" y="120" class="text count">{identified}</text>

  <line x1="300" y1="130" x2="300" y2="170" class="arrow" />

  <rect x="200" y="180" width="200" height="50" class="box" />
  <text x="300" y="200" class="text">Screening</text>
  <text x="300" y="220" class="text count">Records screened</text>
  <text x="410" y="220" class="text count">{screened}</text>

  <line x1="200" y1="230" x2="150" y2="280" class="arrow" />
  <line x1="300" y1="230" x2="300" y2="280" class="arrow" />

  <rect x="50" y="290" width="180" height="40" class="box" style="stroke: #ef4444;" />
  <text x="140" y="315" class="text">Records excluded</text>

  <rect x="200" y="290" width="200" height="50" class="box" />
  <text x="300" y="310" class="text">Full-text assessed</text>
  <text x="300" y="330" class="text count">for eligibility</text>
  <text x="410" y="330" class="text count">{eligibility}</text>

  <line x1="200" y1="340" x2="150" y2="390" class="arrow" />
  <line x1="300" y1="340" x2="300" y2="390" class="arrow" />

  <rect x="50" y="400" width="180" height="40" class="box" style="stroke: #ef4444;" />
  <text x="140" y="425" class="text">Full-text excluded</text>

  <rect x="200" y="400" width="200" height="50" class="box" />
  <text x="300" y="420" class="text">Studies included</text>
  <text x="300" y="440" class="text count">in review</text>
  <text x="410" y="440" class="text count">{included}</text>

  <line x1="300" y1="450" x2="300" y2="500" class="arrow" />

  <rect x="200" y="510" width="200" height="50" class="box" style="fill: #ecfdf5; stroke: #059669;" />
  <text x="300" y="530" class="text">Final Selection</text>
  <text x="300" y="550" class="text count">Included studies</text>
  <text x="410" y="550" class="text count">{included}</text>

  <text x="450" y="315" class="text" style="font-size: 10px;">Excluded: {excluded}</text>
  <text x="450" y="425" class="text" style="font-size: 10px;">with reasons</text>

  <rect x="50" y="600" width="500" height="150" class="box" style="fill: #fef3c7; stroke: #d97706;" />
  <text x="300" y="625" class="text title">Exclusion Reasons</text>
  <text x="70" y="650" class="text" text-anchor="start">• Study design not appropriate</text>
  <text x="70" y="670" class="text" text-anchor="start">• Population not relevant</text>
  <text x="70" y="690" class="text" text-anchor="start">• Intervention/exposure not relevant</text>
  <text x="70" y="710" class="text" text-anchor="start">• Outcomes not reported</text>
  <text x="70" y="730" class="text" text-anchor="start">• Duplicate publication</text>

  <rect x="50" y="770" width="500" height="100" class="box" style="fill: #e0f2fe; stroke: #0284c7;" />
  <text x="300" y="795" class="text title">Summary</text>
  <text x="300" y="820" class="text">Total identified: {identified}</text>
  <text x="300" y="840" class="text">Total screened: {screened}</text>
  <text x="300" y="860" class="text">Studies included: {included} | Studies excluded: {excluded}</text>
</svg>"""

    return svg


@router.get("/export/{review_id}")
async def export_review(review_id: str, format: str = "csv", token: str = None):
    """Export systematic review data"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        response = (
            supabase.table("systematic_reviews")
            .select("*")
            .eq("id", review_id)
            .eq("user_id", user["id"])
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Review not found")

        review = response.data[0]

        screening_records_response = (
            supabase.table("screening_records")
            .select("*")
            .eq("review_id", review_id)
            .execute()
        )

        records = screening_records_response.data or []

        if format == "csv":
            csv_content = generate_csv_export(review, records)
            return {
                "format": "csv",
                "content": csv_content,
                "filename": f"systematic_review_{review_id}.csv",
            }
        elif format == "bibtex":
            bibtex_content = generate_bibtex_export(records)
            return {
                "format": "bibtex",
                "content": bibtex_content,
                "filename": f"systematic_review_{review_id}.bib",
            }
        elif format == "prisma":
            counts = review.get("screening_counts", {})
            svg = generate_prisma_svg(counts, review["research_question"])
            return {
                "format": "svg",
                "content": svg,
                "filename": f"prisma_diagram_{review_id}.svg",
            }
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def generate_csv_export(review: dict, records: list):
    """Generate CSV export of review data"""
    import io
    import csv

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Systematic Review Export"])
    writer.writerow([])
    writer.writerow(["Research Question", review["research_question"]])
    writer.writerow(["Search Terms", review["search_terms"]])
    writer.writerow(["Databases", ", ".join(review["databases"])])
    writer.writerow(["Inclusion Criteria", review["inclusion_criteria"]])
    writer.writerow(["Exclusion Criteria", review["exclusion_criteria"]])
    writer.writerow(["Created", review["created_at"]])
    writer.writerow([])

    writer.writerow(
        ["Title", "Authors", "Year", "DOI", "Stage", "Status", "Reason", "Screened At"]
    )

    for record in records:
        writer.writerow(
            [
                record.get("title", ""),
                ", ".join(record.get("authors", [])),
                record.get("year", ""),
                record.get("doi", ""),
                record.get("stage", ""),
                record.get("status", ""),
                record.get("reason", ""),
                record.get("created_at", ""),
            ]
        )

    return output.getvalue()


def generate_bibtex_export(records: list):
    """Generate BibTeX export of included papers"""
    bibtex = []

    for idx, record in enumerate(records):
        if record.get("status") != "included":
            continue

        cite_key = f"ref{idx}"
        if record.get("doi"):
            cite_key = record["doi"].replace("/", "").replace(".", "")

        authors = " and ".join(record.get("authors", []))

        entry = f"""@article{{{cite_key},
  title = {{{record.get("title", "")}}},
  author = {{{authors}}},
  year = {{{record.get("year", "")}}},
  doi = {{{record.get("doi", "")}}}
}}
"""
        bibtex.append(entry)

    return "\n".join(bibtex)
