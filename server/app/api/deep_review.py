"""
Deep Review API - Capstone Feature
Comprehensive academic document analysis integrating multiple features:
- Literature Search for finding related work
- Citation Booster for citation suggestions
- AI Detector for AI content detection
- Citation Generator for citation formatting

Features:
- Document upload and analysis
- Multi-perspective peer review (methodology expert, domain expert, writing expert)
- Strength/weakness identification
- Citation quality analysis
- AI content detection integration
- Writing quality metrics
- Prioritized improvement suggestions
- Overall quality score calculation
- Export review report
"""

import asyncio
import json
import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel, Field

from core.database import supabase
from core.openai_client import async_client, chat_completion

# Import from existing feature modules
from app.api.literature import (
    Paper,
    search_pubmed,
    search_arxiv,
    search_semantic_scholar,
    deduplicate_papers,
)
from app.api.citations import (
    CitationMetadata,
    CitationStyle,
    CitationFormatter,
    ExportGenerator,
    ExportFormat,
)
from app.api.ai_detector import detection_engine, DetectionResult
from app.api.citation_booster import (
    extract_claims_from_text,
    extract_concepts_from_text,
    identify_citation_gaps,
    Claim,
    Concept,
    CitationGap,
)


router = APIRouter()


# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================

class ReviewerPerspective(str, Enum):
    """Different reviewer perspectives for peer review simulation"""
    METHODOLOGY = "methodology"
    DOMAIN = "domain"
    WRITING = "writing"
    STATISTICAL = "statistical"
    ETHICS = "ethics"


class SeverityLevel(str, Enum):
    """Severity levels for issues"""
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    SUGGESTION = "suggestion"


class DocumentSection(str, Enum):
    """Common academic document sections"""
    ABSTRACT = "abstract"
    INTRODUCTION = "introduction"
    LITERATURE_REVIEW = "literature_review"
    METHODOLOGY = "methodology"
    RESULTS = "results"
    DISCUSSION = "discussion"
    CONCLUSION = "conclusion"
    REFERENCES = "references"
    OTHER = "other"


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class ReviewIssue(BaseModel):
    """A single issue identified in the review"""
    id: str
    category: str
    severity: SeverityLevel
    location: Optional[str] = None
    section: Optional[DocumentSection] = None
    description: str
    suggestion: str
    confidence: float = Field(ge=0, le=1)


class StrengthItem(BaseModel):
    """A strength identified in the document"""
    category: str
    description: str
    section: Optional[DocumentSection] = None
    impact: str  # high, medium, low


class WeaknessItem(BaseModel):
    """A weakness identified in the document"""
    category: str
    description: str
    section: Optional[DocumentSection] = None
    severity: SeverityLevel
    suggestion: str


class MethodologyCritique(BaseModel):
    """Detailed methodology critique"""
    overall_assessment: str
    score: float = Field(ge=0, le=100)
    design_appropriateness: Dict[str, Any]
    sampling_assessment: Optional[Dict[str, Any]] = None
    data_collection: Optional[Dict[str, Any]] = None
    analysis_methods: Optional[Dict[str, Any]] = None
    validity_concerns: List[str]
    reliability_concerns: List[str]
    recommendations: List[str]


class CitationQualityAssessment(BaseModel):
    """Assessment of citation quality"""
    overall_score: float = Field(ge=0, le=100)
    total_citations_needed: int
    citations_present: int
    missing_citations: int
    citation_gaps: List[CitationGap]
    recency_score: float  # How recent are the citations
    relevance_score: float  # How relevant are existing citations
    diversity_score: float  # Diversity of sources
    suggested_citations: List[Paper]
    recommendations: List[str]


class WritingQualityMetrics(BaseModel):
    """Writing quality metrics"""
    overall_score: float = Field(ge=0, le=100)
    clarity_score: float
    coherence_score: float
    grammar_score: float
    academic_tone_score: float
    sentence_variety: float
    avg_sentence_length: float
    vocabulary_diversity: float
    passive_voice_ratio: float
    readability_score: float  # Flesch-Kincaid or similar
    issues: List[ReviewIssue]


class AIContentAnalysis(BaseModel):
    """AI content detection analysis"""
    ai_probability: float
    human_probability: float
    verdict: str
    confidence: float
    flagged_sections: List[Dict[str, Any]]
    recommendations: List[str]


class PeerReviewerFeedback(BaseModel):
    """Feedback from a single peer reviewer perspective"""
    perspective: ReviewerPerspective
    overall_assessment: str
    score: float = Field(ge=0, le=100)
    strengths: List[str]
    weaknesses: List[str]
    critical_issues: List[ReviewIssue]
    recommendations: List[str]
    detailed_comments: List[Dict[str, Any]]


class ImprovementSuggestion(BaseModel):
    """Prioritized improvement suggestion"""
    id: str
    priority: int  # 1 = highest priority
    category: str
    title: str
    description: str
    impact: str  # high, medium, low
    effort: str  # high, medium, low
    section: Optional[DocumentSection] = None
    related_issues: List[str]  # IDs of related issues


class DeepReviewRequest(BaseModel):
    """Request for deep review analysis"""
    text: str = Field(..., min_length=100, description="Document text to analyze")
    document_type: str = Field(default="research_paper", description="Type of document")
    field: Optional[str] = Field(default=None, description="Academic field/discipline")
    include_ai_detection: bool = Field(default=True)
    include_literature_search: bool = Field(default=True)
    include_citation_analysis: bool = Field(default=True)
    reviewer_perspectives: List[ReviewerPerspective] = Field(
        default=[ReviewerPerspective.METHODOLOGY, ReviewerPerspective.DOMAIN, ReviewerPerspective.WRITING]
    )
    max_related_papers: int = Field(default=10, ge=1, le=50)


class DeepReviewResponse(BaseModel):
    """Complete deep review response"""
    review_id: str
    document_summary: Dict[str, Any]
    overall_quality_score: float
    grade: str  # A, B, C, D, F or Accept/Revise/Reject

    # Core analyses
    strengths: List[StrengthItem]
    weaknesses: List[WeaknessItem]
    methodology_critique: Optional[MethodologyCritique] = None
    citation_quality: Optional[CitationQualityAssessment] = None
    writing_quality: WritingQualityMetrics
    ai_content_analysis: Optional[AIContentAnalysis] = None

    # Peer review simulation
    peer_reviews: List[PeerReviewerFeedback]

    # Related work
    related_papers: List[Paper]

    # Improvement suggestions
    improvement_suggestions: List[ImprovementSuggestion]

    # Summary
    executive_summary: str
    verdict: str
    created_at: str


class ExportReviewRequest(BaseModel):
    """Request to export review report"""
    review_id: str
    format: str = Field(default="markdown", description="Export format: markdown, html, pdf, json")
    include_sections: List[str] = Field(
        default=["all"],
        description="Sections to include in export"
    )


class ExportReviewResponse(BaseModel):
    """Response with exported review"""
    format: str
    content: str
    filename: str


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def analyze_document_structure(text: str) -> Dict[str, Any]:
    """Analyze document structure and identify sections"""
    prompt = f"""Analyze this academic document and identify:
1. The document type (research paper, thesis, literature review, etc.)
2. The main sections present
3. Word count and approximate page count
4. The academic field/discipline
5. A brief summary (2-3 sentences)

Document text (first 4000 chars):
{text[:4000]}

Respond in JSON format:
{{
    "document_type": "research_paper",
    "sections_found": ["abstract", "introduction", "methodology", "results", "discussion", "conclusion"],
    "word_count": 5000,
    "estimated_pages": 15,
    "field": "computer science",
    "summary": "Brief summary here",
    "title_if_found": "Paper title or null",
    "has_abstract": true,
    "has_methodology": true,
    "has_references": true
}}"""

    try:
        response = await async_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an academic document analysis expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error analyzing document structure: {e}")
        return {
            "document_type": "unknown",
            "sections_found": [],
            "word_count": len(text.split()),
            "estimated_pages": len(text.split()) // 300,
            "field": "unknown",
            "summary": "Unable to generate summary",
            "error": str(e)
        }


async def identify_strengths_and_weaknesses(text: str, document_info: Dict[str, Any]) -> tuple:
    """Identify strengths and weaknesses in the document"""
    prompt = f"""As an expert academic reviewer, analyze this document and identify its strengths and weaknesses.

Document type: {document_info.get('document_type', 'research paper')}
Field: {document_info.get('field', 'unknown')}

Document text (first 6000 chars):
{text[:6000]}

Identify:
1. At least 3-5 strengths (what the document does well)
2. At least 3-5 weaknesses (areas needing improvement)

For each, specify the category (methodology, writing, analysis, structure, argumentation, etc.)
and the section where it occurs if applicable.

Respond in JSON format:
{{
    "strengths": [
        {{
            "category": "methodology",
            "description": "Clear research design with well-defined variables",
            "section": "methodology",
            "impact": "high"
        }}
    ],
    "weaknesses": [
        {{
            "category": "analysis",
            "description": "Limited statistical analysis of results",
            "section": "results",
            "severity": "major",
            "suggestion": "Include confidence intervals and effect sizes"
        }}
    ]
}}"""

    try:
        response = await async_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a thorough academic peer reviewer providing constructive feedback."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)

        strengths = [
            StrengthItem(
                category=s.get("category", "general"),
                description=s.get("description", ""),
                section=s.get("section"),
                impact=s.get("impact", "medium")
            )
            for s in result.get("strengths", [])
        ]

        weaknesses = [
            WeaknessItem(
                category=w.get("category", "general"),
                description=w.get("description", ""),
                section=w.get("section"),
                severity=SeverityLevel(w.get("severity", "minor")),
                suggestion=w.get("suggestion", "")
            )
            for w in result.get("weaknesses", [])
        ]

        return strengths, weaknesses
    except Exception as e:
        print(f"Error identifying strengths/weaknesses: {e}")
        return [], []


async def critique_methodology(text: str, document_info: Dict[str, Any]) -> MethodologyCritique:
    """Perform detailed methodology critique"""
    prompt = f"""As a methodology expert, critically evaluate the research methodology in this document.

Document type: {document_info.get('document_type', 'research paper')}
Field: {document_info.get('field', 'unknown')}

Document text:
{text[:8000]}

Evaluate:
1. Research design appropriateness
2. Sampling methods (if applicable)
3. Data collection procedures
4. Analysis methods
5. Validity and reliability concerns
6. Overall methodology score (0-100)

Respond in JSON format:
{{
    "overall_assessment": "The methodology is generally sound but has some limitations...",
    "score": 75,
    "design_appropriateness": {{
        "score": 80,
        "assessment": "The research design is appropriate for the research questions",
        "concerns": ["Limited control group discussion"]
    }},
    "sampling_assessment": {{
        "score": 70,
        "sample_size_adequate": true,
        "sampling_method": "convenience sampling",
        "concerns": ["Potential selection bias"]
    }},
    "data_collection": {{
        "score": 75,
        "methods_described": true,
        "instruments_valid": true,
        "concerns": ["Limited detail on data collection timeline"]
    }},
    "analysis_methods": {{
        "score": 72,
        "appropriate_for_data": true,
        "concerns": ["Could benefit from additional statistical tests"]
    }},
    "validity_concerns": ["Internal validity affected by...", "External validity limited due to..."],
    "reliability_concerns": ["Inter-rater reliability not reported"],
    "recommendations": ["Include power analysis", "Add member checking for qualitative data"]
}}"""

    try:
        response = await async_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert research methodologist providing detailed critique."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)

        return MethodologyCritique(
            overall_assessment=result.get("overall_assessment", ""),
            score=result.get("score", 50),
            design_appropriateness=result.get("design_appropriateness", {}),
            sampling_assessment=result.get("sampling_assessment"),
            data_collection=result.get("data_collection"),
            analysis_methods=result.get("analysis_methods"),
            validity_concerns=result.get("validity_concerns", []),
            reliability_concerns=result.get("reliability_concerns", []),
            recommendations=result.get("recommendations", [])
        )
    except Exception as e:
        print(f"Error critiquing methodology: {e}")
        return MethodologyCritique(
            overall_assessment="Unable to perform methodology critique",
            score=0,
            design_appropriateness={},
            validity_concerns=[],
            reliability_concerns=[],
            recommendations=[]
        )


async def assess_writing_quality(text: str) -> WritingQualityMetrics:
    """Assess writing quality using heuristics and GPT analysis"""

    # Calculate basic metrics
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = text.split()

    avg_sentence_length = len(words) / len(sentences) if sentences else 0

    # Vocabulary diversity (type-token ratio)
    unique_words = set(word.lower() for word in words if word.isalpha())
    vocabulary_diversity = len(unique_words) / len(words) if words else 0

    # Passive voice detection (simple heuristic)
    passive_patterns = [
        r'\b(?:is|are|was|were|been|being)\s+\w+ed\b',
        r'\b(?:is|are|was|were|been|being)\s+\w+en\b'
    ]
    passive_count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in passive_patterns)
    passive_voice_ratio = passive_count / len(sentences) if sentences else 0

    # Sentence length variety
    sentence_lengths = [len(s.split()) for s in sentences]
    if len(sentence_lengths) > 1:
        import statistics
        sentence_variety = statistics.stdev(sentence_lengths) / (sum(sentence_lengths) / len(sentence_lengths)) if sentence_lengths else 0
    else:
        sentence_variety = 0

    # GPT-based quality assessment
    prompt = f"""Evaluate the writing quality of this academic text on a scale of 0-100 for each criterion:

Text (first 3000 chars):
{text[:3000]}

Evaluate:
1. Clarity - How clear and understandable is the writing?
2. Coherence - How well do ideas flow and connect?
3. Grammar - How correct is the grammar and punctuation?
4. Academic Tone - How appropriate is the tone for academic writing?
5. Readability - How easy is it to read and comprehend?

Also identify 3-5 specific writing issues with their locations and suggestions.

Respond in JSON format:
{{
    "clarity_score": 75,
    "coherence_score": 80,
    "grammar_score": 85,
    "academic_tone_score": 78,
    "readability_score": 72,
    "issues": [
        {{
            "category": "clarity",
            "severity": "minor",
            "location": "paragraph 2",
            "description": "Unclear pronoun reference",
            "suggestion": "Specify what 'it' refers to"
        }}
    ]
}}"""

    try:
        response = await async_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert academic writing evaluator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)

        # Parse issues
        issues = []
        for i, issue in enumerate(result.get("issues", [])):
            issues.append(ReviewIssue(
                id=f"writing-{i+1}",
                category=issue.get("category", "writing"),
                severity=SeverityLevel(issue.get("severity", "minor")),
                location=issue.get("location"),
                description=issue.get("description", ""),
                suggestion=issue.get("suggestion", ""),
                confidence=0.8
            ))

        # Calculate overall score
        scores = [
            result.get("clarity_score", 70),
            result.get("coherence_score", 70),
            result.get("grammar_score", 70),
            result.get("academic_tone_score", 70),
            result.get("readability_score", 70)
        ]
        overall_score = sum(scores) / len(scores)

        return WritingQualityMetrics(
            overall_score=overall_score,
            clarity_score=result.get("clarity_score", 70),
            coherence_score=result.get("coherence_score", 70),
            grammar_score=result.get("grammar_score", 70),
            academic_tone_score=result.get("academic_tone_score", 70),
            sentence_variety=round(sentence_variety, 3),
            avg_sentence_length=round(avg_sentence_length, 1),
            vocabulary_diversity=round(vocabulary_diversity, 3),
            passive_voice_ratio=round(passive_voice_ratio, 3),
            readability_score=result.get("readability_score", 70),
            issues=issues
        )
    except Exception as e:
        print(f"Error assessing writing quality: {e}")
        return WritingQualityMetrics(
            overall_score=50,
            clarity_score=50,
            coherence_score=50,
            grammar_score=50,
            academic_tone_score=50,
            sentence_variety=round(sentence_variety, 3),
            avg_sentence_length=round(avg_sentence_length, 1),
            vocabulary_diversity=round(vocabulary_diversity, 3),
            passive_voice_ratio=round(passive_voice_ratio, 3),
            readability_score=50,
            issues=[]
        )


async def perform_ai_content_analysis(text: str) -> AIContentAnalysis:
    """Perform AI content detection using the AI Detector module"""
    try:
        result = detection_engine.analyze_document(text)

        # Extract flagged sections
        flagged_sections = []
        for section in result.highlighted_sections:
            if section.ai_probability > 60:  # Flag sections with >60% AI probability
                flagged_sections.append({
                    "text_preview": section.text[:200] + "..." if len(section.text) > 200 else section.text,
                    "ai_probability": section.ai_probability,
                    "classification": section.classification,
                    "indicators": section.indicators
                })

        # Generate recommendations based on AI detection
        recommendations = []
        if result.ai_probability > 70:
            recommendations.append("Significant AI-generated content detected. Consider rewriting key sections in your own voice.")
            recommendations.append("Add more personal insights and original analysis to the flagged sections.")
        elif result.ai_probability > 50:
            recommendations.append("Some sections show AI writing patterns. Review and personalize these areas.")
        else:
            recommendations.append("Content appears primarily human-written.")

        if len(flagged_sections) > 0:
            recommendations.append(f"Review the {len(flagged_sections)} flagged sections for potential AI-generated content.")

        return AIContentAnalysis(
            ai_probability=result.ai_probability,
            human_probability=result.human_probability,
            verdict=result.verdict,
            confidence=result.confidence,
            flagged_sections=flagged_sections,
            recommendations=recommendations
        )
    except Exception as e:
        print(f"Error in AI content analysis: {e}")
        return AIContentAnalysis(
            ai_probability=0,
            human_probability=100,
            verdict="Unable to analyze",
            confidence=0,
            flagged_sections=[],
            recommendations=["AI detection analysis failed"]
        )


async def perform_peer_review(
    text: str,
    perspective: ReviewerPerspective,
    document_info: Dict[str, Any]
) -> PeerReviewerFeedback:
    """Simulate peer review from a specific perspective"""

    perspective_prompts = {
        ReviewerPerspective.METHODOLOGY: """You are a methodology expert reviewer. Focus on:
- Research design and approach
- Sampling and data collection methods
- Analysis techniques
- Validity and reliability
- Reproducibility""",

        ReviewerPerspective.DOMAIN: """You are a domain expert in the paper's field. Focus on:
- Contribution to the field
- Novelty and significance
- Accuracy of domain-specific claims
- Relevance to current research
- Theoretical grounding""",

        ReviewerPerspective.WRITING: """You are a writing and communication expert. Focus on:
- Clarity and readability
- Organization and structure
- Academic tone and style
- Grammar and mechanics
- Figure and table quality""",

        ReviewerPerspective.STATISTICAL: """You are a statistical methods expert. Focus on:
- Appropriateness of statistical tests
- Sample size and power
- Effect sizes and confidence intervals
- Data presentation
- Statistical assumptions""",

        ReviewerPerspective.ETHICS: """You are a research ethics expert. Focus on:
- Ethical considerations
- Informed consent procedures
- Data privacy and protection
- Conflict of interest disclosures
- IRB/ethics approval"""
    }

    system_prompt = perspective_prompts.get(
        perspective,
        "You are an academic peer reviewer."
    )

    prompt = f"""Review this academic document from your expert perspective.

Document type: {document_info.get('document_type', 'research paper')}
Field: {document_info.get('field', 'unknown')}

Document text:
{text[:6000]}

Provide a comprehensive review including:
1. Overall assessment (2-3 sentences)
2. Score (0-100)
3. Key strengths (3-5 items)
4. Key weaknesses (3-5 items)
5. Critical issues that must be addressed
6. Specific recommendations for improvement
7. Detailed comments on specific sections

Respond in JSON format:
{{
    "overall_assessment": "This paper presents interesting findings but has methodological limitations...",
    "score": 72,
    "strengths": ["Clear research questions", "Comprehensive literature review"],
    "weaknesses": ["Limited sample size", "Missing control condition"],
    "critical_issues": [
        {{
            "category": "methodology",
            "severity": "major",
            "description": "Sample size too small for claimed generalizations",
            "suggestion": "Acknowledge limitations or increase sample size"
        }}
    ],
    "recommendations": ["Add power analysis", "Include effect sizes"],
    "detailed_comments": [
        {{
            "section": "methodology",
            "comment": "The sampling method is not clearly described",
            "suggestion": "Provide more detail on participant recruitment"
        }}
    ]
}}"""

    try:
        response = await async_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)

        # Parse critical issues
        critical_issues = []
        for i, issue in enumerate(result.get("critical_issues", [])):
            critical_issues.append(ReviewIssue(
                id=f"{perspective.value}-issue-{i+1}",
                category=issue.get("category", "general"),
                severity=SeverityLevel(issue.get("severity", "major")),
                description=issue.get("description", ""),
                suggestion=issue.get("suggestion", ""),
                confidence=0.85
            ))

        return PeerReviewerFeedback(
            perspective=perspective,
            overall_assessment=result.get("overall_assessment", ""),
            score=result.get("score", 50),
            strengths=result.get("strengths", []),
            weaknesses=result.get("weaknesses", []),
            critical_issues=critical_issues,
            recommendations=result.get("recommendations", []),
            detailed_comments=result.get("detailed_comments", [])
        )
    except Exception as e:
        print(f"Error in peer review ({perspective}): {e}")
        return PeerReviewerFeedback(
            perspective=perspective,
            overall_assessment="Unable to complete review",
            score=0,
            strengths=[],
            weaknesses=[],
            critical_issues=[],
            recommendations=[],
            detailed_comments=[]
        )


async def assess_citation_quality(
    text: str,
    max_suggestions: int = 10
) -> CitationQualityAssessment:
    """Assess citation quality using Citation Booster functionality"""
    try:
        # Extract claims and concepts
        claims, concepts = await asyncio.gather(
            extract_claims_from_text(text),
            extract_concepts_from_text(text)
        )

        # Identify citation gaps
        gaps = await identify_citation_gaps(claims, [])

        # Calculate statistics
        total_claims = len(claims)
        cited_claims = sum(1 for c in claims if c.has_citation)
        missing_citations = total_claims - cited_claims

        # Search for suggested citations based on concepts
        search_tasks = []
        search_queries = [c.term for c in sorted(concepts, key=lambda x: x.importance, reverse=True)[:3]]

        for query in search_queries:
            search_tasks.append(search_pubmed(query, max_results=5))
            search_tasks.append(search_semantic_scholar(query, max_results=5))

        if search_tasks:
            results = await asyncio.gather(*search_tasks)
            all_papers = []
            for paper_list in results:
                all_papers.extend(paper_list)
            suggested_papers = deduplicate_papers(all_papers)[:max_suggestions]
        else:
            suggested_papers = []

        # Calculate scores
        coverage_score = (cited_claims / total_claims * 100) if total_claims > 0 else 100

        # Recency score (based on years mentioned in existing citations - simplified)
        recency_score = 70  # Default moderate score

        # Relevance and diversity scores
        relevance_score = 75  # Would need more sophisticated analysis
        diversity_score = 70  # Would need source analysis

        # Generate recommendations
        recommendations = []
        if missing_citations > 0:
            recommendations.append(f"Add citations for {missing_citations} uncited claims")

        critical_gaps = sum(1 for g in gaps if g.severity == "critical")
        if critical_gaps > 0:
            recommendations.append(f"Address {critical_gaps} critical citation gaps (statistical/factual claims)")

        if coverage_score < 50:
            recommendations.append("Citation coverage is low. Conduct a more thorough literature review.")

        overall_score = (coverage_score * 0.4 + recency_score * 0.2 + relevance_score * 0.2 + diversity_score * 0.2)

        return CitationQualityAssessment(
            overall_score=overall_score,
            total_citations_needed=total_claims,
            citations_present=cited_claims,
            missing_citations=missing_citations,
            citation_gaps=gaps[:10],  # Limit to top 10 gaps
            recency_score=recency_score,
            relevance_score=relevance_score,
            diversity_score=diversity_score,
            suggested_citations=suggested_papers,
            recommendations=recommendations
        )
    except Exception as e:
        print(f"Error assessing citation quality: {e}")
        return CitationQualityAssessment(
            overall_score=0,
            total_citations_needed=0,
            citations_present=0,
            missing_citations=0,
            citation_gaps=[],
            recency_score=0,
            relevance_score=0,
            diversity_score=0,
            suggested_citations=[],
            recommendations=["Citation analysis failed"]
        )


async def find_related_papers(
    text: str,
    concepts: List[Concept],
    max_papers: int = 10
) -> List[Paper]:
    """Find related papers using Literature Search"""
    try:
        # Build search queries from concepts
        search_queries = [c.term for c in sorted(concepts, key=lambda x: x.importance, reverse=True)[:3]]

        if not search_queries:
            # Fallback: extract key phrases from text
            search_queries = [text[:100]]

        # Search across databases
        all_papers = []
        search_tasks = []

        for query in search_queries:
            search_tasks.append(search_pubmed(query, max_results=10))
            search_tasks.append(search_arxiv(query, max_results=10))
            search_tasks.append(search_semantic_scholar(query, max_results=10))

        results = await asyncio.gather(*search_tasks)

        for paper_list in results:
            all_papers.extend(paper_list)

        # Deduplicate and limit
        unique_papers = deduplicate_papers(all_papers)

        return unique_papers[:max_papers]
    except Exception as e:
        print(f"Error finding related papers: {e}")
        return []


def generate_improvement_suggestions(
    strengths: List[StrengthItem],
    weaknesses: List[WeaknessItem],
    methodology_critique: Optional[MethodologyCritique],
    citation_quality: Optional[CitationQualityAssessment],
    writing_quality: WritingQualityMetrics,
    peer_reviews: List[PeerReviewerFeedback]
) -> List[ImprovementSuggestion]:
    """Generate prioritized improvement suggestions"""
    suggestions = []
    priority = 1

    # Critical issues from peer reviews first
    for review in peer_reviews:
        for issue in review.critical_issues:
            if issue.severity == SeverityLevel.CRITICAL:
                suggestions.append(ImprovementSuggestion(
                    id=f"imp-{priority}",
                    priority=priority,
                    category=issue.category,
                    title=f"Critical: {issue.category.title()} Issue",
                    description=issue.description,
                    impact="high",
                    effort="medium",
                    section=issue.section,
                    related_issues=[issue.id]
                ))
                priority += 1

    # Major weaknesses
    for weakness in weaknesses:
        if weakness.severity in [SeverityLevel.CRITICAL, SeverityLevel.MAJOR]:
            suggestions.append(ImprovementSuggestion(
                id=f"imp-{priority}",
                priority=priority,
                category=weakness.category,
                title=f"Address {weakness.category.title()} Weakness",
                description=weakness.description,
                impact="high" if weakness.severity == SeverityLevel.CRITICAL else "medium",
                effort="medium",
                section=weakness.section,
                related_issues=[]
            ))
            priority += 1

    # Methodology improvements
    if methodology_critique and methodology_critique.score < 70:
        for rec in methodology_critique.recommendations[:3]:
            suggestions.append(ImprovementSuggestion(
                id=f"imp-{priority}",
                priority=priority,
                category="methodology",
                title="Methodology Improvement",
                description=rec,
                impact="high",
                effort="high",
                section=DocumentSection.METHODOLOGY,
                related_issues=[]
            ))
            priority += 1

    # Citation improvements
    if citation_quality and citation_quality.missing_citations > 0:
        suggestions.append(ImprovementSuggestion(
            id=f"imp-{priority}",
            priority=priority,
            category="citations",
            title="Add Missing Citations",
            description=f"Add citations for {citation_quality.missing_citations} uncited claims",
            impact="medium",
            effort="medium",
            section=None,
            related_issues=[]
        ))
        priority += 1

    # Writing improvements
    if writing_quality.overall_score < 70:
        for issue in writing_quality.issues[:3]:
            suggestions.append(ImprovementSuggestion(
                id=f"imp-{priority}",
                priority=priority,
                category="writing",
                title=f"Writing: {issue.category.title()}",
                description=issue.description,
                impact="medium",
                effort="low",
                section=issue.section,
                related_issues=[issue.id]
            ))
            priority += 1

    # Sort by priority (already in order) and limit
    return suggestions[:15]


def calculate_overall_score(
    writing_quality: WritingQualityMetrics,
    methodology_critique: Optional[MethodologyCritique],
    citation_quality: Optional[CitationQualityAssessment],
    ai_content: Optional[AIContentAnalysis],
    peer_reviews: List[PeerReviewerFeedback]
) -> tuple:
    """Calculate overall quality score and grade"""
    scores = []
    weights = []

    # Writing quality (weight: 0.25)
    scores.append(writing_quality.overall_score)
    weights.append(0.25)

    # Methodology (weight: 0.30)
    if methodology_critique:
        scores.append(methodology_critique.score)
        weights.append(0.30)

    # Citation quality (weight: 0.15)
    if citation_quality:
        scores.append(citation_quality.overall_score)
        weights.append(0.15)

    # Peer review average (weight: 0.30)
    if peer_reviews:
        avg_peer_score = sum(r.score for r in peer_reviews) / len(peer_reviews)
        scores.append(avg_peer_score)
        weights.append(0.30)

    # Normalize weights
    total_weight = sum(weights)
    weights = [w / total_weight for w in weights]

    # Calculate weighted average
    overall_score = sum(s * w for s, w in zip(scores, weights))

    # AI penalty (if high AI content, reduce score)
    if ai_content and ai_content.ai_probability > 70:
        overall_score *= 0.85  # 15% penalty for high AI content
    elif ai_content and ai_content.ai_probability > 50:
        overall_score *= 0.95  # 5% penalty for moderate AI content

    # Determine grade
    if overall_score >= 90:
        grade = "A (Accept)"
    elif overall_score >= 80:
        grade = "B (Accept with Minor Revisions)"
    elif overall_score >= 70:
        grade = "C (Major Revisions Required)"
    elif overall_score >= 60:
        grade = "D (Revise and Resubmit)"
    else:
        grade = "F (Reject)"

    return round(overall_score, 1), grade


def generate_executive_summary(
    document_info: Dict[str, Any],
    overall_score: float,
    grade: str,
    strengths: List[StrengthItem],
    weaknesses: List[WeaknessItem],
    top_suggestions: List[ImprovementSuggestion]
) -> str:
    """Generate an executive summary of the review"""
    summary_parts = []

    # Opening
    summary_parts.append(f"## Executive Summary\n")
    summary_parts.append(f"**Document Type:** {document_info.get('document_type', 'Research Paper')}")
    summary_parts.append(f"**Field:** {document_info.get('field', 'Not specified')}")
    summary_parts.append(f"**Overall Score:** {overall_score}/100")
    summary_parts.append(f"**Grade/Verdict:** {grade}\n")

    # Key strengths
    summary_parts.append("### Key Strengths")
    for i, strength in enumerate(strengths[:3], 1):
        summary_parts.append(f"{i}. {strength.description}")

    # Key areas for improvement
    summary_parts.append("\n### Key Areas for Improvement")
    for i, weakness in enumerate(weaknesses[:3], 1):
        summary_parts.append(f"{i}. {weakness.description}")

    # Top priority actions
    summary_parts.append("\n### Priority Actions")
    for i, suggestion in enumerate(top_suggestions[:3], 1):
        summary_parts.append(f"{i}. **{suggestion.title}**: {suggestion.description}")

    return "\n".join(summary_parts)


def export_review_to_markdown(review: DeepReviewResponse) -> str:
    """Export review to markdown format"""
    md_parts = []

    # Header
    md_parts.append(f"# Deep Review Report")
    md_parts.append(f"**Review ID:** {review.review_id}")
    md_parts.append(f"**Generated:** {review.created_at}\n")

    # Executive Summary
    md_parts.append(review.executive_summary)
    md_parts.append("")

    # Overall Assessment
    md_parts.append("---\n## Overall Assessment")
    md_parts.append(f"**Quality Score:** {review.overall_quality_score}/100")
    md_parts.append(f"**Grade:** {review.grade}")
    md_parts.append(f"**Verdict:** {review.verdict}\n")

    # Strengths
    md_parts.append("## Strengths")
    for strength in review.strengths:
        md_parts.append(f"- **{strength.category.title()}**: {strength.description} (Impact: {strength.impact})")
    md_parts.append("")

    # Weaknesses
    md_parts.append("## Weaknesses")
    for weakness in review.weaknesses:
        md_parts.append(f"- **{weakness.category.title()}** ({weakness.severity.value}): {weakness.description}")
        md_parts.append(f"  - *Suggestion*: {weakness.suggestion}")
    md_parts.append("")

    # Methodology Critique
    if review.methodology_critique:
        md_parts.append("## Methodology Critique")
        md_parts.append(f"**Score:** {review.methodology_critique.score}/100")
        md_parts.append(f"\n{review.methodology_critique.overall_assessment}\n")

        if review.methodology_critique.validity_concerns:
            md_parts.append("### Validity Concerns")
            for concern in review.methodology_critique.validity_concerns:
                md_parts.append(f"- {concern}")

        if review.methodology_critique.recommendations:
            md_parts.append("\n### Recommendations")
            for rec in review.methodology_critique.recommendations:
                md_parts.append(f"- {rec}")
        md_parts.append("")

    # Writing Quality
    md_parts.append("## Writing Quality")
    wq = review.writing_quality
    md_parts.append(f"**Overall Score:** {wq.overall_score}/100")
    md_parts.append(f"- Clarity: {wq.clarity_score}/100")
    md_parts.append(f"- Coherence: {wq.coherence_score}/100")
    md_parts.append(f"- Grammar: {wq.grammar_score}/100")
    md_parts.append(f"- Academic Tone: {wq.academic_tone_score}/100")
    md_parts.append(f"- Readability: {wq.readability_score}/100")
    md_parts.append("")

    # Citation Quality
    if review.citation_quality:
        cq = review.citation_quality
        md_parts.append("## Citation Quality")
        md_parts.append(f"**Overall Score:** {cq.overall_score}/100")
        md_parts.append(f"- Citations Needed: {cq.total_citations_needed}")
        md_parts.append(f"- Citations Present: {cq.citations_present}")
        md_parts.append(f"- Missing: {cq.missing_citations}")
        if cq.recommendations:
            md_parts.append("\n### Recommendations")
            for rec in cq.recommendations:
                md_parts.append(f"- {rec}")
        md_parts.append("")

    # AI Content Analysis
    if review.ai_content_analysis:
        ai = review.ai_content_analysis
        md_parts.append("## AI Content Analysis")
        md_parts.append(f"**AI Probability:** {ai.ai_probability}%")
        md_parts.append(f"**Verdict:** {ai.verdict}")
        if ai.recommendations:
            for rec in ai.recommendations:
                md_parts.append(f"- {rec}")
        md_parts.append("")

    # Peer Reviews
    md_parts.append("## Peer Review Feedback")
    for pr in review.peer_reviews:
        md_parts.append(f"\n### {pr.perspective.value.title()} Expert")
        md_parts.append(f"**Score:** {pr.score}/100")
        md_parts.append(f"\n{pr.overall_assessment}")

        if pr.strengths:
            md_parts.append("\n**Strengths:**")
            for s in pr.strengths[:3]:
                md_parts.append(f"- {s}")

        if pr.weaknesses:
            md_parts.append("\n**Weaknesses:**")
            for w in pr.weaknesses[:3]:
                md_parts.append(f"- {w}")
    md_parts.append("")

    # Improvement Suggestions
    md_parts.append("## Improvement Suggestions (Prioritized)")
    for i, sugg in enumerate(review.improvement_suggestions, 1):
        md_parts.append(f"\n### {i}. {sugg.title}")
        md_parts.append(f"**Priority:** {sugg.priority} | **Impact:** {sugg.impact} | **Effort:** {sugg.effort}")
        md_parts.append(f"\n{sugg.description}")
    md_parts.append("")

    # Related Papers
    if review.related_papers:
        md_parts.append("## Suggested Related Papers")
        for paper in review.related_papers[:5]:
            authors = ", ".join(paper.authors[:3])
            if len(paper.authors) > 3:
                authors += " et al."
            md_parts.append(f"- {authors} ({paper.year}). *{paper.title}*. {paper.journal or 'N/A'}")

    return "\n".join(md_parts)


def export_review_to_html(review: DeepReviewResponse) -> str:
    """Export review to HTML format"""
    markdown_content = export_review_to_markdown(review)

    # Simple markdown to HTML conversion
    html = markdown_content
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.*</li>\n)+', r'<ul>\g<0></ul>', html)
    html = html.replace('\n\n', '</p><p>')
    html = f'<html><head><title>Deep Review Report</title><style>body{{font-family:Arial,sans-serif;max-width:800px;margin:auto;padding:20px}}h1,h2,h3{{color:#333}}ul{{margin:10px 0}}</style></head><body><p>{html}</p></body></html>'

    return html


# =============================================================================
# API ENDPOINTS
# =============================================================================

@router.post("/analyze", response_model=DeepReviewResponse)
async def perform_deep_review(request: DeepReviewRequest):
    """
    Perform comprehensive deep review of an academic document.

    This endpoint integrates multiple analysis features:
    - Document structure analysis
    - Multi-perspective peer review simulation
    - Strength/weakness identification
    - Methodology critique
    - Citation quality assessment
    - AI content detection
    - Writing quality metrics
    - Related paper discovery
    - Prioritized improvement suggestions

    Returns a complete review with overall quality score and recommendations.
    """
    try:
        # Generate review ID
        review_id = f"dr-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Step 1: Analyze document structure
        document_info = await analyze_document_structure(request.text)
        if request.field:
            document_info["field"] = request.field

        # Step 2: Extract concepts for various analyses
        concepts = await extract_concepts_from_text(request.text)

        # Step 3: Run parallel analyses
        analysis_tasks = []

        # Strengths and weaknesses
        analysis_tasks.append(identify_strengths_and_weaknesses(request.text, document_info))

        # Methodology critique
        analysis_tasks.append(critique_methodology(request.text, document_info))

        # Writing quality
        analysis_tasks.append(assess_writing_quality(request.text))

        # Citation quality (if requested)
        if request.include_citation_analysis:
            analysis_tasks.append(assess_citation_quality(request.text, request.max_related_papers))

        # AI content analysis (if requested)
        if request.include_ai_detection:
            analysis_tasks.append(perform_ai_content_analysis(request.text))

        # Related papers (if requested)
        if request.include_literature_search:
            analysis_tasks.append(find_related_papers(request.text, concepts, request.max_related_papers))

        # Run all analyses
        results = await asyncio.gather(*analysis_tasks)

        # Unpack results
        idx = 0
        strengths, weaknesses = results[idx]
        idx += 1

        methodology_critique = results[idx]
        idx += 1

        writing_quality = results[idx]
        idx += 1

        citation_quality = None
        if request.include_citation_analysis:
            citation_quality = results[idx]
            idx += 1

        ai_content_analysis = None
        if request.include_ai_detection:
            ai_content_analysis = results[idx]
            idx += 1

        related_papers = []
        if request.include_literature_search:
            related_papers = results[idx]
            idx += 1

        # Step 4: Perform peer reviews from multiple perspectives
        peer_review_tasks = [
            perform_peer_review(request.text, perspective, document_info)
            for perspective in request.reviewer_perspectives
        ]
        peer_reviews = await asyncio.gather(*peer_review_tasks)

        # Step 5: Generate improvement suggestions
        improvement_suggestions = generate_improvement_suggestions(
            strengths,
            weaknesses,
            methodology_critique,
            citation_quality,
            writing_quality,
            peer_reviews
        )

        # Step 6: Calculate overall score and grade
        overall_score, grade = calculate_overall_score(
            writing_quality,
            methodology_critique,
            citation_quality,
            ai_content_analysis,
            peer_reviews
        )

        # Step 7: Generate executive summary
        executive_summary = generate_executive_summary(
            document_info,
            overall_score,
            grade,
            strengths,
            weaknesses,
            improvement_suggestions
        )

        # Step 8: Determine verdict
        if overall_score >= 80:
            verdict = "This document demonstrates strong academic quality and is suitable for publication with minor revisions."
        elif overall_score >= 70:
            verdict = "This document has merit but requires significant revisions to meet publication standards."
        elif overall_score >= 60:
            verdict = "This document needs substantial revision addressing methodology, writing, and citation gaps."
        else:
            verdict = "This document requires major rework before it can be considered for publication."

        # Step 9: Save to database
        try:
            review_data = {
                "review_id": review_id,
                "document_summary": document_info,
                "overall_score": overall_score,
                "grade": grade,
                "verdict": verdict
            }
            supabase.table("deep_reviews").insert(review_data).execute()
        except Exception as e:
            print(f"Error saving review to database: {e}")

        return DeepReviewResponse(
            review_id=review_id,
            document_summary=document_info,
            overall_quality_score=overall_score,
            grade=grade,
            strengths=strengths,
            weaknesses=weaknesses,
            methodology_critique=methodology_critique,
            citation_quality=citation_quality,
            writing_quality=writing_quality,
            ai_content_analysis=ai_content_analysis,
            peer_reviews=peer_reviews,
            related_papers=related_papers,
            improvement_suggestions=improvement_suggestions,
            executive_summary=executive_summary,
            verdict=verdict,
            created_at=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deep review failed: {str(e)}")


@router.post("/analyze-file")
async def analyze_uploaded_file(
    file: UploadFile = File(...),
    document_type: str = Form("research_paper"),
    field: Optional[str] = Form(None),
    include_ai_detection: bool = Form(True),
    include_literature_search: bool = Form(True),
    include_citation_analysis: bool = Form(True)
):
    """
    Perform deep review on an uploaded document file.

    Supports .txt and .md files.
    """
    if not file.filename.endswith(('.txt', '.md')):
        raise HTTPException(
            status_code=400,
            detail="Only .txt and .md files are supported"
        )

    try:
        content = await file.read()
        text = content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            text = content.decode('latin-1')
        except Exception:
            raise HTTPException(status_code=400, detail="Failed to decode file content")

    if len(text) < 100:
        raise HTTPException(
            status_code=400,
            detail="Document must be at least 100 characters for meaningful analysis"
        )

    # Create request and perform analysis
    request = DeepReviewRequest(
        text=text,
        document_type=document_type,
        field=field,
        include_ai_detection=include_ai_detection,
        include_literature_search=include_literature_search,
        include_citation_analysis=include_citation_analysis
    )

    return await perform_deep_review(request)


@router.get("/review/{review_id}")
async def get_review(review_id: str):
    """
    Retrieve a previously generated review by ID.
    """
    try:
        response = supabase.table("deep_reviews").select("*").eq("review_id", review_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Review not found")

        return {"success": True, "review": response.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve review: {str(e)}")


@router.post("/export", response_model=ExportReviewResponse)
async def export_review(request: ExportReviewRequest):
    """
    Export a review in various formats (markdown, html, json).
    """
    try:
        # Retrieve review from database
        response = supabase.table("deep_reviews").select("*").eq("review_id", request.review_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Review not found")

        review_data = response.data[0]

        # For now, return the stored data in requested format
        if request.format == "json":
            import json
            content = json.dumps(review_data, indent=2, default=str)
            filename = f"review_{request.review_id}.json"
        elif request.format == "markdown":
            # Generate markdown from stored data
            content = f"# Deep Review Report\n\n**Review ID:** {review_data.get('review_id')}\n"
            content += f"**Overall Score:** {review_data.get('overall_score')}/100\n"
            content += f"**Grade:** {review_data.get('grade')}\n"
            content += f"**Verdict:** {review_data.get('verdict')}\n"
            filename = f"review_{request.review_id}.md"
        elif request.format == "html":
            content = f"<html><body><h1>Deep Review Report</h1>"
            content += f"<p><strong>Review ID:</strong> {review_data.get('review_id')}</p>"
            content += f"<p><strong>Overall Score:</strong> {review_data.get('overall_score')}/100</p>"
            content += f"<p><strong>Grade:</strong> {review_data.get('grade')}</p>"
            content += f"<p><strong>Verdict:</strong> {review_data.get('verdict')}</p>"
            content += "</body></html>"
            filename = f"review_{request.review_id}.html"
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")

        return ExportReviewResponse(
            format=request.format,
            content=content,
            filename=filename
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.post("/quick-review")
async def quick_review(
    text: str = Form(..., min_length=100),
    focus: str = Form("overall", description="Focus area: overall, methodology, writing, citations")
):
    """
    Perform a quick, focused review on a specific aspect.

    Faster than full deep review, suitable for quick feedback.
    """
    try:
        results = {}

        if focus in ["overall", "writing"]:
            results["writing_quality"] = await assess_writing_quality(text)

        if focus in ["overall", "methodology"]:
            doc_info = await analyze_document_structure(text)
            results["methodology_critique"] = await critique_methodology(text, doc_info)

        if focus in ["overall", "citations"]:
            results["citation_quality"] = await assess_citation_quality(text, max_suggestions=5)

        # Calculate quick score
        scores = []
        if "writing_quality" in results:
            scores.append(results["writing_quality"].overall_score)
        if "methodology_critique" in results:
            scores.append(results["methodology_critique"].score)
        if "citation_quality" in results:
            scores.append(results["citation_quality"].overall_score)

        overall_score = sum(scores) / len(scores) if scores else 0

        return {
            "success": True,
            "focus": focus,
            "overall_score": round(overall_score, 1),
            "results": {k: v.model_dump() if hasattr(v, 'model_dump') else v for k, v in results.items()}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick review failed: {str(e)}")


@router.get("/history")
async def get_review_history(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """
    Get history of deep reviews.
    """
    try:
        query = supabase.table("deep_reviews").select("*", count="exact")
        query = query.order("created_at", desc=True)
        query = query.range(offset, offset + limit - 1)

        response = query.execute()

        return {
            "success": True,
            "reviews": response.data or [],
            "total_count": response.count or len(response.data or []),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


@router.delete("/review/{review_id}")
async def delete_review(review_id: str):
    """
    Delete a review record.
    """
    try:
        response = supabase.table("deep_reviews").delete().eq("review_id", review_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Review not found")

        return {"success": True, "message": "Review deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete review: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint for deep review service.
    """
    return {
        "status": "healthy",
        "service": "deep-review",
        "version": "1.0.0",
        "features": [
            "document_analysis",
            "peer_review_simulation",
            "methodology_critique",
            "citation_quality_assessment",
            "ai_content_detection",
            "writing_quality_metrics",
            "improvement_suggestions",
            "related_paper_discovery",
            "review_export"
        ],
        "integrated_services": [
            "literature_search",
            "citation_booster",
            "ai_detector",
            "citation_generator"
        ]
    }
