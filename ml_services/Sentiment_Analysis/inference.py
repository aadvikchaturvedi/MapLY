import sys
import argparse
from model import MapLYSentimentAnalyzer

def main():
    parser = argparse.ArgumentParser(description="MapLY Sentiment Analysis Inference")
    parser.add_argument("--text", type=str, help="Text to analyze", required=False)
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    analyzer = MapLYSentimentAnalyzer()
    
    if args.text:
        result = analyzer.predict(args.text)
        print(f"Input: {args.text}")
        print(f"Sentiment: {result['label']}")
        print(f"Score: {result['normalized_score']:.4f}")
        
    elif args.interactive:
        print("Interactive Sentiment Analysis (Type 'exit' to quit)")
        while True:
            text = input("\nEnter text: ")
            if text.lower() == 'exit':
                break
            result = analyzer.predict(text)
            print(f"Sentiment: {result['label']}")
            print(f"Score: {result['normalized_score']:.4f}")
            print(f"Detailed: {result}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
