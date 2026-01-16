#!/usr/bin/env python3
"""
Quick test script for the explainable chatbot
"""

import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from chatbot.explainable_chatbot import ExplainableSafetyChatbot

def main():
    print("Testing Explainable Safety Chatbot\n")
    
    try:
        # Initialize chatbot
        print("Initializing chatbot...")
        chatbot = ExplainableSafetyChatbot()
        print("✓ Chatbot initialized\n")
        
        # Test with a sample location
        print("Testing with sample location...")
        print("-" * 60)
        
        # Example: Test with a high-risk area (adjust based on your data)
        test_cases = [
            {
                "state": "Delhi",
                "district": "Central Delhi",
                "context": "traveling alone at night"
            },
            {
                "state": "Maharashtra",
                "district": "Mumbai",
                "context": None
            }
        ]
        
        for i, test in enumerate(test_cases, 1):
            print(f"\nTest Case {i}:")
            print(f"Location: {test['district']}, {test['state']}")
            if test['context']:
                print(f"Context: {test['context']}")
            print()
            
            explanation = chatbot.chat(
                test['state'],
                test['district'],
                test['context']
            )
            
            print(explanation)
            print("-" * 60)
        
        print("\n✓ All tests completed successfully!")
        print("\nTo run interactive mode:")
        print("  python -m chatbot.explainable_chatbot")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()