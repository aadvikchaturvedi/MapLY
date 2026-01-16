"""
Test Configuration and Fixtures
================================

Pytest configuration and shared fixtures for testing.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add ml_services to path
ml_services_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ml_services_dir))


@pytest.fixture(scope="session")
def test_client():
    """Create a test client for the API."""
    from api.main import app
    return TestClient(app)


@pytest.fixture(scope="session")
def sample_texts():
    """Sample texts for testing sentiment analysis."""
    return {
        "positive": [
            "I felt very safe walking here at night, good lighting and people around",
            "This area is well-maintained and secure",
            "Great neighborhood with friendly people"
        ],
        "negative": [
            "It was too dark and scary, I saw some shady people",
            "Very unsafe area, avoid at night",
            "Poor lighting and deserted streets"
        ],
        "neutral": [
            "The road was okay, nothing special",
            "Average area",
            "It's fine"
        ]
    }


@pytest.fixture(scope="session")
def sample_locations():
    """Sample locations for testing risk scores."""
    return [
        {"state": "Maharashtra", "district": "Mumbai"},
        {"state": "Delhi", "district": "Central Delhi"},
        {"state": "Karnataka", "district": "Bangalore"},
    ]
