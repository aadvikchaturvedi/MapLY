# MapLY ML Services - API Documentation

Complete API reference for the MapLY ML Services.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. For production deployments, consider adding API key authentication or OAuth2.

## Response Format

All responses are in JSON format with appropriate HTTP status codes.

### Success Response

```json
{
  "data": {},
  "status": "success"
}
```

### Error Response

```json
{
  "error": "ErrorType",
  "message": "Human-readable error message",
  "detail": "Additional error details (only in debug mode)"
}
```

## HTTP Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Model not loaded

---

## System Endpoints

### Health Check

Check the health status of the API and all loaded models.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "models": {
    "sentiment_analyzer": "loaded",
    "risk_engine": "loaded",
    "risk_data": "1234 regions"
  }
}
```

### Metrics

Get performance metrics for the API.

**Endpoint:** `GET /metrics`

**Response:**
```json
{
  "requests": {
    "/api/v1/sentiment/predict": 150,
    "/api/v1/risk/scores": 75
  },
  "errors": {
    "/api/v1/sentiment/predict": 2
  },
  "avg_response_times": {
    "/api/v1/sentiment/predict": 0.234,
    "/api/v1/risk/scores": 0.012
  },
  "avg_inference_times": {
    "sentiment_analysis": 0.189
  }
}
```

---

## Sentiment Analysis Endpoints

### Predict Sentiment (Single)

Analyze the sentiment of a single text.

**Endpoint:** `POST /api/v1/sentiment/predict`

**Request Body:**
```json
{
  "text": "I felt very safe walking here at night"
}
```

**Parameters:**
- `text` (string, required): Text to analyze (1-1000 characters)

**Response:**
```json
{
  "label": "POSITIVE",
  "confidence": 0.9523,
  "normalized_score": 0.8546,
  "probabilities": {
    "positive": 0.9523,
    "negative": 0.0477
  }
}
```

**Response Fields:**
- `label`: Sentiment label (`POSITIVE` or `NEGATIVE`)
- `confidence`: Confidence score (0-1)
- `normalized_score`: Normalized sentiment score (-1 to 1)
  - Close to 1: Very positive (safe)
  - Close to -1: Very negative (unsafe)
  - Close to 0: Neutral
- `probabilities`: Class probabilities

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/sentiment/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "I felt very safe walking here at night"}'
```

### Predict Sentiment (Batch)

Analyze the sentiment of multiple texts in a single request.

**Endpoint:** `POST /api/v1/sentiment/batch`

**Request Body:**
```json
{
  "texts": [
    "Very safe area with good lighting",
    "Too dark and scary",
    "Normal neighborhood"
  ]
}
```

**Parameters:**
- `texts` (array of strings, required): List of texts to analyze (1-100 texts)

**Response:**
```json
{
  "results": [
    {
      "label": "POSITIVE",
      "confidence": 0.95,
      "normalized_score": 0.85,
      "probabilities": {"positive": 0.95, "negative": 0.05}
    },
    {
      "label": "NEGATIVE",
      "confidence": 0.89,
      "normalized_score": -0.72,
      "probabilities": {"positive": 0.11, "negative": 0.89}
    },
    {
      "label": "POSITIVE",
      "confidence": 0.67,
      "normalized_score": 0.34,
      "probabilities": {"positive": 0.67, "negative": 0.33}
    }
  ],
  "total_processed": 3
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/sentiment/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Very safe area",
      "Too dark and scary",
      "Normal neighborhood"
    ]
  }'
```

---

## Risk Score Endpoints

### Get All Risk Scores

Get risk scores for all regions, optionally filtered by state.

**Endpoint:** `GET /api/v1/risk/scores`

**Query Parameters:**
- `state` (string, optional): Filter by state name

**Response:**
```json
{
  "total": 2,
  "data": [
    {
      "state": "Maharashtra",
      "district": "Mumbai",
      "safety_score": 78.45,
      "risk_category": "Moderate Risk"
    },
    {
      "state": "Maharashtra",
      "district": "Pune",
      "safety_score": 85.23,
      "risk_category": "Low Risk"
    }
  ]
}
```

**Risk Categories:**
- `Low Risk`: Safety score ≥ 80
- `Moderate Risk`: Safety score 60-79
- `High Risk`: Safety score < 60

**Examples:**
```bash
# Get all risk scores
curl "http://localhost:8000/api/v1/risk/scores"

# Filter by state
curl "http://localhost:8000/api/v1/risk/scores?state=Maharashtra"
```

### Get Location Risk

Get the risk score for a specific location.

**Endpoint:** `GET /api/v1/risk/location`

**Query Parameters:**
- `state` (string, required): State name
- `district` (string, required): District name

**Response:**
```json
{
  "state": "Maharashtra",
  "district": "Mumbai",
  "safety_score": 78.45,
  "risk_category": "Moderate Risk"
}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/risk/location?state=Maharashtra&district=Mumbai"
```

### Get Available States

Get a list of all available states in the dataset.

**Endpoint:** `GET /api/v1/risk/states`

**Response:**
```json
{
  "total": 3,
  "states": [
    "Delhi",
    "Karnataka",
    "Maharashtra"
  ]
}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/risk/states"
```

### Get Districts by State

Get a list of all districts for a specific state.

**Endpoint:** `GET /api/v1/risk/districts`

**Query Parameters:**
- `state` (string, required): State name

**Response:**
```json
{
  "state": "Maharashtra",
  "total": 2,
  "districts": [
    "Mumbai",
    "Pune"
  ]
}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/risk/districts?state=Maharashtra"
```

---

## Legacy Endpoints

These endpoints are maintained for backward compatibility but are deprecated. Use the `/api/v1/` versions instead.

- `POST /predict/sentiment` → Use `/api/v1/sentiment/predict`
- `GET /risk/scores` → Use `/api/v1/risk/scores`
- `GET /risk/location` → Use `/api/v1/risk/location`

---

## Error Handling

### Validation Errors (422)

```json
{
  "detail": [
    {
      "loc": ["body", "text"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Not Found (404)

```json
{
  "error": "NotFound",
  "message": "Location not found: InvalidDistrict, InvalidState"
}
```

### Service Unavailable (503)

```json
{
  "error": "ServiceUnavailable",
  "message": "Sentiment model not initialized. Please check server logs."
}
```

---

## Rate Limiting

Currently, there is no rate limiting. For production deployments, consider implementing rate limiting based on your requirements.

---

## CORS

The API supports CORS for the following origins (configurable via environment variables):
- `http://localhost:3000`
- `http://localhost:8080`
- Additional origins can be configured in `.env`

---

## Interactive Documentation

The API provides interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Explore all endpoints
- View request/response schemas
- Test endpoints directly from the browser
- Download OpenAPI specification

---

## Client Libraries

### Python

```python
import requests

# Sentiment analysis
response = requests.post(
    "http://localhost:8000/api/v1/sentiment/predict",
    json={"text": "I felt very safe here"}
)
result = response.json()
print(f"Sentiment: {result['label']}, Score: {result['normalized_score']}")

# Risk scores
response = requests.get(
    "http://localhost:8000/api/v1/risk/location",
    params={"state": "Maharashtra", "district": "Mumbai"}
)
risk = response.json()
print(f"Safety Score: {risk['safety_score']}, Category: {risk['risk_category']}")
```

### JavaScript

```javascript
// Sentiment analysis
const response = await fetch('http://localhost:8000/api/v1/sentiment/predict', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({text: 'I felt very safe here'})
});
const result = await response.json();
console.log(`Sentiment: ${result.label}, Score: ${result.normalized_score}`);

// Risk scores
const riskResponse = await fetch(
  'http://localhost:8000/api/v1/risk/location?state=Maharashtra&district=Mumbai'
);
const risk = await riskResponse.json();
console.log(`Safety Score: ${risk.safety_score}, Category: ${risk.risk_category}`);
```

### cURL

See examples throughout this documentation.

---

## Webhooks

Webhooks are not currently supported. Consider implementing them if you need real-time notifications for specific events.

---

## Versioning

The API uses URL-based versioning (`/api/v1/`). Future versions will be released as `/api/v2/`, etc., while maintaining backward compatibility with previous versions.

---

## Support

For API support:
- Check the interactive documentation at `/docs`
- Review this documentation
- Check server logs for detailed error messages
- Open an issue on GitHub
