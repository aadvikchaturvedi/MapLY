# MapLY

Traditional GPS systems optimize only for shortest distance or time, ignoring personal safety risks. MapLY solves this by computing dynamic, data-driven safety scores for every route segment using crime statistics, environmental context, real-time sentiment analysis, and community feedback.

## Architecture

```
MapLY/
├── maply/          # Next.js 16 frontend (TypeScript, Tailwind v4, Leaflet)
├── ml_services/    # FastAPI backend (Python, Transformers, XGBoost, Pinecone)
├── data/           # Crime statistics CSVs (mounted as Docker volume)
└── .github/        # CI pipeline
```

### Frontend (`maply/`)

- **Route Planner** — Enter start/destination, get a safety-optimized route with per-segment risk scoring
- **SOS Alert** — WebSocket + HTTP fallback emergency alerting with GPS location sharing
- **Live Map / Heatmap** — Visualize safety data overlays
- **Community Reports** — User-submitted safety experiences
- **Resources** — Emergency contacts, safety tips, support groups

### Backend (`ml_services/`)

- **Risk Score Engine** — Location-based safety scoring using XGBoost trained on 11,500+ Indian police districts
- **Sentiment Analysis** — Real-time sentiment from user feedback via DistilBERT
- **Chatbot** — Gemini-powered safety assistant with RAG over a Pinecone vector store
- **WebSocket SOS** — Persistent connection for low-latency emergency alerts

## Quick Start

### Prerequisites

- Node.js 20+, Python 3.11+, Docker (optional)

### 1. Backend

```bash
cd ml_services
cp .env.example .env          # Edit with your API keys
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

API: http://localhost:8000 | Docs: http://localhost:8000/docs

### 2. Frontend

```bash
cd maply
npm install
npm run dev
```

App: http://localhost:3000

### Docker (backend only)

```bash
cd ml_services
docker-compose up -d
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_FASTAPI_URL` | `http://localhost:8000` | Backend URL (frontend) |
| `GEMINI_API_KEY` | — | Google Gemini API key (chatbot) |
| `PINECONE_API_KEY` | — | Pinecone vector DB key (RAG) |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed frontend origins |

## Scripts

| Command | Directory | Description |
|---|---|---|
| `npm run dev` | `maply/` | Start Next.js dev server |
| `npm run build` | `maply/` | Production build |
| `npm run typecheck` | `maply/` | TypeScript type checking |
| `npm run lint` | `maply/` | ESLint |
| `pytest tests/ -v --cov` | `ml_services/` | Run backend tests |
| `flake8 .` | `ml_services/` | Python linting |

## Tech Stack

- **Frontend:** Next.js 16, React 19, TypeScript, Tailwind CSS v4, Framer Motion, Leaflet, Zustand
- **Backend:** FastAPI, Pydantic, Transformers (DistilBERT), XGBoost, scikit-learn, Pinecone, Google GenAI
- **Infrastructure:** Docker, Docker Compose, Uvicorn

## API Overview

| Endpoint | Description |
|---|---|
| `GET /api/v1/risk/scores` | All risk scores (optional `?state=` filter) |
| `GET /api/v1/risk/location` | Risk for a specific state + district |
| `POST /api/v1/sentiment/predict` | Analyze safety sentiment of text |
| `POST /api/v1/chatbot/query` | Ask the safety chatbot |
| `WS /ws/sos` | WebSocket SOS alert |
| `GET /health` | Health check |

## License

See [LICENSE](LICENSE).
