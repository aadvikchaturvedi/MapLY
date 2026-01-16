"""
Pinecone-Enhanced RAG Chatbot
==============================

Advanced RAG system using Pinecone vector database for semantic search.
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
from chatbot.pinecone_kb import PineconeKnowledgeBase

# Load environment variables
load_dotenv(parent_dir / ".env")


class PineconeRAGChatbot:
    """
    Advanced RAG chatbot using Pinecone for semantic search.
    Provides highly relevant technical explanations.
    """
    
    def __init__(self, use_pinecone: bool = True):
        """
        Initialize the Pinecone-enhanced chatbot.
        
        Args:
            use_pinecone: Whether to use Pinecone (falls back to basic RAG if False)
        """
        # Initialize Gemini client
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.0-flash-exp"
        
        # Initialize risk score engine
        self.risk_engine = RiskScoreAPI()
        self.risk_data = None
        
        # Initialize Pinecone knowledge base
        self.use_pinecone = use_pinecone
        self.pinecone_kb = None
        
        if use_pinecone:
            try:
                self.pinecone_kb = PineconeKnowledgeBase()
                print("✓ Pinecone vector search enabled")
            except Exception as e:
                print(f"⚠ Pinecone initialization failed: {e}")
                print("  Falling back to basic RAG")
                self.use_pinecone = False
        
        # Load risk data
        self._load_risk_data()
        
        print("✓ Pinecone-Enhanced RAG Chatbot initialized")
    
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
    
    def retrieve_context(
        self,
        query: str,
        query_type: Optional[str] = None,
        top_k: int = 3
    ) -> str:
        """
        Retrieve relevant context using Pinecone semantic search.
        
        Args:
            query: Search query
            query_type: Optional filter by type (risk_score, sentiment, etc.)
            top_k: Number of results to retrieve
            
        Returns:
            Combined context from top results
        """
        if not self.use_pinecone or not self.pinecone_kb:
            return ""
        
        try:
            print(f"DEBUG: Searching Pinecone for: '{query}'")
            # Search Pinecone
            results = self.pinecone_kb.search(
                query=query,
                top_k=top_k,
                filter_type=query_type
            )
            print(f"DEBUG: Found {len(results)} results")
            
            # Combine results
            context_parts = []
            for i, result in enumerate(results, 1):
                context_parts.append(f"[Source {i} - {result['section']}]")
                context_parts.append(result['text'])
                context_parts.append("")  # Empty line
            
            combined = "\n".join(context_parts)
            # print(f"DEBUG: Context length: {len(combined)}")
            return combined
            
        except Exception as e:
            print(f"⚠ Pinecone search error: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def generate_explanation(
        self,
        state: str,
        district: str,
        risk_info: Dict,
        user_context: Optional[str] = None,
        include_technical: bool = False
    ) -> str:
        """
        Generate explanation using Pinecone-retrieved context.
        
        Args:
            state: State name
            district: District name
            risk_info: Risk information dictionary
            user_context: Optional user context
            include_technical: Whether to include technical details
        """
        safety_score = risk_info["safety_score"]
        risk_category = risk_info["risk_category"]
        
        # Build search query for Pinecone
        if include_technical:
            search_query = f"How is the risk score calculated? Explain the machine learning model and features used for safety scoring."
            query_type = "risk_score"
        else:
            search_query = f"Safety risk explanation for {risk_category} areas"
            query_type = None
        
        # Retrieve context from Pinecone
        kb_context = self.retrieve_context(search_query, query_type, top_k=2)
        
        # Create enhanced prompt
        prompt = f"""You are an AI safety advisor with deep knowledge of machine learning and women's safety.

Location: {district}, {state}
Safety Score: {safety_score}/100
Risk Category: {risk_category}

{"TECHNICAL KNOWLEDGE BASE (Retrieved from vector database):" if kb_context else ""}
{kb_context if kb_context else ""}

{"User Context: " + user_context if user_context else ""}

Task: Provide a clear, empathetic explanation that includes:

1. **Risk Level Summary**: What "{risk_category}" means practically

{"2. **How We Calculated This** (Use the knowledge base above):" if include_technical and kb_context else "2. **Key Risk Factors**:"}
{"   - Explain the ML model (XGBoost) and its features" if include_technical else "   - Main factors contributing to this score"}
{"   - Describe the crime categories and their weights" if include_technical else "   - Based on government crime data"}
{"   - Explain the 0-100 scoring system" if include_technical else ""}

{"3. **Model Reasoning** (Based on knowledge base):" if include_technical and kb_context else "3. **Safety Recommendations**:"}
{"   - Which specific features influenced this score" if include_technical else "   - 3-4 specific, actionable tips"}
{"   - Why certain crimes have higher weights" if include_technical else ""}
{"   - How the final calculation was performed" if include_technical else ""}

{"4. **Safety Recommendations**:" if include_technical else "4. **Data Source**:"}
   {"3-4 specific, actionable safety tips" if include_technical else "Mention this is based on government data (NCRB)"}

{"5. **Transparency Note**:" if include_technical else ""}
{"   - Data source: Government crime statistics (NCRB)" if include_technical else ""}
{"   - Model: XGBoost with documented features" if include_technical else ""}
{"   - Reproducible and auditable" if include_technical else ""}

Keep the tone supportive and informative. Use the knowledge base information to provide accurate technical details.
Limit response to {"350-400" if include_technical else "200-250"} words.
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
Our XGBoost machine learning model analyzes government crime data across 7 categories:
- Crimes weighted by severity (rape=9/10, kidnapping=7/10, dowry deaths=10/10)
- Features: Total crimes, domestic violence ratio, public safety incidents
- Score normalized to 0-100 scale (higher = safer)
- Data source: National Crime Records Bureau (NCRB)

**Model Reasoning:**
The {safety_score}/100 score reflects comprehensive analysis of:
- Historical crime patterns in this district
- Weighted severity of different crime types
- Comparison with regional averages
- Trend analysis over multiple years
"""
        
        explanation = f"""
🚨 Safety Alert for {district}, {state}

**Risk Level: {risk_category}**
Safety Score: {safety_score}/100

This area has been classified as {risk_category.lower()} based on machine learning analysis of government crime statistics.
{technical_section}

**Safety Recommendations:**
• Stay in well-lit, populated areas
• Share your location with trusted contacts
• Be aware of your surroundings
• Consider traveling in groups when possible
• Keep emergency contacts readily available

**Data Source:**
This assessment uses official government crime statistics from the National Crime Records Bureau (NCRB), analyzed using XGBoost machine learning for transparent, data-driven safety insights.
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
        Main chat interface with Pinecone-enhanced RAG.
        
        Args:
            state: State name
            district: District name
            user_context: Optional context
            explain_technical: Whether to include technical details
        """
        # Get risk information
        risk_info = self.get_location_risk(state, district)
        
        if not risk_info:
            return f"❌ Sorry, I don't have safety data for {district}, {state}. Please check the location name and try again."
        
        # Check if high-risk zone
        safety_score = risk_info["safety_score"]
        risk_category = risk_info["risk_category"]
        
        if risk_category == "High Risk":
            print(f"\n⚠️  HIGH RISK ZONE DETECTED: {district}, {state}")
            print(f"Safety Score: {safety_score}/100\n")
        
        # Generate explanation with Pinecone context
        explanation = self.generate_explanation(
            state, district, risk_info, user_context, explain_technical
        )
        
        return explanation
    
    def ask_question(self, question: str, topic: Optional[str] = None) -> str:
        """
        Ask a question about the ML system using Pinecone search.
        
        Args:
            question: Question to ask
            topic: Optional topic filter (risk_score, sentiment, explainability)
            
        Returns:
            AI-generated answer based on knowledge base
        """
        if not self.use_pinecone or not self.pinecone_kb:
            return "Pinecone is not available. Please check your configuration."
        
        try:
            # Search for relevant context
            context = self.retrieve_context(question, topic, top_k=3)
            
            if not context:
                return "I couldn't find relevant information in the knowledge base."
            
            # Generate answer
            prompt = f"""Based on this technical documentation:

{context}

Answer this question clearly and accurately:
{question}

Provide a comprehensive but accessible answer. Include:
1. Direct answer to the question
2. Key technical details
3. Why it matters
4. Examples if relevant

Limit to 250-300 words.
"""
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            return response.text
            
        except Exception as e:
            return f"Error generating answer: {e}"
    
    def interactive_mode(self):
        """Run interactive mode with Pinecone features."""
        print("\n" + "="*70)
        print("🛡️  MapLY Pinecone-Enhanced RAG Chatbot")
        print("="*70)
        print("\nFeatures:")
        print("  • Semantic search with Pinecone vector database")
        print("  • AI-powered explanations with retrieved context")
        print("  • Technical ML details on demand")
        print("\nCommands:")
        print("  • Enter location → Get safety explanation")
        print("  • ask [question] → Ask about the ML system")
        print("  • quit → Exit")
        print()
        
        while True:
            try:
                print("-" * 70)
                user_input = input("Enter command (or state name): ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Stay safe! Goodbye.")
                    break
                
                # Handle ask commands
                if user_input.lower().startswith('ask'):
                    question = user_input[3:].strip()
                    if not question:
                        question = input("What would you like to know? ").strip()
                    
                    print(f"\n🔍 Searching knowledge base...\n")
                    answer = self.ask_question(question)
                    print(answer)
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
                if technical:
                    print("🔍 Retrieving technical information from vector database...")
                explanation = self.chat(state, district, context, technical)
                print(explanation)
                print("="*70 + "\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Stay safe! Goodbye.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")


def main():
    """Main function."""
    try:
        chatbot = PineconeRAGChatbot(use_pinecone=True)
        chatbot.interactive_mode()
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
