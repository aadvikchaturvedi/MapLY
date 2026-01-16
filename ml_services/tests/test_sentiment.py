"""
Sentiment Analysis Module Tests
================================

Unit tests for the sentiment analysis model.
"""

import pytest
from Sentiment_Analysis.model import MapLYSentimentAnalyzer
from Sentiment_Analysis.config import LABEL_MAP


class TestSentimentAnalyzer:
    """Test suite for MapLYSentimentAnalyzer."""
    
    @pytest.fixture(scope="class")
    def analyzer(self):
        """Create a sentiment analyzer instance."""
        return MapLYSentimentAnalyzer()
    
    def test_model_initialization(self, analyzer):
        """Test that the model initializes correctly."""
        assert analyzer is not None
        assert analyzer.model is not None
        assert analyzer.tokenizer is not None
    
    def test_positive_sentiment(self, analyzer):
        """Test prediction on positive text."""
        text = "I felt very safe walking here at night, good lighting"
        result = analyzer.predict(text)
        
        assert "label" in result
        assert "confidence" in result
        assert "normalized_score" in result
        assert "probabilities" in result
        
        assert result["label"] in ["POSITIVE", "NEGATIVE"]
        assert 0 <= result["confidence"] <= 1
        assert -1 <= result["normalized_score"] <= 1
    
    def test_negative_sentiment(self, analyzer):
        """Test prediction on negative text."""
        text = "It was too dark and scary, very unsafe"
        result = analyzer.predict(text)
        
        assert result["label"] in ["POSITIVE", "NEGATIVE"]
        assert 0 <= result["confidence"] <= 1
        assert -1 <= result["normalized_score"] <= 1
    
    def test_batch_predictions(self, analyzer, sample_texts):
        """Test multiple predictions."""
        all_texts = (
            sample_texts["positive"] + 
            sample_texts["negative"] + 
            sample_texts["neutral"]
        )
        
        results = [analyzer.predict(text) for text in all_texts]
        
        assert len(results) == len(all_texts)
        for result in results:
            assert "label" in result
            assert "confidence" in result
    
    def test_empty_text_handling(self, analyzer):
        """Test handling of edge cases."""
        # Very short text
        result = analyzer.predict("Safe")
        assert result is not None
        
        # Single word
        result = analyzer.predict("Dangerous")
        assert result is not None
    
    def test_probability_sum(self, analyzer):
        """Test that probabilities sum to approximately 1."""
        text = "This is a test"
        result = analyzer.predict(text)
        
        prob_sum = (
            result["probabilities"]["positive"] + 
            result["probabilities"]["negative"]
        )
        
        assert abs(prob_sum - 1.0) < 0.01  # Allow small floating point error
    
    def test_normalized_score_range(self, analyzer, sample_texts):
        """Test that normalized scores are in valid range."""
        for category, texts in sample_texts.items():
            for text in texts:
                result = analyzer.predict(text)
                assert -1 <= result["normalized_score"] <= 1
