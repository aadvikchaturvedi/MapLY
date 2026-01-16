# MapLY ML Services - Quick Reference

## 🚀 Quick Commands

### Start the Service

\`\`\`bash
# Local development
cd /Users/aadvikchaturvedi/Desktop/MapLY/ml_services
source .venv/bin/activate
./scripts/start.sh

# Docker
docker-compose up -d

# Production
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
\`\`\`

### Test the Service

\`\`\`bash
# Run all tests
./scripts/test.sh

# Specific tests
pytest tests/test_sentiment.py -v
pytest tests/test_risk_engine.py -v
pytest api/test_api.py -v

# With coverage
pytest tests/ --cov --cov-report=html
\`\`\`

### Build Docker Image

\`\`\`bash
./scripts/build.sh
# Or manually:
docker build -t maply-ml-services:latest .
\`\`\`

## 📡 API Quick Reference

### Base URL
\`\`\`
http://localhost:8000
\`\`\`

### Key Endpoints

**Health Check:**
\`\`\`bash
curl http://localhost:8000/health
\`\`\`

**Sentiment Analysis:**
\`\`\`bash
curl -X POST http://localhost:8000/api/v1/sentiment/predict \\
  -H "Content-Type: application/json" \\
  -d '{"text": "I felt very safe here"}'
\`\`\`

**Batch Sentiment:**
\`\`\`bash
curl -X POST http://localhost:8000/api/v1/sentiment/batch \\
  -H "Content-Type: application/json" \\
  -d '{"texts": ["Safe area", "Unsafe area"]}'
\`\`\`

**Risk Scores:**
\`\`\`bash
curl http://localhost:8000/api/v1/risk/scores
curl http://localhost:8000/api/v1/risk/scores?state=Maharashtra
curl "http://localhost:8000/api/v1/risk/location?state=Maharashtra&district=Mumbai"
\`\`\`

**Metrics:**
\`\`\`bash
curl http://localhost:8000/metrics
\`\`\`

## 🔧 Configuration

### Environment Variables

\`\`\`bash
# Copy example
cp .env.example .env

# Edit configuration
nano .env
\`\`\`

### Key Settings

\`\`\`env
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
LOG_LEVEL=INFO
LOG_FORMAT=json
\`\`\`

## 📚 Documentation

- **Main Docs**: [README.md](README.md)
- **API Reference**: [API_DOCS.md](API_DOCS.md)
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Interactive**: http://localhost:8000/docs

## 🐛 Troubleshooting

### Service won't start
\`\`\`bash
# Check logs
docker-compose logs -f

# Check health
curl http://localhost:8000/health
\`\`\`

### Model not loading
- Check memory allocation (need 4GB+ RAM)
- Verify model files are accessible
- Check logs for detailed errors

### CORS errors
- Update `CORS_ORIGINS` in `.env`
- Restart service after changes

### Port already in use
\`\`\`bash
# Change port in .env
API_PORT=8001

# Or kill existing process
lsof -ti:8000 | xargs kill -9
\`\`\`

## 📊 File Structure

\`\`\`
ml_services/
├── api/              # API layer
├── Sentiment_Analysis/  # Sentiment model
├── Risk_Score_Engine/   # Risk scoring
├── utils/            # Utilities
├── tests/            # Test suite
├── scripts/          # Helper scripts
├── config.py         # Configuration
├── requirements.txt  # Dependencies
├── Dockerfile        # Docker config
└── docker-compose.yml  # Docker Compose
\`\`\`

## 🎯 Common Tasks

### Add new endpoint
1. Define schema in `api/schemas.py`
2. Add endpoint in `api/main.py`
3. Add tests in `api/test_api.py`
4. Update `API_DOCS.md`

### Update dependencies
\`\`\`bash
pip install <package>
pip freeze > requirements.txt
\`\`\`

### Deploy to production
1. Review [DEPLOYMENT.md](DEPLOYMENT.md)
2. Choose platform (Docker/AWS/GCP/Azure)
3. Configure environment
4. Deploy using provided scripts

## 🔗 Useful Links

- Interactive API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Web Interface: http://localhost:8000
- Health Check: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics
