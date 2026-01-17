"""
Chatbot API Integration
========================

FastAPI endpoints for the explainable safety chatbot.
Supports Pinecone-enhanced RAG, Standard RAG, and Basic Chatbot.
"""

import sys
import os
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

# Add parent directory to path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

# Import various chatbot implementations
from chatbot.explainable_chatbot import ExplainableSafetyChatbot
try:
    from chatbot.rag_chatbot import RAGEnhancedChatbot
    from chatbot.pinecone_rag_chatbot import PineconeRAGChatbot
except ImportError:
    RAGEnhancedChatbot = None
    PineconeRAGChatbot = None

# Create router
router = APIRouter(prefix="/api/v1/chatbot", tags=["Chatbot"])

# Global chatbot instance
chatbot = None


def initialize_chatbot():
    """
    Initialize the best available chatbot on startup.
    Priority: PineconeRAG > RAGEnhanced > ExplainableSafety
    """
    global chatbot
    try:
        # Check environment for Pinecone support
        if os.getenv("PINECONE_API_KEY") and PineconeRAGChatbot:
            print("🌟 Initializing Pinecone-Enhanced RAG Chatbot...")
            chatbot = PineconeRAGChatbot(use_pinecone=True)
            print("✓ Pinecone RAG Chatbot initialized successfully")
        
        # Fallback to Standard RAG
        elif RAGEnhancedChatbot:
            print("📚 Initializing Standard RAG Chatbot...")
            chatbot = RAGEnhancedChatbot()
            print("✓ Standard RAG Chatbot initialized successfully")
        
        # Fallback to Basic Chatbot
        else:
            print("🤖 Initializing Basic Explainable Chatbot...")
            chatbot = ExplainableSafetyChatbot()
            print("✓ Basic Chatbot initialized successfully")
            
    except Exception as e:
        print(f"✗ Failed to initialize enhanced chatbot: {e}")
        print("Falling back to basic chatbot...")
        try:
            chatbot = ExplainableSafetyChatbot()
            print("✓ Basic Chatbot initialized (fallback mode)")
        except Exception as e2:
            print(f"✗ CRITICAL: Failed to initialize any chatbot: {e2}")


# Request/Response models
class ChatRequest(BaseModel):
    """Request model for chatbot."""
    state: str = Field(..., min_length=1, description="State name")
    district: str = Field(..., min_length=1, description="District name")
    context: Optional[str] = Field(None, description="Optional user context")
    include_technical: bool = Field(False, description="Include technical ML explanations")


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
    - **include_technical**: Request detailed ML reasoning (default: False)
    
    Returns detailed explanation with safety recommendations.
    """
    if not chatbot:
        raise HTTPException(
            status_code=503,
            detail="Chatbot not initialized. Please check server logs."
        )
    
    try:
        # Check if the chatbot supports technical explanations
        is_rag_capable = hasattr(chatbot, 'chat') and 'explain_technical' in chatbot.chat.__code__.co_varnames
        
        # Get risk information (works for all variants)
        # Note: older ExplainableSafetyChatbot might not expose get_location_risk directly in the same way 
        # or might handle chat differently. Let's rely on the common 'chat' or 'generate_explanation' method if possible
        # but the current implementations differ slightly. RAG ones use chat().
        
        # Let's use the 'chat' method which is common to RAG bots, 
        # but ExplainableSafetyChatbot also has chat().
        # However, ExplainableSafetyChatbot.chat returning string is only for CLI.
        # We need structured data.
        
        # All implementations have get_location_risk
        risk_info = chatbot.get_location_risk(request.state, request.district)
        
        if not risk_info:
            raise HTTPException(
                status_code=404,
                detail=f"Location not found: {request.district}, {request.state}"
            )
        
        # Generate explanation
        if is_rag_capable:
            explanation = chatbot.generate_explanation(
                request.state,
                request.district,
                risk_info,
                request.context,
                include_technical=request.include_technical
            )
        else:
            # Fallback for basic chatbot (no technical flag)
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
        "chatbot_type": type(chatbot).__name__ if chatbot else None,
        "chatbot_ready": chatbot is not None
    }
