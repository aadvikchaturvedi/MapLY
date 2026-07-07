"""
MapLY ML Services API
=====================

Production-ready FastAPI application for sentiment analysis and risk scoring.
"""

import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Add ml_services to sys.path
current_dir = Path(__file__).resolve().parent
ml_services_dir = current_dir.parent
sys.path.append(str(ml_services_dir))

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import local modules
from config import settings
from utils.logger import setup_logging, get_logger
from utils.metrics import metrics, track_time
from Sentiment_Analysis.model import MapLYSentimentAnalyzer
from Risk_Score_Engine.model import RiskScoreAPI as RiskEngine

# Import API components
# Import API components
from .schemas import (
    SentimentRequest,
    SentimentResponse,
    BatchSentimentRequest,
    BatchSentimentResponse,
    RiskScoreResponse,
    AllRiskScoresResponse,
    CoordinateRiskRequest,
    CoordinateRiskResponse,
    RouteRiskRequest,
    RouteRiskResponse,
    RouteSegment,
    HealthResponse,
    MetricsResponse,
    ErrorResponse,
)
from .middleware import LoggingMiddleware, ErrorHandlingMiddleware
from chatbot.api import router as chatbot_router, initialize_chatbot

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Production-ready API for sentiment analysis, risk scoring, and safety chatbot",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)

# Include Chatbot Router
app.include_router(chatbot_router)

# Global model instances
sentiment_analyzer = None
risk_engine = None
risk_data_cache = None


@app.on_event("startup")
async def startup_event():
    """Initialize models and resources on startup."""
    global sentiment_analyzer, risk_engine, risk_data_cache
    
    logger.info("Starting MapLY ML Services...")
    
    # Initialize Chatbot
    logger.info("Initializing Safety Chatbot...")
    initialize_chatbot()
    
    # Load Sentiment Analyzer
    try:
        logger.info("Loading Sentiment Analyzer...")
        sentiment_analyzer = MapLYSentimentAnalyzer()
        logger.info("✓ Sentiment Analyzer loaded successfully")
    except Exception as e:
        logger.error(f"✗ Failed to load Sentiment Analyzer: {e}", exc_info=True)
    
    # Load Risk Engine
    try:
        logger.info("Loading Risk Score Engine...")
        risk_engine = RiskEngine()
        
        # Pre-load data
        data_dir = settings.DATA_DIR
        csv_files = [str(p) for p in data_dir.glob("*.csv")]
        
        if csv_files:
            logger.info(f"Found {len(csv_files)} CSV files, processing...")
            result = risk_engine.get_navigation_data(csv_files)
            
            if result.get("status") == "success":
                risk_data_cache = result.get("data", [])
                logger.info(f"✓ Risk Engine loaded with {len(risk_data_cache)} regions")
            else:
                logger.warning(f"Risk Engine processing failed: {result.get('message')}")
        else:
            logger.warning(f"No CSV data found in {data_dir}")
    except Exception as e:
        logger.error(f"✗ Failed to load Risk Engine: {e}", exc_info=True)
    
    logger.info("MapLY ML Services startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down MapLY ML Services...")


# ============================================
# Health & Metrics Endpoints
# ============================================

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint.
    
    Returns the status of the API and all loaded models.
    """
    from chatbot.api import chatbot_health
    chatbot_status = await chatbot_health()
    
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "models": {
            "sentiment_analyzer": "loaded" if sentiment_analyzer else "not loaded",
            "risk_engine": "loaded" if risk_engine else "not loaded",
            "risk_data": f"{len(risk_data_cache)} regions" if risk_data_cache else "not loaded",
            "chatbot": chatbot_status["status"]
        }
    }


@app.get("/metrics", response_model=MetricsResponse, tags=["System"])
async def get_metrics():
    """
    Get performance metrics.
    
    Returns request counts, error rates, and response times.
    """
    return metrics.get_stats()


# ============================================
# Frontend Interface
# ============================================

@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
async def root():
    """Serve the sentiment analysis testing interface."""
    html_path = current_dir / "templates" / "index.html"
    if html_path.exists():
        return html_path.read_text()
    return JSONResponse(
        content={"message": "MapLY ML API is running", "docs": "/docs"}
    )


# ============================================
# Sentiment Analysis Endpoints
# ============================================

@app.post(
    "/api/v1/sentiment/predict",
    response_model=SentimentResponse,
    tags=["Sentiment Analysis"],
    summary="Analyze sentiment of a single text"
)
async def predict_sentiment(request: SentimentRequest):
    """
    Analyze the sentiment of a single text.
    
    - **text**: The text to analyze (1-1000 characters)
    
    Returns sentiment label, confidence, normalized score, and probabilities.
    """
    if not sentiment_analyzer:
        raise HTTPException(
            status_code=503,
            detail="Sentiment model not initialized. Please check server logs."
        )
    
    try:
        with track_time("sentiment_analysis"):
            result = sentiment_analyzer.predict(request.text)
        
        logger.debug(f"Sentiment prediction: {result['label']} ({result['confidence']:.2f})")
        return result
        
    except Exception as e:
        logger.error(f"Sentiment prediction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post(
    "/api/v1/sentiment/batch",
    response_model=BatchSentimentResponse,
    tags=["Sentiment Analysis"],
    summary="Analyze sentiment of multiple texts"
)
async def predict_sentiment_batch(request: BatchSentimentRequest):
    """
    Analyze the sentiment of multiple texts in a single request.
    
    - **texts**: List of texts to analyze (1-100 texts)
    
    Returns a list of sentiment analysis results.
    """
    if not sentiment_analyzer:
        raise HTTPException(
            status_code=503,
            detail="Sentiment model not initialized. Please check server logs."
        )
    
    try:
        results = []
        
        with track_time("batch_sentiment_analysis"):
            for text in request.texts:
                result = sentiment_analyzer.predict(text)
                results.append(result)
        
        logger.info(f"Batch prediction completed: {len(results)} texts processed")
        
        return {
            "results": results,
            "total_processed": len(results)
        }
        
    except Exception as e:
        logger.error(f"Batch sentiment prediction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


# ============================================
# Risk Score Endpoints
# ============================================

@app.get(
    "/api/v1/risk/scores",
    response_model=AllRiskScoresResponse,
    tags=["Risk Scores"],
    summary="Get all risk scores"
)
async def get_all_risk_scores(
    state: Optional[str] = Query(None, description="Filter by state name")
):
    """
    Get risk scores for all regions or filter by state.
    
    - **state** (optional): Filter results by state name
    
    Returns a list of all risk scores with safety scores and risk categories.
    """
    if risk_data_cache is None:
        raise HTTPException(
            status_code=503,
            detail="Risk data not available. Please check server logs."
        )
    
    try:
        data = risk_data_cache
        
        if state:
            data = [d for d in data if d["state"].lower() == state.lower()]
            logger.debug(f"Filtered risk scores for state: {state}, found {len(data)} regions")
        
        return {"total": len(data), "data": data}
        
    except Exception as e:
        logger.error(f"Failed to retrieve risk scores: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve risk scores: {str(e)}")


@app.get(
    "/api/v1/risk/location",
    response_model=RiskScoreResponse,
    tags=["Risk Scores"],
    summary="Get risk score for specific location"
)
async def get_location_risk(
    state: str = Query(..., description="State name"),
    district: str = Query(..., description="District name")
):
    """
    Get the risk score for a specific location.
    
    - **state**: State name (required)
    - **district**: District name (required)
    
    Returns the safety score and risk category for the specified location.
    """
    if risk_data_cache is None:
        raise HTTPException(
            status_code=503,
            detail="Risk data not available. Please check server logs."
        )
    
    try:
        # Case-insensitive search
        match = next(
            (d for d in risk_data_cache 
             if d["state"].lower() == state.lower() and d["district"].lower() == district.lower()),
            None
        )
        
        if match:
            logger.debug(f"Found risk score for {district}, {state}")
            return match
        else:
            logger.warning(f"Location not found: {district}, {state}")
            raise HTTPException(
                status_code=404,
                detail=f"Location not found: {district}, {state}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve location risk: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve location risk: {str(e)}")


@app.get(
    "/api/v1/risk/states",
    tags=["Risk Scores"],
    summary="Get list of available states"
)
async def get_available_states():
    """
    Get a list of all available states in the dataset.
    
    Returns a list of unique state names.
    """
    if risk_data_cache is None:
        raise HTTPException(
            status_code=503,
            detail="Risk data not available. Please check server logs."
        )
    
    try:
        states = sorted(list(set(d["state"] for d in risk_data_cache)))
        return {"total": len(states), "states": states}
        
    except Exception as e:
        logger.error(f"Failed to retrieve states: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve states: {str(e)}")


@app.get(
    "/api/v1/risk/districts",
    tags=["Risk Scores"],
    summary="Get list of districts for a state"
)
async def get_districts_by_state(
    state: str = Query(..., description="State name")
):
    """
    Get a list of all districts for a specific state.
    
    - **state**: State name (required)
    
    Returns a list of district names for the specified state.
    """
    if risk_data_cache is None:
        raise HTTPException(
            status_code=503,
            detail="Risk data not available. Please check server logs."
        )
    
    try:
        districts = sorted(list(set(
            d["district"] for d in risk_data_cache 
            if d["state"].lower() == state.lower()
        )))
        
        if not districts:
            raise HTTPException(
                status_code=404,
                detail=f"No districts found for state: {state}"
            )
        
        return {"state": state, "total": len(districts), "districts": districts}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve districts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve districts: {str(e)}")


# ============================================
# Coordinate / Route Risk Endpoints
# ============================================

# Mock JWT token accepted by the WebSocket SOS endpoint.
# Used in lieu of a real JWT validation in this development milestone.
MOCK_SOS_TOKEN = "mock-jwt-token"


def _risk_engine_ready() -> bool:
    """Return True if the risk engine is loaded with risk data."""
    return risk_engine is not None and bool(getattr(risk_engine, "_risk_lookup", {}))


@app.get(
    "/api/v1/risk/coordinate",
    response_model=CoordinateRiskResponse,
    tags=["Risk Scores"],
    summary="Get risk score for a single coordinate",
)
async def get_coordinate_risk(
    lat: float = Query(..., ge=-90, le=90, description="Latitude in decimal degrees"),
    lng: float = Query(..., ge=-180, le=180, description="Longitude in decimal degrees"),
):
    """Look up the nearest district's safety score for a (lat, lng) coordinate.

    Returns the district, state, safety score, risk category, and a normalized
    risk score (``risk_score = 1 - safety_score / 100``) for the nearest known
    district centroid.
    """
    if not _risk_engine_ready():
        raise HTTPException(
            status_code=503,
            detail="Risk engine not ready. Please check server logs.",
        )

    try:
        result = risk_engine.get_risk_for_coordinate(lat, lng)
        logger.debug(
            "Coordinate risk lookup: (%.6f, %.6f) -> %s, %s (score=%.2f)",
            lat,
            lng,
            result.get("district"),
            result.get("state"),
            result.get("safety_score", 0.0),
        )
        return result
    except Exception as e:
        logger.error("Coordinate risk lookup failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Coordinate risk lookup failed: {str(e)}"
        )


@app.post(
    "/api/v1/risk/route",
    response_model=RouteRiskResponse,
    tags=["Risk Scores"],
    summary="Get per-coordinate risk scores for a route",
)
async def get_route_risk(request: RouteRiskRequest):
    """Score every coordinate on a route against the nearest known district.

    - **coordinates**: ordered list of ``[lat, lng]`` pairs along the route.

    Returns ``segments`` in the same order as the input, each containing the
    input coordinate, a normalized risk score, and a risk category.
    """
    if not _risk_engine_ready():
        raise HTTPException(
            status_code=503,
            detail="Risk engine not ready. Please check server logs.",
        )

    try:
        segments: list[RouteSegment] = []
        for lat, lng in request.coordinates:
            record = risk_engine.get_risk_for_coordinate(lat, lng)
            segments.append(
                RouteSegment(
                    lat=float(lat),
                    lng=float(lng),
                    risk_score=float(record.get("risk_score", 1.0)),
                    risk_category=str(record.get("risk_category", "Unknown")),
                )
            )

        logger.info(
            "Route risk computed for %d coordinates", len(segments)
        )
        return RouteRiskResponse(segments=segments, total=len(segments))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Route risk computation failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Route risk computation failed: {str(e)}"
        )


# ============================================
# WebSocket SOS endpoint
# ============================================

# ------------------------------------------------------------------
# Geospatial helpers
# ------------------------------------------------------------------


def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance in metres between two (lat, lng) points."""
    R = 6_371_008.8
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ============================================
# SOS HTTP Fallback Endpoint
# ============================================

# In-memory store for SOS events (ephemeral — logs to logger).
_SOS_EVENTS: list[dict] = []


@app.post("/api/v1/sos", tags=["SOS"])
async def receive_sos_http(payload: dict):
    """HTTP fallback for SOS location streaming.

    Expects a JSON body with ``lat``, ``lng``, ``timestamp``, and ``token``
    fields. The token must match the configured mock JWT value.

    Returns ``{"status": "ok", "received_at": "<ISO-8601>"}`` on success.
    """
    token = payload.get("token")
    if token != MOCK_SOS_TOKEN:
        raise HTTPException(status_code=401, detail="invalid token")

    lat = payload.get("lat")
    lng = payload.get("lng")
    if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
        raise HTTPException(status_code=400, detail="lat and lng must be numbers")

    if abs(lat) > 90 or abs(lng) > 180:
        raise HTTPException(status_code=400, detail="coordinates out of range")

    received_at = datetime.now(timezone.utc).isoformat()
    event = {
        "lat": float(lat),
        "lng": float(lng),
        "timestamp": payload.get("timestamp", 0),
        "received_at": received_at,
    }
    _SOS_EVENTS.append(event)
    logger.info("SOS HTTP payload: lat=%s lng=%s", lat, lng)

    return {"status": "ok", "received_at": received_at}


@app.get("/api/v1/sos/events", tags=["SOS"])
async def get_sos_events(limit: int = Query(10, ge=1, le=100)):
    """Return the most recent SOS events (ephemeral in-memory)."""
    return {"total": len(_SOS_EVENTS), "events": _SOS_EVENTS[-limit:]}


# ============================================
# Reports Endpoints
# ============================================

_REPORTS: list[dict] = []
_report_id_counter = 0


@app.post("/api/v1/reports", tags=["Reports"])
async def create_report(payload: dict):
    """Submit a user safety report.

    Expected JSON body:
        - ``lat`` (float, required)
        - ``lng`` (float, required)
        - ``category`` (str, optional, default "general")
        - ``description`` (str, optional)
        - ``timestamp`` (int, optional, epoch ms)

    Returns ``{"status": "ok", "id": "<uuid>", "created_at": "<ISO-8601>"}``.
    """
    global _report_id_counter

    lat = payload.get("lat")
    lng = payload.get("lng")

    if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
        raise HTTPException(status_code=400, detail="lat and lng are required numbers")

    if abs(lat) > 90 or abs(lng) > 180:
        raise HTTPException(status_code=400, detail="coordinates out of range")

    _report_id_counter += 1
    created_at = datetime.now(timezone.utc).isoformat()
    report = {
        "id": _report_id_counter,
        "lat": float(lat),
        "lng": float(lng),
        "category": str(payload.get("category", "general")),
        "description": str(payload.get("description", "")),
        "timestamp": payload.get("timestamp", int(datetime.now(timezone.utc).timestamp() * 1000)),
        "created_at": created_at,
    }
    _REPORTS.append(report)
    logger.info("Report created: id=%s category=%s lat=%s lng=%s", report["id"], report["category"], lat, lng)

    return {"status": "ok", "id": report["id"], "created_at": created_at}


@app.get("/api/v1/reports", tags=["Reports"])
async def get_reports(
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    radius: float = Query(1000.0, ge=0),
    category: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
):
    """Fetch reports, optionally filtered by proximity and category.

    - ``lat``, ``lng``, ``radius`` (metres): spatial filter
    - ``category``: filter by category string
    - ``limit``: max reports to return
    """
    results = list(_REPORTS)

    if category:
        results = [r for r in results if r["category"].lower() == category.lower()]

    if lat is not None and lng is not None and radius > 0:
        filtered = []
        for r in results:
            d = haversine(float(lat), float(lng), r["lat"], r["lng"])
            if d <= radius:
                filtered.append(r)
        results = filtered

    results.sort(key=lambda r: r.get("created_at", ""), reverse=True)

    return {"total": len(results), "reports": results[:limit]}


@app.websocket("/ws/sos")
async def websocket_sos(websocket: WebSocket):
    """Receive SOS payloads over WebSocket.

    Expected payload (JSON): ``{"lat": float, "lng": float, "timestamp": str,
    "token": str}``. The token must equal the configured ``mock-jwt-token``.

    On success, the server replies with ``{"status": "ok", "received_at":
    "<ISO-8601 timestamp>"}`` and logs the payload at INFO level. No broadcast
    is performed in this milestone.
    """
    await websocket.accept()
    try:
        payload = await websocket.receive_json()
    except WebSocketDisconnect:
        return
    except Exception as e:
        logger.warning("SOS WebSocket received invalid payload: %s", e)
        try:
            await websocket.send_json(
                {"status": "error", "message": "invalid json payload"}
            )
        finally:
            await websocket.close()
        return

    if not isinstance(payload, dict):
        logger.warning("SOS payload is not a JSON object: %r", payload)
        await websocket.send_json(
            {"status": "error", "message": "payload must be a JSON object"}
        )
        await websocket.close()
        return

    token = payload.get("token")
    if token != MOCK_SOS_TOKEN:
        logger.warning("SOS WebSocket rejected: invalid token (got %r)", token)
        await websocket.send_json({"status": "error", "message": "invalid token"})
        await websocket.close()
        return

    received_at = datetime.now(timezone.utc).isoformat()
    logger.info(
        "SOS payload received: lat=%s lng=%s timestamp=%s token=%s",
        payload.get("lat"),
        payload.get("lng"),
        payload.get("timestamp"),
        token,
    )

    await websocket.send_json({"status": "ok", "received_at": received_at})
    await websocket.close()


# ============================================
# Legacy Endpoints (for backward compatibility)
# ============================================

@app.post("/predict/sentiment", response_model=SentimentResponse, tags=["Legacy"], deprecated=True)
async def predict_sentiment_legacy(request: SentimentRequest):
    """Legacy endpoint. Use /api/v1/sentiment/predict instead."""
    return await predict_sentiment(request)


@app.get("/risk/scores", response_model=AllRiskScoresResponse, tags=["Legacy"], deprecated=True)
async def get_all_risk_scores_legacy(state: Optional[str] = None):
    """Legacy endpoint. Use /api/v1/risk/scores instead."""
    return await get_all_risk_scores(state)


@app.get("/risk/location", response_model=RiskScoreResponse, tags=["Legacy"], deprecated=True)
async def get_location_risk_legacy(state: str, district: str):
    """Legacy endpoint. Use /api/v1/risk/location instead."""
    return await get_location_risk(state, district)


# ============================================
# Main Entry Point
# ============================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )
