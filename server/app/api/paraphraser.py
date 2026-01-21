from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from core.database import supabase, get_user_from_token
from openai import OpenAI
import os

router = APIRouter()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class ParaphraseRequest(BaseModel):
    text: str
    intensity: str = "medium"


class VocabularyEnhancement(BaseModel):
    original: str
    suggestion: str
    position: List[int]


class ParaphraseResponse(BaseModel):
    original: str
    paraphrased: str
    vocabulary_enhancements: List[VocabularyEnhancement]
    intensity: str


def get_intensity_prompt(intensity: str) -> str:
    """Get paraphrasing prompt based on intensity level"""
    prompts = {
        "light": "Make minimal surface-level changes to improve flow and readability. Keep the original structure and most words. Focus on smoothing transitions and fixing any awkward phrasing.",
        "medium": "Rewrite with moderate changes to improve clarity and style. Change some vocabulary and sentence structures while maintaining the same meaning. Use more varied sentence patterns.",
        "strong": "Significantly rephrase the text with different wording and sentence structures. Maintain the same academic meaning but use entirely new expressions. Be creative with reorganization.",
    }
    return prompts.get(intensity, prompts["medium"])


def preserve_citations(text: str) -> List[str]:
    """Extract and preserve citations in [Author et al., Year] format"""
    import re

    citation_pattern = r"\[[^\]]+\]"
    citations = re.findall(citation_pattern, text)
    return citations


async def generate_paraphrase(
    text: str, intensity: str
) -> tuple[str, List[VocabularyEnhancement]]:
    """Generate paraphrased text and vocabulary enhancements using GPT-4"""

    citations = preserve_citations(text)
    citation_context = (
        f"IMPORTANT: The following citations MUST be preserved exactly as written: {', '.join(citations)}"
        if citations
        else ""
    )

    intensity_prompt = get_intensity_prompt(intensity)

    system_prompt = f"""You are an expert academic paraphraser. Your task is to rewrite academic text while preserving all meaning, citations, and academic rigor.

{intensity_prompt}

Additional requirements:
1. Preserve ALL citations in the exact format [Author et al., Year]
2. Maintain academic tone and appropriate scholarly language
3. DO NOT change the underlying meaning or factual content
4. Ensure the paraphrased text flows naturally
5. Use sophisticated academic vocabulary where appropriate
6. {citation_context}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Paraphrase the following text:\n\n{text}",
                },
            ],
            temperature=0.7,
            max_tokens=2000,
        )

        paraphrased = response.choices[0].message.content.strip()

        # Generate vocabulary enhancements
        vocab_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert academic editor. Identify 3-5 vocabulary words or phrases in the original text that could be enhanced with more precise academic alternatives. Return ONLY a JSON array of objects with 'original', 'suggestion', and 'position' (word index) fields.",
                },
                {
                    "role": "user",
                    "content": f"Original text: {text}\n\nIdentify vocabulary enhancements in JSON format.",
                },
            ],
            temperature=0.5,
            response_format={"type": "json_object"},
        )

        vocab_content = vocab_response.choices[0].message.content
        vocabulary_enhancements = []

        if vocab_content:
            import json

            try:
                vocab_data = json.loads(vocab_content)
                if "enhancements" in vocab_data:
                    for item in vocab_data["enhancements"]:
                        vocabulary_enhancements.append(VocabularyEnhancement(**item))
            except json.JSONDecodeError:
                pass

        return paraphrased, vocabulary_enhancements

    except Exception as e:
        print(f"Error generating paraphrase: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate paraphrase")


async def save_paraphrase(
    user_id: str,
    original: str,
    paraphrased: str,
    intensity: str,
    enhancements: List[VocabularyEnhancement],
):
    """Save paraphrase to database"""
    try:
        paraphrase_data = {
            "user_id": user_id,
            "original_text": original,
            "paraphrased_text": paraphrased,
            "intensity": intensity,
            "vocabulary_enhancements": [e.dict() for e in enhancements],
        }
        supabase.table("paraphrases").insert(paraphrase_data).execute()
    except Exception as e:
        print(f"Error saving paraphrase: {e}")


@router.post("/paraphrase", response_model=ParaphraseResponse)
async def paraphrase_text(request: ParaphraseRequest, token: str = None):
    """Paraphrase text with specified intensity"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Validate intensity
    if request.intensity not in ["light", "medium", "strong"]:
        raise HTTPException(
            status_code=400, detail="Intensity must be one of: light, medium, strong"
        )

    # Validate text
    if not request.text or len(request.text.strip()) < 10:
        raise HTTPException(
            status_code=400, detail="Text must be at least 10 characters long"
        )

    # Generate paraphrase
    paraphrased, vocabulary_enhancements = await generate_paraphrase(
        request.text, request.intensity
    )

    # Save to database
    await save_paraphrase(
        user["id"],
        request.text,
        paraphrased,
        request.intensity,
        vocabulary_enhancements,
    )

    return ParaphraseResponse(
        original=request.text,
        paraphrased=paraphrased,
        vocabulary_enhancements=vocabulary_enhancements,
        intensity=request.intensity,
    )


@router.get("/history")
async def get_paraphrase_history(token: str = None):
    """Get user's paraphrase history"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        response = (
            supabase.table("paraphrases")
            .select("*")
            .eq("user_id", user["id"])
            .order("created_at", desc=True)
            .limit(50)
            .execute()
        )

        return {"paraphrases": response.data}
    except Exception as e:
        print(f"Error fetching paraphrase history: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch paraphrase history"
        )
