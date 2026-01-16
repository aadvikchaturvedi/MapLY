import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
try:
    from . import config
except ImportError:
    import config

class MapLYSentimentAnalyzer:
    def __init__(self):
        """
        Initialize the Sentiment Analyzer with a pre-trained model.
        """
        print(f"Loading Sentiment Analysis Model: {config.MODEL_NAME}...")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(config.MODEL_NAME)
        self.model = AutoModelForSequenceClassification.from_pretrained(config.MODEL_NAME)
        self.model.to(self.device)
        self.model.eval()
        print("Model loaded successfully.")

    def predict(self, text):
        """
        Predict sentiment score for a given text.
        
        Args:
            text (str): Input feedback text.
            
        Returns:
            dict: Dictionary containing:
                - 'label': "POSITIVE" or "NEGATIVE"
                - 'score': Confidence score of the label (0 to 1)
                - 'normalized_score': Sentiment score mapped to [-1, 1] range.
                                      Close to -1 is very negative (unsafe),
                                      Close to +1 is very positive (safe).
        """
        inputs = self.tokenizer(
            text, 
            padding=True, 
            truncation=True, 
            max_length=config.MAX_LENGTH, 
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=1)
            
        # Get predicted label and probability
        pred_label_idx = torch.argmax(probs, dim=1).item()
        confidence = probs[0][pred_label_idx].item()
        
        label_str = config.LABEL_MAP.get(pred_label_idx, "UNKNOWN")
        
        # Calculate normalized score [-1, 1]
        # SST-2: 0=Negative, 1=Positive
        # If Positive: Score is simply the probability of class 1 (range 0.5 to 1.0 ideally)
        # If Negative: Score should be negative. We can treat prob(class 1) as the continuous score.
        # Let's use prob(POSITIVE) - prob(NEGATIVE) to get a range of [-1, 1]
        
        prob_neg = probs[0][0].item()
        prob_pos = probs[0][1].item()
        
        normalized_score = prob_pos - prob_neg
        
        return {
            "label": label_str,
            "confidence": confidence,
            "normalized_score": normalized_score,
            "probabilities": {
                "negative": prob_neg,
                "positive": prob_pos
            }
        }

if __name__ == "__main__":
    # Quick sanity check
    analyzer = MapLYSentimentAnalyzer()
    test_texts = [
        "I felt very safe on this route, good lighting.",
        "It was too dark and scary, I saw some shady people.",
        "The road was okay, nothing special."
    ]
    
    for text in test_texts:
        result = analyzer.predict(text)
        print(f"Text: {text}")
        print(f"Result: {result}\n")
