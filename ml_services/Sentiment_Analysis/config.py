# Configuration for MapLY Sentiment Analysis Model

MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"
MAX_LENGTH = 128

# Label mapping for SST-2
# 0: NEGATIVE, 1: POSITIVE
LABEL_MAP = {
    0: "NEGATIVE",
    1: "POSITIVE"
}

# Risk Adjustment Factor (Lambda)
# Used to adjust the safety risk score based on sentiment
# UpdatedRisk = OldRisk + LAMBDA * (NegativeSentimentScore)
LEARNING_RATE_LAMBDA = 0.05
