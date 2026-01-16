"""
Explainable Safety Chatbot
===========================

Provides detailed explanations for high-risk zones using Gemini AI.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, List
from google import genai
from dotenv import load_dotenv

# Add parent directory to path for imports
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from Risk_Score_Engine.model import RiskScoreAPI

# Load environment variables
load_dotenv(parent_dir / ".env")


class ExplainableSafetyChatbot:
    """
    Chatbot that provides explainable AI responses for safety risk zones.
    Uses Gemini AI to generate human-friendly explanations.
    """
    
    def __init__(self):
        """Initialize the chatbot with Gemini AI and risk score engine."""
        # Initialize Gemini client
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.0-flash-exp"
        
        # Initialize risk score engine
        self.risk_engine = RiskScoreAPI()
        self.risk_data = None
        
        # Load risk data
        self._load_risk_data()
        
        print("✓ Explainable Safety Chatbot initialized successfully")
    
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
                else:
                    print(f"⚠ Failed to load risk data: {result.get('message')}")
            else:
                print(f"⚠ No CSV files found in {data_dir}")
        except Exception as e:
            print(f"⚠ Error loading risk data: {e}")
    
    def get_location_risk(self, state: str, district: str) -> Optional[Dict]:
        """
        Get risk information for a specific location.
        
        Args:
            state: State name
            district: District name
            
        Returns:
            Dictionary with risk information or None if not found
        """
        if not self.risk_data:
            return None
        
        # Case-insensitive search
        match = next(
            (d for d in self.risk_data 
             if d["state"].lower() == state.lower() and 
                d["district"].lower() == district.lower()),
            None
        )
        
        return match
    
    def _get_crime_statistics(self, state: str, district: str) -> Dict:
        """
        Get detailed crime statistics for explanation.
        This is a placeholder - in production, fetch from database.
        """
        # This would fetch actual crime data from your database
        # For now, returning sample data structure
        return {
            "total_crimes": "Data from government records",
            "major_categories": [
                "Crimes against women",
                "Public safety incidents",
                "Domestic violence cases"
            ],
            "trend": "Based on historical data analysis"
        }
    
    def generate_explanation(
        self, 
        state: str, 
        district: str, 
        risk_info: Dict,
        user_context: Optional[str] = None
    ) -> str:
        """
        Generate an explainable AI response for the risk zone.
        
        Args:
            state: State name
            district: District name
            risk_info: Risk information dictionary
            user_context: Optional user context (e.g., "traveling alone at night")
            
        Returns:
            Human-friendly explanation from Gemini AI
        """
        safety_score = risk_info["safety_score"]
        risk_category = risk_info["risk_category"]
        
        # Get additional context
        crime_stats = self._get_crime_statistics(state, district)
        
        # Create detailed prompt for Gemini
        prompt = f"""You are a women's safety advisor providing clear, empathetic explanations about safety risks.

Location: {district}, {state}
Safety Score: {safety_score}/100
Risk Category: {risk_category}

Context:
- This safety score is calculated using machine learning analysis of government crime data
- The score considers multiple factors including crimes against women, public safety incidents, and historical trends
- Scores range from 0-100, where higher scores indicate safer areas

Task: Provide a clear, empathetic explanation to a user who is entering or considering this area. Include:

1. **Risk Level Summary**: Briefly explain what "{risk_category}" means in practical terms
2. **Key Factors**: Explain the main factors contributing to this risk level (based on crime statistics)
3. **Safety Recommendations**: Provide 3-4 specific, actionable safety tips for this area
4. **Positive Notes**: If applicable, mention any positive aspects or safer times/areas

{"User Context: " + user_context if user_context else ""}

Keep the tone supportive and informative, not alarmist. Focus on empowering the user with knowledge and practical advice.
Limit response to 200-250 words."""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            # Fallback explanation if AI fails
            return self._generate_fallback_explanation(state, district, risk_info)
    
    def _generate_fallback_explanation(
        self, 
        state: str, 
        district: str, 
        risk_info: Dict
    ) -> str:
        """Generate a basic explanation if AI service fails."""
        safety_score = risk_info["safety_score"]
        risk_category = risk_info["risk_category"]
        
        explanation = f"""
🚨 Safety Alert for {district}, {state}

Risk Level: {risk_category}
Safety Score: {safety_score}/100

This area has been classified as {risk_category.lower()} based on analysis of government crime data and safety statistics.

Safety Recommendations:
• Stay in well-lit, populated areas
• Share your location with trusted contacts
• Be aware of your surroundings
• Consider traveling in groups when possible
• Keep emergency contacts readily available

For more detailed information, please check local safety resources or contact local authorities.
"""
        return explanation.strip()
    
    def chat(self, state: str, district: str, user_context: Optional[str] = None) -> str:
        """
        Main chat interface for getting safety explanations.
        
        Args:
            state: State name
            district: District name
            user_context: Optional context about user's situation
            
        Returns:
            Explanation text
        """
        # Get risk information
        risk_info = self.get_location_risk(state, district)
        
        if not risk_info:
            return f"❌ Sorry, I don't have safety data for {district}, {state}. Please check the location name and try again."
        
        # Check if it's a high-risk zone
        safety_score = risk_info["safety_score"]
        risk_category = risk_info["risk_category"]
        
        # Generate explanation for any risk level, but emphasize high-risk
        if risk_category == "High Risk":
            print(f"\n⚠️  HIGH RISK ZONE DETECTED: {district}, {state}")
            print(f"Safety Score: {safety_score}/100\n")
        
        # Generate AI explanation
        explanation = self.generate_explanation(state, district, risk_info, user_context)
        
        return explanation
    
    def interactive_mode(self):
        """Run the chatbot in interactive mode."""
        print("\n" + "="*60)
        print("🛡️  MapLY Explainable Safety Chatbot")
        print("="*60)
        print("\nI'll help you understand safety risks in different areas.")
        print("Type 'quit' or 'exit' to stop.\n")
        
        while True:
            try:
                # Get location input
                print("-" * 60)
                state = input("Enter state name (or 'quit'): ").strip()
                
                if state.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Stay safe! Goodbye.")
                    break
                
                district = input("Enter district name: ").strip()
                
                if not state or not district:
                    print("❌ Please provide both state and district names.\n")
                    continue
                
                # Optional context
                context_input = input("Any additional context? (optional, press Enter to skip): ").strip()
                context = context_input if context_input else None
                
                # Get explanation
                print("\n" + "="*60)
                explanation = self.chat(state, district, context)
                print(explanation)
                print("="*60 + "\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Stay safe! Goodbye.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")


def main():
    """Main function to run the chatbot."""
    try:
        chatbot = ExplainableSafetyChatbot()
        chatbot.interactive_mode()
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
