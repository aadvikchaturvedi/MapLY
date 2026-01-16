import unittest
from model import MapLYSentimentAnalyzer

class TestSentimentAnalyzer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Initializing model for tests...")
        cls.analyzer = MapLYSentimentAnalyzer()

    def test_positive_sentiment(self):
        text = "This area is well lit and I felt safe."
        result = self.analyzer.predict(text)
        self.assertEqual(result['label'], "POSITIVE")
        self.assertGreater(result['normalized_score'], 0.0)

    def test_negative_sentiment(self):
        text = "Very dangerous area, no street lights."
        result = self.analyzer.predict(text)
        self.assertEqual(result['label'], "NEGATIVE")
        self.assertLess(result['normalized_score'], 0.0)

    def test_neutral_ish_sentiment(self):
        # Depending on the model, this might swing either way, but score should be closer to 0 than extreme cases
        text = "It is a road."
        result = self.analyzer.predict(text)
        print(f"Neutral text check: '{text}' -> {result['normalized_score']}")
        # Not asserting strict bounds for neutral as SST-2 is binary, 
        # but checking it doesn't crash is good.

if __name__ == '__main__': 
    unittest.main()
