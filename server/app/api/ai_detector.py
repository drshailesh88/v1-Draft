"""
AI Detector API - Agent E
Detects AI-generated content using heuristic-based analysis.

Features:
- Text analysis endpoint for AI detection
- Sentence-level analysis with highlighting
- Document-level aggregation
- Confidence scoring
- Detection history

Heuristic Analysis Approach:
- Sentence structure uniformity
- Vocabulary diversity (TTR - Type-Token Ratio)
- Punctuation patterns
- Sentence length variation
- Common AI writing patterns
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import re
import math
from collections import Counter
import statistics

from core.database import supabase

router = APIRouter()


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class SentenceAnalysis(BaseModel):
    """Analysis result for a single sentence."""
    text: str
    start_index: int
    end_index: int
    ai_probability: float
    classification: str  # "ai", "human", "uncertain"
    indicators: List[str]


class DocumentMetrics(BaseModel):
    """Document-level metrics from analysis."""
    total_sentences: int
    total_words: int
    total_characters: int
    avg_sentence_length: float
    sentence_length_std: float
    type_token_ratio: float
    punctuation_diversity: float
    avg_word_length: float
    complex_sentence_ratio: float
    passive_voice_ratio: float
    transition_word_ratio: float


class DetectionResult(BaseModel):
    """Complete detection result."""
    ai_probability: float
    human_probability: float
    verdict: str
    confidence: float
    highlighted_sections: List[SentenceAnalysis]
    document_metrics: DocumentMetrics
    analysis_breakdown: Dict[str, float]


class DetectTextRequest(BaseModel):
    """Request body for text detection."""
    text: str = Field(..., min_length=50, description="Text to analyze (minimum 50 characters)")


class DetectTextResponse(BaseModel):
    """Response for text detection."""
    success: bool
    result: DetectionResult
    detection_id: Optional[str] = None


class DetectionHistoryItem(BaseModel):
    """Single item in detection history."""
    id: str
    text_preview: str
    ai_probability: float
    human_probability: float
    verdict: str
    confidence: float
    created_at: str


class DetectionHistoryResponse(BaseModel):
    """Response for detection history."""
    success: bool
    detections: List[DetectionHistoryItem]
    total_count: int


# ============================================================================
# AI DETECTION HEURISTICS ENGINE
# ============================================================================

class AIDetectionEngine:
    """
    Heuristic-based AI detection engine.

    Analyzes text using multiple linguistic features that tend to differ
    between AI-generated and human-written text.
    """

    # Common AI transition words and phrases
    AI_TRANSITION_PATTERNS = [
        r'\bfurthermore\b', r'\bmoreover\b', r'\badditionally\b',
        r'\bin conclusion\b', r'\bto summarize\b', r'\bin summary\b',
        r'\bconsequently\b', r'\btherefore\b', r'\bhence\b',
        r'\bit is worth noting\b', r'\bit is important to\b',
        r'\bnevertheless\b', r'\bnonetheless\b', r'\bhowever\b',
        r'\bon the other hand\b', r'\bin contrast\b',
        r'\bsignificantly\b', r'\bnotably\b', r'\bspecifically\b',
        r'\bin this context\b', r'\bin this regard\b',
        r'\bas mentioned\b', r'\bas discussed\b', r'\bas noted\b'
    ]

    # Patterns common in AI writing
    AI_PHRASE_PATTERNS = [
        r'\bit is essential to\b', r'\bit is crucial to\b',
        r'\bthis highlights\b', r'\bthis demonstrates\b',
        r'\bthis underscores\b', r'\bthis illustrates\b',
        r'\bcan be attributed to\b', r'\bplays a crucial role\b',
        r'\bplays an important role\b', r'\bplays a significant role\b',
        r'\bin today\'s world\b', r'\bin the modern era\b',
        r'\bhas gained significant\b', r'\bhas become increasingly\b',
        r'\bprovides valuable insights\b', r'\boffers a comprehensive\b',
        r'\bit is imperative\b', r'\bit is paramount\b',
        r'\bfacilitates\b', r'\bleverage\b', r'\butilize\b',
        r'\bdelve into\b', r'\bembark on\b', r'\bnavigate\b'
    ]

    # Common hedging phrases in AI text
    AI_HEDGING_PATTERNS = [
        r'\bit can be argued\b', r'\bone could argue\b',
        r'\bit seems that\b', r'\bit appears that\b',
        r'\bit may be\b', r'\bit might be\b',
        r'\bthere is evidence to suggest\b', r'\bresearch suggests\b',
        r'\bstudies indicate\b', r'\bexperts believe\b'
    ]

    # Passive voice patterns
    PASSIVE_PATTERNS = [
        r'\b(?:is|are|was|were|been|being)\s+\w+ed\b',
        r'\b(?:is|are|was|were|been|being)\s+\w+en\b',
        r'\bhas been\b', r'\bhave been\b', r'\bwill be\b'
    ]

    def __init__(self):
        self.compiled_ai_transitions = [re.compile(p, re.IGNORECASE) for p in self.AI_TRANSITION_PATTERNS]
        self.compiled_ai_phrases = [re.compile(p, re.IGNORECASE) for p in self.AI_PHRASE_PATTERNS]
        self.compiled_ai_hedging = [re.compile(p, re.IGNORECASE) for p in self.AI_HEDGING_PATTERNS]
        self.compiled_passive = [re.compile(p, re.IGNORECASE) for p in self.PASSIVE_PATTERNS]

    def split_into_sentences(self, text: str) -> List[tuple]:
        """Split text into sentences with their positions."""
        # Pattern to split on sentence boundaries
        pattern = r'(?<=[.!?])\s+(?=[A-Z])'

        sentences = []
        last_end = 0

        for match in re.finditer(pattern, text):
            sentence = text[last_end:match.start()].strip()
            if sentence:
                sentences.append((sentence, last_end, match.start()))
            last_end = match.end()

        # Don't forget the last sentence
        if last_end < len(text):
            sentence = text[last_end:].strip()
            if sentence:
                sentences.append((sentence, last_end, len(text)))

        # If no sentences found, treat entire text as one sentence
        if not sentences and text.strip():
            sentences = [(text.strip(), 0, len(text))]

        return sentences

    def tokenize(self, text: str) -> List[str]:
        """Simple word tokenization."""
        # Remove punctuation and split by whitespace
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        return words

    def calculate_ttr(self, words: List[str]) -> float:
        """Calculate Type-Token Ratio (vocabulary diversity)."""
        if not words:
            return 0.0
        unique_words = set(words)
        return len(unique_words) / len(words)

    def calculate_sentence_length_stats(self, sentences: List[tuple]) -> tuple:
        """Calculate mean and std of sentence lengths."""
        if not sentences:
            return 0.0, 0.0

        lengths = [len(self.tokenize(s[0])) for s in sentences]
        if len(lengths) < 2:
            return lengths[0] if lengths else 0.0, 0.0

        mean_length = statistics.mean(lengths)
        std_length = statistics.stdev(lengths)
        return mean_length, std_length

    def calculate_punctuation_diversity(self, text: str) -> float:
        """Calculate diversity of punctuation usage."""
        punctuation = re.findall(r'[.,;:!?\-\'"()\[\]{}]', text)
        if not punctuation:
            return 0.0

        punct_counts = Counter(punctuation)
        total = len(punctuation)

        # Calculate entropy as diversity measure
        entropy = 0.0
        for count in punct_counts.values():
            p = count / total
            entropy -= p * math.log2(p) if p > 0 else 0

        # Normalize by max possible entropy
        max_entropy = math.log2(len(punct_counts)) if len(punct_counts) > 1 else 1
        return entropy / max_entropy if max_entropy > 0 else 0.0

    def count_pattern_matches(self, text: str, patterns: List[re.Pattern]) -> int:
        """Count how many times patterns match in text."""
        count = 0
        for pattern in patterns:
            count += len(pattern.findall(text))
        return count

    def calculate_complex_sentence_ratio(self, sentences: List[tuple]) -> float:
        """Calculate ratio of complex sentences (with subordinate clauses)."""
        if not sentences:
            return 0.0

        complex_markers = [
            r'\b(?:which|that|who|whom|whose|where|when|while|although|because|since|unless|if|whether)\b'
        ]
        complex_pattern = re.compile('|'.join(complex_markers), re.IGNORECASE)

        complex_count = sum(1 for s in sentences if complex_pattern.search(s[0]))
        return complex_count / len(sentences)

    def analyze_sentence(self, sentence: str, start_idx: int, end_idx: int) -> SentenceAnalysis:
        """Analyze a single sentence for AI indicators."""
        indicators = []
        ai_score = 0.0

        words = self.tokenize(sentence)
        word_count = len(words)

        # Check for AI transition words
        transition_count = self.count_pattern_matches(sentence, self.compiled_ai_transitions)
        if transition_count > 0:
            indicators.append(f"transition_words:{transition_count}")
            ai_score += min(transition_count * 0.1, 0.3)

        # Check for AI phrase patterns
        phrase_count = self.count_pattern_matches(sentence, self.compiled_ai_phrases)
        if phrase_count > 0:
            indicators.append(f"ai_phrases:{phrase_count}")
            ai_score += min(phrase_count * 0.15, 0.4)

        # Check for hedging patterns
        hedging_count = self.count_pattern_matches(sentence, self.compiled_ai_hedging)
        if hedging_count > 0:
            indicators.append(f"hedging:{hedging_count}")
            ai_score += min(hedging_count * 0.1, 0.2)

        # Check for passive voice
        passive_count = self.count_pattern_matches(sentence, self.compiled_passive)
        if passive_count > 0 and word_count > 0:
            passive_ratio = passive_count / word_count
            if passive_ratio > 0.1:
                indicators.append(f"passive_voice:{passive_count}")
                ai_score += 0.1

        # Sentence length analysis (AI tends to have more uniform length)
        if 15 <= word_count <= 25:  # "Perfect" length range common in AI
            indicators.append("typical_ai_length")
            ai_score += 0.05

        # Check for overly formal words
        formal_words = ['utilize', 'facilitate', 'implement', 'leverage', 'optimize',
                       'comprehensive', 'significant', 'substantial', 'fundamental']
        formal_count = sum(1 for w in words if w in formal_words)
        if formal_count > 0:
            indicators.append(f"formal_words:{formal_count}")
            ai_score += min(formal_count * 0.1, 0.2)

        # Cap the score at 1.0
        ai_score = min(ai_score, 1.0)

        # Determine classification
        if ai_score >= 0.6:
            classification = "ai"
        elif ai_score <= 0.3:
            classification = "human"
        else:
            classification = "uncertain"

        return SentenceAnalysis(
            text=sentence,
            start_index=start_idx,
            end_index=end_idx,
            ai_probability=round(ai_score * 100, 2),
            classification=classification,
            indicators=indicators
        )

    def analyze_document(self, text: str) -> DetectionResult:
        """Perform complete document analysis."""
        # Split into sentences
        sentences = self.split_into_sentences(text)

        # Tokenize entire document
        all_words = self.tokenize(text)

        # Calculate document-level metrics
        avg_len, std_len = self.calculate_sentence_length_stats(sentences)
        ttr = self.calculate_ttr(all_words)
        punct_diversity = self.calculate_punctuation_diversity(text)
        avg_word_length = statistics.mean([len(w) for w in all_words]) if all_words else 0
        complex_ratio = self.calculate_complex_sentence_ratio(sentences)

        # Calculate passive voice ratio
        total_passive = self.count_pattern_matches(text, self.compiled_passive)
        passive_ratio = total_passive / len(sentences) if sentences else 0

        # Calculate transition word ratio
        total_transitions = self.count_pattern_matches(text, self.compiled_ai_transitions)
        transition_ratio = total_transitions / len(sentences) if sentences else 0

        document_metrics = DocumentMetrics(
            total_sentences=len(sentences),
            total_words=len(all_words),
            total_characters=len(text),
            avg_sentence_length=round(avg_len, 2),
            sentence_length_std=round(std_len, 2),
            type_token_ratio=round(ttr, 4),
            punctuation_diversity=round(punct_diversity, 4),
            avg_word_length=round(avg_word_length, 2),
            complex_sentence_ratio=round(complex_ratio, 4),
            passive_voice_ratio=round(passive_ratio, 4),
            transition_word_ratio=round(transition_ratio, 4)
        )

        # Analyze each sentence
        sentence_analyses = []
        for sentence_text, start_idx, end_idx in sentences:
            analysis = self.analyze_sentence(sentence_text, start_idx, end_idx)
            sentence_analyses.append(analysis)

        # Calculate overall AI probability from multiple signals
        analysis_breakdown = self._calculate_analysis_breakdown(document_metrics, sentence_analyses)

        # Weighted combination of signals
        weights = {
            'sentence_uniformity': 0.15,
            'vocabulary_diversity': 0.15,
            'ai_phrases': 0.25,
            'transition_density': 0.15,
            'passive_voice': 0.10,
            'sentence_ai_avg': 0.20
        }

        ai_probability = sum(
            analysis_breakdown.get(key, 0) * weight
            for key, weight in weights.items()
        )

        # Ensure probability is in valid range
        ai_probability = max(0, min(100, ai_probability))
        human_probability = 100 - ai_probability

        # Determine verdict
        if ai_probability >= 70:
            verdict = "Likely AI-generated"
        elif ai_probability >= 50:
            verdict = "Mixed/Uncertain - Contains AI patterns"
        elif ai_probability >= 30:
            verdict = "Mostly human-written with some AI assistance"
        else:
            verdict = "Likely human-written"

        # Calculate confidence based on consistency of signals
        signal_values = [analysis_breakdown[k] for k in weights.keys() if k in analysis_breakdown]
        if len(signal_values) > 1:
            signal_std = statistics.stdev(signal_values)
            confidence = max(50, 100 - signal_std)  # Higher std = lower confidence
        else:
            confidence = 60  # Default moderate confidence

        return DetectionResult(
            ai_probability=round(ai_probability, 2),
            human_probability=round(human_probability, 2),
            verdict=verdict,
            confidence=round(confidence, 2),
            highlighted_sections=sentence_analyses,
            document_metrics=document_metrics,
            analysis_breakdown=analysis_breakdown
        )

    def _calculate_analysis_breakdown(
        self,
        metrics: DocumentMetrics,
        sentence_analyses: List[SentenceAnalysis]
    ) -> Dict[str, float]:
        """Calculate breakdown of AI signals."""
        breakdown = {}

        # Sentence uniformity score (AI tends to have more uniform sentence lengths)
        # Lower std relative to mean = more uniform = higher AI score
        if metrics.avg_sentence_length > 0:
            cv = metrics.sentence_length_std / metrics.avg_sentence_length  # Coefficient of variation
            # CV < 0.3 is very uniform, CV > 0.6 is quite varied
            uniformity_score = max(0, min(100, (0.6 - cv) / 0.6 * 100))
        else:
            uniformity_score = 50
        breakdown['sentence_uniformity'] = uniformity_score

        # Vocabulary diversity (AI often has lower diversity for longer texts)
        # TTR typically ranges from 0.3 to 0.7
        # Lower TTR = less diverse = potentially more AI
        ttr_score = max(0, min(100, (0.7 - metrics.type_token_ratio) / 0.4 * 100))
        breakdown['vocabulary_diversity'] = ttr_score

        # AI phrase density
        total_ai_phrases = sum(
            int(ind.split(':')[1])
            for sa in sentence_analyses
            for ind in sa.indicators
            if ind.startswith('ai_phrases:')
        )
        phrase_density = total_ai_phrases / metrics.total_sentences if metrics.total_sentences > 0 else 0
        breakdown['ai_phrases'] = min(100, phrase_density * 200)  # Scale: 0.5 phrases/sentence = 100

        # Transition word density
        transition_score = min(100, metrics.transition_word_ratio * 150)  # Scale up
        breakdown['transition_density'] = transition_score

        # Passive voice score
        passive_score = min(100, metrics.passive_voice_ratio * 100)
        breakdown['passive_voice'] = passive_score

        # Average sentence-level AI probability
        if sentence_analyses:
            avg_sentence_ai = statistics.mean([sa.ai_probability for sa in sentence_analyses])
        else:
            avg_sentence_ai = 50
        breakdown['sentence_ai_avg'] = avg_sentence_ai

        return {k: round(v, 2) for k, v in breakdown.items()}


# Initialize the detection engine
detection_engine = AIDetectionEngine()


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/detect-text", response_model=DetectTextResponse)
async def detect_ai_text(request: DetectTextRequest):
    """
    Detect AI-generated content in text.

    Analyzes the provided text using multiple heuristic signals:
    - Sentence structure uniformity
    - Vocabulary diversity (Type-Token Ratio)
    - AI-specific phrase patterns
    - Passive voice usage
    - Transition word density

    Returns detailed analysis with sentence-level highlighting.
    """
    try:
        # Validate input
        if len(request.text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Text must be at least 50 characters for meaningful analysis"
            )

        # Perform analysis
        result = detection_engine.analyze_document(request.text)

        # Save to database (without user_id for development mode)
        detection_id = await save_detection(
            user_id=None,  # Development mode - no auth
            text=request.text,
            result=result
        )

        return DetectTextResponse(
            success=True,
            result=result,
            detection_id=detection_id
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/detect-file", response_model=DetectTextResponse)
async def detect_ai_file(file: UploadFile = File(...)):
    """
    Detect AI-generated content in an uploaded text file.

    Supports .txt files. Reads the file content and performs
    the same analysis as the text endpoint.
    """
    try:
        # Validate file type
        if not file.filename.endswith(('.txt', '.md')):
            raise HTTPException(
                status_code=400,
                detail="Only .txt and .md files are supported"
            )

        # Read file content
        content = await file.read()
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            text = content.decode('latin-1')

        # Validate content length
        if len(text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="File content must be at least 50 characters"
            )

        # Perform analysis
        result = detection_engine.analyze_document(text)

        # Save to database
        detection_id = await save_detection(
            user_id=None,
            text=text,
            result=result
        )

        return DetectTextResponse(
            success=True,
            result=result,
            detection_id=detection_id
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File analysis failed: {str(e)}")


@router.get("/detection/{detection_id}")
async def get_detection(detection_id: str):
    """
    Retrieve a specific detection result by ID.
    """
    try:
        response = supabase.table('ai_detections').select('*').eq('id', detection_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Detection not found")

        detection = response.data[0]
        return {
            "success": True,
            "detection": detection
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve detection: {str(e)}")


@router.get("/history", response_model=DetectionHistoryResponse)
async def get_detection_history(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user_id: Optional[str] = Query(default=None)
):
    """
    Get detection history.

    In development mode (no auth), returns all detections or filters by user_id if provided.
    """
    try:
        query = supabase.table('ai_detections').select('*', count='exact')

        if user_id:
            query = query.eq('user_id', user_id)

        query = query.order('created_at', desc=True).range(offset, offset + limit - 1)
        response = query.execute()

        detections = [
            DetectionHistoryItem(
                id=d['id'],
                text_preview=d['text'][:100] + '...' if len(d['text']) > 100 else d['text'],
                ai_probability=d['ai_probability'],
                human_probability=d['human_probability'],
                verdict=d['verdict'],
                confidence=d['confidence'],
                created_at=d['created_at']
            )
            for d in response.data
        ]

        return DetectionHistoryResponse(
            success=True,
            detections=detections,
            total_count=response.count or len(detections)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


@router.delete("/detection/{detection_id}")
async def delete_detection(detection_id: str):
    """
    Delete a detection record.
    """
    try:
        response = supabase.table('ai_detections').delete().eq('id', detection_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Detection not found")

        return {"success": True, "message": "Detection deleted"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete detection: {str(e)}")


@router.post("/analyze-batch")
async def analyze_batch(texts: List[str]):
    """
    Analyze multiple texts in batch.

    Useful for analyzing multiple paragraphs or sections separately.
    """
    try:
        if len(texts) > 20:
            raise HTTPException(
                status_code=400,
                detail="Maximum 20 texts per batch"
            )

        results = []
        for i, text in enumerate(texts):
            if len(text.strip()) < 20:
                results.append({
                    "index": i,
                    "error": "Text too short for analysis",
                    "result": None
                })
            else:
                result = detection_engine.analyze_document(text)
                results.append({
                    "index": i,
                    "error": None,
                    "result": result.model_dump()
                })

        return {
            "success": True,
            "results": results,
            "total_analyzed": len([r for r in results if r['result'] is not None])
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint for the AI detector service.
    """
    return {
        "status": "healthy",
        "service": "ai-detector",
        "version": "1.0.0",
        "features": [
            "text_analysis",
            "file_analysis",
            "sentence_highlighting",
            "batch_analysis",
            "detection_history"
        ]
    }


# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

async def save_detection(
    user_id: Optional[str],
    text: str,
    result: DetectionResult
) -> Optional[str]:
    """
    Save AI detection result to database.

    Returns the detection ID if successful, None otherwise.
    """
    try:
        detection_data = {
            'user_id': user_id,
            'text': text[:5000],  # Store first 5000 chars
            'ai_probability': result.ai_probability,
            'human_probability': result.human_probability,
            'verdict': result.verdict,
            'confidence': result.confidence
        }

        response = supabase.table('ai_detections').insert(detection_data).execute()

        if response.data:
            return response.data[0].get('id')
        return None

    except Exception as e:
        print(f"Error saving detection: {e}")
        return None
