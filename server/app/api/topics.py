from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from core.database import supabase, get_user_from_token
from core.openai_client import chat_completion
import json

router = APIRouter()


class TopicDiscoveryRequest(BaseModel):
    research_field: str
    num_topics: int = 10


class Topic(BaseModel):
    name: str
    relevance: float
    description: str
    gap_analysis: str
    trending_score: float


class TopicDiscoveryResponse(BaseModel):
    topics: List[Topic]
    research_field: str


@router.post("/discover", response_model=TopicDiscoveryResponse)
async def discover_topics(request: TopicDiscoveryRequest, token: str = None):
    """Discover research topics in a given field with relevance, gap analysis, and trending scores"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        topics = await generate_topics_with_gpt(
            request.research_field, request.num_topics
        )

        save_topics_to_db(user["id"], request.research_field, topics)

        return TopicDiscoveryResponse(
            topics=topics, research_field=request.research_field
        )
    except Exception as e:
        print(f"Error discovering topics: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error discovering topics: {str(e)}"
        )


async def generate_topics_with_gpt(research_field: str, num_topics: int) -> List[Topic]:
    """Use GPT-4 to generate research topics with analysis"""

    prompt = f"""You are an expert academic researcher specializing in {research_field}. 
Generate {num_topics} cutting-edge research topics that are currently relevant and impactful.

For each topic, provide:
1. A clear, specific topic name
2. A relevance score (0.0 to 1.0) based on importance and impact
3. A brief description of the topic
4. A gap analysis: what specific research questions remain unanswered or under-explored
5. A trending score (0.0 to 1.0) based on recent interest and citation potential

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "name": "Topic Name",
    "relevance": 0.85,
    "description": "Brief description of the topic...",
    "gap_analysis": "Specific research gaps and questions...",
    "trending_score": 0.78
  }},
  ...
]

Ensure all scores are between 0.0 and 1.0."""

    try:
        response = await chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert academic researcher. Always return valid JSON arrays.",
                },
                {"role": "user", "content": prompt},
            ],
            model="gpt-4",
            temperature=0.7,
        )

        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()

        topics_data = json.loads(cleaned_response)

        topics = []
        for topic_data in topics_data:
            topics.append(
                Topic(
                    name=topic_data["name"],
                    relevance=float(topic_data["relevance"]),
                    description=topic_data["description"],
                    gap_analysis=topic_data["gap_analysis"],
                    trending_score=float(topic_data["trending_score"]),
                )
            )

        return topics

    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response was: {response}")
        raise HTTPException(status_code=500, detail="Failed to parse AI response")
    except Exception as e:
        print(f"GPT generation error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate topics: {str(e)}"
        )


def save_topics_to_db(user_id: str, research_field: str, topics: List[Topic]):
    """Save discovered topics to database"""
    try:
        for topic in topics:
            topic_data = {
                "user_id": user_id,
                "research_field": research_field,
                "topic_name": topic.name,
                "relevance_score": topic.relevance,
                "gap_analysis": topic.gap_analysis,
                "trending_score": topic.trending_score,
                "description": topic.description,
            }
            supabase.table("research_topics").insert(topic_data).execute()
    except Exception as e:
        print(f"Error saving topics to database: {e}")


@router.get("/history")
async def get_topic_history(token: str = None):
    """Get user's topic discovery history"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        response = (
            supabase.table("research_topics")
            .select("*")
            .eq("user_id", user["id"])
            .order("created_at", desc=True)
            .execute()
        )

        return {"topics": response.data if response.data else []}
    except Exception as e:
        print(f"Error fetching topic history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch history")


@router.delete("/history")
async def clear_topic_history(token: str = None):
    """Clear user's topic discovery history"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        supabase.table("research_topics").delete().eq("user_id", user["id"]).execute()
        return {"status": "success", "message": "History cleared"}
    except Exception as e:
        print(f"Error clearing topic history: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear history")
