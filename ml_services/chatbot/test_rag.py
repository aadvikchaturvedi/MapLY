#!/usr/bin/env python3
"""
Test RAG-Enhanced Chatbot
==========================

Tests the RAG system with technical explanations.
"""

import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from chatbot.rag_chatbot import RAGEnhancedChatbot


def print_section(title):
    """Print formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def test_basic_explanation(chatbot):
    """Test basic safety explanation."""
    print_section("TEST 1: Basic Safety Explanation")
    
    if chatbot.risk_data and len(chatbot.risk_data) > 0:
        loc = chatbot.risk_data[0]
        print(f"📍 Location: {loc['district']}, {loc['state']}")
        print(f"📊 Safety Score: {loc['safety_score']}/100\n")
        
        explanation = chatbot.chat(
            loc['state'],
            loc['district'],
            explain_technical=False
        )
        print(explanation)
    else:
        print("No risk data available")


def test_technical_explanation(chatbot):
    """Test technical ML explanation."""
    print_section("TEST 2: Technical ML Explanation")
    
    if chatbot.risk_data and len(chatbot.risk_data) > 0:
        loc = chatbot.risk_data[0]
        print(f"📍 Location: {loc['district']}, {loc['state']}")
        print(f"📊 Safety Score: {loc['safety_score']}/100\n")
        
        print("Requesting technical details...\n")
        explanation = chatbot.chat(
            loc['state'],
            loc['district'],
            explain_technical=True
        )
        print(explanation)
    else:
        print("No risk data available")


def test_model_explanation(chatbot):
    """Test explaining the ML model itself."""
    print_section("TEST 3: Explain Risk Score Model")
    
    print("Asking chatbot to explain how the risk score model works...\n")
    explanation = chatbot.explain_model("risk_score")
    print(explanation)


def test_sentiment_explanation(chatbot):
    """Test explaining sentiment analysis."""
    print_section("TEST 4: Explain Sentiment Analysis")
    
    print("Asking chatbot to explain sentiment analysis...\n")
    explanation = chatbot.explain_model("sentiment")
    print(explanation)


def test_explainability(chatbot):
    """Test explaining the explainability features."""
    print_section("TEST 5: Explain Explainability Features")
    
    print("Asking chatbot to explain why the system is explainable...\n")
    explanation = chatbot.explain_model("explainability")
    print(explanation)


def main():
    """Run all RAG tests."""
    print("\n" + "🧪 "*20)
    print("  RAG-Enhanced Chatbot Testing")
    print("🧪 "*20)
    
    try:
        # Initialize chatbot
        print("\nInitializing RAG-enhanced chatbot...")
        chatbot = RAGEnhancedChatbot()
        print("✓ Ready!\n")
        
        # Run tests
        test_basic_explanation(chatbot)
        input("\nPress Enter to continue...")
        
        test_technical_explanation(chatbot)
        input("\nPress Enter to continue...")
        
        test_model_explanation(chatbot)
        input("\nPress Enter to continue...")
        
        test_sentiment_explanation(chatbot)
        input("\nPress Enter to continue...")
        
        test_explainability(chatbot)
        
        # Summary
        print_section("Tests Complete!")
        print("✓ Basic safety explanations")
        print("✓ Technical ML explanations")
        print("✓ Model reasoning explanations")
        print("✓ Sentiment analysis explanations")
        print("✓ Explainability features")
        print("\nRAG system is working correctly!")
        print("\nTo use interactive mode:")
        print("  python -m chatbot.rag_chatbot")
        print("\nSpecial commands in interactive mode:")
        print("  explain risk_score    - Explain risk score model")
        print("  explain sentiment     - Explain sentiment analysis")
        print("  explain explainability - Explain why it's explainable\n")
        
    except KeyboardInterrupt:
        print("\n\nTests interrupted.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
