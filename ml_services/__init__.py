"""
MapLY ML Services
=================

Production-ready machine learning services for MapLY women safety application.

Modules:
    - Sentiment_Analysis: Real-time safety sentiment analysis from user feedback
    - Risk_Score_Engine: Location-based safety risk scoring
    - api: RESTful API endpoints for frontend/backend integration
"""

__version__ = "1.0.0"
__author__ = "MapLY Team"

from .Sentiment_Analysis.model import MapLYSentimentAnalyzer
from .Risk_Score_Engine.model import RiskScoreAPI

__all__ = ["MapLYSentimentAnalyzer", "RiskScoreAPI"]
