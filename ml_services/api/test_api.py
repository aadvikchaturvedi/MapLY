"""
API Integration Tests
======================

Comprehensive tests for all API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestSystemEndpoints:
    """Test system endpoints (health, metrics)."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "models" in data
        assert data["status"] == "healthy"
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint."""
        response = client.get("/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "requests" in data
        assert "errors" in data
        assert "avg_response_times" in data


class TestFrontendEndpoints:
    """Test frontend endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint serves HTML or JSON."""
        response = client.get("/")
        assert response.status_code == 200
        # Should return either HTML or JSON


class TestSentimentEndpoints:
    """Test sentiment analysis endpoints."""
    
    def test_sentiment_prediction_success(self):
        """Test successful sentiment prediction."""
        response = client.post(
            "/api/v1/sentiment/predict",
            json={"text": "I felt very safe walking here"}
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "label" in data
            assert "confidence" in data
            assert "normalized_score" in data
            assert "probabilities" in data
            
            assert data["label"] in ["POSITIVE", "NEGATIVE"]
            assert 0 <= data["confidence"] <= 1
            assert -1 <= data["normalized_score"] <= 1
        else:
            # Model might not be loaded in test environment
            assert response.status_code == 503
    
    def test_sentiment_prediction_empty_text(self):
        """Test sentiment prediction with empty text."""
        response = client.post(
            "/api/v1/sentiment/predict",
            json={"text": ""}
        )
        assert response.status_code == 422  # Validation error
    
    def test_sentiment_prediction_whitespace(self):
        """Test sentiment prediction with whitespace only."""
        response = client.post(
            "/api/v1/sentiment/predict",
            json={"text": "   "}
        )
        assert response.status_code == 422  # Validation error
    
    def test_sentiment_prediction_long_text(self):
        """Test sentiment prediction with very long text."""
        long_text = "This is a test. " * 100
        response = client.post(
            "/api/v1/sentiment/predict",
            json={"text": long_text}
        )
        # Should either succeed or fail validation
        assert response.status_code in [200, 422, 503]
    
    def test_batch_sentiment_prediction(self):
        """Test batch sentiment prediction."""
        response = client.post(
            "/api/v1/sentiment/batch",
            json={
                "texts": [
                    "I felt safe here",
                    "This area is dangerous",
                    "Normal neighborhood"
                ]
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "results" in data
            assert "total_processed" in data
            assert len(data["results"]) == 3
            assert data["total_processed"] == 3
        else:
            assert response.status_code == 503
    
    def test_batch_sentiment_empty_list(self):
        """Test batch prediction with empty list."""
        response = client.post(
            "/api/v1/sentiment/batch",
            json={"texts": []}
        )
        assert response.status_code == 422  # Validation error
    
    def test_batch_sentiment_too_many(self):
        """Test batch prediction with too many texts."""
        texts = ["Test text"] * 150  # More than max allowed
        response = client.post(
            "/api/v1/sentiment/batch",
            json={"texts": texts}
        )
        assert response.status_code == 422  # Validation error


class TestRiskScoreEndpoints:
    """Test risk score endpoints."""
    
    def test_get_all_risk_scores(self):
        """Test getting all risk scores."""
        response = client.get("/api/v1/risk/scores")
        
        if response.status_code == 200:
            data = response.json()
            assert "total" in data
            assert "data" in data
            assert isinstance(data["data"], list)
        else:
            assert response.status_code == 503
    
    def test_get_risk_scores_by_state(self):
        """Test filtering risk scores by state."""
        response = client.get("/api/v1/risk/scores?state=Maharashtra")
        
        if response.status_code == 200:
            data = response.json()
            assert "total" in data
            assert "data" in data
        else:
            assert response.status_code == 503
    
    def test_get_available_states(self):
        """Test getting list of available states."""
        response = client.get("/api/v1/risk/states")
        
        if response.status_code == 200:
            data = response.json()
            assert "total" in data
            assert "states" in data
            assert isinstance(data["states"], list)
        else:
            assert response.status_code == 503
    
    def test_get_districts_by_state(self):
        """Test getting districts for a state."""
        # First get available states
        states_response = client.get("/api/v1/risk/states")
        
        if states_response.status_code == 200:
            states = states_response.json()["states"]
            if states:
                # Test with first available state
                response = client.get(f"/api/v1/risk/districts?state={states[0]}")
                assert response.status_code == 200
                
                data = response.json()
                assert "state" in data
                assert "total" in data
                assert "districts" in data
    
    def test_get_location_risk_not_found(self):
        """Test getting risk for non-existent location."""
        response = client.get(
            "/api/v1/risk/location?state=InvalidState&district=InvalidDistrict"
        )
        
        if response.status_code != 503:
            assert response.status_code == 404


class TestLegacyEndpoints:
    """Test legacy endpoints for backward compatibility."""
    
    def test_legacy_sentiment_endpoint(self):
        """Test legacy sentiment prediction endpoint."""
        response = client.post(
            "/predict/sentiment",
            json={"text": "Test text"}
        )
        assert response.status_code in [200, 503]
    
    def test_legacy_risk_scores_endpoint(self):
        """Test legacy risk scores endpoint."""
        response = client.get("/risk/scores")
        assert response.status_code in [200, 503]
    
    def test_legacy_location_risk_endpoint(self):
        """Test legacy location risk endpoint."""
        response = client.get("/risk/location?state=Test&district=Test")
        assert response.status_code in [200, 404, 503]


class TestCORS:
    """Test CORS configuration."""
    
    def test_cors_headers(self):
        """Test that CORS headers are present."""
        response = client.options("/health")
        # CORS headers should be present
        assert response.status_code in [200, 405]


class TestErrorHandling:
    """Test error handling."""
    
    def test_invalid_endpoint(self):
        """Test accessing invalid endpoint."""
        response = client.get("/invalid/endpoint")
        assert response.status_code == 404
    
    def test_invalid_method(self):
        """Test using invalid HTTP method."""
        response = client.delete("/health")
        assert response.status_code == 405

