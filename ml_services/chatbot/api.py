"""
Chatbot API Integration
========================

FastAPI endpoints for the explainable safety chatbot.
"""

import sys
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Add parent directory to path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from chatbot.explainable_chatbot import ExplainableSafetyChatbot

# Create router
router = APIRouter(prefix="/api/v1/chatbot", tags=["Chatbot"])

# Global chatbot instance
chatbot = None


def initialize_chatbot():
    """Initialize the chatbot on startup."""
    global chatbot
    try:
        chatbot = ExplainableSafetyChatbot()
        print("✓ Chatbot initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize chatbot: {e}")


# Request/Response models
class ChatRequest(BaseModel):
    """Request model for chatbot."""
    state: str = Field(..., min_length=1, description="State name")
    district: str = Field(..., min_length=1, description="District name")
    context: Optional[str] = Field(None, description="Optional user context")


class ChatResponse(BaseModel):
    """Response model for chatbot."""
    state: str
    district: str
    safety_score: float
    risk_category: str
    explanation: str


@router.post("/explain", response_model=ChatResponse)
async def get_safety_explanation(request: ChatRequest):
    """
    Get an explainable AI response for a location's safety risk.
    
    - **state**: State name (required)
    - **district**: District name (required)
    - **context**: Optional context about user's situation
    
    Returns detailed explanation with safety recommendations.
    """
    if not chatbot:
        raise HTTPException(
            status_code=503,
            detail="Chatbot not initialized. Please check server logs."
        )
    
    try:
        # Get risk information
        risk_info = chatbot.get_location_risk(request.state, request.district)
        
        if not risk_info:
            raise HTTPException(
                status_code=404,
                detail=f"Location not found: {request.district}, {request.state}"
            )
        
        # Generate explanation
        explanation = chatbot.generate_explanation(
            request.state,
            request.district,
            risk_info,
            request.context
        )
        
        return {
            "state": risk_info["state"],
            "district": risk_info["district"],
            "safety_score": risk_info["safety_score"],
            "risk_category": risk_info["risk_category"],
            "explanation": explanation
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate explanation: {str(e)}"
        )


@router.get("/health")
async def chatbot_health():
    """Check if chatbot is initialized and ready."""
    return {
        "status": "healthy" if chatbot else "not initialized",
        "chatbot_ready": chatbot is not None
    }
