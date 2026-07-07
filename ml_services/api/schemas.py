"""
API Request/Response Schemas
=============================

Pydantic models for request validation and response serialization.
"""

from typing import Dict, List, Optional, Tuple
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
# Spatial / Coordinate-based Risk Schemas
# ============================================

class CoordinateRiskRequest(BaseModel):
    """Request model for coordinate-based risk lookup.

    Latitudes must be in [-90, 90] and longitudes in [-180, 180].
    """

    lat: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    lng: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees")


class CoordinateRiskResponse(BaseModel):
    """Response model for a coordinate-based risk lookup.

    ``risk_score`` is normalized to ``[0, 1]`` where higher means riskier and is
    derived from the backend ``safety_score`` as ``risk_score = 1 - safety_score/100``.
    """

    state: str = Field(..., description="State name (nearest centroid)")
    district: str = Field(..., description="District name (nearest centroid)")
    safety_score: float = Field(..., ge=0, le=100, description="Safety score (0-100, higher = safer)")
    risk_category: str = Field(..., description="Risk category (Low/Moderate/High Risk)")
    risk_score: float = Field(..., ge=0, le=1, description="Risk score (0-1, higher = riskier)")


class RouteRiskRequest(BaseModel):
    """Request model for route-based risk scoring.

    ``coordinates`` is an ordered list of ``[lat, lng]`` pairs representing
    points along a route. The response will contain a risk assessment for
    each input coordinate in the same order.
    """

    coordinates: List[List[float]] = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="List of [lat, lng] coordinates along the route",
    )

    @field_validator("coordinates")
    @classmethod
    def validate_coordinates(cls, v: List[List[float]]) -> List[List[float]]:
        if not v:
            raise ValueError("coordinates list cannot be empty")
        cleaned: List[List[float]] = []
        for idx, coord in enumerate(v):
            if not isinstance(coord, (list, tuple)) or len(coord) != 2:
                raise ValueError(
                    f"coordinates[{idx}] must be a [lat, lng] pair of length 2"
                )
            try:
                lat = float(coord[0])
                lng = float(coord[1])
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"coordinates[{idx}] must contain numeric lat/lng values"
                ) from exc
            if not (-90.0 <= lat <= 90.0):
                raise ValueError(
                    f"coordinates[{idx}] latitude {lat} out of range [-90, 90]"
                )
            if not (-180.0 <= lng <= 180.0):
                raise ValueError(
                    f"coordinates[{idx}] longitude {lng} out of range [-180, 180]"
                )
            cleaned.append([lat, lng])
        return cleaned


class RouteSegment(BaseModel):
    """A single segment of a route with its risk classification."""

    lat: float = Field(..., description="Latitude of the segment")
    lng: float = Field(..., description="Longitude of the segment")
    risk_score: float = Field(..., ge=0, le=1, description="Risk score (0-1, higher = riskier)")
    risk_category: str = Field(..., description="Risk category (Low/Moderate/High Risk)")


class RouteRiskResponse(BaseModel):
    """Response model for route-based risk scoring."""

    segments: List[RouteSegment] = Field(
        ..., description="Per-coordinate risk segments matching input order"
    )
    total: int = Field(..., description="Total number of segments returned")


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
