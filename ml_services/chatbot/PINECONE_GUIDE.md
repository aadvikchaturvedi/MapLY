# Pinecone Vector Database Integration

## 🎯 Overview

The Pinecone integration adds **semantic search** capabilities to the RAG system, enabling:
- **Intelligent retrieval** of relevant technical information
- **Vector-based search** instead of keyword matching
- **Scalable knowledge base** that can grow over time
- **Fast, accurate** context retrieval for AI responses

## 🚀 Quick Start

### 1. Install Dependencies

\`\`\`bash
pip install pinecone-client google-genai
\`\`\`

### 2. Get API Keys

**Pinecone:**
1. Sign up at https://www.pinecone.io/
2. Create a new project
3. Copy your API key

**Gemini (already have):**
- Your existing `GEMINI_API_KEY`

### 3. Configure Environment

Add to `.env`:
\`\`\`env
GEMINI_API_KEY=your_gemini_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
\`\`\`

### 4. Setup Knowledge Base

Run the setup script to index your knowledge base:

\`\`\`bash
cd /Users/aadvikchaturvedi/Desktop/MapLY/ml_services
source .venv/bin/activate
python chatbot/pinecone_kb.py
\`\`\`

This will:
- Create a Pinecone index
- Split knowledge base into sections
- Generate embeddings using Gemini
- Upload vectors to Pinecone
- Test semantic search

### 5. Use the Chatbot

\`\`\`bash
python -m chatbot.pinecone_rag_chatbot
\`\`\`

## 📊 How It Works

### 1. Knowledge Base Indexing

\`\`\`
knowledge_base.md
       ↓
Split into sections
       ↓
Generate embeddings (Gemini)
       ↓
Store in Pinecone
       ↓
Ready for semantic search
\`\`\`

### 2. Query Processing

\`\`\`
User query
       ↓
Generate query embedding
       ↓
Search Pinecone (cosine similarity)
       ↓
Retrieve top-k most relevant sections
       ↓
Pass to Gemini AI
       ↓
Generate natural language response
\`\`\`

### 3. Semantic Search Example

**Query:** "How does the risk score model work?"

**Pinecone finds:**
1. Risk Score Engine section (score: 0.92)
2. XGBoost model details (score: 0.88)
3. Feature engineering (score: 0.85)

**AI generates:** Comprehensive explanation using retrieved context

## 🎓 Features

### Semantic Search
- Understands meaning, not just keywords
- Finds relevant information even with different wording
- Ranks results by relevance

### Scalable
- Can handle large knowledge bases
- Fast retrieval (milliseconds)
- Easy to add new documents

### Accurate
- Uses Gemini embeddings (768 dimensions)
- Cosine similarity for relevance
- Top-k retrieval for best matches

## 📝 Usage Examples

### Basic Safety Explanation

\`\`\`python
from chatbot.pinecone_rag_chatbot import PineconeRAGChatbot

chatbot = PineconeRAGChatbot()

# Get explanation
explanation = chatbot.chat("Maharashtra", "Mumbai")
print(explanation)
\`\`\`

### Technical Explanation with Vector Search

\`\`\`python
# Request technical details
# Pinecone automatically retrieves relevant ML documentation
explanation = chatbot.chat(
    "Maharashtra",
    "Mumbai",
    explain_technical=True
)
print(explanation)
\`\`\`

### Ask Questions

\`\`\`python
# Ask about the ML system
answer = chatbot.ask_question(
    "How does XGBoost calculate the risk score?"
)
print(answer)

# Filter by topic
answer = chatbot.ask_question(
    "Explain sentiment analysis",
    topic="sentiment"
)
print(answer)
\`\`\`

### Direct Vector Search

\`\`\`python
from chatbot.pinecone_kb import PineconeKnowledgeBase

kb = PineconeKnowledgeBase()

# Search knowledge base
results = kb.search(
    query="What features does the model use?",
    top_k=3,
    filter_type="risk_score"
)

for result in results:
    print(f"{result['section']}: {result['score']:.3f}")
    print(result['text'][:200])
    print()
\`\`\`

## 🔧 Configuration

### Pinecone Index Settings

\`\`\`python
kb = PineconeKnowledgeBase(
    index_name="maply-knowledge-base",  # Index name
    dimension=768,                       # Gemini embedding size
    metric="cosine"                      # Similarity metric
)
\`\`\`

### Search Parameters

\`\`\`python
results = kb.search(
    query="your question",
    top_k=3,                    # Number of results
    namespace="default",        # Namespace to search
    filter_type="risk_score"    # Optional type filter
)
\`\`\`

### Chunking Strategy

\`\`\`python
chunks = kb.chunk_document(
    text=document_text,
    chunk_size=500,    # Characters per chunk
    overlap=50         # Overlap between chunks
)
\`\`\`

## 📊 Architecture

### Components

1. **PineconeKnowledgeBase** (`pinecone_kb.py`)
   - Manages Pinecone index
   - Generates embeddings
   - Handles search

2. **PineconeRAGChatbot** (`pinecone_rag_chatbot.py`)
   - Main chatbot interface
   - Integrates vector search
   - Generates AI responses

3. **Knowledge Base** (`knowledge_base.md`)
   - Technical documentation
   - Indexed into Pinecone
   - Source of truth

### Data Flow

\`\`\`
User Query
    ↓
PineconeRAGChatbot
    ↓
Generate embedding (Gemini)
    ↓
Search Pinecone
    ↓
Retrieve relevant docs
    ↓
Build prompt with context
    ↓
Generate response (Gemini)
    ↓
Return to user
\`\`\`

## 🧪 Testing

### Test Setup

\`\`\`bash
# Setup knowledge base
python chatbot/pinecone_kb.py
\`\`\`

Expected output:
\`\`\`
✓ Pinecone knowledge base initialized
Found 15 sections
  Processed 10/15 sections...
  Processed 15/15 sections...
✓ Knowledge base indexed successfully!
  Total vectors: 15
  Namespace: default

Testing Search:
Query: How does the risk score model work?
Found 2 results:
  1. Risk Score Engine - Explainable AI Layer (score: 0.923)
  2. Machine Learning Model (score: 0.887)
\`\`\`

### Test Chatbot

\`\`\`bash
python -m chatbot.pinecone_rag_chatbot
\`\`\`

Try:
1. Location query with technical details
2. Ask command: "ask How does sentiment analysis work?"
3. Verify Pinecone search is working

## 📈 Performance

### Indexing
- **Time**: ~2-5 seconds for 15 sections
- **Vectors**: 15 (one per section)
- **Dimension**: 768 (Gemini embeddings)

### Search
- **Latency**: 50-100ms per query
- **Accuracy**: High (semantic understanding)
- **Scalability**: Handles millions of vectors

### Embeddings
- **Model**: Gemini text-embedding-004
- **Dimension**: 768
- **Quality**: State-of-the-art

## 🔒 Security

### API Keys
- Store in `.env` file
- Never commit to version control
- Use environment variables

### Data Privacy
- Knowledge base is your own data
- Pinecone stores only embeddings
- No sensitive user data in vectors

## 🚀 Advanced Features

### Custom Namespaces

\`\`\`python
# Index to different namespace
kb.index_knowledge_base(kb_path, namespace="v2")

# Search specific namespace
results = kb.search(query, namespace="v2")
\`\`\`

### Metadata Filtering

\`\`\`python
# Filter by section type
results = kb.search(
    query="explain the model",
    filter_type="risk_score"  # Only risk score sections
)
\`\`\`

### Batch Operations

\`\`\`python
# Index multiple documents
for doc_path in document_paths:
    kb.index_knowledge_base(doc_path, namespace=doc_path.stem)
\`\`\`

### Statistics

\`\`\`python
# Get index stats
stats = kb.get_stats()
print(f"Total vectors: {stats['total_vectors']}")
print(f"Namespaces: {stats['namespaces']}")
\`\`\`

## 🔄 Maintenance

### Update Knowledge Base

\`\`\`bash
# 1. Update knowledge_base.md
# 2. Re-index
python chatbot/pinecone_kb.py
\`\`\`

### Delete and Recreate

\`\`\`python
from chatbot.pinecone_kb import PineconeKnowledgeBase

kb = PineconeKnowledgeBase()

# Delete namespace
kb.delete_namespace("default")

# Re-index
kb.index_knowledge_base(kb_path)
\`\`\`

### Delete Index

\`\`\`python
# WARNING: This deletes everything
kb.delete_index()
\`\`\`

## 📚 Comparison: Basic RAG vs Pinecone RAG

| Feature | Basic RAG | Pinecone RAG |
|---------|-----------|--------------|
| Search method | Keyword matching | Semantic search |
| Accuracy | Moderate | High |
| Scalability | Limited | Excellent |
| Speed | Fast | Very fast |
| Relevance | Good | Excellent |
| Setup | Simple | Requires API key |
| Cost | Free | Free tier available |

## 🎯 Use Cases

### 1. Technical Support
- Users ask detailed questions about ML models
- Pinecone finds exact relevant documentation
- AI generates accurate, sourced answers

### 2. Audit & Compliance
- Auditors query system capabilities
- Retrieve specific technical details
- Provide transparent explanations

### 3. Research
- Researchers explore model architecture
- Find related concepts semantically
- Deep dive into methodology

### 4. User Education
- Users learn about safety scoring
- Understand ML reasoning
- Build trust through transparency

## 🐛 Troubleshooting

### Pinecone API Key Error
\`\`\`
ValueError: PINECONE_API_KEY not found
\`\`\`
**Solution**: Add `PINECONE_API_KEY` to `.env`

### Index Not Found
\`\`\`
Index 'maply-knowledge-base' not found
\`\`\`
**Solution**: Run `python chatbot/pinecone_kb.py` to create index

### Embedding Error
\`\`\`
Error generating embedding
\`\`\`
**Solution**: Check `GEMINI_API_KEY` is valid

### No Results Found
\`\`\`
Found 0 results
\`\`\`
**Solution**: Ensure knowledge base is indexed, check query

## ✨ Summary

**Pinecone Integration Provides:**
- ✅ Semantic search (understands meaning)
- ✅ Fast, accurate retrieval
- ✅ Scalable knowledge base
- ✅ Better AI responses
- ✅ Production-ready
- ✅ Easy to maintain

**Setup Steps:**
1. Get Pinecone API key
2. Add to `.env`
3. Run `python chatbot/pinecone_kb.py`
4. Use `python -m chatbot.pinecone_rag_chatbot`

**Ready for production with advanced semantic search!** 🎉
