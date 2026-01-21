from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from core.database import supabase, get_user_from_token
from core.openai_client import chat_completion
import json

router = APIRouter()

SECTION_TYPES = [
    "abstract",
    "introduction",
    "methods",
    "results",
    "discussion",
    "conclusion",
]

SECTION_PROMPTS = {
    "abstract": """Write an abstract for an academic paper on the following topic. 
Include: background/context, objective, methods, key results, and conclusion.
Keep it concise (200-250 words) and use formal academic language.""",
    "introduction": """Write an introduction section for an academic paper on the following topic.
Include: background information, problem statement, research gap, objectives, and paper structure.
Use clear academic language and proper transitions.""",
    "methods": """Write a methods/methodology section for an academic paper based on the key points provided.
Include: research design, data collection, analysis methods, and any tools/technologies used.
Be specific and detailed enough for replication.""",
    "results": """Write a results section based on the key points provided.
Present findings clearly, use appropriate academic language, avoid interpretation in this section.
Focus on objective reporting of data and observations.""",
    "discussion": """Write a discussion section based on the results provided.
Interpret findings, compare with existing literature, acknowledge limitations, and suggest implications.
Use balanced, critical academic language.""",
    "conclusion": """Write a conclusion section summarizing the paper.
Restate main findings, emphasize significance, suggest future research directions.
Keep it concise and impactful.""",
}


class CreateProjectRequest(BaseModel):
    title: str
    topic: str
    research_questions: str


class GenerateSectionRequest(BaseModel):
    project_id: str
    section_type: str
    paper_topic: str
    key_points: str
    selected_papers: List[dict]


class SaveSectionRequest(BaseModel):
    project_id: str
    section_type: str
    content: str
    word_count: int
    citations_used: List[str]


class GenerateSectionResponse(BaseModel):
    generated_text: str
    word_count: int
    citations_used: List[str]


class ProjectResponse(BaseModel):
    id: str
    user_id: str
    title: str
    topic: str
    research_questions: str
    sections: List[dict]
    created_at: str
    updated_at: str


@router.post("/create-project")
async def create_project(request: CreateProjectRequest, token: str = None):
    """Create a new AI writing project"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    project_data = {
        "user_id": user["id"],
        "title": request.title,
        "topic": request.topic,
        "research_questions": request.research_questions,
    }

    response = supabase.table("ai_writer_projects").insert(project_data).execute()

    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create project")

    return {"project_id": response.data[0]["id"]}


@router.post("/generate-section", response_model=GenerateSectionResponse)
async def generate_section(request: GenerateSectionRequest, token: str = None):
    """Generate a paper section using GPT-4"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if request.section_type not in SECTION_TYPES:
        raise HTTPException(status_code=400, detail="Invalid section type")

    # Get section prompt
    base_prompt = SECTION_PROMPTS.get(request.section_type, "")

    # Build context from selected papers
    papers_context = ""
    if request.selected_papers:
        papers_context = "\n\nKey references for citations:\n"
        for i, paper in enumerate(request.selected_papers[:5], 1):
            authors_str = ", ".join(paper.get("authors", []))
            papers_context += f"\n{i}. {paper.get('title', '')} by {authors_str} ({paper.get('year', '')})"

    # Build full prompt
    full_prompt = f"""{base_prompt}

Topic: {request.paper_topic}

Key points to include:
{request.key_points}

{papers_context}

Generate the {request.section_type} section with proper academic tone. Include citations from the provided papers where relevant using [Author, Year] format."""

    try:
        # Generate with GPT-4
        generated_text = await chat_completion(
            messages=[{"role": "user", "content": full_prompt}],
            model="gpt-4",
            temperature=0.7,
        )

        # Extract citations (simple pattern matching)
        citations = []
        if request.selected_papers:
            for paper in request.selected_papers:
                authors = paper.get("authors", [])
                if authors:
                    year = paper.get("year", "")
                    citation_key = f"[{authors[0].split()[-1]} {year}]"
                    if citation_key in generated_text:
                        citations.append(paper.get("title", ""))

        word_count = len(generated_text.split())

        return GenerateSectionResponse(
            generated_text=generated_text,
            word_count=word_count,
            citations_used=citations,
        )

    except Exception as e:
        print(f"Error generating section: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate section")


@router.post("/save-section")
async def save_section(request: SaveSectionRequest, token: str = None):
    """Save a generated section"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Check if project belongs to user
    project = (
        supabase.table("ai_writer_projects")
        .select("*")
        .eq("id", request.project_id)
        .execute()
    )
    if not project.data or project.data[0]["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    # Check if section exists
    existing = (
        supabase.table("ai_writer_sections")
        .select("*")
        .eq("project_id", request.project_id)
        .eq("section_type", request.section_type)
        .execute()
    )

    section_data = {
        "project_id": request.project_id,
        "section_type": request.section_type,
        "content": request.content,
        "word_count": request.word_count,
        "citations_used": request.citations_used,
    }

    if existing.data:
        # Update existing section
        supabase.table("ai_writer_sections").update(section_data).eq(
            "id", existing.data[0]["id"]
        ).execute()
    else:
        # Insert new section
        supabase.table("ai_writer_sections").insert(section_data).execute()

    return {"status": "success"}


@router.get("/project/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, token: str = None):
    """Get full project with all sections"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Get project
    project = (
        supabase.table("ai_writer_projects").select("*").eq("id", project_id).execute()
    )
    if not project.data:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.data[0]["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get sections
    sections = (
        supabase.table("ai_writer_sections")
        .select("*")
        .eq("project_id", project_id)
        .execute()
    )

    return ProjectResponse(
        id=project.data[0]["id"],
        user_id=project.data[0]["user_id"],
        title=project.data[0]["title"],
        topic=project.data[0]["topic"],
        research_questions=project.data[0]["research_questions"],
        sections=sections.data if sections.data else [],
        created_at=project.data[0]["created_at"],
        updated_at=project.data[0]["updated_at"],
    )


@router.get("/projects")
async def list_projects(token: str = None):
    """List user's projects"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    response = (
        supabase.table("ai_writer_projects")
        .select("*")
        .eq("user_id", user["id"])
        .order("created_at", desc=True)
        .execute()
    )

    return {"projects": response.data if response.data else []}


@router.delete("/project/{project_id}")
async def delete_project(project_id: str, token: str = None):
    """Delete a project and all its sections"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Check ownership
    project = (
        supabase.table("ai_writer_projects").select("*").eq("id", project_id).execute()
    )
    if not project.data or project.data[0]["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    # Delete sections (cascade)
    supabase.table("ai_writer_sections").delete().eq("project_id", project_id).execute()

    # Delete project
    supabase.table("ai_writer_projects").delete().eq("id", project_id).execute()

    return {"status": "success"}
