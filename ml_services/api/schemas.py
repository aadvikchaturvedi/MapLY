"""
API Request/Response Schemas
=============================

Pydantic models for request validation and response serialization.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


# ============================================
# Sentiment Analysis Schemas
# ============================================

class SentimentRequest(BaseModel):
    """Request model for sentiment analysis."""
    text: str = Field(..., min_length=1, max_length=1000, description="Text to analyze")
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v.strip()


class SentimentResponse(BaseModel):
    """Response model for sentiment analysis."""
    label: str = Field(..., description="Sentiment label (POSITIVE/NEGATIVE)")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    normalized_score: float = Field(..., ge=-1, le=1, description="Normalized sentiment score")
    probabilities: Dict[str, float] = Field(..., description="Class probabilities")


class BatchSentimentRequest(BaseModel):
    """Request model for batch sentiment analysis."""
    texts: List[str] = Field(..., min_length=1, max_length=100, description="List of texts to analyze")
    
    @field_validator('texts')
    @classmethod
    def validate_texts(cls, v):
        if not v:
            raise ValueError("Texts list cannot be empty")
        for text in v:
            if not text.strip():
                raise ValueError("Text cannot be empty or whitespace only")
        return [text.strip() for text in v]


class BatchSentimentResponse(BaseModel):
    """Response model for batch sentiment analysis."""
    results: List[SentimentResponse] = Field(..., description="List of sentiment analysis results")
    total_processed: int = Field(..., description="Total number of texts processed")


# ============================================
# Risk Score Schemas
# ============================================

class RiskScoreResponse(BaseModel):
    """Response model for individual risk score."""
    state: str = Field(..., description="State name")
    district: str = Field(..., description="District name")
    safety_score: float = Field(..., ge=0, le=100, description="Safety score (0-100)")
    risk_category: str = Field(..., description="Risk category (Low/Moderate/High Risk)")


class AllRiskScoresResponse(BaseModel):
    """Response model for all risk scores."""
    total: int = Field(..., description="Total number of regions")
    data: List[RiskScoreResponse] = Field(..., description="List of risk scores")


class LocationRiskRequest(BaseModel):
    """Request model for location-specific risk."""
    state: str = Field(..., min_length=1, description="State name")
    district: str = Field(..., min_length=1, description="District name")


# ============================================
# Health & Metrics Schemas
# ============================================

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    models: Dict[str, str] = Field(..., description="Model status")


class MetricsResponse(BaseModel):
    """Response model for metrics."""
    requests: Dict[str, int] = Field(..., description="Request counts by endpoint")
    errors: Dict[str, int] = Field(..., description="Error counts by endpoint")
    avg_response_times: Dict[str, float] = Field(..., description="Average response times")
    avg_inference_times: Dict[str, float] = Field(..., description="Average inference times")


# ============================================
# Error Schemas
# ============================================

class ErrorResponse(BaseModel):
    """Response model for errors."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
