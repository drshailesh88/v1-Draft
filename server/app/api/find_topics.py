"""
Find Topics / Research Gap Finder API
Research topic discovery, trending topics, gap analysis, and research questions generation.
"""

import asyncio
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from core.database import supabase
from core.openai_client import chat_completion, generate_embedding

# Import literature search functions for topic validation
from app.api.literature import (
    search_pubmed,
    search_arxiv,
    search_semantic_scholar,
    Paper,
    deduplicate_papers,
)

router = APIRouter()


# === Pydantic Models ===


class TopicDiscoveryRequest(BaseModel):
    """Request model for topic discovery"""

    field: str = Field(..., min_length=1, description="Research field or domain")
    keywords: List[str] = Field(
        default=[], description="Specific keywords to focus on"
    )
    max_topics: int = Field(default=10, ge=1, le=50, description="Maximum topics to return")


class Topic(BaseModel):
    """Model for a research topic"""

    id: Optional[str] = None
    name: str
    description: str
    field: str
    keywords: List[str] = []
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    trend_score: Optional[float] = None
    paper_count: Optional[int] = None
    recent_paper_count: Optional[int] = None
    related_topics: List[str] = []
    potential_questions: List[str] = []


class TopicDiscoveryResponse(BaseModel):
    """Response model for topic discovery"""

    topics: List[Topic]
    field: str
    keywords: List[str]
    generated_at: str


class TrendingTopicsRequest(BaseModel):
    """Request model for trending topics"""

    field: str = Field(..., min_length=1, description="Research field")
    time_window: str = Field(
        default="1year",
        description="Time window: 1month, 3months, 6months, 1year, 2years",
    )
    max_topics: int = Field(default=10, ge=1, le=30)


class TrendingTopic(BaseModel):
    """Model for a trending topic"""

    name: str
    description: str
    trend_score: float = Field(ge=0.0, le=1.0)
    growth_rate: Optional[str] = None
    recent_papers: int = 0
    key_papers: List[str] = []
    emerging: bool = False


class TrendingTopicsResponse(BaseModel):
    """Response model for trending topics"""

    trending_topics: List[TrendingTopic]
    field: str
    time_window: str
    analysis_date: str


class ResearchGapRequest(BaseModel):
    """Request model for research gap analysis"""

    field: str = Field(..., min_length=1, description="Research field")
    subtopic: Optional[str] = Field(default=None, description="Specific subtopic to analyze")
    keywords: List[str] = Field(default=[], description="Keywords to focus on")


class ResearchGap(BaseModel):
    """Model for a research gap"""

    title: str
    description: str
    gap_type: str  # methodological, theoretical, empirical, application
    importance: str  # high, medium, low
    difficulty: str  # high, medium, low
    existing_work: List[str] = []
    suggested_approaches: List[str] = []
    potential_impact: str


class ResearchGapResponse(BaseModel):
    """Response model for research gap analysis"""

    gaps: List[ResearchGap]
    field: str
    subtopic: Optional[str]
    analysis_summary: str
    total_papers_analyzed: int


class TopicClusterRequest(BaseModel):
    """Request model for topic clustering"""

    field: str = Field(..., min_length=1, description="Research field")
    keywords: List[str] = Field(default=[], description="Keywords to include")
    num_clusters: int = Field(default=5, ge=2, le=15)


class ClusterNode(BaseModel):
    """Model for a cluster node (for visualization)"""

    id: str
    name: str
    size: float  # Relative size for visualization
    group: int  # Cluster group number
    keywords: List[str] = []


class ClusterLink(BaseModel):
    """Model for a cluster link (for visualization)"""

    source: str
    target: str
    strength: float  # Connection strength


class TopicClusterResponse(BaseModel):
    """Response model for topic clustering"""

    nodes: List[ClusterNode]
    links: List[ClusterLink]
    clusters: List[Dict[str, Any]]
    field: str


class RelatedTopicsRequest(BaseModel):
    """Request model for related topics"""

    topic: str = Field(..., min_length=1, description="Source topic")
    field: str = Field(..., min_length=1, description="Research field")
    depth: int = Field(default=2, ge=1, le=3, description="Exploration depth")
    max_related: int = Field(default=10, ge=1, le=30)


class RelatedTopic(BaseModel):
    """Model for a related topic"""

    name: str
    relation_type: str  # parent, child, sibling, related, emerging
    relation_strength: float = Field(ge=0.0, le=1.0)
    description: str
    common_keywords: List[str] = []


class RelatedTopicsResponse(BaseModel):
    """Response model for related topics"""

    source_topic: str
    related_topics: List[RelatedTopic]
    field: str


class ResearchQuestionsRequest(BaseModel):
    """Request model for research questions generation"""

    topic: str = Field(..., min_length=1, description="Research topic")
    field: str = Field(..., min_length=1, description="Research field")
    question_type: str = Field(
        default="all",
        description="Type: exploratory, descriptive, explanatory, evaluative, all",
    )
    num_questions: int = Field(default=10, ge=1, le=30)


class ResearchQuestion(BaseModel):
    """Model for a research question"""

    question: str
    type: str  # exploratory, descriptive, explanatory, evaluative
    rationale: str
    methodology_hints: List[str] = []
    related_concepts: List[str] = []
    novelty_score: float = Field(ge=0.0, le=1.0)


class ResearchQuestionsResponse(BaseModel):
    """Response model for research questions"""

    questions: List[ResearchQuestion]
    topic: str
    field: str


class TopicValidationRequest(BaseModel):
    """Request model for topic validation"""

    topic: str = Field(..., min_length=1, description="Topic to validate")
    field: str = Field(..., min_length=1, description="Research field")


class TopicValidationResponse(BaseModel):
    """Response model for topic validation"""

    topic: str
    is_valid: bool
    relevance_score: float
    paper_count: int
    recent_papers: List[Paper]
    validation_notes: str
    suggested_refinements: List[str] = []


class SaveTopicRequest(BaseModel):
    """Request model for saving a topic"""

    topic: Topic
    notes: Optional[str] = None
    tags: List[str] = Field(default=[])


class HotTopicsRequest(BaseModel):
    """Request model for hot topics"""

    field: str = Field(..., min_length=1, description="Research field")
    max_topics: int = Field(default=15, ge=1, le=30)


class HotTopic(BaseModel):
    """Model for a hot topic"""

    name: str
    description: str
    heat_score: float = Field(ge=0.0, le=1.0)
    reasons: List[str] = []
    key_researchers: List[str] = []
    key_institutions: List[str] = []
    funding_opportunities: List[str] = []
    recent_breakthroughs: List[str] = []


class HotTopicsResponse(BaseModel):
    """Response model for hot topics"""

    hot_topics: List[HotTopic]
    field: str
    analysis_date: str


# === Helper Functions ===


async def analyze_topics_with_gpt(
    field: str, keywords: List[str], context: str, task: str
) -> str:
    """Use GPT-4 to analyze topics"""
    messages = [
        {
            "role": "system",
            "content": """You are an expert academic research advisor specializing in
identifying research topics, trends, and gaps across all scientific disciplines.
Provide detailed, accurate, and actionable insights. Always respond with valid JSON.""",
        },
        {
            "role": "user",
            "content": f"""Field: {field}
Keywords: {', '.join(keywords) if keywords else 'None specified'}

Context:
{context}

Task: {task}

Respond with valid JSON only, no additional text.""",
        },
    ]

    response = await chat_completion(messages, model="gpt-4", temperature=0.7)
    return response


async def get_recent_literature_context(
    field: str, keywords: List[str], max_papers: int = 20
) -> tuple[str, List[Paper]]:
    """Get recent literature to provide context for topic analysis"""
    query = f"{field} {' '.join(keywords)}" if keywords else field

    # Search across sources concurrently
    results = await asyncio.gather(
        search_semantic_scholar(query, max_results=max_papers, year_start=2022),
        search_arxiv(query, max_results=max_papers, year_start=2022),
        search_pubmed(query, max_results=max_papers, year_start=2022),
    )

    all_papers = []
    for paper_list in results:
        all_papers.extend(paper_list)

    # Deduplicate
    papers = deduplicate_papers(all_papers)[:max_papers]

    # Create context string
    context_parts = []
    for i, paper in enumerate(papers[:15], 1):
        context_parts.append(
            f"{i}. {paper.title} ({paper.year}) - {paper.journal or paper.source}"
        )

    context = "\n".join(context_parts) if context_parts else "No recent papers found."
    return context, papers


# === API Endpoints ===


@router.post("/discover", response_model=TopicDiscoveryResponse)
async def discover_topics(request: TopicDiscoveryRequest):
    """
    Discover research topics based on field and keywords.

    Uses AI to analyze the research landscape and identify promising topics.
    """
    try:
        # Get literature context
        context, papers = await get_recent_literature_context(
            request.field, request.keywords
        )

        task = f"""Identify {request.max_topics} promising research topics in this field.

For each topic, provide:
- name: Concise topic name
- description: 2-3 sentence description
- keywords: 3-5 relevant keywords
- relevance_score: 0-1 score for current relevance
- related_topics: 2-3 related topic names
- potential_questions: 2-3 research questions

Return as JSON array with structure:
[{{"name": "...", "description": "...", "keywords": [...], "relevance_score": 0.8, "related_topics": [...], "potential_questions": [...]}}]"""

        response = await analyze_topics_with_gpt(
            request.field, request.keywords, context, task
        )

        # Parse response
        try:
            # Handle potential markdown code blocks
            clean_response = response.strip()
            if clean_response.startswith("```"):
                clean_response = clean_response.split("```")[1]
                if clean_response.startswith("json"):
                    clean_response = clean_response[4:]
            clean_response = clean_response.strip()

            topics_data = json.loads(clean_response)
        except json.JSONDecodeError:
            # Fallback parsing
            topics_data = []

        topics = []
        for td in topics_data[:request.max_topics]:
            topic = Topic(
                name=td.get("name", "Unknown Topic"),
                description=td.get("description", ""),
                field=request.field,
                keywords=td.get("keywords", []),
                relevance_score=min(1.0, max(0.0, td.get("relevance_score", 0.5))),
                paper_count=len(papers),
                related_topics=td.get("related_topics", []),
                potential_questions=td.get("potential_questions", []),
            )
            topics.append(topic)

        return TopicDiscoveryResponse(
            topics=topics,
            field=request.field,
            keywords=request.keywords,
            generated_at=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Topic discovery failed: {str(e)}")


@router.post("/trending", response_model=TrendingTopicsResponse)
async def get_trending_topics(request: TrendingTopicsRequest):
    """
    Identify trending topics in a research field based on recent literature.

    Analyzes publication patterns to find emerging and growing research areas.
    """
    try:
        # Determine year start based on time window
        year_map = {
            "1month": 2024,
            "3months": 2024,
            "6months": 2024,
            "1year": 2024,
            "2years": 2023,
        }
        year_start = year_map.get(request.time_window, 2024)

        # Get recent literature
        context, papers = await get_recent_literature_context(
            request.field, [], max_papers=30
        )

        task = f"""Analyze these recent publications to identify {request.max_topics} trending topics.

For each trending topic, provide:
- name: Topic name
- description: Brief description of why it's trending
- trend_score: 0-1 score (1 = highest trend)
- growth_rate: "rapid", "steady", or "emerging"
- key_papers: 2-3 relevant paper titles from the context
- emerging: true if this is a newly emerging topic

Return as JSON array:
[{{"name": "...", "description": "...", "trend_score": 0.9, "growth_rate": "rapid", "key_papers": [...], "emerging": false}}]"""

        response = await analyze_topics_with_gpt(request.field, [], context, task)

        # Parse response
        try:
            clean_response = response.strip()
            if clean_response.startswith("```"):
                clean_response = clean_response.split("```")[1]
                if clean_response.startswith("json"):
                    clean_response = clean_response[4:]
            clean_response = clean_response.strip()

            topics_data = json.loads(clean_response)
        except json.JSONDecodeError:
            topics_data = []

        trending = []
        for td in topics_data[:request.max_topics]:
            topic = TrendingTopic(
                name=td.get("name", "Unknown"),
                description=td.get("description", ""),
                trend_score=min(1.0, max(0.0, td.get("trend_score", 0.5))),
                growth_rate=td.get("growth_rate", "steady"),
                recent_papers=len(papers),
                key_papers=td.get("key_papers", []),
                emerging=td.get("emerging", False),
            )
            trending.append(topic)

        return TrendingTopicsResponse(
            trending_topics=trending,
            field=request.field,
            time_window=request.time_window,
            analysis_date=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Trending topics analysis failed: {str(e)}"
        )


@router.post("/gaps", response_model=ResearchGapResponse)
async def identify_research_gaps(request: ResearchGapRequest):
    """
    Identify research gaps in a field.

    Analyzes existing literature to find under-explored areas and opportunities.
    """
    try:
        # Get literature context
        keywords = request.keywords.copy()
        if request.subtopic:
            keywords.insert(0, request.subtopic)

        context, papers = await get_recent_literature_context(
            request.field, keywords, max_papers=25
        )

        task = f"""Analyze the research landscape and identify significant research gaps.

Subtopic focus: {request.subtopic or 'General field analysis'}

For each gap, provide:
- title: Concise gap title
- description: Detailed description of the gap
- gap_type: "methodological", "theoretical", "empirical", or "application"
- importance: "high", "medium", or "low"
- difficulty: "high", "medium", or "low" (to address this gap)
- existing_work: 2-3 relevant existing works
- suggested_approaches: 2-3 potential approaches to address the gap
- potential_impact: Description of potential research impact

Identify 5-8 significant gaps.

Return as JSON array:
[{{"title": "...", "description": "...", "gap_type": "...", "importance": "...", "difficulty": "...", "existing_work": [...], "suggested_approaches": [...], "potential_impact": "..."}}]"""

        response = await analyze_topics_with_gpt(request.field, keywords, context, task)

        # Parse response
        try:
            clean_response = response.strip()
            if clean_response.startswith("```"):
                clean_response = clean_response.split("```")[1]
                if clean_response.startswith("json"):
                    clean_response = clean_response[4:]
            clean_response = clean_response.strip()

            gaps_data = json.loads(clean_response)
        except json.JSONDecodeError:
            gaps_data = []

        gaps = []
        for gd in gaps_data:
            gap = ResearchGap(
                title=gd.get("title", "Unknown Gap"),
                description=gd.get("description", ""),
                gap_type=gd.get("gap_type", "empirical"),
                importance=gd.get("importance", "medium"),
                difficulty=gd.get("difficulty", "medium"),
                existing_work=gd.get("existing_work", []),
                suggested_approaches=gd.get("suggested_approaches", []),
                potential_impact=gd.get("potential_impact", ""),
            )
            gaps.append(gap)

        # Generate summary
        summary_task = f"""Based on the {len(gaps)} research gaps identified, provide a 2-3 sentence summary of the overall state of research gaps in {request.field}. Return just the summary text, no JSON."""

        summary = await chat_completion(
            [{"role": "user", "content": summary_task}], model="gpt-4", temperature=0.5
        )

        return ResearchGapResponse(
            gaps=gaps,
            field=request.field,
            subtopic=request.subtopic,
            analysis_summary=summary.strip(),
            total_papers_analyzed=len(papers),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Research gap analysis failed: {str(e)}"
        )


@router.post("/clusters", response_model=TopicClusterResponse)
async def get_topic_clusters(request: TopicClusterRequest):
    """
    Generate topic clustering data for visualization.

    Returns nodes and links suitable for network visualization (D3.js, etc.)
    """
    try:
        # Get literature context
        context, papers = await get_recent_literature_context(
            request.field, request.keywords, max_papers=30
        )

        task = f"""Analyze the research landscape and create {request.num_clusters} topic clusters.

For each cluster, identify:
- Main topic (node)
- Related subtopics (nodes)
- Connections between topics (links)

Return as JSON with structure:
{{
  "clusters": [
    {{
      "id": "cluster_1",
      "name": "Cluster Name",
      "main_topic": "Main Topic Name",
      "subtopics": ["Subtopic 1", "Subtopic 2", "Subtopic 3"],
      "keywords": ["keyword1", "keyword2"],
      "size": 0.8
    }}
  ],
  "connections": [
    {{"source": "Topic A", "target": "Topic B", "strength": 0.7}}
  ]
}}

Create {request.num_clusters} distinct clusters with 3-5 subtopics each.
Include cross-cluster connections where relevant."""

        response = await analyze_topics_with_gpt(
            request.field, request.keywords, context, task
        )

        # Parse response
        try:
            clean_response = response.strip()
            if clean_response.startswith("```"):
                clean_response = clean_response.split("```")[1]
                if clean_response.startswith("json"):
                    clean_response = clean_response[4:]
            clean_response = clean_response.strip()

            cluster_data = json.loads(clean_response)
        except json.JSONDecodeError:
            cluster_data = {"clusters": [], "connections": []}

        # Build nodes and links
        nodes = []
        links = []
        node_ids = set()

        clusters_info = []
        for i, cluster in enumerate(cluster_data.get("clusters", [])):
            cluster_id = cluster.get("id", f"cluster_{i}")
            main_topic = cluster.get("main_topic", f"Topic {i}")
            subtopics = cluster.get("subtopics", [])
            keywords = cluster.get("keywords", [])
            size = cluster.get("size", 0.5)

            # Add main topic node
            main_node_id = f"{cluster_id}_main"
            nodes.append(
                ClusterNode(
                    id=main_node_id,
                    name=main_topic,
                    size=size,
                    group=i,
                    keywords=keywords,
                )
            )
            node_ids.add(main_node_id)

            # Add subtopic nodes
            subtopic_ids = []
            for j, subtopic in enumerate(subtopics):
                subtopic_id = f"{cluster_id}_sub_{j}"
                nodes.append(
                    ClusterNode(
                        id=subtopic_id,
                        name=subtopic,
                        size=size * 0.5,
                        group=i,
                        keywords=[],
                    )
                )
                node_ids.add(subtopic_id)
                subtopic_ids.append(subtopic_id)

                # Link subtopic to main topic
                links.append(
                    ClusterLink(source=main_node_id, target=subtopic_id, strength=0.8)
                )

            clusters_info.append(
                {
                    "id": cluster_id,
                    "name": cluster.get("name", main_topic),
                    "main_topic": main_topic,
                    "subtopics": subtopics,
                    "keywords": keywords,
                }
            )

        # Add cross-cluster connections
        for conn in cluster_data.get("connections", []):
            source_name = conn.get("source", "")
            target_name = conn.get("target", "")
            strength = conn.get("strength", 0.5)

            # Find matching nodes
            source_node = next(
                (n for n in nodes if source_name.lower() in n.name.lower()), None
            )
            target_node = next(
                (n for n in nodes if target_name.lower() in n.name.lower()), None
            )

            if source_node and target_node and source_node.id != target_node.id:
                links.append(
                    ClusterLink(
                        source=source_node.id, target=target_node.id, strength=strength
                    )
                )

        return TopicClusterResponse(
            nodes=nodes, links=links, clusters=clusters_info, field=request.field
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Topic clustering failed: {str(e)}"
        )


@router.post("/related", response_model=RelatedTopicsResponse)
async def find_related_topics(request: RelatedTopicsRequest):
    """
    Find topics related to a given research topic.

    Explores the topic space to find connected and similar research areas.
    """
    try:
        # Get literature context
        context, papers = await get_recent_literature_context(
            request.field, [request.topic], max_papers=25
        )

        task = f"""Find {request.max_related} topics related to "{request.topic}".

For each related topic, provide:
- name: Topic name
- relation_type: "parent" (broader), "child" (narrower), "sibling" (same level), "related" (conceptually connected), or "emerging" (new related area)
- relation_strength: 0-1 score for how strongly related
- description: Brief description of the topic
- common_keywords: 2-4 keywords shared with the source topic

Explore to depth {request.depth} (1=direct relations, 2=second-degree, 3=third-degree).

Return as JSON array:
[{{"name": "...", "relation_type": "...", "relation_strength": 0.8, "description": "...", "common_keywords": [...]}}]"""

        response = await analyze_topics_with_gpt(
            request.field, [request.topic], context, task
        )

        # Parse response
        try:
            clean_response = response.strip()
            if clean_response.startswith("```"):
                clean_response = clean_response.split("```")[1]
                if clean_response.startswith("json"):
                    clean_response = clean_response[4:]
            clean_response = clean_response.strip()

            topics_data = json.loads(clean_response)
        except json.JSONDecodeError:
            topics_data = []

        related = []
        for td in topics_data[:request.max_related]:
            topic = RelatedTopic(
                name=td.get("name", "Unknown"),
                relation_type=td.get("relation_type", "related"),
                relation_strength=min(1.0, max(0.0, td.get("relation_strength", 0.5))),
                description=td.get("description", ""),
                common_keywords=td.get("common_keywords", []),
            )
            related.append(topic)

        return RelatedTopicsResponse(
            source_topic=request.topic, related_topics=related, field=request.field
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Related topics search failed: {str(e)}"
        )


@router.post("/questions", response_model=ResearchQuestionsResponse)
async def generate_research_questions(request: ResearchQuestionsRequest):
    """
    Generate potential research questions for a topic.

    Creates novel, well-formulated research questions based on the current state of the field.
    """
    try:
        # Get literature context
        context, papers = await get_recent_literature_context(
            request.field, [request.topic], max_papers=25
        )

        question_type_filter = ""
        if request.question_type != "all":
            question_type_filter = f"Focus on {request.question_type} questions."

        task = f"""Generate {request.num_questions} research questions for the topic "{request.topic}".

{question_type_filter}

Question types to include:
- exploratory: Questions that explore new phenomena or relationships
- descriptive: Questions that describe characteristics or patterns
- explanatory: Questions that explain why or how something occurs
- evaluative: Questions that assess effectiveness or outcomes

For each question, provide:
- question: The research question
- type: Question type
- rationale: Why this question is important/novel
- methodology_hints: 2-3 suggested research methods
- related_concepts: 2-4 related concepts
- novelty_score: 0-1 score for how novel this question is

Return as JSON array:
[{{"question": "...", "type": "...", "rationale": "...", "methodology_hints": [...], "related_concepts": [...], "novelty_score": 0.8}}]"""

        response = await analyze_topics_with_gpt(
            request.field, [request.topic], context, task
        )

        # Parse response
        try:
            clean_response = response.strip()
            if clean_response.startswith("```"):
                clean_response = clean_response.split("```")[1]
                if clean_response.startswith("json"):
                    clean_response = clean_response[4:]
            clean_response = clean_response.strip()

            questions_data = json.loads(clean_response)
        except json.JSONDecodeError:
            questions_data = []

        questions = []
        for qd in questions_data[:request.num_questions]:
            question = ResearchQuestion(
                question=qd.get("question", ""),
                type=qd.get("type", "exploratory"),
                rationale=qd.get("rationale", ""),
                methodology_hints=qd.get("methodology_hints", []),
                related_concepts=qd.get("related_concepts", []),
                novelty_score=min(1.0, max(0.0, qd.get("novelty_score", 0.5))),
            )
            questions.append(question)

        return ResearchQuestionsResponse(
            questions=questions, topic=request.topic, field=request.field
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Research questions generation failed: {str(e)}"
        )


@router.post("/validate", response_model=TopicValidationResponse)
async def validate_topic(request: TopicValidationRequest):
    """
    Validate a research topic against existing literature.

    Checks if the topic is viable and provides refinement suggestions.
    """
    try:
        # Search for papers on this topic
        query = f"{request.topic} {request.field}"

        results = await asyncio.gather(
            search_semantic_scholar(query, max_results=15),
            search_arxiv(query, max_results=15),
            search_pubmed(query, max_results=15),
        )

        all_papers = []
        for paper_list in results:
            all_papers.extend(paper_list)

        papers = deduplicate_papers(all_papers)
        paper_count = len(papers)

        # Calculate relevance based on paper count and recency
        recent_papers = [p for p in papers if p.year and int(p.year) >= 2022]

        # Determine relevance score
        if paper_count >= 20:
            relevance = 0.9
        elif paper_count >= 10:
            relevance = 0.7
        elif paper_count >= 5:
            relevance = 0.5
        elif paper_count >= 1:
            relevance = 0.3
        else:
            relevance = 0.1

        # Adjust for recency
        if recent_papers:
            relevance = min(1.0, relevance + 0.1)

        is_valid = paper_count >= 3 and relevance >= 0.3

        # Generate validation notes and refinements using GPT
        paper_context = "\n".join(
            [f"- {p.title} ({p.year})" for p in papers[:10]]
        )

        validation_task = f"""Analyze this research topic: "{request.topic}" in the field of {request.field}.

Found {paper_count} related papers, including:
{paper_context}

Provide:
1. A brief validation note (2-3 sentences) about the topic's viability
2. 3-5 suggestions to refine or improve the topic

Return as JSON:
{{"validation_notes": "...", "refinements": ["...", "..."]}}"""

        gpt_response = await chat_completion(
            [{"role": "user", "content": validation_task}], model="gpt-4", temperature=0.5
        )

        try:
            clean_response = gpt_response.strip()
            if clean_response.startswith("```"):
                clean_response = clean_response.split("```")[1]
                if clean_response.startswith("json"):
                    clean_response = clean_response[4:]
            clean_response = clean_response.strip()

            validation_data = json.loads(clean_response)
            validation_notes = validation_data.get("validation_notes", "Topic validation complete.")
            refinements = validation_data.get("refinements", [])
        except json.JSONDecodeError:
            validation_notes = f"Found {paper_count} related papers. Topic appears {'viable' if is_valid else 'needs refinement'}."
            refinements = []

        return TopicValidationResponse(
            topic=request.topic,
            is_valid=is_valid,
            relevance_score=relevance,
            paper_count=paper_count,
            recent_papers=papers[:5],
            validation_notes=validation_notes,
            suggested_refinements=refinements,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Topic validation failed: {str(e)}"
        )


@router.post("/hot-topics", response_model=HotTopicsResponse)
async def get_hot_topics(request: HotTopicsRequest):
    """
    Get hot topics in a research field.

    Identifies the most active and impactful research areas currently.
    """
    try:
        # Get recent literature context
        context, papers = await get_recent_literature_context(
            request.field, [], max_papers=35
        )

        task = f"""Identify the {request.max_topics} hottest research topics in {request.field} right now.

For each hot topic, provide:
- name: Topic name
- description: Why this topic is hot (2-3 sentences)
- heat_score: 0-1 score (1 = hottest)
- reasons: 3-4 reasons why this topic is hot
- key_researchers: 2-3 prominent researchers (if identifiable from papers)
- key_institutions: 2-3 leading institutions
- funding_opportunities: 1-2 potential funding areas
- recent_breakthroughs: 2-3 recent breakthrough findings

Return as JSON array:
[{{"name": "...", "description": "...", "heat_score": 0.95, "reasons": [...], "key_researchers": [...], "key_institutions": [...], "funding_opportunities": [...], "recent_breakthroughs": [...]}}]"""

        response = await analyze_topics_with_gpt(request.field, [], context, task)

        # Parse response
        try:
            clean_response = response.strip()
            if clean_response.startswith("```"):
                clean_response = clean_response.split("```")[1]
                if clean_response.startswith("json"):
                    clean_response = clean_response[4:]
            clean_response = clean_response.strip()

            topics_data = json.loads(clean_response)
        except json.JSONDecodeError:
            topics_data = []

        hot_topics = []
        for td in topics_data[:request.max_topics]:
            topic = HotTopic(
                name=td.get("name", "Unknown"),
                description=td.get("description", ""),
                heat_score=min(1.0, max(0.0, td.get("heat_score", 0.5))),
                reasons=td.get("reasons", []),
                key_researchers=td.get("key_researchers", []),
                key_institutions=td.get("key_institutions", []),
                funding_opportunities=td.get("funding_opportunities", []),
                recent_breakthroughs=td.get("recent_breakthroughs", []),
            )
            hot_topics.append(topic)

        return HotTopicsResponse(
            hot_topics=hot_topics,
            field=request.field,
            analysis_date=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Hot topics analysis failed: {str(e)}"
        )


@router.post("/save-topic")
async def save_topic(request: SaveTopicRequest, user_id: Optional[str] = None):
    """
    Save/bookmark a research topic for later reference.
    """
    if not user_id:
        user_id = "dev-user"

    try:
        topic_data = {
            "user_id": user_id,
            "name": request.topic.name,
            "description": request.topic.description,
            "field": request.topic.field,
            "keywords": request.topic.keywords,
            "relevance_score": request.topic.relevance_score,
            "trend_score": request.topic.trend_score,
            "related_topics": request.topic.related_topics,
            "potential_questions": request.topic.potential_questions,
            "notes": request.notes,
            "tags": request.tags,
            "metadata": {
                "paper_count": request.topic.paper_count,
                "recent_paper_count": request.topic.recent_paper_count,
            },
        }

        result = supabase.table("saved_topics").insert(topic_data).execute()

        return {
            "status": "success",
            "topic_id": result.data[0]["id"] if result.data else None,
            "message": f"Topic '{request.topic.name}' saved successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save topic: {str(e)}")


@router.get("/saved-topics")
async def get_saved_topics(
    user_id: Optional[str] = None,
    field: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=100),
):
    """
    Get user's saved/bookmarked topics.
    """
    if not user_id:
        user_id = "dev-user"

    try:
        query = (
            supabase.table("saved_topics")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
        )

        if field:
            query = query.eq("field", field)

        response = query.limit(limit).execute()

        return {
            "topics": response.data if response.data else [],
            "total": len(response.data) if response.data else 0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get topics: {str(e)}")


@router.delete("/saved-topics/{topic_id}")
async def delete_saved_topic(topic_id: str, user_id: Optional[str] = None):
    """
    Delete a saved topic.
    """
    if not user_id:
        user_id = "dev-user"

    try:
        supabase.table("saved_topics").delete().eq("id", topic_id).eq(
            "user_id", user_id
        ).execute()

        return {"status": "success", "message": "Topic deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete topic: {str(e)}")


@router.get("/explore/{field}")
async def explore_field(
    field: str,
    depth: str = Query(default="overview", description="overview, detailed, comprehensive"),
):
    """
    Get a comprehensive exploration of a research field.

    Combines trending topics, hot topics, and research gaps into one view.
    """
    try:
        # Run multiple analyses concurrently
        trending_task = get_trending_topics(
            TrendingTopicsRequest(field=field, max_topics=5)
        )
        hot_task = get_hot_topics(HotTopicsRequest(field=field, max_topics=5))
        gaps_task = identify_research_gaps(ResearchGapRequest(field=field))

        trending_result, hot_result, gaps_result = await asyncio.gather(
            trending_task, hot_task, gaps_task
        )

        return {
            "field": field,
            "depth": depth,
            "exploration": {
                "trending_topics": trending_result.trending_topics,
                "hot_topics": hot_result.hot_topics,
                "research_gaps": gaps_result.gaps,
                "analysis_summary": gaps_result.analysis_summary,
            },
            "generated_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Field exploration failed: {str(e)}"
        )
