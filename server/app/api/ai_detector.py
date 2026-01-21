from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from core.database import supabase, get_user_from_token
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

router = APIRouter()

# Load AI detection model (lazy loading)
model = None
tokenizer = None
MODEL_NAME = "roberta-base-openai-detector"


def load_model():
    """Load the AI detection model on first use"""
    global model, tokenizer
    if model is None:
        print("Loading AI detection model...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        model.eval()
        print("AI detection model loaded")
    return model, tokenizer


class DetectTextRequest(BaseModel):
    text: str


class DetectionResult(BaseModel):
    ai_probability: float
    human_probability: float
    verdict: str
    confidence: float
    highlighted_sections: List[dict]


class DetectTextResponse(BaseModel):
    result: DetectionResult


@router.post("/detect-text", response_model=DetectTextResponse)
async def detect_ai_text(request: DetectTextRequest, token: str = None):
    """Detect AI-generated content in text"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Analyze text for AI patterns
    result = analyze_text(request.text)

    # Save detection to database
    await save_detection(user["id"], request.text, result)

    return DetectTextResponse(result=result)


@router.post("/detect-file")
async def detect_ai_file(
    file,  # UploadFile
    token: str = None,
):
    """Detect AI-generated content in uploaded file"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Read file content
    content = await file.read()
    text = content.decode("utf-8")

    # Analyze text
    result = analyze_text(text)

    # Save detection to database
    await save_detection(user["id"], text, result)

    return DetectTextResponse(result=result)


def analyze_text(text: str) -> DetectionResult:
    """Analyze text for AI-generated content using HuggingFace model"""
    try:
        # Load model if not loaded
        ai_model, ai_tokenizer = load_model()

        # Truncate text if too long
        max_length = 512
        if len(text) > max_length * 4:  # Approximate character limit
            text = text[: max_length * 4]

        # Tokenize and predict
        inputs = ai_tokenizer(
            text, return_tensors="pt", truncation=True, max_length=max_length
        )

        with torch.no_grad():
            outputs = ai_model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

        # Get AI and human probabilities
        # Model typically outputs: [human, AI] or [AI, human] depending on the specific model
        probs = predictions[0].tolist()

        # roberta-base-openai-detector has 2 classes: "human" and "machine"
        human_prob = probs[0]  # Assuming first class is human
        ai_prob = probs[1]  # Assuming second class is AI/machine

        # Determine verdict
        if ai_prob > 0.7:
            verdict = "Likely AI-generated"
        elif ai_prob > 0.5:
            verdict = "Possibly AI-generated"
        elif ai_prob > 0.3:
            verdict = "Possibly human-written"
        else:
            verdict = "Likely human-written"

        confidence = max(ai_prob, human_prob)

        # Highlight sections (simplified - just flag entire text)
        highlighted_sections = [
            {
                "start": 0,
                "end": len(text),
                "type": "high_ai_probability" if ai_prob > 0.5 else "human_written",
                "score": round(ai_prob * 100, 2),
            }
        ]

        return DetectionResult(
            ai_probability=round(ai_prob * 100, 2),
            human_probability=round(human_prob * 100, 2),
            verdict=verdict,
            confidence=round(confidence * 100, 2),
            highlighted_sections=highlighted_sections,
        )

    except Exception as e:
        print(f"Error in AI detection: {e}")
        # Fallback to placeholder
        return DetectionResult(
            ai_probability=50.0,
            human_probability=50.0,
            verdict="Unable to determine",
            confidence=0.0,
            highlighted_sections=[],
        )


async def save_detection(user_id: str, text: str, result: DetectionResult):
    """Save AI detection to database"""
    try:
        detection_data = {
            "user_id": user_id,
            "text": text[:500],  # Store first 500 chars
            "ai_probability": result.ai_probability,
            "human_probability": result.human_probability,
            "verdict": result.verdict,
            "confidence": result.confidence,
        }
        supabase.table("ai_detections").insert(detection_data).execute()
    except Exception as e:
        print(f"Error saving detection: {e}")
