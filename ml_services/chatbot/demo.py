#!/usr/bin/env python3
"""
Chatbot Demo - Explainable Safety Alerts
=========================================

Demonstrates the explainable chatbot with various scenarios.
"""

import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from chatbot.explainable_chatbot import ExplainableSafetyChatbot


def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def demo_high_risk_zone(chatbot):
    """Demonstrate high-risk zone explanation."""
    print_header("DEMO 1: High-Risk Zone Alert")
    
    # Find a high-risk location from the data
    if chatbot.risk_data:
        high_risk_locations = [
            loc for loc in chatbot.risk_data 
            if loc["risk_category"] == "High Risk"
        ]
        
        if high_risk_locations:
            loc = high_risk_locations[0]
            print(f"📍 Location: {loc['district']}, {loc['state']}")
            print(f"⚠️  Risk Category: {loc['risk_category']}")
            print(f"📊 Safety Score: {loc['safety_score']}/100\n")
            
            print("Generating AI explanation...\n")
            explanation = chatbot.chat(
                loc['state'],
                loc['district'],
                "planning to visit this area tomorrow afternoon"
            )
            print(explanation)
        else:
            print("No high-risk locations found in dataset.")
    else:
        print("No risk data loaded.")


def demo_moderate_risk_zone(chatbot):
    """Demonstrate moderate-risk zone explanation."""
    print_header("DEMO 2: Moderate-Risk Zone Alert")
    
    if chatbot.risk_data:
        moderate_risk_locations = [
            loc for loc in chatbot.risk_data 
            if loc["risk_category"] == "Moderate Risk"
        ]
        
        if moderate_risk_locations:
            loc = moderate_risk_locations[0]
            print(f"📍 Location: {loc['district']}, {loc['state']}")
            print(f"⚠️  Risk Category: {loc['risk_category']}")
            print(f"📊 Safety Score: {loc['safety_score']}/100\n")
            
            print("Generating AI explanation...\n")
            explanation = chatbot.chat(
                loc['state'],
                loc['district'],
                "traveling alone at night"
            )
            print(explanation)
        else:
            print("No moderate-risk locations found in dataset.")
    else:
        print("No risk data loaded.")


def demo_low_risk_zone(chatbot):
    """Demonstrate low-risk zone explanation."""
    print_header("DEMO 3: Low-Risk Zone (Safe Area)")
    
    if chatbot.risk_data:
        low_risk_locations = [
            loc for loc in chatbot.risk_data 
            if loc["risk_category"] == "Low Risk"
        ]
        
        if low_risk_locations:
            loc = low_risk_locations[0]
            print(f"📍 Location: {loc['district']}, {loc['state']}")
            print(f"✅ Risk Category: {loc['risk_category']}")
            print(f"📊 Safety Score: {loc['safety_score']}/100\n")
            
            print("Generating AI explanation...\n")
            explanation = chatbot.chat(
                loc['state'],
                loc['district']
            )
            print(explanation)
        else:
            print("No low-risk locations found in dataset.")
    else:
        print("No risk data loaded.")


def demo_contextual_advice(chatbot):
    """Demonstrate context-aware advice."""
    print_header("DEMO 4: Context-Aware Safety Advice")
    
    if chatbot.risk_data and len(chatbot.risk_data) > 0:
        loc = chatbot.risk_data[0]
        
        contexts = [
            "traveling with family during daytime",
            "commuting to work early morning",
            "returning home late at night alone"
        ]
        
        print(f"📍 Location: {loc['district']}, {loc['state']}")
        print(f"📊 Safety Score: {loc['safety_score']}/100\n")
        
        for i, context in enumerate(contexts, 1):
            print(f"\n--- Scenario {i}: {context} ---\n")
            explanation = chatbot.chat(
                loc['state'],
                loc['district'],
                context
            )
            print(explanation)
            print()


def main():
    """Run all demos."""
    print("\n" + "🛡️ "*20)
    print("  MapLY Explainable Safety Chatbot - Demo")
    print("🛡️ "*20)
    
    try:
        # Initialize chatbot
        print("\nInitializing chatbot...")
        chatbot = ExplainableSafetyChatbot()
        print("✓ Ready!\n")
        
        # Run demos
        demo_high_risk_zone(chatbot)
        input("\nPress Enter to continue to next demo...")
        
        demo_moderate_risk_zone(chatbot)
        input("\nPress Enter to continue to next demo...")
        
        demo_low_risk_zone(chatbot)
        input("\nPress Enter to continue to next demo...")
        
        demo_contextual_advice(chatbot)
        
        # Final message
        print_header("Demo Complete!")
        print("Key Features Demonstrated:")
        print("  ✓ High-risk zone detection and alerts")
        print("  ✓ Detailed AI-generated explanations")
        print("  ✓ Context-aware safety recommendations")
        print("  ✓ Risk categorization (High/Moderate/Low)")
        print("  ✓ Actionable safety tips")
        print("\nTo use the interactive chatbot:")
        print("  python -m chatbot.explainable_chatbot")
        print("\nTo integrate with API:")
        print("  See chatbot/README.md for details\n")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
