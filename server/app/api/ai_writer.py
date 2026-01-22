"""
AI Writer API - Agent F
Academic writing assistant with section generation, citation insertion, and export capabilities.
Uses Literature Search for finding and citing papers.
"""

import io
import os
import uuid
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from core.database import supabase
from core.openai_client import async_client, chat_completion

# Import from literature search for citation integration
from app.api.literature import (
    Paper,
    LiteratureSearchRequest,
    search_literature,
    generate_bibtex,
    generate_apa,
)

router = APIRouter()

# === Database Schema (for reference) ===
"""
-- Writing Projects Table
CREATE TABLE writing_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL DEFAULT 'dev-user',
    title TEXT NOT NULL,
    description TEXT,
    document_type TEXT DEFAULT 'research_paper',
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Writing Sections Table
CREATE TABLE writing_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES writing_projects(id) ON DELETE CASCADE,
    section_type TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT DEFAULT '',
    order_index INTEGER DEFAULT 0,
    word_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Writing Versions Table (for history)
CREATE TABLE writing_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES writing_projects(id) ON DELETE CASCADE,
    section_id UUID REFERENCES writing_sections(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    change_summary TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Project Citations Table
CREATE TABLE project_citations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES writing_projects(id) ON DELETE CASCADE,
    paper_title TEXT NOT NULL,
    authors TEXT[] NOT NULL,
    year TEXT,
    journal TEXT,
    doi TEXT,
    url TEXT,
    citation_key TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_writing_sections_project ON writing_sections(project_id);
CREATE INDEX idx_writing_versions_section ON writing_versions(section_id);
CREATE INDEX idx_project_citations_project ON project_citations(project_id);
"""


# === Enums and Constants ===

class SectionType(str, Enum):
    ABSTRACT = "abstract"
    INTRODUCTION = "introduction"
    LITERATURE_REVIEW = "literature_review"
    METHODS = "methods"
    RESULTS = "results"
    DISCUSSION = "discussion"
    CONCLUSION = "conclusion"
    REFERENCES = "references"
    CUSTOM = "custom"


class DocumentType(str, Enum):
    RESEARCH_PAPER = "research_paper"
    THESIS = "thesis"
    DISSERTATION = "dissertation"
    REVIEW_ARTICLE = "review_article"
    CASE_STUDY = "case_study"
    REPORT = "report"


class ExportFormat(str, Enum):
    MARKDOWN = "markdown"
    LATEX = "latex"
    DOCX = "docx"
    HTML = "html"


SECTION_ORDER = {
    SectionType.ABSTRACT: 1,
    SectionType.INTRODUCTION: 2,
    SectionType.LITERATURE_REVIEW: 3,
    SectionType.METHODS: 4,
    SectionType.RESULTS: 5,
    SectionType.DISCUSSION: 6,
    SectionType.CONCLUSION: 7,
    SectionType.REFERENCES: 8,
    SectionType.CUSTOM: 9,
}


# === Academic Writing Prompts ===

ACADEMIC_TONE_SYSTEM_PROMPT = """You are an expert academic writing assistant specializing in scientific and scholarly publications.

Your writing must:
1. Use formal, objective, and precise language
2. Avoid colloquialisms, contractions, and informal expressions
3. Use passive voice appropriately for scientific writing
4. Include hedging language where appropriate (e.g., "suggests", "indicates", "may")
5. Follow academic conventions for the specific section type
6. Be clear, concise, and well-structured
7. Use discipline-appropriate terminology
8. Maintain logical flow between sentences and paragraphs

Always produce publication-quality academic text."""

SECTION_PROMPTS = {
    SectionType.ABSTRACT: """Write a concise academic abstract for the following research.
The abstract should:
- Be 150-300 words
- Include: background/context, objective/aim, methods (briefly), key results, and conclusions
- Use past tense for methods and results
- Avoid citations and abbreviations (unless widely known)
- Capture the essence of the entire paper

Research topic and context:
{context}

Key points to cover:
{key_points}""",

    SectionType.INTRODUCTION: """Write an academic introduction section for the following research.
The introduction should:
- Start with a broad context/background (funnel approach)
- Identify the research gap or problem
- State the research question/objective clearly
- Briefly mention the approach/methodology
- Outline the paper structure (optional)
- Include appropriate citations where marked with [CITE]
- Be 2-4 paragraphs

Research topic:
{context}

Key points to cover:
{key_points}""",

    SectionType.LITERATURE_REVIEW: """Write a comprehensive literature review section for the following research topic.
The literature review should:
- Synthesize existing research on the topic
- Identify themes, patterns, and debates in the literature
- Critically evaluate and compare different studies
- Show how your research builds on or differs from existing work
- Use appropriate citations throughout (mark with [CITE: topic])
- Maintain logical organization (thematic or chronological)

Research topic:
{context}

Key themes to cover:
{key_points}""",

    SectionType.METHODS: """Write a detailed methods/methodology section for the following research.
The methods section should:
- Be written in past tense
- Provide enough detail for replication
- Include: study design, participants/samples, materials, procedures, data analysis
- Be organized with clear subheadings
- Justify methodological choices where appropriate
- Address ethical considerations if relevant

Research context:
{context}

Methods details:
{key_points}""",

    SectionType.RESULTS: """Write a results section for the following research.
The results section should:
- Present findings objectively without interpretation
- Use past tense
- Organize results logically (by hypothesis, theme, or importance)
- Reference tables and figures where appropriate (e.g., "As shown in Table 1...")
- Include statistical information if applicable
- Highlight key findings

Research context:
{context}

Key findings:
{key_points}""",

    SectionType.DISCUSSION: """Write an academic discussion section for the following research.
The discussion section should:
- Interpret and explain the results
- Compare findings with previous literature (use [CITE] markers)
- Address the research question/hypothesis
- Discuss implications (theoretical and practical)
- Acknowledge limitations
- Suggest future research directions
- Be balanced and objective

Research context:
{context}

Key findings to discuss:
{key_points}""",

    SectionType.CONCLUSION: """Write a concise conclusion section for the following research.
The conclusion should:
- Summarize key findings (without repeating results verbatim)
- Address the main research question/objective
- Highlight the contribution to the field
- Briefly mention implications
- End with a forward-looking statement
- Be 1-2 paragraphs
- NOT introduce new information

Research context:
{context}

Key points to conclude:
{key_points}""",

    SectionType.CUSTOM: """Write an academic section on the following topic.
The section should:
- Follow academic writing conventions
- Use formal, precise language
- Include citations where appropriate (mark with [CITE])
- Be well-structured with clear logic

Topic:
{context}

Key points to cover:
{key_points}""",
}

TONE_VALIDATION_PROMPT = """Analyze the following text for academic tone and style. Rate each aspect from 1-10 and provide specific feedback.

Text to analyze:
{text}

Evaluate:
1. Formality (avoids colloquialisms, contractions)
2. Objectivity (avoids personal opinions, uses evidence)
3. Precision (uses specific, accurate terminology)
4. Hedging (appropriate use of cautious language)
5. Structure (logical flow, clear organization)
6. Clarity (easy to understand, not unnecessarily complex)

Provide your analysis in JSON format:
{{
    "overall_score": <1-10>,
    "formality": {{"score": <1-10>, "feedback": "<specific feedback>"}},
    "objectivity": {{"score": <1-10>, "feedback": "<specific feedback>"}},
    "precision": {{"score": <1-10>, "feedback": "<specific feedback>"}},
    "hedging": {{"score": <1-10>, "feedback": "<specific feedback>"}},
    "structure": {{"score": <1-10>, "feedback": "<specific feedback>"}},
    "clarity": {{"score": <1-10>, "feedback": "<specific feedback>"}},
    "suggestions": ["<improvement suggestion 1>", "<improvement suggestion 2>", ...],
    "is_academic": <true/false>
}}"""


# === Pydantic Models ===

class WritingProjectCreate(BaseModel):
    """Request model for creating a writing project"""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    document_type: DocumentType = DocumentType.RESEARCH_PAPER


class WritingProjectUpdate(BaseModel):
    """Request model for updating a writing project"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    document_type: Optional[DocumentType] = None
    status: Optional[str] = None


class WritingProject(BaseModel):
    """Response model for a writing project"""
    id: str
    user_id: str
    title: str
    description: Optional[str]
    document_type: str
    status: str
    created_at: str
    updated_at: str
    sections: Optional[List[Dict]] = None
    word_count: Optional[int] = None


class SectionCreate(BaseModel):
    """Request model for creating a section"""
    section_type: SectionType
    title: Optional[str] = None
    content: Optional[str] = ""


class SectionUpdate(BaseModel):
    """Request model for updating a section"""
    title: Optional[str] = None
    content: Optional[str] = None


class SectionGenerateRequest(BaseModel):
    """Request model for AI section generation"""
    section_type: SectionType
    context: str = Field(..., min_length=10, description="Topic or research context")
    key_points: List[str] = Field(default=[], description="Key points to cover")
    include_citations: bool = Field(default=True, description="Search for and include citations")
    citation_topics: List[str] = Field(default=[], description="Topics to search for citations")
    max_words: Optional[int] = Field(default=None, ge=50, le=5000)
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)


class SectionResponse(BaseModel):
    """Response model for a section"""
    id: str
    project_id: str
    section_type: str
    title: str
    content: str
    order_index: int
    word_count: int
    created_at: str
    updated_at: str


class CitationInsertRequest(BaseModel):
    """Request model for inserting a citation"""
    search_query: str = Field(..., min_length=2)
    section_id: str
    position: Optional[int] = None  # Character position, None = end


class ToneValidationRequest(BaseModel):
    """Request model for tone validation"""
    text: str = Field(..., min_length=20)


class ToneValidationResponse(BaseModel):
    """Response model for tone validation"""
    overall_score: float
    is_academic: bool
    aspects: Dict[str, Dict[str, Any]]
    suggestions: List[str]


class ExportRequest(BaseModel):
    """Request model for export"""
    format: ExportFormat
    include_references: bool = True
    include_title_page: bool = False


class VersionHistoryResponse(BaseModel):
    """Response model for version history"""
    versions: List[Dict]
    total: int


class CitationResponse(BaseModel):
    """Response model for a citation"""
    id: str
    citation_key: str
    paper_title: str
    authors: List[str]
    year: Optional[str]
    journal: Optional[str]
    doi: Optional[str]
    formatted_citation: str


# === Helper Functions ===

def count_words(text: str) -> int:
    """Count words in text"""
    if not text:
        return 0
    return len(text.split())


def generate_citation_key(authors: List[str], year: str) -> str:
    """Generate a unique citation key"""
    if authors:
        first_author = authors[0].split()[-1] if authors[0] else "Unknown"
    else:
        first_author = "Unknown"
    year_str = year or "XXXX"
    return f"{first_author}{year_str}_{uuid.uuid4().hex[:4]}"


async def get_project_citations(project_id: str) -> List[Dict]:
    """Get all citations for a project"""
    try:
        response = (
            supabase.table("project_citations")
            .select("*")
            .eq("project_id", project_id)
            .order("created_at")
            .execute()
        )
        return response.data or []
    except Exception:
        return []


async def search_and_format_citations(
    topics: List[str],
    max_per_topic: int = 3
) -> List[Dict]:
    """Search literature and format citations for insertion"""
    all_citations = []

    for topic in topics:
        try:
            request = LiteratureSearchRequest(
                query=topic,
                sources=["semantic_scholar", "pubmed"],
                max_results=max_per_topic,
            )
            response = await search_literature(request)

            for paper in response.papers[:max_per_topic]:
                citation = {
                    "key": generate_citation_key(paper.authors, paper.year),
                    "paper": paper,
                    "formatted_apa": generate_apa(paper),
                    "formatted_bibtex": generate_bibtex(paper),
                }
                all_citations.append(citation)
        except Exception as e:
            print(f"Error searching citations for '{topic}': {e}")
            continue

    return all_citations


def format_citations_for_text(citations: List[Dict]) -> str:
    """Format citations for inline text"""
    if not citations:
        return ""

    citation_texts = []
    for c in citations:
        paper = c.get("paper")
        if paper:
            if len(paper.authors) == 1:
                author_str = paper.authors[0].split()[-1]
            elif len(paper.authors) == 2:
                author_str = f"{paper.authors[0].split()[-1]} & {paper.authors[1].split()[-1]}"
            else:
                author_str = f"{paper.authors[0].split()[-1]} et al."
            citation_texts.append(f"({author_str}, {paper.year})")

    return " ".join(citation_texts)


# === Writing Project CRUD ===

@router.post("/projects", response_model=WritingProject)
async def create_project(project: WritingProjectCreate, user_id: Optional[str] = None):
    """Create a new writing project"""
    if not user_id:
        user_id = "dev-user"

    try:
        project_data = {
            "user_id": user_id,
            "title": project.title,
            "description": project.description,
            "document_type": project.document_type.value,
            "status": "draft",
        }

        result = supabase.table("writing_projects").insert(project_data).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create project")

        return WritingProject(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")


@router.get("/projects", response_model=List[WritingProject])
async def list_projects(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """List all writing projects for a user"""
    if not user_id:
        user_id = "dev-user"

    try:
        query = (
            supabase.table("writing_projects")
            .select("*")
            .eq("user_id", user_id)
        )

        if status:
            query = query.eq("status", status)

        response = (
            query
            .order("updated_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        projects = []
        for p in response.data or []:
            # Get section count and word count for each project
            sections_resp = (
                supabase.table("writing_sections")
                .select("word_count")
                .eq("project_id", p["id"])
                .execute()
            )
            total_words = sum(s.get("word_count", 0) for s in sections_resp.data or [])

            project = WritingProject(**p)
            project.word_count = total_words
            projects.append(project)

        return projects

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list projects: {str(e)}")


@router.get("/projects/{project_id}", response_model=WritingProject)
async def get_project(project_id: str, include_sections: bool = True):
    """Get a specific writing project with optional sections"""
    try:
        # Get project
        response = (
            supabase.table("writing_projects")
            .select("*")
            .eq("id", project_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Project not found")

        project_data = response.data[0]

        # Get sections if requested
        sections = []
        total_words = 0
        if include_sections:
            sections_resp = (
                supabase.table("writing_sections")
                .select("*")
                .eq("project_id", project_id)
                .order("order_index")
                .execute()
            )
            sections = sections_resp.data or []
            total_words = sum(s.get("word_count", 0) for s in sections)

        project = WritingProject(**project_data)
        project.sections = sections
        project.word_count = total_words

        return project

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project: {str(e)}")


@router.patch("/projects/{project_id}", response_model=WritingProject)
async def update_project(project_id: str, update: WritingProjectUpdate):
    """Update a writing project"""
    try:
        update_data = {k: v for k, v in update.model_dump().items() if v is not None}

        if "document_type" in update_data:
            update_data["document_type"] = update_data["document_type"].value

        update_data["updated_at"] = datetime.utcnow().isoformat()

        result = (
            supabase.table("writing_projects")
            .update(update_data)
            .eq("id", project_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Project not found")

        return WritingProject(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update project: {str(e)}")


@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a writing project and all its sections"""
    try:
        # Delete is cascaded via foreign key constraints
        result = (
            supabase.table("writing_projects")
            .delete()
            .eq("id", project_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Project not found")

        return {"status": "success", "message": "Project deleted"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")


# === Section Management ===

@router.post("/projects/{project_id}/sections", response_model=SectionResponse)
async def create_section(project_id: str, section: SectionCreate):
    """Create a new section in a project"""
    try:
        # Verify project exists
        project_resp = (
            supabase.table("writing_projects")
            .select("id")
            .eq("id", project_id)
            .execute()
        )

        if not project_resp.data:
            raise HTTPException(status_code=404, detail="Project not found")

        # Get the next order index
        existing_sections = (
            supabase.table("writing_sections")
            .select("order_index")
            .eq("project_id", project_id)
            .order("order_index", desc=True)
            .limit(1)
            .execute()
        )

        next_order = 0
        if existing_sections.data:
            next_order = existing_sections.data[0]["order_index"] + 1
        else:
            # Use default order for section type
            next_order = SECTION_ORDER.get(section.section_type, 9)

        # Default title based on section type
        title = section.title or section.section_type.value.replace("_", " ").title()

        section_data = {
            "project_id": project_id,
            "section_type": section.section_type.value,
            "title": title,
            "content": section.content or "",
            "order_index": next_order,
            "word_count": count_words(section.content or ""),
        }

        result = supabase.table("writing_sections").insert(section_data).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create section")

        # Update project timestamp
        supabase.table("writing_projects").update(
            {"updated_at": datetime.utcnow().isoformat()}
        ).eq("id", project_id).execute()

        return SectionResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create section: {str(e)}")


@router.get("/projects/{project_id}/sections", response_model=List[SectionResponse])
async def list_sections(project_id: str):
    """List all sections in a project"""
    try:
        response = (
            supabase.table("writing_sections")
            .select("*")
            .eq("project_id", project_id)
            .order("order_index")
            .execute()
        )

        return [SectionResponse(**s) for s in response.data or []]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sections: {str(e)}")


@router.get("/sections/{section_id}", response_model=SectionResponse)
async def get_section(section_id: str):
    """Get a specific section"""
    try:
        response = (
            supabase.table("writing_sections")
            .select("*")
            .eq("id", section_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Section not found")

        return SectionResponse(**response.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get section: {str(e)}")


@router.patch("/sections/{section_id}", response_model=SectionResponse)
async def update_section(section_id: str, update: SectionUpdate, save_version: bool = True):
    """Update a section and optionally save to version history"""
    try:
        # Get current section for versioning
        current = (
            supabase.table("writing_sections")
            .select("*")
            .eq("id", section_id)
            .execute()
        )

        if not current.data:
            raise HTTPException(status_code=404, detail="Section not found")

        current_section = current.data[0]

        # Save version if content is changing
        if save_version and update.content and update.content != current_section.get("content"):
            # Get next version number
            versions = (
                supabase.table("writing_versions")
                .select("version_number")
                .eq("section_id", section_id)
                .order("version_number", desc=True)
                .limit(1)
                .execute()
            )

            next_version = 1
            if versions.data:
                next_version = versions.data[0]["version_number"] + 1

            version_data = {
                "project_id": current_section["project_id"],
                "section_id": section_id,
                "content": current_section["content"],
                "version_number": next_version,
                "change_summary": f"Version {next_version} saved before update",
            }

            supabase.table("writing_versions").insert(version_data).execute()

        # Update section
        update_data = {k: v for k, v in update.model_dump().items() if v is not None}

        if "content" in update_data:
            update_data["word_count"] = count_words(update_data["content"])

        update_data["updated_at"] = datetime.utcnow().isoformat()

        result = (
            supabase.table("writing_sections")
            .update(update_data)
            .eq("id", section_id)
            .execute()
        )

        # Update project timestamp
        supabase.table("writing_projects").update(
            {"updated_at": datetime.utcnow().isoformat()}
        ).eq("id", current_section["project_id"]).execute()

        return SectionResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update section: {str(e)}")


@router.delete("/sections/{section_id}")
async def delete_section(section_id: str):
    """Delete a section"""
    try:
        # Get section to find project
        section = (
            supabase.table("writing_sections")
            .select("project_id")
            .eq("id", section_id)
            .execute()
        )

        if not section.data:
            raise HTTPException(status_code=404, detail="Section not found")

        project_id = section.data[0]["project_id"]

        # Delete section (versions cascade deleted)
        supabase.table("writing_sections").delete().eq("id", section_id).execute()

        # Update project timestamp
        supabase.table("writing_projects").update(
            {"updated_at": datetime.utcnow().isoformat()}
        ).eq("id", project_id).execute()

        return {"status": "success", "message": "Section deleted"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete section: {str(e)}")


# === AI Section Generation ===

@router.post("/projects/{project_id}/generate-section", response_model=SectionResponse)
async def generate_section(
    project_id: str,
    request: SectionGenerateRequest,
    auto_save: bool = True,
):
    """Generate a section using AI with optional citation integration"""
    try:
        # Verify project exists
        project_resp = (
            supabase.table("writing_projects")
            .select("*")
            .eq("id", project_id)
            .execute()
        )

        if not project_resp.data:
            raise HTTPException(status_code=404, detail="Project not found")

        project = project_resp.data[0]

        # Prepare citations if requested
        citations = []
        citation_context = ""

        if request.include_citations and request.citation_topics:
            citations = await search_and_format_citations(request.citation_topics)
            if citations:
                citation_context = "\n\nAvailable citations to use:\n"
                for c in citations:
                    paper = c.get("paper")
                    if paper:
                        citation_context += f"- [{c['key']}]: {paper.title} ({paper.year})\n"
                citation_context += "\nInsert citations using the format [key] where appropriate."

        # Format key points
        key_points_str = "\n".join(f"- {point}" for point in request.key_points) if request.key_points else "None specified"

        # Get the section-specific prompt
        section_prompt = SECTION_PROMPTS.get(request.section_type, SECTION_PROMPTS[SectionType.CUSTOM])

        user_prompt = section_prompt.format(
            context=request.context,
            key_points=key_points_str,
        )

        if citation_context:
            user_prompt += citation_context

        if request.max_words:
            user_prompt += f"\n\nTarget length: approximately {request.max_words} words."

        # Add document type context
        user_prompt += f"\n\nDocument type: {project['document_type'].replace('_', ' ')}."

        # Generate content with GPT-4
        messages = [
            {"role": "system", "content": ACADEMIC_TONE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        response = await async_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=request.temperature,
            max_tokens=4000,
        )

        generated_content = response.choices[0].message.content

        # Save generated section if auto_save is enabled
        if auto_save:
            # Get the next order index
            existing = (
                supabase.table("writing_sections")
                .select("order_index")
                .eq("project_id", project_id)
                .order("order_index", desc=True)
                .limit(1)
                .execute()
            )

            next_order = SECTION_ORDER.get(request.section_type, 9)
            if existing.data:
                # Check if this section type already exists
                same_type = (
                    supabase.table("writing_sections")
                    .select("id")
                    .eq("project_id", project_id)
                    .eq("section_type", request.section_type.value)
                    .execute()
                )
                if same_type.data:
                    next_order = existing.data[0]["order_index"] + 1

            section_title = request.section_type.value.replace("_", " ").title()

            section_data = {
                "project_id": project_id,
                "section_type": request.section_type.value,
                "title": section_title,
                "content": generated_content,
                "order_index": next_order,
                "word_count": count_words(generated_content),
            }

            result = supabase.table("writing_sections").insert(section_data).execute()

            # Save citations to project
            if citations:
                for c in citations:
                    paper = c.get("paper")
                    if paper:
                        citation_data = {
                            "project_id": project_id,
                            "paper_title": paper.title,
                            "authors": paper.authors,
                            "year": paper.year,
                            "journal": paper.journal,
                            "doi": paper.doi,
                            "url": paper.url,
                            "citation_key": c["key"],
                        }
                        try:
                            supabase.table("project_citations").insert(citation_data).execute()
                        except Exception:
                            pass  # Skip duplicate citations

            # Update project timestamp
            supabase.table("writing_projects").update(
                {"updated_at": datetime.utcnow().isoformat()}
            ).eq("id", project_id).execute()

            return SectionResponse(**result.data[0])
        else:
            # Return generated content without saving
            return SectionResponse(
                id="preview",
                project_id=project_id,
                section_type=request.section_type.value,
                title=request.section_type.value.replace("_", " ").title(),
                content=generated_content,
                order_index=0,
                word_count=count_words(generated_content),
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat(),
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate section: {str(e)}")


# === Citation Management ===

@router.post("/projects/{project_id}/search-citations")
async def search_citations_for_project(project_id: str, query: str, max_results: int = 10):
    """Search for citations to add to a project"""
    try:
        request = LiteratureSearchRequest(
            query=query,
            sources=["semantic_scholar", "pubmed", "arxiv"],
            max_results=max_results,
        )

        response = await search_literature(request)

        # Format results with citation keys
        results = []
        for paper in response.papers:
            citation_key = generate_citation_key(paper.authors, paper.year)
            results.append({
                "citation_key": citation_key,
                "paper": paper.model_dump(),
                "formatted_apa": generate_apa(paper),
                "formatted_bibtex": generate_bibtex(paper),
            })

        return {"results": results, "total": len(results)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search citations: {str(e)}")


@router.post("/projects/{project_id}/add-citation", response_model=CitationResponse)
async def add_citation_to_project(project_id: str, paper: Paper):
    """Add a citation to a project"""
    try:
        citation_key = generate_citation_key(paper.authors, paper.year)

        citation_data = {
            "project_id": project_id,
            "paper_title": paper.title,
            "authors": paper.authors,
            "year": paper.year,
            "journal": paper.journal,
            "doi": paper.doi,
            "url": paper.url,
            "citation_key": citation_key,
        }

        result = supabase.table("project_citations").insert(citation_data).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to add citation")

        data = result.data[0]

        return CitationResponse(
            id=data["id"],
            citation_key=data["citation_key"],
            paper_title=data["paper_title"],
            authors=data["authors"],
            year=data["year"],
            journal=data["journal"],
            doi=data["doi"],
            formatted_citation=generate_apa(paper),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add citation: {str(e)}")


@router.get("/projects/{project_id}/citations")
async def get_project_citations_endpoint(project_id: str):
    """Get all citations for a project"""
    try:
        citations = await get_project_citations(project_id)

        formatted = []
        for c in citations:
            paper = Paper(
                title=c.get("paper_title", ""),
                authors=c.get("authors", []),
                year=c.get("year", ""),
                journal=c.get("journal"),
                doi=c.get("doi"),
                url=c.get("url"),
                source="project_citation",
            )

            formatted.append({
                "id": c["id"],
                "citation_key": c["citation_key"],
                "paper_title": c["paper_title"],
                "authors": c["authors"],
                "year": c["year"],
                "formatted_apa": generate_apa(paper),
                "formatted_bibtex": generate_bibtex(paper),
            })

        return {"citations": formatted, "total": len(formatted)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get citations: {str(e)}")


@router.delete("/projects/{project_id}/citations/{citation_id}")
async def remove_citation_from_project(project_id: str, citation_id: str):
    """Remove a citation from a project"""
    try:
        result = (
            supabase.table("project_citations")
            .delete()
            .eq("id", citation_id)
            .eq("project_id", project_id)
            .execute()
        )

        return {"status": "success", "message": "Citation removed"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove citation: {str(e)}")


# === Version History ===

@router.get("/sections/{section_id}/versions", response_model=VersionHistoryResponse)
async def get_section_versions(section_id: str, limit: int = 20):
    """Get version history for a section"""
    try:
        response = (
            supabase.table("writing_versions")
            .select("*")
            .eq("section_id", section_id)
            .order("version_number", desc=True)
            .limit(limit)
            .execute()
        )

        return VersionHistoryResponse(
            versions=response.data or [],
            total=len(response.data or []),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get versions: {str(e)}")


@router.post("/sections/{section_id}/restore/{version_id}")
async def restore_section_version(section_id: str, version_id: str):
    """Restore a section to a previous version"""
    try:
        # Get the version
        version = (
            supabase.table("writing_versions")
            .select("*")
            .eq("id", version_id)
            .eq("section_id", section_id)
            .execute()
        )

        if not version.data:
            raise HTTPException(status_code=404, detail="Version not found")

        # Save current content as new version
        current = (
            supabase.table("writing_sections")
            .select("*")
            .eq("id", section_id)
            .execute()
        )

        if current.data:
            current_section = current.data[0]

            # Get next version number
            versions = (
                supabase.table("writing_versions")
                .select("version_number")
                .eq("section_id", section_id)
                .order("version_number", desc=True)
                .limit(1)
                .execute()
            )

            next_version = (versions.data[0]["version_number"] + 1) if versions.data else 1

            version_data = {
                "project_id": current_section["project_id"],
                "section_id": section_id,
                "content": current_section["content"],
                "version_number": next_version,
                "change_summary": f"Saved before restoring to version {version.data[0]['version_number']}",
            }

            supabase.table("writing_versions").insert(version_data).execute()

        # Restore the version
        restore_content = version.data[0]["content"]

        result = (
            supabase.table("writing_sections")
            .update({
                "content": restore_content,
                "word_count": count_words(restore_content),
                "updated_at": datetime.utcnow().isoformat(),
            })
            .eq("id", section_id)
            .execute()
        )

        return {
            "status": "success",
            "message": f"Restored to version {version.data[0]['version_number']}",
            "section": result.data[0] if result.data else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restore version: {str(e)}")


# === Academic Tone Validation ===

@router.post("/validate-tone", response_model=ToneValidationResponse)
async def validate_academic_tone(request: ToneValidationRequest):
    """Validate text for academic tone and style"""
    try:
        messages = [
            {"role": "system", "content": "You are an expert in academic writing and style analysis. Respond only with valid JSON."},
            {"role": "user", "content": TONE_VALIDATION_PROMPT.format(text=request.text)},
        ]

        response = await async_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.3,
            max_tokens=1500,
        )

        result_text = response.choices[0].message.content

        # Parse JSON response
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(result_text)
        except json.JSONDecodeError:
            # Fallback to default response
            result = {
                "overall_score": 5,
                "formality": {"score": 5, "feedback": "Unable to analyze"},
                "objectivity": {"score": 5, "feedback": "Unable to analyze"},
                "precision": {"score": 5, "feedback": "Unable to analyze"},
                "hedging": {"score": 5, "feedback": "Unable to analyze"},
                "structure": {"score": 5, "feedback": "Unable to analyze"},
                "clarity": {"score": 5, "feedback": "Unable to analyze"},
                "suggestions": ["Please try again with different text"],
                "is_academic": True,
            }

        return ToneValidationResponse(
            overall_score=result.get("overall_score", 5),
            is_academic=result.get("is_academic", True),
            aspects={
                "formality": result.get("formality", {}),
                "objectivity": result.get("objectivity", {}),
                "precision": result.get("precision", {}),
                "hedging": result.get("hedging", {}),
                "structure": result.get("structure", {}),
                "clarity": result.get("clarity", {}),
            },
            suggestions=result.get("suggestions", []),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate tone: {str(e)}")


@router.post("/improve-text")
async def improve_academic_text(text: str, focus_areas: Optional[List[str]] = None):
    """Improve text to be more academic"""
    try:
        focus_str = ", ".join(focus_areas) if focus_areas else "overall academic quality"

        prompt = f"""Improve the following text to make it more suitable for academic publication.
Focus on: {focus_str}

Original text:
{text}

Provide the improved text only, without explanations."""

        messages = [
            {"role": "system", "content": ACADEMIC_TONE_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        response = await async_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.5,
            max_tokens=2000,
        )

        improved_text = response.choices[0].message.content

        return {
            "original_text": text,
            "improved_text": improved_text,
            "word_count_original": count_words(text),
            "word_count_improved": count_words(improved_text),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to improve text: {str(e)}")


# === Export Functions ===

def export_to_markdown(project: dict, sections: List[dict], citations: List[dict]) -> str:
    """Export project to Markdown format"""
    md = f"# {project['title']}\n\n"

    if project.get('description'):
        md += f"*{project['description']}*\n\n"

    md += "---\n\n"

    # Add sections
    for section in sections:
        md += f"## {section['title']}\n\n"
        md += f"{section['content']}\n\n"

    # Add references if there are citations
    if citations:
        md += "## References\n\n"
        for c in citations:
            paper = Paper(
                title=c.get("paper_title", ""),
                authors=c.get("authors", []),
                year=c.get("year", ""),
                journal=c.get("journal"),
                doi=c.get("doi"),
                url=c.get("url"),
                source="export",
            )
            md += f"- {generate_apa(paper)}\n"

    return md


def export_to_latex(project: dict, sections: List[dict], citations: List[dict]) -> str:
    """Export project to LaTeX format"""
    latex = r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{natbib}

"""

    # Escape special LaTeX characters
    def escape_latex(text):
        if not text:
            return ""
        chars = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\^{}',
        }
        for char, replacement in chars.items():
            text = text.replace(char, replacement)
        return text

    latex += f"\\title{{{escape_latex(project['title'])}}}\n"
    latex += r"\author{Author Name}"
    latex += "\n"
    latex += r"\date{\today}"
    latex += "\n\n"
    latex += r"\begin{document}"
    latex += "\n\n"
    latex += r"\maketitle"
    latex += "\n\n"

    # Add sections
    for section in sections:
        section_type = section.get('section_type', 'custom')
        title = escape_latex(section.get('title', section_type.replace('_', ' ').title()))
        content = escape_latex(section.get('content', ''))

        if section_type == 'abstract':
            latex += r"\begin{abstract}"
            latex += f"\n{content}\n"
            latex += r"\end{abstract}"
            latex += "\n\n"
        else:
            latex += f"\\section{{{title}}}\n"
            latex += f"{content}\n\n"

    # Add bibliography if there are citations
    if citations:
        latex += r"\section{References}"
        latex += "\n"
        latex += r"\begin{thebibliography}{99}"
        latex += "\n"

        for c in citations:
            key = c.get('citation_key', 'unknown')
            authors = ", ".join(c.get('authors', ['Unknown']))
            title = escape_latex(c.get('paper_title', 'Untitled'))
            year = c.get('year', 'n.d.')
            journal = escape_latex(c.get('journal', ''))

            latex += f"\\bibitem{{{key}}}\n"
            latex += f"{escape_latex(authors)} ({year}). {title}."
            if journal:
                latex += f" \\textit{{{journal}}}."
            latex += "\n\n"

        latex += r"\end{thebibliography}"
        latex += "\n"

    latex += r"\end{document}"

    return latex


def export_to_docx_content(project: dict, sections: List[dict], citations: List[dict]) -> str:
    """
    Export project to DOCX-compatible format.
    Returns a simple text format that can be used with python-docx or as plain text.
    For full DOCX support, python-docx would be needed.
    """
    # For simplicity, we'll create a structured text format
    # In production, you'd use python-docx to create a proper .docx file

    content = f"TITLE: {project['title']}\n"
    content += "=" * 60 + "\n\n"

    if project.get('description'):
        content += f"Description: {project['description']}\n\n"

    # Add sections
    for section in sections:
        content += "-" * 40 + "\n"
        content += f"SECTION: {section['title'].upper()}\n"
        content += "-" * 40 + "\n\n"
        content += f"{section['content']}\n\n"

    # Add references
    if citations:
        content += "=" * 60 + "\n"
        content += "REFERENCES\n"
        content += "=" * 60 + "\n\n"

        for i, c in enumerate(citations, 1):
            paper = Paper(
                title=c.get("paper_title", ""),
                authors=c.get("authors", []),
                year=c.get("year", ""),
                journal=c.get("journal"),
                doi=c.get("doi"),
                url=c.get("url"),
                source="export",
            )
            content += f"[{i}] {generate_apa(paper)}\n\n"

    return content


def export_to_html(project: dict, sections: List[dict], citations: List[dict]) -> str:
    """Export project to HTML format"""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project['title']}</title>
    <style>
        body {{
            font-family: 'Times New Roman', Times, serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{
            text-align: center;
            margin-bottom: 10px;
        }}
        .description {{
            text-align: center;
            font-style: italic;
            color: #666;
            margin-bottom: 30px;
        }}
        h2 {{
            margin-top: 30px;
            border-bottom: 1px solid #ccc;
            padding-bottom: 10px;
        }}
        .abstract {{
            background-color: #f9f9f9;
            padding: 20px;
            border-left: 3px solid #0066cc;
            margin: 20px 0;
        }}
        .references {{
            font-size: 0.9em;
        }}
        .references li {{
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <h1>{project['title']}</h1>
"""

    if project.get('description'):
        html += f'    <p class="description">{project["description"]}</p>\n'

    # Add sections
    for section in sections:
        section_type = section.get('section_type', 'custom')
        title = section.get('title', section_type.replace('_', ' ').title())
        content = section.get('content', '').replace('\n', '<br>\n        ')

        if section_type == 'abstract':
            html += f"""
    <div class="abstract">
        <h2>{title}</h2>
        <p>{content}</p>
    </div>
"""
        else:
            html += f"""
    <h2>{title}</h2>
    <p>{content}</p>
"""

    # Add references
    if citations:
        html += """
    <h2>References</h2>
    <ol class="references">
"""
        for c in citations:
            paper = Paper(
                title=c.get("paper_title", ""),
                authors=c.get("authors", []),
                year=c.get("year", ""),
                journal=c.get("journal"),
                doi=c.get("doi"),
                url=c.get("url"),
                source="export",
            )
            html += f"        <li>{generate_apa(paper)}</li>\n"

        html += "    </ol>\n"

    html += """
</body>
</html>"""

    return html


@router.post("/projects/{project_id}/export")
async def export_project(project_id: str, request: ExportRequest):
    """Export a project to the specified format"""
    try:
        # Get project
        project_resp = (
            supabase.table("writing_projects")
            .select("*")
            .eq("id", project_id)
            .execute()
        )

        if not project_resp.data:
            raise HTTPException(status_code=404, detail="Project not found")

        project = project_resp.data[0]

        # Get sections
        sections_resp = (
            supabase.table("writing_sections")
            .select("*")
            .eq("project_id", project_id)
            .order("order_index")
            .execute()
        )

        sections = sections_resp.data or []

        # Get citations if needed
        citations = []
        if request.include_references:
            citations = await get_project_citations(project_id)

        # Generate export
        if request.format == ExportFormat.MARKDOWN:
            content = export_to_markdown(project, sections, citations)
            content_type = "text/markdown"
            file_ext = "md"
        elif request.format == ExportFormat.LATEX:
            content = export_to_latex(project, sections, citations)
            content_type = "application/x-latex"
            file_ext = "tex"
        elif request.format == ExportFormat.DOCX:
            content = export_to_docx_content(project, sections, citations)
            content_type = "text/plain"  # Would be application/vnd.openxmlformats-officedocument.wordprocessingml.document for real docx
            file_ext = "txt"  # Would be .docx with python-docx
        elif request.format == ExportFormat.HTML:
            content = export_to_html(project, sections, citations)
            content_type = "text/html"
            file_ext = "html"
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")

        # Create filename
        safe_title = "".join(c for c in project['title'] if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
        filename = f"{safe_title}.{file_ext}"

        return {
            "filename": filename,
            "content": content,
            "content_type": content_type,
            "format": request.format.value,
            "sections_count": len(sections),
            "citations_count": len(citations),
            "word_count": sum(s.get("word_count", 0) for s in sections),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export project: {str(e)}")


@router.get("/projects/{project_id}/download/{format}")
async def download_project(project_id: str, format: ExportFormat, include_references: bool = True):
    """Download a project as a file"""
    try:
        export_request = ExportRequest(format=format, include_references=include_references)
        result = await export_project(project_id, export_request)

        content = result["content"]
        filename = result["filename"]
        content_type = result["content_type"]

        # Create streaming response
        return StreamingResponse(
            io.BytesIO(content.encode('utf-8')),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download project: {str(e)}")


# === Writing Statistics ===

@router.get("/projects/{project_id}/stats")
async def get_project_stats(project_id: str):
    """Get writing statistics for a project"""
    try:
        # Get sections
        sections_resp = (
            supabase.table("writing_sections")
            .select("*")
            .eq("project_id", project_id)
            .execute()
        )

        sections = sections_resp.data or []

        # Get citations
        citations = await get_project_citations(project_id)

        # Get version count
        versions_resp = (
            supabase.table("writing_versions")
            .select("id")
            .eq("project_id", project_id)
            .execute()
        )

        # Calculate stats
        total_words = sum(s.get("word_count", 0) for s in sections)
        section_stats = []

        for section in sections:
            section_stats.append({
                "section_type": section["section_type"],
                "title": section["title"],
                "word_count": section.get("word_count", 0),
            })

        return {
            "total_sections": len(sections),
            "total_words": total_words,
            "total_citations": len(citations),
            "total_versions": len(versions_resp.data or []),
            "sections": section_stats,
            "estimated_pages": round(total_words / 250, 1),  # ~250 words per page
            "estimated_reading_time_minutes": round(total_words / 200, 1),  # ~200 words per minute
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
