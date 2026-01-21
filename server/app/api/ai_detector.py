from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from core.database import supabase, get_user_from_token

router = APIRouter()

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
async def detect_ai_text(
    request: DetectTextRequest,
    token: str = None
):
    """Detect AI-generated content in text"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Analyze text for AI patterns
    result = analyze_text(request.text)
    
    # Save detection to database
    await save_detection(user['id'], request.text, result)
    
    return DetectTextResponse(result=result)

@router.post("/detect-file")
async def detect_ai_file(
    file,  # UploadFile
    token: str = None
):
    """Detect AI-generated content in uploaded file"""
    user = await get_user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Read file content
    content = await file.read()
    text = content.decode('utf-8')
    
    # Analyze text
    result = analyze_text(text)
    
    # Save detection to database
    await save_detection(user['id'], text, result)
    
    return DetectTextResponse(result=result)

def analyze_text(text: str) -> DetectionResult:
    """Analyze text for AI-generated content"""
    # TODO: Integrate HuggingFace AI detector model
    # Placeholder implementation with simple heuristics
    
    text_length = len(text)
    words = text.split()
    
    # Simple heuristic analysis (not actual AI detection)
    # Real implementation would use trained model
    ai_score = 0.3  # Placeholder
    human_score = 1.0 - ai_score
    
    verdict = "Likely human-written" if ai_score < 0.5 else "Likely AI-generated"
    confidence = max(ai_score, human_score)
    
    return DetectionResult(
        ai_probability=round(ai_score * 100, 2),
        human_probability=round(human_score * 100, 2),
        verdict=verdict,
        confidence=round(confidence * 100, 2),
        highlighted_sections=[]
    )

async def save_detection(user_id: str, text: str, result: DetectionResult):
    """Save AI detection to database"""
    try:
        detection_data = {
            'user_id': user_id,
            'text': text[:500],  # Store first 500 chars
            'ai_probability': result.ai_probability,
            'human_probability': result.human_probability,
            'verdict': result.verdict,
            'confidence': result.confidence
        }
        supabase.table('ai_detections').insert(detection_data).execute()
    except Exception as e:
        print(f"Error saving detection: {e}")
