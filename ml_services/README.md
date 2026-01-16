# MapLY ML Services

Production-ready machine learning services for the MapLY women safety application, providing real-time sentiment analysis and location-based risk scoring.

## 🌟 Features

- **Sentiment Analysis**: Real-time safety sentiment analysis from user feedback using transformer models
- **Risk Score Engine**: Location-based safety risk scoring using machine learning
- **RESTful API**: Comprehensive API with versioning, CORS support, and OpenAPI documentation
- **Production Ready**: Docker containerization, logging, monitoring, and error handling
- **Fully Tested**: Comprehensive test suite with unit and integration tests
- **Easy Deployment**: Docker Compose for local development, ready for cloud deployment

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Configuration](#configuration)
- [Project Structure](#project-structure)

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Build and start the services
docker-compose up -d

# Check service health
curl http://localhost:8000/health

# View logs
docker-compose logs -f
```

### Local Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Start the server
./scripts/start.sh
# Or manually:
python -m uvicorn api.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Web Interface**: http://localhost:8000

## 📦 Installation

### Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)
- 4GB+ RAM (for ML models)

### Step-by-Step Installation

1. **Clone the repository**
   ```bash
   cd ml_services
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Prepare data** (if using risk score engine)
   ```bash
   # Place CSV files in ../data/ directory
   ```

6. **Start the service**
   ```bash
   ./scripts/start.sh
   ```

## 📚 API Documentation

### Endpoints Overview

#### System Endpoints

- `GET /health` - Health check with model status
- `GET /metrics` - Performance metrics

#### Sentiment Analysis

- `POST /api/v1/sentiment/predict` - Analyze single text
- `POST /api/v1/sentiment/batch` - Analyze multiple texts

#### Risk Scores

- `GET /api/v1/risk/scores` - Get all risk scores (optional state filter)
- `GET /api/v1/risk/location` - Get risk for specific location
- `GET /api/v1/risk/states` - List available states
- `GET /api/v1/risk/districts` - List districts for a state

### Example Usage

#### Sentiment Analysis

```bash
curl -X POST "http://localhost:8000/api/v1/sentiment/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "I felt very safe walking here at night"}'
```

Response:
```json
{
  "label": "POSITIVE",
  "confidence": 0.95,
  "normalized_score": 0.85,
  "probabilities": {
    "positive": 0.95,
    "negative": 0.05
  }
}
```

#### Batch Sentiment Analysis

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

#### Risk Scores

```bash
# Get all risk scores
curl "http://localhost:8000/api/v1/risk/scores"

# Filter by state
curl "http://localhost:8000/api/v1/risk/scores?state=Maharashtra"

# Get specific location
curl "http://localhost:8000/api/v1/risk/location?state=Maharashtra&district=Mumbai"
```

For complete API documentation, visit http://localhost:8000/docs after starting the server.

## 🛠️ Development

### Project Structure

```
ml_services/
├── api/                    # API layer
│   ├── main.py            # FastAPI application
│   ├── schemas.py         # Pydantic models
│   ├── middleware.py      # Custom middleware
│   └── templates/         # HTML templates
├── Sentiment_Analysis/    # Sentiment analysis module
│   ├── model.py          # Sentiment analyzer
│   └── config.py         # Model configuration
├── Risk_Score_Engine/     # Risk scoring module
│   └── model.py          # Risk score calculator
├── utils/                 # Utilities
│   ├── logger.py         # Logging configuration
│   └── metrics.py        # Performance metrics
├── tests/                 # Test suite
├── scripts/               # Utility scripts
├── config.py             # Global configuration
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker configuration
└── docker-compose.yml    # Docker Compose setup
```

### Running in Development Mode

```bash
# With auto-reload
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Or use the run script
python api/run.py
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## 🧪 Testing

### Run All Tests

```bash
# Using the test script
./scripts/test.sh

# Or manually
pytest tests/ -v --cov
```

### Run Specific Tests

```bash
# Test sentiment analysis
pytest tests/test_sentiment.py -v

# Test risk engine
pytest tests/test_risk_engine.py -v

# Test API
pytest api/test_api.py -v
```

### Coverage Report

```bash
pytest tests/ --cov --cov-report=html
# Open htmlcov/index.html in browser
```

## 🚢 Deployment

### Docker Deployment

```bash
# Build image
./scripts/build.sh

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f ml-api

# Stop services
docker-compose down
```

### Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions for:
- AWS (ECS, EC2, Lambda)
- Google Cloud Platform (Cloud Run, GKE)
- Azure (Container Instances, AKS)
- Kubernetes
- Traditional VPS

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# API Settings
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false

# CORS Settings
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Performance
MAX_WORKERS=4
REQUEST_TIMEOUT=30
```

### Configuration Options

All configuration is managed through `config.py` using Pydantic settings:

- **API Settings**: Host, port, reload
- **CORS**: Allowed origins, methods, headers
- **Paths**: Data directory, logs directory
- **Sentiment Analysis**: Model name, max length, batch size
- **Risk Engine**: Cache TTL
- **Logging**: Level, format
- **Performance**: Workers, timeout

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### Metrics

```bash
curl http://localhost:8000/metrics
```

Returns:
- Request counts by endpoint
- Error counts
- Average response times
- Average inference times

### Logs

Logs are written to:
- Console (stdout)
- `logs/` directory (if configured)

Log format can be JSON or text (configured via `LOG_FORMAT`).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## 📄 License

See LICENSE file for details.

## 🆘 Support

For issues and questions:
- Check the [API Documentation](http://localhost:8000/docs)
- Review [DEPLOYMENT.md](DEPLOYMENT.md)
- Open an issue on GitHub

## 🔗 Related Documentation

- [API Documentation](API_DOCS.md) - Detailed API reference
- [Deployment Guide](DEPLOYMENT.md) - Production deployment instructions
- [Architecture](docs/architecture.md) - System architecture overview
