"""
Systematic Literature Review API - Agent G
Complete PRISMA-compliant systematic review workflow with multi-source search,
screening, bias assessment, and data extraction.

SQL Schema for Supabase (run in SQL Editor):
--------------------------------------------

-- Systematic Review Projects
CREATE TABLE systematic_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL DEFAULT 'dev-user',
    title TEXT NOT NULL,
    description TEXT,
    research_question TEXT NOT NULL,
    objectives TEXT[],
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'protocol', 'searching', 'screening', 'extraction', 'synthesis', 'completed')),
    protocol_registration TEXT,  -- e.g., PROSPERO ID
    start_date TIMESTAMP DEFAULT NOW(),
    target_completion_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Inclusion/Exclusion Criteria (PICOS framework)
CREATE TABLE review_criteria (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID REFERENCES systematic_reviews(id) ON DELETE CASCADE,
    criterion_type TEXT NOT NULL CHECK (criterion_type IN ('inclusion', 'exclusion')),
    category TEXT CHECK (category IN ('population', 'intervention', 'comparator', 'outcome', 'study_design', 'timeframe', 'language', 'other')),
    description TEXT NOT NULL,
    priority INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Studies in Review (from search results)
CREATE TABLE review_studies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID REFERENCES systematic_reviews(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    authors TEXT[],
    year TEXT,
    journal TEXT,
    doi TEXT,
    abstract TEXT,
    source TEXT,
    url TEXT,
    pmid TEXT,
    arxiv_id TEXT,
    citation_count INTEGER,
    full_text_url TEXT,
    full_text_available BOOLEAN DEFAULT FALSE,
    prisma_stage TEXT DEFAULT 'identification' CHECK (prisma_stage IN ('identification', 'screening', 'eligibility', 'included', 'excluded')),
    exclusion_reason TEXT,
    exclusion_stage TEXT,
    duplicate_of UUID REFERENCES review_studies(id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Screening Decisions
CREATE TABLE screening_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    study_id UUID REFERENCES review_studies(id) ON DELETE CASCADE,
    reviewer_id TEXT NOT NULL DEFAULT 'dev-user',
    stage TEXT NOT NULL CHECK (stage IN ('title_abstract', 'full_text')),
    decision TEXT NOT NULL CHECK (decision IN ('include', 'exclude', 'maybe', 'conflict')),
    exclusion_criteria_id UUID REFERENCES review_criteria(id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Risk of Bias Assessment (Cochrane ROB2 simplified)
CREATE TABLE risk_of_bias (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    study_id UUID REFERENCES review_studies(id) ON DELETE CASCADE,
    assessor_id TEXT NOT NULL DEFAULT 'dev-user',
    -- ROB2 domains (simplified)
    randomization_process TEXT CHECK (randomization_process IN ('low', 'some_concerns', 'high', 'not_applicable')),
    randomization_notes TEXT,
    deviations_interventions TEXT CHECK (deviations_interventions IN ('low', 'some_concerns', 'high', 'not_applicable')),
    deviations_notes TEXT,
    missing_outcome_data TEXT CHECK (missing_outcome_data IN ('low', 'some_concerns', 'high', 'not_applicable')),
    missing_data_notes TEXT,
    outcome_measurement TEXT CHECK (outcome_measurement IN ('low', 'some_concerns', 'high', 'not_applicable')),
    measurement_notes TEXT,
    selective_reporting TEXT CHECK (selective_reporting IN ('low', 'some_concerns', 'high', 'not_applicable')),
    reporting_notes TEXT,
    overall_bias TEXT CHECK (overall_bias IN ('low', 'some_concerns', 'high')),
    overall_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Data Extraction Templates
CREATE TABLE extraction_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID REFERENCES systematic_reviews(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    fields JSONB NOT NULL,  -- Array of field definitions
    created_at TIMESTAMP DEFAULT NOW()
);

-- Extracted Data
CREATE TABLE extracted_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    study_id UUID REFERENCES review_studies(id) ON DELETE CASCADE,
    template_id UUID REFERENCES extraction_templates(id),
    extractor_id TEXT NOT NULL DEFAULT 'dev-user',
    data JSONB NOT NULL,  -- Key-value pairs matching template fields
    verified BOOLEAN DEFAULT FALSE,
    verified_by TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Search Strategies
CREATE TABLE review_search_strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID REFERENCES systematic_reviews(id) ON DELETE CASCADE,
    database_name TEXT NOT NULL,
    search_query TEXT NOT NULL,
    filters JSONB,
    results_count INTEGER,
    search_date TIMESTAMP DEFAULT NOW(),
    notes TEXT
);

-- Indexes
CREATE INDEX idx_review_studies_review ON review_studies(review_id);
CREATE INDEX idx_review_studies_stage ON review_studies(prisma_stage);
CREATE INDEX idx_screening_decisions_study ON screening_decisions(study_id);
CREATE INDEX idx_risk_of_bias_study ON risk_of_bias(study_id);
CREATE INDEX idx_extracted_data_study ON extracted_data(study_id);
"""

import asyncio
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from enum import Enum

from core.database import supabase

# Import from literature search module for multi-source search
from app.api.literature import (
    search_pubmed,
    search_arxiv,
    search_semantic_scholar,
    deduplicate_papers,
    Paper,
    LiteratureSearchRequest,
)

router = APIRouter()


# === Enums ===


class ReviewStatus(str, Enum):
    DRAFT = "draft"
    PROTOCOL = "protocol"
    SEARCHING = "searching"
    SCREENING = "screening"
    EXTRACTION = "extraction"
    SYNTHESIS = "synthesis"
    COMPLETED = "completed"


class PRISMAStage(str, Enum):
    IDENTIFICATION = "identification"
    SCREENING = "screening"
    ELIGIBILITY = "eligibility"
    INCLUDED = "included"
    EXCLUDED = "excluded"


class ScreeningStage(str, Enum):
    TITLE_ABSTRACT = "title_abstract"
    FULL_TEXT = "full_text"


class ScreeningDecisionType(str, Enum):
    INCLUDE = "include"
    EXCLUDE = "exclude"
    MAYBE = "maybe"
    CONFLICT = "conflict"


class CriterionType(str, Enum):
    INCLUSION = "inclusion"
    EXCLUSION = "exclusion"


class CriterionCategory(str, Enum):
    POPULATION = "population"
    INTERVENTION = "intervention"
    COMPARATOR = "comparator"
    OUTCOME = "outcome"
    STUDY_DESIGN = "study_design"
    TIMEFRAME = "timeframe"
    LANGUAGE = "language"
    OTHER = "other"


class BiasRating(str, Enum):
    LOW = "low"
    SOME_CONCERNS = "some_concerns"
    HIGH = "high"
    NOT_APPLICABLE = "not_applicable"


# === Pydantic Models ===


class SystematicReviewCreate(BaseModel):
    """Create a new systematic review project"""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    research_question: str = Field(..., min_length=10)
    objectives: Optional[List[str]] = None
    protocol_registration: Optional[str] = None
    target_completion_date: Optional[datetime] = None


class SystematicReviewUpdate(BaseModel):
    """Update systematic review"""
    title: Optional[str] = None
    description: Optional[str] = None
    research_question: Optional[str] = None
    objectives: Optional[List[str]] = None
    status: Optional[ReviewStatus] = None
    protocol_registration: Optional[str] = None
    target_completion_date: Optional[datetime] = None


class SystematicReviewResponse(BaseModel):
    """Systematic review response"""
    id: str
    user_id: str
    title: str
    description: Optional[str]
    research_question: str
    objectives: Optional[List[str]]
    status: str
    protocol_registration: Optional[str]
    start_date: Optional[datetime]
    target_completion_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class CriterionCreate(BaseModel):
    """Create inclusion/exclusion criterion"""
    criterion_type: CriterionType
    category: Optional[CriterionCategory] = None
    description: str = Field(..., min_length=1)
    priority: int = Field(default=1, ge=1, le=10)


class CriterionResponse(BaseModel):
    """Criterion response"""
    id: str
    review_id: str
    criterion_type: str
    category: Optional[str]
    description: str
    priority: int
    created_at: datetime


class ReviewStudyCreate(BaseModel):
    """Add study to review"""
    title: str
    authors: List[str] = []
    year: Optional[str] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    abstract: Optional[str] = None
    source: str = "manual"
    url: Optional[str] = None
    pmid: Optional[str] = None
    arxiv_id: Optional[str] = None


class ReviewStudyResponse(BaseModel):
    """Review study response"""
    id: str
    review_id: str
    title: str
    authors: List[str]
    year: Optional[str]
    journal: Optional[str]
    doi: Optional[str]
    abstract: Optional[str]
    source: str
    url: Optional[str]
    pmid: Optional[str]
    arxiv_id: Optional[str]
    prisma_stage: str
    exclusion_reason: Optional[str]
    full_text_available: bool
    notes: Optional[str]
    created_at: datetime


class ScreeningDecisionCreate(BaseModel):
    """Create screening decision"""
    stage: ScreeningStage
    decision: ScreeningDecisionType
    exclusion_criteria_id: Optional[str] = None
    notes: Optional[str] = None


class RiskOfBiasCreate(BaseModel):
    """Create/update risk of bias assessment"""
    randomization_process: Optional[BiasRating] = None
    randomization_notes: Optional[str] = None
    deviations_interventions: Optional[BiasRating] = None
    deviations_notes: Optional[str] = None
    missing_outcome_data: Optional[BiasRating] = None
    missing_data_notes: Optional[str] = None
    outcome_measurement: Optional[BiasRating] = None
    measurement_notes: Optional[str] = None
    selective_reporting: Optional[BiasRating] = None
    reporting_notes: Optional[str] = None
    overall_bias: Optional[BiasRating] = None
    overall_notes: Optional[str] = None


class RiskOfBiasResponse(BaseModel):
    """Risk of bias response"""
    id: str
    study_id: str
    assessor_id: str
    randomization_process: Optional[str]
    randomization_notes: Optional[str]
    deviations_interventions: Optional[str]
    deviations_notes: Optional[str]
    missing_outcome_data: Optional[str]
    missing_data_notes: Optional[str]
    outcome_measurement: Optional[str]
    measurement_notes: Optional[str]
    selective_reporting: Optional[str]
    reporting_notes: Optional[str]
    overall_bias: Optional[str]
    overall_notes: Optional[str]
    created_at: datetime


class ExtractionFieldDefinition(BaseModel):
    """Definition of a data extraction field"""
    name: str = Field(..., min_length=1)
    field_type: str = Field(default="text")  # text, number, date, select, multiselect, boolean
    required: bool = False
    options: Optional[List[str]] = None  # For select/multiselect
    description: Optional[str] = None


class ExtractionTemplateCreate(BaseModel):
    """Create data extraction template"""
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    fields: List[ExtractionFieldDefinition]


class ExtractionTemplateResponse(BaseModel):
    """Extraction template response"""
    id: str
    review_id: str
    name: str
    description: Optional[str]
    fields: List[Dict[str, Any]]
    created_at: datetime


class ExtractedDataCreate(BaseModel):
    """Create extracted data entry"""
    template_id: str
    data: Dict[str, Any]


class ExtractedDataResponse(BaseModel):
    """Extracted data response"""
    id: str
    study_id: str
    template_id: str
    extractor_id: str
    data: Dict[str, Any]
    verified: bool
    verified_by: Optional[str]
    created_at: datetime


class SearchStrategyCreate(BaseModel):
    """Record search strategy"""
    database_name: str
    search_query: str
    filters: Optional[Dict[str, Any]] = None
    results_count: Optional[int] = None
    notes: Optional[str] = None


class PRISMAFlowData(BaseModel):
    """PRISMA flow diagram data structure"""
    identification: Dict[str, int]
    screening: Dict[str, int]
    eligibility: Dict[str, int]
    included: Dict[str, int]
    flow_arrows: List[Dict[str, Any]]


class MultiSourceSearchRequest(BaseModel):
    """Request for multi-source literature search"""
    query: str = Field(..., min_length=1)
    sources: List[str] = Field(default=["pubmed", "arxiv", "semantic_scholar"])
    max_results_per_source: int = Field(default=50, ge=1, le=200)
    year_start: Optional[int] = None
    year_end: Optional[int] = None
    auto_deduplicate: bool = True


# === Helper Functions ===


def get_user_id() -> str:
    """Get current user ID (development mode - no auth)"""
    return "dev-user"


# === API Endpoints ===


# --- Systematic Review CRUD ---


@router.post("/reviews", response_model=SystematicReviewResponse)
async def create_review(review: SystematicReviewCreate):
    """
    Create a new systematic review project.

    This creates a PRISMA-compliant systematic review with:
    - Research question (PICO format recommended)
    - Objectives
    - Protocol registration tracking
    """
    user_id = get_user_id()

    try:
        review_data = {
            "user_id": user_id,
            "title": review.title,
            "description": review.description,
            "research_question": review.research_question,
            "objectives": review.objectives,
            "protocol_registration": review.protocol_registration,
            "target_completion_date": review.target_completion_date.isoformat() if review.target_completion_date else None,
            "status": "draft",
        }

        result = supabase.table("systematic_reviews").insert(review_data).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create review")

        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create review: {str(e)}")


@router.get("/reviews", response_model=List[SystematicReviewResponse])
async def list_reviews(
    status: Optional[ReviewStatus] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """List all systematic reviews for the current user"""
    user_id = get_user_id()

    try:
        query = (
            supabase.table("systematic_reviews")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
        )

        if status:
            query = query.eq("status", status.value)

        result = query.execute()
        return result.data if result.data else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list reviews: {str(e)}")


@router.get("/reviews/{review_id}", response_model=SystematicReviewResponse)
async def get_review(review_id: str):
    """Get a specific systematic review"""
    try:
        result = (
            supabase.table("systematic_reviews")
            .select("*")
            .eq("id", review_id)
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Review not found")

        return result.data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get review: {str(e)}")


@router.patch("/reviews/{review_id}", response_model=SystematicReviewResponse)
async def update_review(review_id: str, update: SystematicReviewUpdate):
    """Update a systematic review"""
    try:
        update_data = {k: v for k, v in update.model_dump().items() if v is not None}

        if "status" in update_data:
            update_data["status"] = update_data["status"].value if hasattr(update_data["status"], 'value') else update_data["status"]

        if "target_completion_date" in update_data and update_data["target_completion_date"]:
            update_data["target_completion_date"] = update_data["target_completion_date"].isoformat()

        update_data["updated_at"] = datetime.utcnow().isoformat()

        result = (
            supabase.table("systematic_reviews")
            .update(update_data)
            .eq("id", review_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Review not found")

        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update review: {str(e)}")


@router.delete("/reviews/{review_id}")
async def delete_review(review_id: str):
    """Delete a systematic review and all associated data"""
    try:
        result = (
            supabase.table("systematic_reviews")
            .delete()
            .eq("id", review_id)
            .execute()
        )

        return {"status": "deleted", "review_id": review_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete review: {str(e)}")


# --- Inclusion/Exclusion Criteria ---


@router.post("/reviews/{review_id}/criteria", response_model=CriterionResponse)
async def add_criterion(review_id: str, criterion: CriterionCreate):
    """
    Add inclusion or exclusion criterion to a review.

    Categories follow PICOS framework:
    - population: Target population characteristics
    - intervention: Intervention/exposure of interest
    - comparator: Comparison group/control
    - outcome: Primary and secondary outcomes
    - study_design: Acceptable study designs (RCT, cohort, etc.)
    - timeframe: Publication date restrictions
    - language: Language restrictions
    - other: Other criteria
    """
    try:
        criterion_data = {
            "review_id": review_id,
            "criterion_type": criterion.criterion_type.value,
            "category": criterion.category.value if criterion.category else None,
            "description": criterion.description,
            "priority": criterion.priority,
        }

        result = supabase.table("review_criteria").insert(criterion_data).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to add criterion")

        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add criterion: {str(e)}")


@router.get("/reviews/{review_id}/criteria", response_model=List[CriterionResponse])
async def list_criteria(
    review_id: str,
    criterion_type: Optional[CriterionType] = None
):
    """List all criteria for a review"""
    try:
        query = (
            supabase.table("review_criteria")
            .select("*")
            .eq("review_id", review_id)
            .order("priority", desc=False)
        )

        if criterion_type:
            query = query.eq("criterion_type", criterion_type.value)

        result = query.execute()
        return result.data if result.data else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list criteria: {str(e)}")


@router.delete("/reviews/{review_id}/criteria/{criterion_id}")
async def delete_criterion(review_id: str, criterion_id: str):
    """Delete a criterion"""
    try:
        result = (
            supabase.table("review_criteria")
            .delete()
            .eq("id", criterion_id)
            .eq("review_id", review_id)
            .execute()
        )

        return {"status": "deleted", "criterion_id": criterion_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete criterion: {str(e)}")


# --- Multi-Source Search Integration ---


@router.post("/reviews/{review_id}/search")
async def search_and_import(review_id: str, request: MultiSourceSearchRequest):
    """
    Search multiple literature databases and import results into the review.

    Integrates with Literature Search module (Agent B) to search:
    - PubMed
    - arXiv
    - Semantic Scholar

    Results are automatically imported as studies in the 'identification' stage.
    """
    try:
        # Verify review exists
        review_result = (
            supabase.table("systematic_reviews")
            .select("id")
            .eq("id", review_id)
            .single()
            .execute()
        )

        if not review_result.data:
            raise HTTPException(status_code=404, detail="Review not found")

        # Search all sources concurrently
        all_papers = []
        tasks = []

        if "pubmed" in request.sources:
            tasks.append(("pubmed", search_pubmed(
                request.query,
                request.max_results_per_source,
                request.year_start,
                request.year_end
            )))

        if "arxiv" in request.sources:
            tasks.append(("arxiv", search_arxiv(
                request.query,
                request.max_results_per_source,
                request.year_start,
                request.year_end
            )))

        if "semantic_scholar" in request.sources:
            tasks.append(("semantic_scholar", search_semantic_scholar(
                request.query,
                request.max_results_per_source,
                request.year_start,
                request.year_end
            )))

        # Execute searches
        source_counts = {}
        if tasks:
            results = await asyncio.gather(*[t[1] for t in tasks])
            for i, (source_name, _) in enumerate(tasks):
                source_papers = results[i]
                source_counts[source_name] = len(source_papers)
                all_papers.extend(source_papers)

        # Deduplicate if requested
        if request.auto_deduplicate:
            papers_to_import = deduplicate_papers(all_papers)
            duplicates_removed = len(all_papers) - len(papers_to_import)
        else:
            papers_to_import = all_papers
            duplicates_removed = 0

        # Import papers as studies
        imported_count = 0
        for paper in papers_to_import:
            study_data = {
                "review_id": review_id,
                "title": paper.title,
                "authors": paper.authors,
                "year": paper.year,
                "journal": paper.journal,
                "doi": paper.doi,
                "abstract": paper.abstract,
                "source": paper.source,
                "url": paper.url,
                "pmid": paper.pmid,
                "arxiv_id": paper.arxiv_id,
                "citation_count": paper.citation_count,
                "prisma_stage": "identification",
            }

            try:
                supabase.table("review_studies").insert(study_data).execute()
                imported_count += 1
            except Exception:
                # Skip duplicates (same DOI in this review)
                pass

        # Record search strategy
        strategy_data = {
            "review_id": review_id,
            "database_name": ", ".join(request.sources),
            "search_query": request.query,
            "filters": {
                "year_start": request.year_start,
                "year_end": request.year_end,
                "max_results_per_source": request.max_results_per_source,
            },
            "results_count": imported_count,
        }

        supabase.table("review_search_strategies").insert(strategy_data).execute()

        # Update review status
        supabase.table("systematic_reviews").update({
            "status": "searching",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", review_id).execute()

        return {
            "status": "success",
            "total_found": len(all_papers),
            "duplicates_removed": duplicates_removed,
            "imported": imported_count,
            "source_counts": source_counts,
            "query": request.query,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/reviews/{review_id}/search-strategies")
async def get_search_strategies(review_id: str):
    """Get all recorded search strategies for a review"""
    try:
        result = (
            supabase.table("review_search_strategies")
            .select("*")
            .eq("review_id", review_id)
            .order("search_date", desc=True)
            .execute()
        )

        return {"strategies": result.data if result.data else []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get strategies: {str(e)}")


# --- Study Management ---


@router.post("/reviews/{review_id}/studies", response_model=ReviewStudyResponse)
async def add_study_manually(review_id: str, study: ReviewStudyCreate):
    """Manually add a study to the review"""
    try:
        study_data = {
            "review_id": review_id,
            "title": study.title,
            "authors": study.authors,
            "year": study.year,
            "journal": study.journal,
            "doi": study.doi,
            "abstract": study.abstract,
            "source": study.source,
            "url": study.url,
            "pmid": study.pmid,
            "arxiv_id": study.arxiv_id,
            "prisma_stage": "identification",
        }

        result = supabase.table("review_studies").insert(study_data).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to add study")

        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add study: {str(e)}")


@router.get("/reviews/{review_id}/studies", response_model=List[ReviewStudyResponse])
async def list_studies(
    review_id: str,
    stage: Optional[PRISMAStage] = None,
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0)
):
    """List all studies in a review, optionally filtered by PRISMA stage"""
    try:
        query = (
            supabase.table("review_studies")
            .select("*")
            .eq("review_id", review_id)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
        )

        if stage:
            query = query.eq("prisma_stage", stage.value)

        result = query.execute()
        return result.data if result.data else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list studies: {str(e)}")


@router.get("/reviews/{review_id}/studies/{study_id}", response_model=ReviewStudyResponse)
async def get_study(review_id: str, study_id: str):
    """Get a specific study"""
    try:
        result = (
            supabase.table("review_studies")
            .select("*")
            .eq("id", study_id)
            .eq("review_id", review_id)
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Study not found")

        return result.data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get study: {str(e)}")


@router.patch("/reviews/{review_id}/studies/{study_id}")
async def update_study(
    review_id: str,
    study_id: str,
    notes: Optional[str] = Body(None),
    full_text_url: Optional[str] = Body(None),
    full_text_available: Optional[bool] = Body(None)
):
    """Update study metadata"""
    try:
        update_data = {"updated_at": datetime.utcnow().isoformat()}

        if notes is not None:
            update_data["notes"] = notes
        if full_text_url is not None:
            update_data["full_text_url"] = full_text_url
        if full_text_available is not None:
            update_data["full_text_available"] = full_text_available

        result = (
            supabase.table("review_studies")
            .update(update_data)
            .eq("id", study_id)
            .eq("review_id", review_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Study not found")

        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update study: {str(e)}")


@router.delete("/reviews/{review_id}/studies/{study_id}")
async def delete_study(review_id: str, study_id: str):
    """Delete a study from the review"""
    try:
        result = (
            supabase.table("review_studies")
            .delete()
            .eq("id", study_id)
            .eq("review_id", review_id)
            .execute()
        )

        return {"status": "deleted", "study_id": study_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete study: {str(e)}")


# --- Screening Workflow ---


@router.post("/reviews/{review_id}/studies/{study_id}/screen")
async def screen_study(review_id: str, study_id: str, decision: ScreeningDecisionCreate):
    """
    Record a screening decision for a study.

    Screening stages:
    - title_abstract: Initial screening based on title and abstract
    - full_text: Full-text screening for eligibility

    Decisions:
    - include: Study meets criteria, advance to next stage
    - exclude: Study does not meet criteria (provide reason)
    - maybe: Uncertain, flag for discussion
    - conflict: Reviewers disagree (for dual screening)
    """
    user_id = get_user_id()

    try:
        # Record the decision
        decision_data = {
            "study_id": study_id,
            "reviewer_id": user_id,
            "stage": decision.stage.value,
            "decision": decision.decision.value,
            "exclusion_criteria_id": decision.exclusion_criteria_id,
            "notes": decision.notes,
        }

        supabase.table("screening_decisions").insert(decision_data).execute()

        # Update study PRISMA stage based on decision
        new_stage = None
        exclusion_reason = None

        if decision.decision == ScreeningDecisionType.INCLUDE:
            if decision.stage == ScreeningStage.TITLE_ABSTRACT:
                new_stage = "screening"
            elif decision.stage == ScreeningStage.FULL_TEXT:
                new_stage = "included"
        elif decision.decision == ScreeningDecisionType.EXCLUDE:
            new_stage = "excluded"
            exclusion_reason = decision.notes
        elif decision.decision == ScreeningDecisionType.MAYBE:
            # Keep in current stage but flag
            if decision.stage == ScreeningStage.TITLE_ABSTRACT:
                new_stage = "screening"  # Move to screening for further review
            else:
                new_stage = "eligibility"

        if new_stage:
            update_data = {
                "prisma_stage": new_stage,
                "updated_at": datetime.utcnow().isoformat(),
            }
            if exclusion_reason:
                update_data["exclusion_reason"] = exclusion_reason
                update_data["exclusion_stage"] = decision.stage.value

            supabase.table("review_studies").update(update_data).eq("id", study_id).execute()

        return {
            "status": "success",
            "study_id": study_id,
            "decision": decision.decision.value,
            "new_stage": new_stage,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record decision: {str(e)}")


@router.get("/reviews/{review_id}/studies/{study_id}/decisions")
async def get_screening_decisions(review_id: str, study_id: str):
    """Get all screening decisions for a study"""
    try:
        result = (
            supabase.table("screening_decisions")
            .select("*")
            .eq("study_id", study_id)
            .order("created_at", desc=True)
            .execute()
        )

        return {"decisions": result.data if result.data else []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get decisions: {str(e)}")


@router.post("/reviews/{review_id}/bulk-screen")
async def bulk_screen_studies(
    review_id: str,
    study_ids: List[str] = Body(...),
    decision: ScreeningDecisionCreate = Body(...)
):
    """Apply the same screening decision to multiple studies"""
    user_id = get_user_id()
    results = []

    for study_id in study_ids:
        try:
            decision_data = {
                "study_id": study_id,
                "reviewer_id": user_id,
                "stage": decision.stage.value,
                "decision": decision.decision.value,
                "exclusion_criteria_id": decision.exclusion_criteria_id,
                "notes": decision.notes,
            }

            supabase.table("screening_decisions").insert(decision_data).execute()

            # Update PRISMA stage
            new_stage = None
            if decision.decision == ScreeningDecisionType.INCLUDE:
                new_stage = "screening" if decision.stage == ScreeningStage.TITLE_ABSTRACT else "included"
            elif decision.decision == ScreeningDecisionType.EXCLUDE:
                new_stage = "excluded"

            if new_stage:
                update_data = {
                    "prisma_stage": new_stage,
                    "updated_at": datetime.utcnow().isoformat(),
                }
                if decision.decision == ScreeningDecisionType.EXCLUDE:
                    update_data["exclusion_reason"] = decision.notes
                    update_data["exclusion_stage"] = decision.stage.value

                supabase.table("review_studies").update(update_data).eq("id", study_id).execute()

            results.append({"study_id": study_id, "status": "success"})
        except Exception as e:
            results.append({"study_id": study_id, "status": "error", "error": str(e)})

    return {"results": results, "total": len(results)}


# --- PRISMA Flow Diagram ---


@router.get("/reviews/{review_id}/prisma-flow", response_model=PRISMAFlowData)
async def get_prisma_flow(review_id: str):
    """
    Generate PRISMA 2020 flow diagram data.

    Returns structured data representing the PRISMA flow:
    - Identification: Records from databases and other sources
    - Screening: Records after duplicates removed, screened
    - Eligibility: Full-text articles assessed
    - Included: Studies included in review

    This data can be used to render an SVG/image on the frontend.
    """
    try:
        # Get all studies for this review
        studies_result = (
            supabase.table("review_studies")
            .select("prisma_stage, source, exclusion_stage, exclusion_reason")
            .eq("review_id", review_id)
            .execute()
        )

        studies = studies_result.data if studies_result.data else []

        # Count by stage
        stage_counts = {
            "identification": 0,
            "screening": 0,
            "eligibility": 0,
            "included": 0,
            "excluded": 0,
        }

        source_counts = {}
        exclusion_by_stage = {
            "title_abstract": {"count": 0, "reasons": {}},
            "full_text": {"count": 0, "reasons": {}},
        }

        for study in studies:
            stage = study.get("prisma_stage", "identification")
            source = study.get("source", "other")

            # Count by source (for identification)
            source_counts[source] = source_counts.get(source, 0) + 1

            # Count by stage
            if stage in stage_counts:
                stage_counts[stage] += 1

            # Track exclusion reasons
            if stage == "excluded":
                exc_stage = study.get("exclusion_stage", "title_abstract")
                exc_reason = study.get("exclusion_reason", "Not specified")

                if exc_stage in exclusion_by_stage:
                    exclusion_by_stage[exc_stage]["count"] += 1
                    reasons = exclusion_by_stage[exc_stage]["reasons"]
                    reasons[exc_reason] = reasons.get(exc_reason, 0) + 1

        # Calculate totals for each PRISMA stage
        total_identified = len(studies)
        total_after_duplicates = total_identified  # Duplicates already removed during import

        # Studies that passed title/abstract screening
        screened = stage_counts["screening"] + stage_counts["eligibility"] + stage_counts["included"]

        # Studies assessed for eligibility (full-text)
        assessed_eligibility = stage_counts["eligibility"] + stage_counts["included"]

        # Studies included
        included = stage_counts["included"]

        # Build flow data
        flow_data = PRISMAFlowData(
            identification={
                "total_records": total_identified,
                "by_source": source_counts,
                "duplicates_removed": 0,  # Already handled
                "records_after_dedup": total_after_duplicates,
            },
            screening={
                "records_screened": total_after_duplicates,
                "records_excluded": exclusion_by_stage["title_abstract"]["count"],
                "exclusion_reasons": exclusion_by_stage["title_abstract"]["reasons"],
            },
            eligibility={
                "full_text_assessed": screened,
                "full_text_excluded": exclusion_by_stage["full_text"]["count"],
                "exclusion_reasons": exclusion_by_stage["full_text"]["reasons"],
            },
            included={
                "total_included": included,
                "in_quantitative": included,  # Could be split if tracking separately
                "in_qualitative": 0,
            },
            flow_arrows=[
                {"from": "identification", "to": "screening", "count": total_after_duplicates},
                {"from": "screening", "to": "eligibility", "count": screened},
                {"from": "eligibility", "to": "included", "count": included},
            ]
        )

        return flow_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PRISMA flow: {str(e)}")


@router.get("/reviews/{review_id}/prisma-svg")
async def get_prisma_svg(review_id: str):
    """
    Generate PRISMA flow diagram as SVG.

    Returns an SVG string that can be directly embedded or saved.
    """
    try:
        # Get flow data
        flow_data = await get_prisma_flow(review_id)

        # Generate SVG
        svg = generate_prisma_svg(flow_data)

        return {"svg": svg, "content_type": "image/svg+xml"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate SVG: {str(e)}")


def generate_prisma_svg(flow: PRISMAFlowData) -> str:
    """Generate PRISMA 2020 flow diagram as SVG"""

    # SVG dimensions and styling
    width = 800
    height = 700
    box_width = 200
    box_height = 60
    margin = 50

    # Color scheme
    colors = {
        "identification": "#4299E1",  # Blue
        "screening": "#48BB78",       # Green
        "eligibility": "#ECC94B",     # Yellow
        "included": "#9F7AEA",        # Purple
        "excluded": "#FC8181",        # Red
    }

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        '<style>',
        '  .box { stroke: #2D3748; stroke-width: 2; rx: 8; }',
        '  .text { font-family: Arial, sans-serif; font-size: 12px; fill: #1A202C; text-anchor: middle; }',
        '  .title { font-weight: bold; font-size: 14px; }',
        '  .arrow { stroke: #4A5568; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }',
        '  .section-title { font-size: 16px; font-weight: bold; fill: #2D3748; }',
        '</style>',
        '<defs>',
        '  <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">',
        '    <polygon points="0 0, 10 3.5, 0 7" fill="#4A5568" />',
        '  </marker>',
        '</defs>',
    ]

    # Identification section
    id_x = width // 2 - box_width // 2
    id_y = margin

    svg_parts.append(f'<text x="{margin}" y="{id_y + 10}" class="section-title">Identification</text>')
    svg_parts.append(f'<rect x="{id_x}" y="{id_y + 20}" width="{box_width}" height="{box_height}" class="box" fill="{colors["identification"]}20" />')
    svg_parts.append(f'<text x="{id_x + box_width//2}" y="{id_y + 45}" class="text title">Records Identified</text>')
    svg_parts.append(f'<text x="{id_x + box_width//2}" y="{id_y + 65}" class="text">n = {flow.identification["total_records"]}</text>')

    # Arrow to screening
    arrow_y1 = id_y + 20 + box_height
    arrow_y2 = id_y + 140
    svg_parts.append(f'<line x1="{width//2}" y1="{arrow_y1}" x2="{width//2}" y2="{arrow_y2}" class="arrow" />')

    # Screening section
    screen_y = id_y + 150
    svg_parts.append(f'<text x="{margin}" y="{screen_y + 10}" class="section-title">Screening</text>')

    # Records screened box
    svg_parts.append(f'<rect x="{id_x}" y="{screen_y + 20}" width="{box_width}" height="{box_height}" class="box" fill="{colors["screening"]}20" />')
    svg_parts.append(f'<text x="{id_x + box_width//2}" y="{screen_y + 45}" class="text title">Records Screened</text>')
    svg_parts.append(f'<text x="{id_x + box_width//2}" y="{screen_y + 65}" class="text">n = {flow.screening["records_screened"]}</text>')

    # Excluded at screening
    excl_x = id_x + box_width + 80
    svg_parts.append(f'<rect x="{excl_x}" y="{screen_y + 20}" width="{box_width}" height="{box_height}" class="box" fill="{colors["excluded"]}20" />')
    svg_parts.append(f'<text x="{excl_x + box_width//2}" y="{screen_y + 45}" class="text title">Records Excluded</text>')
    svg_parts.append(f'<text x="{excl_x + box_width//2}" y="{screen_y + 65}" class="text">n = {flow.screening["records_excluded"]}</text>')

    # Arrow to excluded
    svg_parts.append(f'<line x1="{id_x + box_width}" y1="{screen_y + 50}" x2="{excl_x}" y2="{screen_y + 50}" class="arrow" />')

    # Arrow to eligibility
    svg_parts.append(f'<line x1="{width//2}" y1="{screen_y + 20 + box_height}" x2="{width//2}" y2="{screen_y + 140}" class="arrow" />')

    # Eligibility section
    elig_y = screen_y + 150
    svg_parts.append(f'<text x="{margin}" y="{elig_y + 10}" class="section-title">Eligibility</text>')

    svg_parts.append(f'<rect x="{id_x}" y="{elig_y + 20}" width="{box_width}" height="{box_height}" class="box" fill="{colors["eligibility"]}20" />')
    svg_parts.append(f'<text x="{id_x + box_width//2}" y="{elig_y + 45}" class="text title">Full-text Assessed</text>')
    svg_parts.append(f'<text x="{id_x + box_width//2}" y="{elig_y + 65}" class="text">n = {flow.eligibility["full_text_assessed"]}</text>')

    # Excluded at eligibility
    svg_parts.append(f'<rect x="{excl_x}" y="{elig_y + 20}" width="{box_width}" height="{box_height}" class="box" fill="{colors["excluded"]}20" />')
    svg_parts.append(f'<text x="{excl_x + box_width//2}" y="{elig_y + 45}" class="text title">Full-text Excluded</text>')
    svg_parts.append(f'<text x="{excl_x + box_width//2}" y="{elig_y + 65}" class="text">n = {flow.eligibility["full_text_excluded"]}</text>')

    svg_parts.append(f'<line x1="{id_x + box_width}" y1="{elig_y + 50}" x2="{excl_x}" y2="{elig_y + 50}" class="arrow" />')

    # Arrow to included
    svg_parts.append(f'<line x1="{width//2}" y1="{elig_y + 20 + box_height}" x2="{width//2}" y2="{elig_y + 140}" class="arrow" />')

    # Included section
    incl_y = elig_y + 150
    svg_parts.append(f'<text x="{margin}" y="{incl_y + 10}" class="section-title">Included</text>')

    svg_parts.append(f'<rect x="{id_x}" y="{incl_y + 20}" width="{box_width}" height="{box_height}" class="box" fill="{colors["included"]}20" />')
    svg_parts.append(f'<text x="{id_x + box_width//2}" y="{incl_y + 45}" class="text title">Studies Included</text>')
    svg_parts.append(f'<text x="{id_x + box_width//2}" y="{incl_y + 65}" class="text">n = {flow.included["total_included"]}</text>')

    svg_parts.append('</svg>')

    return '\n'.join(svg_parts)


# --- Risk of Bias Assessment (Cochrane ROB2 Simplified) ---


@router.post("/reviews/{review_id}/studies/{study_id}/risk-of-bias", response_model=RiskOfBiasResponse)
async def assess_risk_of_bias(
    review_id: str,
    study_id: str,
    assessment: RiskOfBiasCreate
):
    """
    Create or update risk of bias assessment for a study.

    Uses simplified Cochrane ROB2 domains:
    1. Randomization process
    2. Deviations from intended interventions
    3. Missing outcome data
    4. Measurement of the outcome
    5. Selection of reported result

    Ratings: low, some_concerns, high, not_applicable
    """
    user_id = get_user_id()

    try:
        # Check if assessment exists
        existing = (
            supabase.table("risk_of_bias")
            .select("id")
            .eq("study_id", study_id)
            .eq("assessor_id", user_id)
            .execute()
        )

        assessment_data = {
            "study_id": study_id,
            "assessor_id": user_id,
            **{k: v.value if hasattr(v, 'value') else v for k, v in assessment.model_dump().items() if v is not None},
            "updated_at": datetime.utcnow().isoformat(),
        }

        if existing.data:
            # Update existing
            result = (
                supabase.table("risk_of_bias")
                .update(assessment_data)
                .eq("id", existing.data[0]["id"])
                .execute()
            )
        else:
            # Create new
            result = supabase.table("risk_of_bias").insert(assessment_data).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to save assessment")

        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assess risk of bias: {str(e)}")


@router.get("/reviews/{review_id}/studies/{study_id}/risk-of-bias")
async def get_risk_of_bias(review_id: str, study_id: str):
    """Get risk of bias assessment for a study"""
    try:
        result = (
            supabase.table("risk_of_bias")
            .select("*")
            .eq("study_id", study_id)
            .execute()
        )

        return {"assessments": result.data if result.data else []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get assessment: {str(e)}")


@router.get("/reviews/{review_id}/risk-of-bias-summary")
async def get_risk_of_bias_summary(review_id: str):
    """
    Get summary of risk of bias across all included studies.

    Returns counts by domain and overall bias distribution.
    """
    try:
        # Get all included studies
        studies_result = (
            supabase.table("review_studies")
            .select("id")
            .eq("review_id", review_id)
            .eq("prisma_stage", "included")
            .execute()
        )

        study_ids = [s["id"] for s in (studies_result.data or [])]

        if not study_ids:
            return {
                "total_studies": 0,
                "assessed": 0,
                "domain_summary": {},
                "overall_summary": {},
            }

        # Get all assessments
        rob_result = (
            supabase.table("risk_of_bias")
            .select("*")
            .in_("study_id", study_ids)
            .execute()
        )

        assessments = rob_result.data or []

        # Summarize by domain
        domains = [
            "randomization_process",
            "deviations_interventions",
            "missing_outcome_data",
            "outcome_measurement",
            "selective_reporting",
        ]

        domain_summary = {}
        for domain in domains:
            domain_summary[domain] = {"low": 0, "some_concerns": 0, "high": 0, "not_applicable": 0}
            for assessment in assessments:
                rating = assessment.get(domain)
                if rating and rating in domain_summary[domain]:
                    domain_summary[domain][rating] += 1

        # Overall summary
        overall_summary = {"low": 0, "some_concerns": 0, "high": 0}
        for assessment in assessments:
            overall = assessment.get("overall_bias")
            if overall and overall in overall_summary:
                overall_summary[overall] += 1

        return {
            "total_studies": len(study_ids),
            "assessed": len(assessments),
            "domain_summary": domain_summary,
            "overall_summary": overall_summary,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")


# --- Data Extraction Templates ---


@router.post("/reviews/{review_id}/extraction-templates", response_model=ExtractionTemplateResponse)
async def create_extraction_template(review_id: str, template: ExtractionTemplateCreate):
    """
    Create a data extraction template.

    Define fields to extract from each study:
    - text: Free text input
    - number: Numeric value
    - date: Date value
    - select: Single selection from options
    - multiselect: Multiple selections from options
    - boolean: Yes/No
    """
    try:
        template_data = {
            "review_id": review_id,
            "name": template.name,
            "description": template.description,
            "fields": [f.model_dump() for f in template.fields],
        }

        result = supabase.table("extraction_templates").insert(template_data).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create template")

        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")


@router.get("/reviews/{review_id}/extraction-templates", response_model=List[ExtractionTemplateResponse])
async def list_extraction_templates(review_id: str):
    """List all extraction templates for a review"""
    try:
        result = (
            supabase.table("extraction_templates")
            .select("*")
            .eq("review_id", review_id)
            .order("created_at", desc=True)
            .execute()
        )

        return result.data if result.data else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list templates: {str(e)}")


@router.get("/reviews/{review_id}/extraction-templates/{template_id}", response_model=ExtractionTemplateResponse)
async def get_extraction_template(review_id: str, template_id: str):
    """Get a specific extraction template"""
    try:
        result = (
            supabase.table("extraction_templates")
            .select("*")
            .eq("id", template_id)
            .eq("review_id", review_id)
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Template not found")

        return result.data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get template: {str(e)}")


@router.delete("/reviews/{review_id}/extraction-templates/{template_id}")
async def delete_extraction_template(review_id: str, template_id: str):
    """Delete an extraction template"""
    try:
        result = (
            supabase.table("extraction_templates")
            .delete()
            .eq("id", template_id)
            .eq("review_id", review_id)
            .execute()
        )

        return {"status": "deleted", "template_id": template_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete template: {str(e)}")


# --- Data Extraction ---


@router.post("/reviews/{review_id}/studies/{study_id}/extract", response_model=ExtractedDataResponse)
async def extract_data(review_id: str, study_id: str, extraction: ExtractedDataCreate):
    """
    Extract data from a study using a template.

    The data object should contain key-value pairs matching the template fields.
    """
    user_id = get_user_id()

    try:
        extraction_data = {
            "study_id": study_id,
            "template_id": extraction.template_id,
            "extractor_id": user_id,
            "data": extraction.data,
            "verified": False,
        }

        result = supabase.table("extracted_data").insert(extraction_data).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to save extraction")

        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract data: {str(e)}")


@router.get("/reviews/{review_id}/studies/{study_id}/extractions")
async def get_study_extractions(review_id: str, study_id: str):
    """Get all extracted data for a study"""
    try:
        result = (
            supabase.table("extracted_data")
            .select("*, extraction_templates(name, fields)")
            .eq("study_id", study_id)
            .execute()
        )

        return {"extractions": result.data if result.data else []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get extractions: {str(e)}")


@router.patch("/reviews/{review_id}/extractions/{extraction_id}/verify")
async def verify_extraction(review_id: str, extraction_id: str):
    """Mark an extraction as verified"""
    user_id = get_user_id()

    try:
        result = (
            supabase.table("extracted_data")
            .update({
                "verified": True,
                "verified_by": user_id,
                "updated_at": datetime.utcnow().isoformat(),
            })
            .eq("id", extraction_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Extraction not found")

        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify extraction: {str(e)}")


# --- Export ---


@router.get("/reviews/{review_id}/export")
async def export_review(
    review_id: str,
    format: str = Query(default="json", description="Export format: json, csv")
):
    """
    Export complete review data.

    Includes:
    - Review metadata
    - Criteria
    - All studies with screening decisions
    - Risk of bias assessments
    - Extracted data
    - PRISMA flow statistics
    """
    try:
        # Get review
        review_result = (
            supabase.table("systematic_reviews")
            .select("*")
            .eq("id", review_id)
            .single()
            .execute()
        )

        if not review_result.data:
            raise HTTPException(status_code=404, detail="Review not found")

        review = review_result.data

        # Get criteria
        criteria_result = (
            supabase.table("review_criteria")
            .select("*")
            .eq("review_id", review_id)
            .execute()
        )

        # Get studies
        studies_result = (
            supabase.table("review_studies")
            .select("*")
            .eq("review_id", review_id)
            .execute()
        )

        # Get study IDs for related queries
        study_ids = [s["id"] for s in (studies_result.data or [])]

        # Get screening decisions
        decisions = []
        if study_ids:
            decisions_result = (
                supabase.table("screening_decisions")
                .select("*")
                .in_("study_id", study_ids)
                .execute()
            )
            decisions = decisions_result.data or []

        # Get risk of bias
        rob = []
        if study_ids:
            rob_result = (
                supabase.table("risk_of_bias")
                .select("*")
                .in_("study_id", study_ids)
                .execute()
            )
            rob = rob_result.data or []

        # Get extracted data
        extractions = []
        if study_ids:
            extractions_result = (
                supabase.table("extracted_data")
                .select("*")
                .in_("study_id", study_ids)
                .execute()
            )
            extractions = extractions_result.data or []

        # Get templates
        templates_result = (
            supabase.table("extraction_templates")
            .select("*")
            .eq("review_id", review_id)
            .execute()
        )

        # Get search strategies
        strategies_result = (
            supabase.table("review_search_strategies")
            .select("*")
            .eq("review_id", review_id)
            .execute()
        )

        # Get PRISMA flow
        prisma_flow = await get_prisma_flow(review_id)

        export_data = {
            "review": review,
            "criteria": criteria_result.data or [],
            "search_strategies": strategies_result.data or [],
            "studies": studies_result.data or [],
            "screening_decisions": decisions,
            "risk_of_bias_assessments": rob,
            "extraction_templates": templates_result.data or [],
            "extracted_data": extractions,
            "prisma_flow": prisma_flow.model_dump(),
            "export_date": datetime.utcnow().isoformat(),
        }

        if format == "csv":
            # Return studies as CSV
            import csv
            from io import StringIO

            output = StringIO()

            if studies_result.data:
                writer = csv.DictWriter(
                    output,
                    fieldnames=["title", "authors", "year", "journal", "doi", "abstract", "source", "prisma_stage", "exclusion_reason"]
                )
                writer.writeheader()

                for study in studies_result.data:
                    writer.writerow({
                        "title": study.get("title", ""),
                        "authors": "; ".join(study.get("authors", [])),
                        "year": study.get("year", ""),
                        "journal": study.get("journal", ""),
                        "doi": study.get("doi", ""),
                        "abstract": study.get("abstract", ""),
                        "source": study.get("source", ""),
                        "prisma_stage": study.get("prisma_stage", ""),
                        "exclusion_reason": study.get("exclusion_reason", ""),
                    })

            return {
                "format": "csv",
                "content": output.getvalue(),
                "filename": f"systematic_review_{review_id}.csv",
            }

        return export_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export review: {str(e)}")


@router.get("/reviews/{review_id}/statistics")
async def get_review_statistics(review_id: str):
    """
    Get comprehensive statistics for the review.

    Includes study counts by stage, source distribution, screening progress, etc.
    """
    try:
        # Get all studies
        studies_result = (
            supabase.table("review_studies")
            .select("prisma_stage, source, exclusion_stage")
            .eq("review_id", review_id)
            .execute()
        )

        studies = studies_result.data or []

        # Count by stage
        stage_counts = {}
        source_counts = {}
        exclusion_stage_counts = {}

        for study in studies:
            stage = study.get("prisma_stage", "identification")
            source = study.get("source", "other")
            exc_stage = study.get("exclusion_stage")

            stage_counts[stage] = stage_counts.get(stage, 0) + 1
            source_counts[source] = source_counts.get(source, 0) + 1

            if exc_stage:
                exclusion_stage_counts[exc_stage] = exclusion_stage_counts.get(exc_stage, 0) + 1

        # Get screening decisions count
        study_ids = [s.get("id") for s in studies if s.get("id")]

        screening_stats = {"total_decisions": 0}
        if study_ids:
            decisions_result = (
                supabase.table("screening_decisions")
                .select("decision")
                .in_("study_id", study_ids)
                .execute()
            )

            decisions = decisions_result.data or []
            screening_stats["total_decisions"] = len(decisions)

            decision_counts = {}
            for d in decisions:
                dec = d.get("decision", "unknown")
                decision_counts[dec] = decision_counts.get(dec, 0) + 1
            screening_stats["by_decision"] = decision_counts

        return {
            "total_studies": len(studies),
            "by_stage": stage_counts,
            "by_source": source_counts,
            "exclusions_by_stage": exclusion_stage_counts,
            "screening": screening_stats,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


# === Predefined Templates ===


@router.post("/reviews/{review_id}/templates/default")
async def create_default_templates(review_id: str):
    """
    Create default extraction templates for common systematic review types.

    Creates templates for:
    - Study characteristics
    - Intervention details
    - Outcome data
    - Quality assessment
    """
    try:
        templates = [
            {
                "review_id": review_id,
                "name": "Study Characteristics",
                "description": "Basic study information and design",
                "fields": [
                    {"name": "study_design", "field_type": "select", "required": True,
                     "options": ["RCT", "Cohort", "Case-control", "Cross-sectional", "Case series", "Qualitative", "Mixed methods"]},
                    {"name": "country", "field_type": "text", "required": True},
                    {"name": "setting", "field_type": "text", "required": False},
                    {"name": "sample_size", "field_type": "number", "required": True},
                    {"name": "population_description", "field_type": "text", "required": True},
                    {"name": "age_range", "field_type": "text", "required": False},
                    {"name": "gender_distribution", "field_type": "text", "required": False},
                    {"name": "funding_source", "field_type": "text", "required": False},
                    {"name": "conflicts_of_interest", "field_type": "boolean", "required": False},
                ],
            },
            {
                "review_id": review_id,
                "name": "Intervention Details",
                "description": "Intervention and comparator information",
                "fields": [
                    {"name": "intervention_type", "field_type": "text", "required": True},
                    {"name": "intervention_description", "field_type": "text", "required": True},
                    {"name": "intervention_duration", "field_type": "text", "required": False},
                    {"name": "intervention_frequency", "field_type": "text", "required": False},
                    {"name": "comparator_type", "field_type": "text", "required": True},
                    {"name": "comparator_description", "field_type": "text", "required": False},
                    {"name": "co_interventions", "field_type": "text", "required": False},
                ],
            },
            {
                "review_id": review_id,
                "name": "Outcome Data",
                "description": "Primary and secondary outcomes",
                "fields": [
                    {"name": "outcome_name", "field_type": "text", "required": True},
                    {"name": "outcome_type", "field_type": "select", "required": True,
                     "options": ["Primary", "Secondary"]},
                    {"name": "measurement_tool", "field_type": "text", "required": False},
                    {"name": "timepoint", "field_type": "text", "required": False},
                    {"name": "intervention_n", "field_type": "number", "required": True},
                    {"name": "intervention_mean", "field_type": "number", "required": False},
                    {"name": "intervention_sd", "field_type": "number", "required": False},
                    {"name": "control_n", "field_type": "number", "required": True},
                    {"name": "control_mean", "field_type": "number", "required": False},
                    {"name": "control_sd", "field_type": "number", "required": False},
                    {"name": "effect_size", "field_type": "number", "required": False},
                    {"name": "confidence_interval", "field_type": "text", "required": False},
                    {"name": "p_value", "field_type": "number", "required": False},
                ],
            },
        ]

        created = []
        for template in templates:
            result = supabase.table("extraction_templates").insert(template).execute()
            if result.data:
                created.append(result.data[0])

        return {"status": "success", "templates_created": len(created), "templates": created}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create templates: {str(e)}")
