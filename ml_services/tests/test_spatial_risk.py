"""
Spatial / Coordinate Risk Tests
================================

Lightweight tests for the coordinate- and route-based risk endpoints that
mock ``RiskScoreAPI`` to avoid loading heavy ML models (XGBoost, sentiment
pipelines, RAG, etc.).

The tests monkeypatch the global ``risk_engine`` inside ``api.main`` so the
endpoints can be exercised end-to-end through FastAPI's ``TestClient``
without any data files or trained models being present.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Make sure ml_services is importable when running this file directly.
_ML_SERVICES = Path(__file__).resolve().parent.parent
if str(_ML_SERVICES) not in sys.path:
    sys.path.insert(0, str(_ML_SERVICES))


# ---------------------------------------------------------------
# Mock RiskScoreAPI factory
# ---------------------------------------------------------------


class _MockRiskEngine:
    """Minimal stand-in for RiskScoreAPI used by the spatial endpoints.

    Only the surface that ``api.main`` actually touches is implemented:
    a truthy ``_risk_lookup`` and ``get_risk_for_coordinate``.
    """

    def __init__(self):
        # Non-empty so ``_risk_engine_ready()`` returns True.
        self._risk_lookup = {
            ("delhi", "new delhi"): {
                "state": "Delhi",
                "district": "New Delhi",
                "safety_score": 72.5,
                "risk_category": "Moderate Risk",
            },
            ("maharashtra", "mumbai"): {
                "state": "Maharashtra",
                "district": "Mumbai",
                "safety_score": 81.0,
                "risk_category": "Low Risk",
            },
            ("west bengal", "kolkata"): {
                "state": "West Bengal",
                "district": "Kolkata",
                "safety_score": 55.0,
                "risk_category": "High Risk",
            },
        }
        self._centroid_lookup = {
            "delhi": {"new delhi": [28.6139, 77.2090]},
            "maharashtra": {"mumbai": [19.0760, 72.8777]},
            "west bengal": {"kolkata": [22.5726, 88.3639]},
        }
        self._tree = None  # Not needed for mocked responses
        self.call_log = []  # Records every coordinate lookup for assertions

    def get_risk_for_coordinate(self, lat: float, lng: float) -> dict:
        lat_f = float(lat)
        lng_f = float(lng)
        self.call_log.append((lat_f, lng_f))

        # Deterministic synthetic mapping: just pick a record based on rough
        # geography so different inputs produce different outputs.
        if lng_f < 75.0:
            record = self._risk_lookup[("delhi", "new delhi")]
        elif lng_f < 80.0:
            record = self._risk_lookup[("maharashtra", "mumbai")]
        else:
            record = self._risk_lookup[("west bengal", "kolkata")]

        safety_score = float(record["safety_score"])
        risk_score = round(1.0 - (safety_score / 100.0), 4)
        return {
            "state": record["state"],
            "district": record["district"],
            "safety_score": safety_score,
            "risk_category": record["risk_category"],
            "risk_score": max(0.0, min(1.0, risk_score)),
        }


@pytest.fixture
def client_with_mock_risk_engine(monkeypatch):
    """Yield a TestClient with ``api.main.risk_engine`` patched out.

    The FastAPI app is imported lazily so the patched module attribute is in
    place before any route handler reads it.
    """
    from api import main as api_main

    mock_engine = _MockRiskEngine()
    api_main.risk_engine = mock_engine
    # ``_risk_engine_ready`` is a free function in main.py; rebind it so it
    # always reports ready while the patched engine is installed.
    api_main._risk_engine_ready = lambda: True

    with TestClient(api_main.app) as client:
        yield client, mock_engine

    # Clean up so other tests get a fresh module state.
    api_main.risk_engine = None
    api_main._risk_engine_ready = lambda: (
        api_main.risk_engine is not None
        and bool(getattr(api_main.risk_engine, "_risk_lookup", {}))
    )


# ---------------------------------------------------------------
# Tests
# ---------------------------------------------------------------


class TestGetRiskForCoordinateUnit:
    """Unit-level coverage for the mocked RiskScoreAPI."""

    def test_returns_expected_keys(self):
        engine = _MockRiskEngine()
        result = engine.get_risk_for_coordinate(19.0760, 72.8777)

        expected_keys = {
            "state",
            "district",
            "safety_score",
            "risk_category",
            "risk_score",
        }
        assert expected_keys.issubset(result.keys())

        # Sanity check on the numeric ranges.
        assert 0.0 <= result["safety_score"] <= 100.0
        assert 0.0 <= result["risk_score"] <= 1.0
        assert result["risk_category"] in {"Low Risk", "Moderate Risk", "High Risk"}

    def test_risk_score_is_one_minus_safety_over_100(self):
        engine = _MockRiskEngine()
        result = engine.get_risk_for_coordinate(22.5726, 88.3639)
        expected = round(1.0 - (result["safety_score"] / 100.0), 4)
        assert result["risk_score"] == expected


class TestCoordinateEndpoint:
    """HTTP-level tests for ``GET /api/v1/risk/coordinate``."""

    def test_coordinate_endpoint_returns_200(self, client_with_mock_risk_engine):
        client, _engine = client_with_mock_risk_engine
        response = client.get("/api/v1/risk/coordinate?lat=19.0760&lng=72.8777")

        assert response.status_code == 200
        body = response.json()
        for key in ("state", "district", "safety_score", "risk_category", "risk_score"):
            assert key in body, f"missing key {key!r} in response {body!r}"

    def test_coordinate_endpoint_rejects_invalid_lat(self, client_with_mock_risk_engine):
        client, _engine = client_with_mock_risk_engine
        # Latitude 91 is above the valid 90 limit.
        response = client.get("/api/v1/risk/coordinate?lat=91&lng=72.8777")
        assert response.status_code == 422

    def test_coordinate_endpoint_rejects_invalid_lng(self, client_with_mock_risk_engine):
        client, _engine = client_with_mock_risk_engine
        # Longitude 181 is outside the valid [-180, 180] range.
        response = client.get("/api/v1/risk/coordinate?lat=19.0760&lng=181")
        assert response.status_code == 422

    def test_coordinate_endpoint_rejects_missing_query(self, client_with_mock_risk_engine):
        client, _engine = client_with_mock_risk_engine
        response = client.get("/api/v1/risk/coordinate")
        assert response.status_code == 422


class TestRouteEndpoint:
    """HTTP-level tests for ``POST /api/v1/risk/route``."""

    def test_route_returns_one_segment_per_coordinate(self, client_with_mock_risk_engine):
        client, engine = client_with_mock_risk_engine

        coords = [
            [28.6139, 77.2090],
            [19.0760, 72.8777],
            [22.5726, 88.3639],
            [28.6139, 77.2090],
        ]
        payload = {"coordinates": coords}
        response = client.post("/api/v1/risk/route", json=payload)

        assert response.status_code == 200, response.text
        body = response.json()

        assert body["total"] == len(coords)
        assert len(body["segments"]) == len(coords)

        for segment, (lat, lng) in zip(body["segments"], coords):
            assert segment["lat"] == lat
            assert segment["lng"] == lng
            assert 0.0 <= segment["risk_score"] <= 1.0
            assert segment["risk_category"] in {
                "Low Risk",
                "Moderate Risk",
                "High Risk",
                "Unknown",
            }

        # The underlying engine should have been called once per coordinate.
        assert len(engine.call_log) == len(coords)

    def test_route_rejects_out_of_range_coordinate(self, client_with_mock_risk_engine):
        client, _engine = client_with_mock_risk_engine
        payload = {"coordinates": [[19.0760, 72.8777], [999.0, 72.8777]]}
        response = client.post("/api/v1/risk/route", json=payload)
        assert response.status_code == 422

    def test_route_rejects_empty_coordinates(self, client_with_mock_risk_engine):
        client, _engine = client_with_mock_risk_engine
        response = client.post("/api/v1/risk/route", json={"coordinates": []})
        assert response.status_code == 422

    def test_route_rejects_wrong_shape(self, client_with_mock_risk_engine):
        client, _engine = client_with_mock_risk_engine
        # Each coordinate must be a length-2 list, not a single number.
        response = client.post(
            "/api/v1/risk/route",
            json={"coordinates": [[19.0760, 72.8777], [22.5726]]},
        )
        assert response.status_code == 422
