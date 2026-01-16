"""
RAG-Enhanced Explainable Safety Chatbot
========================================

Integrates Retrieval-Augmented Generation (RAG) to provide detailed
technical explanations about the ML models and reasoning.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, List
from google import genai
from dotenv import load_dotenv

# Add parent directory to path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from Risk_Score_Engine.model import RiskScoreAPI

# Load environment variables
load_dotenv(parent_dir / ".env")


class RAGEnhancedChatbot:
    """
    Enhanced chatbot with RAG for technical explanations.
    Uses knowledge base to provide detailed reasoning about ML models.
    """
    
    def __init__(self):
        """Initialize the RAG-enhanced chatbot."""
        # Initialize Gemini client
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.0-flash-exp"
        
        # Initialize risk score engine
        self.risk_engine = RiskScoreAPI()
        self.risk_data = None
        
        # Load knowledge base
        self.knowledge_base = self._load_knowledge_base()
        
        # Load risk data
        self._load_risk_data()
        
        print("✓ RAG-Enhanced Chatbot initialized successfully")
    
    def _load_knowledge_base(self) -> str:
        """Load the technical knowledge base for RAG."""
        kb_path = Path(__file__).parent / "knowledge_base.md"
        
        if kb_path.exists():
            with open(kb_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✓ Loaded knowledge base ({len(content)} characters)")
            return content
        else:
            print("⚠ Knowledge base not found, using basic mode")
            return ""
    
    def _load_risk_data(self):
        """Load risk score data from CSV files."""
        try:
            data_dir = parent_dir.parent / "data"
            csv_files = [str(p) for p in data_dir.glob("*.csv")]
            
            if csv_files:
                result = self.risk_engine.get_navigation_data(csv_files)
                if result.get("status") == "success":
                    self.risk_data = result.get("data", [])
                    print(f"✓ Loaded risk data for {len(self.risk_data)} regions")
        except Exception as e:
            print(f"⚠ Error loading risk data: {e}")
    
    def get_location_risk(self, state: str, district: str) -> Optional[Dict]:
        """Get risk information for a specific location."""
        if not self.risk_data:
            return None
        
        match = next(
            (d for d in self.risk_data 
             if d["state"].lower() == state.lower() and 
                d["district"].lower() == district.lower()),
            None
        )
        
        return match
    
    def _extract_relevant_context(self, query_type: str) -> str:
        """
        Extract relevant sections from knowledge base based on query type.
        
        Args:
            query_type: Type of explanation needed (risk_score, sentiment, general)
        """
        if not self.knowledge_base:
            return ""
        
        # Simple keyword-based extraction (can be enhanced with embeddings)
        if query_type == "risk_score":
            # Extract risk score engine section
            start = self.knowledge_base.find("## Risk Score Engine")
            end = self.knowledge_base.find("## Sentiment Analysis")
            if start != -1 and end != -1:
                return self.knowledge_base[start:end]
        
        elif query_type == "sentiment":
            # Extract sentiment analysis section
            start = self.knowledge_base.find("## Sentiment Analysis")
            end = self.knowledge_base.find("## Why This Approach")
            if start != -1 and end != -1:
                return self.knowledge_base[start:end]
        
        elif query_type == "explainability":
            # Extract explainability section
            start = self.knowledge_base.find("## Why This Approach is Explainable")
            end = self.knowledge_base.find("## Technical Specifications")
            if start != -1 and end != -1:
                return self.knowledge_base[start:end]
        
        # Return full knowledge base for general queries
        return self.knowledge_base[:5000]  # Limit to avoid token limits
    
    def generate_explanation(
        self,
        state: str,
        district: str,
        risk_info: Dict,
        user_context: Optional[str] = None,
        include_technical: bool = False
    ) -> str:
        """
        Generate RAG-enhanced explanation with technical details.
        
        Args:
            state: State name
            district: District name
            risk_info: Risk information dictionary
            user_context: Optional user context
            include_technical: Whether to include technical ML details
        """
        safety_score = risk_info["safety_score"]
        risk_category = risk_info["risk_category"]
        
        # Extract relevant context from knowledge base
        if include_technical:
            kb_context = self._extract_relevant_context("risk_score")
        else:
            kb_context = ""
        
        # Create enhanced prompt with RAG context
        prompt = f"""You are an AI safety advisor with deep knowledge of machine learning and women's safety.

Location: {district}, {state}
Safety Score: {safety_score}/100
Risk Category: {risk_category}

{"TECHNICAL CONTEXT (Use this to explain the reasoning):" if kb_context else ""}
{kb_context if kb_context else ""}

{"User Context: " + user_context if user_context else ""}

Task: Provide a clear, empathetic explanation that includes:

1. **Risk Level Summary**: What "{risk_category}" means practically

2. **How We Calculated This** (if technical details requested):
   - Explain that the score is based on government crime data
   - Mention the ML model (XGBoost) analyzes multiple crime categories
   - Note that crimes are weighted by severity (e.g., rape, kidnapping have higher weights)
   - Explain the 0-100 scale (higher = safer)

3. **Key Risk Factors**: Main factors contributing to this score
   - Based on crime statistics in the knowledge base
   - Mention specific crime categories if relevant

4. **Safety Recommendations**: 3-4 specific, actionable tips

5. **Transparency Note**: Briefly mention this is based on:
   - Government crime statistics (NCRB data)
   - Machine learning analysis
   - Historical trends

{"6. **Technical Details** (since user requested): Explain the ML reasoning:" if include_technical else ""}
{"   - Which features the model considered" if include_technical else ""}
{"   - Why certain crimes have higher weights" if include_technical else ""}
{"   - How the final score was calculated" if include_technical else ""}

Keep the tone supportive and informative. Balance technical accuracy with accessibility.
Limit response to {"300-350" if include_technical else "200-250"} words.
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return self._generate_fallback_explanation(state, district, risk_info, include_technical)
    
    def _generate_fallback_explanation(
        self,
        state: str,
        district: str,
        risk_info: Dict,
        include_technical: bool = False
    ) -> str:
        """Generate fallback explanation if AI fails."""
        safety_score = risk_info["safety_score"]
        risk_category = risk_info["risk_category"]
        
        technical_section = ""
        if include_technical:
            technical_section = f"""

**How This Score Was Calculated:**
Our machine learning model (XGBoost) analyzes government crime data across 7 categories:
- Crimes are weighted by severity (rape, kidnapping have highest weights)
- Multiple factors considered: total crimes, domestic violence, public safety incidents
- Score normalized to 0-100 scale (higher = safer)
- Based on National Crime Records Bureau (NCRB) data

**Model Reasoning:**
The {safety_score}/100 score reflects analysis of historical crime patterns, weighted by severity and type. The model considers both volume and nature of incidents to provide a comprehensive safety assessment.
"""
        
        explanation = f"""
🚨 Safety Alert for {district}, {state}

**Risk Level: {risk_category}**
Safety Score: {safety_score}/100

This area has been classified as {risk_category.lower()} based on analysis of government crime data and safety statistics.
{technical_section}

**Safety Recommendations:**
• Stay in well-lit, populated areas
• Share your location with trusted contacts
• Be aware of your surroundings
• Consider traveling in groups when possible
• Keep emergency contacts readily available

**Data Source:**
This assessment is based on official government crime statistics from the National Crime Records Bureau (NCRB), analyzed using machine learning to provide transparent, data-driven safety insights.

For more detailed information, please check local safety resources or contact local authorities.
"""
        return explanation.strip()
    
    def chat(
        self,
        state: str,
        district: str,
        user_context: Optional[str] = None,
        explain_technical: bool = False
    ) -> str:
        """
        Main chat interface with RAG enhancement.
        
        Args:
            state: State name
            district: District name
            user_context: Optional context about user's situation
            explain_technical: Whether to include technical ML explanations
        """
        # Get risk information
        risk_info = self.get_location_risk(state, district)
        
        if not risk_info:
            return f"❌ Sorry, I don't have safety data for {district}, {state}. Please check the location name and try again."
        
        # Check if it's a high-risk zone
        safety_score = risk_info["safety_score"]
        risk_category = risk_info["risk_category"]
        
        # Generate explanation
        if risk_category == "High Risk":
            print(f"\n⚠️  HIGH RISK ZONE DETECTED: {district}, {state}")
            print(f"Safety Score: {safety_score}/100\n")
        
        explanation = self.generate_explanation(
            state, district, risk_info, user_context, explain_technical
        )
        
        return explanation
    
    def explain_model(self, aspect: str = "general") -> str:
        """
        Explain specific aspects of the ML models.
        
        Args:
            aspect: What to explain (risk_score, sentiment, explainability, general)
        """
        context = self._extract_relevant_context(aspect)
        
        prompt = f"""Based on this technical documentation about our ML system:

{context}

Provide a clear, accessible explanation of how our {aspect} system works.
Include:
1. What it does
2. How it works (simplified)
3. Why it's trustworthy (explainability)
4. Key technical details (but keep it understandable)

Limit to 250-300 words. Use analogies where helpful.
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Error generating explanation: {e}"
    
    def interactive_mode(self):
        """Run the chatbot in interactive mode with RAG features."""
        print("\n" + "="*70)
        print("🛡️  MapLY RAG-Enhanced Explainable Safety Chatbot")
        print("="*70)
        print("\nI can explain safety risks AND the ML reasoning behind them!")
        print("Type 'quit' to exit, 'explain [topic]' for ML explanations.\n")
        
        while True:
            try:
                print("-" * 70)
                user_input = input("Enter command (or state name): ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Stay safe! Goodbye.")
                    break
                
                # Handle explain commands
                if user_input.lower().startswith('explain'):
                    parts = user_input.split(maxsplit=1)
                    topic = parts[1] if len(parts) > 1 else "general"
                    
                    print(f"\n📚 Explaining: {topic}\n")
                    explanation = self.explain_model(topic)
                    print(explanation)
                    print()
                    continue
                
                # Regular location query
                state = user_input
                district = input("Enter district name: ").strip()
                
                if not state or not district:
                    print("❌ Please provide both state and district names.\n")
                    continue
                
                context_input = input("Context (optional): ").strip()
                context = context_input if context_input else None
                
                technical = input("Include technical ML details? (y/n): ").strip().lower() == 'y'
                
                print("\n" + "="*70)
                explanation = self.chat(state, district, context, technical)
                print(explanation)
                print("="*70 + "\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Stay safe! Goodbye.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")


def main():
    """Main function to run the RAG-enhanced chatbot."""
    try:
        chatbot = RAGEnhancedChatbot()
        chatbot.interactive_mode()
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
