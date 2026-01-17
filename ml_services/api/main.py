"""
MapLY ML Services API
=====================

Production-ready FastAPI application for sentiment analysis and risk scoring.
"""

import sys
from pathlib import Path
from typing import Optional

# Add ml_services to sys.path
current_dir = Path(__file__).resolve().parent
ml_services_dir = current_dir.parent
sys.path.append(str(ml_services_dir))

from fastapi import FastAPI, HTTPException, Query
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
