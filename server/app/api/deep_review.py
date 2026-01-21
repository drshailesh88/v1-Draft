from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from core.database import supabase, get_user_from_token
from core.openai_client import chat_completion
import asyncio
import json
from langgraph.graph import StateGraph, END
from typing import TypedDict

router = APIRouter()


class AnalyzeRequest(BaseModel):
    paper_content: str
    paper_title: str
    comparison_papers: Optional[List[Dict[str, Any]]] = None


class Rating(BaseModel):
    score: float
    explanation: str
    strengths: List[str]
    weaknesses: List[str]


class SimilarityResult(BaseModel):
    paper_title: str
    similarity_score: float
    common_themes: List[str]
    methodological_differences: List[str]


class AnalyzeResponse(BaseModel):
    review_id: str
    overall_rating: Rating
    methods_critique: Dict[str, Any]
    results_critique: Dict[str, Any]
    discussion_critique: Dict[str, Any]
    suggestions: List[str]
    similarity_analysis: List[SimilarityResult]
    agent_tasks: Dict[str, Any]


class SaveReviewRequest(BaseModel):
    review_id: str
    paper_title: str
    paper_content: str
    comparison_papers: Optional[List[Dict[str, Any]]] = None
    overall_rating: Dict[str, Any]
    methods_critique: str
    results_critique: str
    discussion_critique: str
    suggestions: str
    similarity_analysis: Dict[str, Any]
    agent_tasks: Optional[Dict[str, Any]] = None


class Review(BaseModel):
    id: str
    paper_title: str
    overall_rating: Dict[str, Any]
    created_at: str


class ReviewsResponse(BaseModel):
    reviews: List[Review]


class ReviewState(TypedDict):
    paper_content: str
    paper_title: str
    comparison_papers: List[Dict[str, Any]]
    methods_critique: Optional[Dict[str, Any]]
    results_critique: Optional[Dict[str, Any]]
    discussion_critique: Optional[Dict[str, Any]]
    overall_rating: Optional[Dict[str, Any]]
    suggestions: Optional[List[str]]
    similarity_analysis: Optional[List[Dict[str, Any]]]
    agent_tasks: Dict[str, Any]


async def methods_reviewer_agent(state: ReviewState) -> ReviewState:
    """Agent that critiques the methods section"""
    try:
        prompt = f"""You are an expert research methods reviewer. Critique the methods section of this paper.

Paper Title: {state["paper_title"]}

Paper Content:
{state["paper_content"][:3000]}

Provide a structured critique with:
1. Methodology appropriateness (score 1-10, explanation)
2. Sample size and power analysis (score 1-10, explanation)
3. Study design quality (score 1-10, explanation)
4. Measurement validity (score 1-10, explanation)
5. Key strengths (list)
6. Key weaknesses (list)
7. Specific recommendations for improvement

Return as JSON with these keys:
{{
    "methodology_appropriateness": {{"score": <1-10>, "explanation": "..."}},
    "sample_size": {{"score": <1-10>, "explanation": "..."}},
    "study_design": {{"score": <1-10>, "explanation": "..."}},
    "measurement_validity": {{"score": <1-10>, "explanation": "..."}},
    "strengths": ["...", "..."],
    "weaknesses": ["...", "..."],
    "recommendations": ["...", "..."]
}}"""

        response = await chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4",
            temperature=0.3,
        )

        try:
            critique = json.loads(response)
        except json.JSONDecodeError:
            critique = {
                "methodology_appropriateness": {
                    "score": 5,
                    "explanation": "Unable to parse",
                },
                "sample_size": {"score": 5, "explanation": "Unable to parse"},
                "study_design": {"score": 5, "explanation": "Unable to parse"},
                "measurement_validity": {"score": 5, "explanation": "Unable to parse"},
                "strengths": [],
                "weaknesses": [],
                "recommendations": [],
            }

        state["methods_critique"] = critique
        state["agent_tasks"]["methods_reviewer"] = {
            "status": "completed",
            "timestamp": str(asyncio.get_event_loop().time()),
        }

    except Exception as e:
        print(f"Methods reviewer error: {e}")
        state["methods_critique"] = {"error": str(e)}
        state["agent_tasks"]["methods_reviewer"] = {"status": "error", "error": str(e)}

    return state


async def results_reviewer_agent(state: ReviewState) -> ReviewState:
    """Agent that critiques the results section"""
    try:
        prompt = f"""You are an expert statistical analysis reviewer. Critique the results section of this paper.

Paper Title: {state["paper_title"]}

Paper Content:
{state["paper_content"][:3000]}

Provide a structured critique with:
1. Statistical appropriateness (score 1-10, explanation)
2. Data visualization quality (score 1-10, explanation)
3. Result interpretation (score 1-10, explanation)
4. Key strengths (list)
5. Key weaknesses (list)
6. Specific recommendations for improvement

Return as JSON with these keys:
{{
    "statistical_appropriateness": {{"score": <1-10>, "explanation": "..."}},
    "data_visualization": {{"score": <1-10>, "explanation": "..."}},
    "result_interpretation": {{"score": <1-10>, "explanation": "..."}},
    "strengths": ["...", "..."],
    "weaknesses": ["...", "..."],
    "recommendations": ["...", "..."]
}}"""

        response = await chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4",
            temperature=0.3,
        )

        try:
            critique = json.loads(response)
        except json.JSONDecodeError:
            critique = {
                "statistical_appropriateness": {
                    "score": 5,
                    "explanation": "Unable to parse",
                },
                "data_visualization": {"score": 5, "explanation": "Unable to parse"},
                "result_interpretation": {"score": 5, "explanation": "Unable to parse"},
                "strengths": [],
                "weaknesses": [],
                "recommendations": [],
            }

        state["results_critique"] = critique
        state["agent_tasks"]["results_reviewer"] = {
            "status": "completed",
            "timestamp": str(asyncio.get_event_loop().time()),
        }

    except Exception as e:
        print(f"Results reviewer error: {e}")
        state["results_critique"] = {"error": str(e)}
        state["agent_tasks"]["results_reviewer"] = {"status": "error", "error": str(e)}

    return state


async def discussion_reviewer_agent(state: ReviewState) -> ReviewState:
    """Agent that critiques the discussion section"""
    try:
        prompt = f"""You are an expert academic writing reviewer. Critique the discussion section of this paper.

Paper Title: {state["paper_title"]}

Paper Content:
{state["paper_content"][:3000]}

Provide a structured critique with:
1. Argument coherence (score 1-10, explanation)
2. Integration with literature (score 1-10, explanation)
3. Limitations acknowledgment (score 1-10, explanation)
4. Future directions (score 1-10, explanation)
5. Key strengths (list)
6. Key weaknesses (list)
7. Specific recommendations for improvement

Return as JSON with these keys:
{{
    "argument_coherence": {{"score": <1-10>, "explanation": "..."}},
    "literature_integration": {{"score": <1-10>, "explanation": "..."}},
    "limitations_acknowledgment": {{"score": <1-10>, "explanation": "..."}},
    "future_directions": {{"score": <1-10>, "explanation": "..."}},
    "strengths": ["...", "..."],
    "weaknesses": ["...", "..."],
    "recommendations": ["...", "..."]
}}"""

        response = await chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4",
            temperature=0.3,
        )

        try:
            critique = json.loads(response)
        except json.JSONDecodeError:
            critique = {
                "argument_coherence": {"score": 5, "explanation": "Unable to parse"},
                "literature_integration": {
                    "score": 5,
                    "explanation": "Unable to parse",
                },
                "limitations_acknowledgment": {
                    "score": 5,
                    "explanation": "Unable to parse",
                },
                "future_directions": {"score": 5, "explanation": "Unable to parse"},
                "strengths": [],
                "weaknesses": [],
                "recommendations": [],
            }

        state["discussion_critique"] = critique
        state["agent_tasks"]["discussion_reviewer"] = {
            "status": "completed",
            "timestamp": str(asyncio.get_event_loop().time()),
        }

    except Exception as e:
        print(f"Discussion reviewer error: {e}")
        state["discussion_critique"] = {"error": str(e)}
        state["agent_tasks"]["discussion_reviewer"] = {
            "status": "error",
            "error": str(e),
        }

    return state


async def overall_rating_agent(state: ReviewState) -> ReviewState:
    """Agent that provides overall rating based on all critiques"""
    try:
        methods = state.get("methods_critique", {})
        results = state.get("results_critique", {})
        discussion = state.get("discussion_critique", {})

        prompt = f"""You are a senior journal editor. Provide an overall assessment and rating for this paper based on the critiques.

Paper Title: {state["paper_title"]}

Methods Critique:
{json.dumps(methods, indent=2)}

Results Critique:
{json.dumps(results, indent=2)}

Discussion Critique:
{json.dumps(discussion, indent=2)}

Provide:
1. Overall quality score (1-10)
2. Verdict (Accept, Minor Revision, Major Revision, Reject)
3. Comprehensive explanation
4. Key strengths (top 3-5)
5. Key weaknesses (top 3-5)

Return as JSON with these keys:
{{
    "score": <1-10>,
    "verdict": "Accept/Minor Revision/Major Revision/Reject",
    "explanation": "...",
    "strengths": ["...", "..."],
    "weaknesses": ["...", "..."]
}}"""

        response = await chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4",
            temperature=0.2,
        )

        try:
            rating = json.loads(response)
        except json.JSONDecodeError:
            rating = {
                "score": 5,
                "verdict": "Unable to determine",
                "explanation": "Unable to parse rating",
                "strengths": [],
                "weaknesses": [],
            }

        state["overall_rating"] = rating
        state["agent_tasks"]["overall_rating"] = {
            "status": "completed",
            "timestamp": str(asyncio.get_event_loop().time()),
        }

    except Exception as e:
        print(f"Overall rating error: {e}")
        state["overall_rating"] = {"error": str(e)}
        state["agent_tasks"]["overall_rating"] = {"status": "error", "error": str(e)}

    return state


async def suggestion_generator_agent(state: ReviewState) -> ReviewState:
    """Agent that generates suggestions for improvement"""
    try:
        methods = state.get("methods_critique", {})
        results = state.get("results_critique", {})
        discussion = state.get("discussion_critique", {})

        prompt = f"""Generate actionable suggestions for improving this paper.

Paper Title: {state["paper_title"]}

Methods Critique:
{json.dumps(methods, indent=2)}

Results Critique:
{json.dumps(results, indent=2)}

Discussion Critique:
{json.dumps(discussion, indent=2)}

Generate 10 specific, actionable suggestions prioritized by impact:
1. 3 high-priority suggestions (critical fixes)
2. 4 medium-priority suggestions (significant improvements)
3. 3 low-priority suggestions (nice-to-have improvements)

For each suggestion, provide:
- Category (Methods/Results/Discussion/General)
- Priority (High/Medium/Low)
- Specific action
- Expected impact

Return as JSON with these keys:
{{
    "suggestions": [
        {{
            "category": "...",
            "priority": "...",
            "action": "...",
            "expected_impact": "..."
        }}
    ]
}}"""

        response = await chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4",
            temperature=0.5,
        )

        try:
            suggestions_data = json.loads(response)
            state["suggestions"] = suggestions_data.get("suggestions", [])
        except json.JSONDecodeError:
            state["suggestions"] = []

        state["agent_tasks"]["suggestion_generator"] = {
            "status": "completed",
            "timestamp": str(asyncio.get_event_loop().time()),
        }

    except Exception as e:
        print(f"Suggestion generator error: {e}")
        state["suggestions"] = []
        state["agent_tasks"]["suggestion_generator"] = {
            "status": "error",
            "error": str(e),
        }

    return state


async def similarity_analyzer_agent(state: ReviewState) -> ReviewState:
    """Agent that analyzes similarity with comparison papers"""
    try:
        comparison_papers = state.get("comparison_papers", [])
        if not comparison_papers:
            state["similarity_analysis"] = []
            state["agent_tasks"]["similarity_analyzer"] = {
                "status": "skipped",
                "reason": "No comparison papers",
            }
            return state

        similarities = []
        for paper in comparison_papers[:5]:
            prompt = f"""Compare this paper with a comparison paper.

Main Paper:
Title: {state["paper_title"]}
Content: {state["paper_content"][:2000]}

Comparison Paper:
Title: {paper.get("title", "N/A")}
Authors: {", ".join(paper.get("authors", []))}
Abstract: {paper.get("abstract", "N/A")}
Journal: {paper.get("journal", "N/A")}

Analyze and provide:
1. Similarity score (0-100)
2. Common research themes (list)
3. Methodological differences (list)
4. Which paper is stronger and why

Return as JSON with these keys:
{{
    "paper_title": "...",
    "similarity_score": <0-100>,
    "common_themes": ["...", "..."],
    "methodological_differences": ["...", "..."],
    "stronger_paper": "...",
    "reasoning": "..."
}}"""

            response = await chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model="gpt-4",
                temperature=0.3,
            )

            try:
                comparison = json.loads(response)
                similarities.append(comparison)
            except json.JSONDecodeError:
                pass

        state["similarity_analysis"] = similarities
        state["agent_tasks"]["similarity_analyzer"] = {
            "status": "completed",
            "timestamp": str(asyncio.get_event_loop().time()),
        }

    except Exception as e:
        print(f"Similarity analyzer error: {e}")
        state["similarity_analysis"] = []
        state["agent_tasks"]["similarity_analyzer"] = {
            "status": "error",
            "error": str(e),
        }

    return state


def build_review_graph():
    """Build the LangGraph for multi-agent paper review"""
    workflow = StateGraph(ReviewState)

    workflow.add_node("methods_reviewer", methods_reviewer_agent)
    workflow.add_node("results_reviewer", results_reviewer_agent)
    workflow.add_node("discussion_reviewer", discussion_reviewer_agent)
    workflow.add_node("overall_rating", overall_rating_agent)
    workflow.add_node("suggestion_generator", suggestion_generator_agent)
    workflow.add_node("similarity_analyzer", similarity_analyzer_agent)

    workflow.set_entry_point("methods_reviewer")

    workflow.add_edge("methods_reviewer", "results_reviewer")
    workflow.add_edge("results_reviewer", "discussion_reviewer")
    workflow.add_edge("discussion_reviewer", "overall_rating")
    workflow.add_edge("overall_rating", "suggestion_generator")
    workflow.add_edge("suggestion_generator", "similarity_analyzer")
    workflow.add_edge("similarity_analyzer", END)

    return workflow.compile()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_paper(request: AnalyzeRequest, token: str = None):
    """Run multi-agent deep review analysis on a paper"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        import uuid

        review_id = str(uuid.uuid4())

        initial_state = ReviewState(
            paper_content=request.paper_content,
            paper_title=request.paper_title,
            comparison_papers=request.comparison_papers or [],
            methods_critique=None,
            results_critique=None,
            discussion_critique=None,
            overall_rating=None,
            suggestions=None,
            similarity_analysis=None,
            agent_tasks={
                "methods_reviewer": {"status": "pending"},
                "results_reviewer": {"status": "pending"},
                "discussion_reviewer": {"status": "pending"},
                "overall_rating": {"status": "pending"},
                "suggestion_generator": {"status": "pending"},
                "similarity_analyzer": {"status": "pending"},
            },
        )

        graph = build_review_graph()
        final_state = await graph.ainvoke(initial_state)

        similarity_results = [
            SimilarityResult(
                paper_title=comp.get("paper_title", ""),
                similarity_score=comp.get("similarity_score", 0),
                common_themes=comp.get("common_themes", []),
                methodological_differences=comp.get("methodological_differences", []),
            )
            for comp in (final_state.get("similarity_analysis") or [])
        ]

        overall_rating_data = final_state.get("overall_rating", {})
        overall_rating = Rating(
            score=overall_rating_data.get("score", 0),
            explanation=overall_rating_data.get("explanation", ""),
            strengths=overall_rating_data.get("strengths", []),
            weaknesses=overall_rating_data.get("weaknesses", []),
        )

        return AnalyzeResponse(
            review_id=review_id,
            overall_rating=overall_rating,
            methods_critique=final_state.get("methods_critique", {}),
            results_critique=final_state.get("results_critique", {}),
            discussion_critique=final_state.get("discussion_critique", {}),
            suggestions=[
                s.get("action", "") for s in (final_state.get("suggestions") or [])
            ],
            similarity_analysis=similarity_results,
            agent_tasks=final_state.get("agent_tasks", {}),
        )

    except Exception as e:
        print(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save-review")
async def save_review(request: SaveReviewRequest, token: str = None):
    """Save deep review to database"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        review_data = {
            "user_id": user["id"],
            "paper_title": request.paper_title,
            "paper_content": request.paper_content[:10000],
            "comparison_papers": request.comparison_papers,
            "overall_rating": request.overall_rating,
            "methods_critique": request.methods_critique,
            "results_critique": request.results_critique,
            "discussion_critique": request.discussion_critique,
            "suggestions": request.suggestions,
            "similarity_analysis": request.similarity_analysis,
            "agent_tasks": request.agent_tasks,
        }

        response = supabase.table("deep_reviews").insert(review_data).execute()
        review = response.data[0] if response.data else None

        if not review:
            raise HTTPException(status_code=500, detail="Failed to save review")

        return {"status": "success", "review_id": review["id"]}

    except Exception as e:
        print(f"Save review error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reviews", response_model=ReviewsResponse)
async def get_reviews(token: str = None):
    """Get user's review history"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        response = (
            supabase.table("deep_reviews")
            .select("id, paper_title, overall_rating, created_at")
            .eq("user_id", user["id"])
            .order("created_at", desc=True)
            .execute()
        )

        reviews = [
            Review(
                id=r["id"],
                paper_title=r["paper_title"],
                overall_rating=r["overall_rating"],
                created_at=r["created_at"],
            )
            for r in (response.data or [])
        ]

        return ReviewsResponse(reviews=reviews)

    except Exception as e:
        print(f"Get reviews error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/review/{review_id}")
async def get_review_detail(review_id: str, token: str = None):
    """Get detailed review by ID"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        response = (
            supabase.table("deep_reviews")
            .select("*")
            .eq("id", review_id)
            .eq("user_id", user["id"])
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Review not found")

        return {"review": response.data[0]}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Get review detail error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
