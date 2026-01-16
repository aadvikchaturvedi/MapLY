#!/usr/bin/env python3
"""
Test Pinecone RAG Chatbot
==========================

Tests the Pinecone-enhanced chatbot.
"""

import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from chatbot.pinecone_rag_chatbot import PineconeRAGChatbot

def main():
    print("\n" + "🧪 "*20)
    print("  Pinecone RAG Chatbot Testing")
    print("🧪 "*20)
    
    try:
        # Initialize chatbot
        print("\nInitializing Pinecone chatbot...")
        chatbot = PineconeRAGChatbot(use_pinecone=True)
        print("✓ Ready!\n")
        
        # Test 1: Ask a question (uses Pinecone search)
        print("-" * 60)
        question = "How does the risk score model work?"
        print(f"Test 1: Asking question: '{question}'")
        answer = chatbot.ask_question(question)
        print("\nAnswer:")
        print(answer)
        
        # Test 2: Location query with technical explanation
        print("-" * 60)
        print("Test 2: Location query (Mumbai) with technical details")
        explanation = chatbot.chat(
            "Maharashtra", 
            "Mumbai", 
            explain_technical=True
        )
        print("\nExplanation:")
        print(explanation)
        
        print("\n" + "="*60)
        print("✓ Pinecone integration tests passed!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
