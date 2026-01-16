# RAG-Enhanced Explainable Safety Chatbot

## 🎯 Overview

The **RAG (Retrieval-Augmented Generation) Enhanced Chatbot** combines the power of Gemini AI with a comprehensive technical knowledge base to provide:

1. **User-Friendly Explanations**: Simple safety advice for general users
2. **Technical ML Explanations**: Detailed reasoning about how the ML models work
3. **Transparent AI**: Full visibility into the decision-making process

## 🆕 What's New with RAG

### Knowledge Base Integration
- **Comprehensive Documentation**: 15,000+ words of technical documentation
- **ML Model Details**: Complete explanation of risk score engine and sentiment analysis
- **Explainability Features**: Documentation of why the system is trustworthy

### Enhanced Capabilities
- **Technical Mode**: Users can request detailed ML explanations
- **Model Explanation**: Ask the chatbot to explain how the ML models work
- **Context-Aware Retrieval**: Automatically fetches relevant technical information

## 📦 Files Created

1. **`knowledge_base.md`** - Comprehensive technical documentation
   - Risk Score Engine details
   - Sentiment Analysis architecture
   - Explainability features
   - Technical specifications

2. **`rag_chatbot.py`** - RAG-enhanced chatbot implementation
   - Knowledge base loading
   - Context extraction
   - Technical explanation generation

3. **`test_rag.py`** - Comprehensive testing script
   - Tests all RAG features
   - Demonstrates capabilities

## 🚀 Quick Start

### Basic Usage (Simple Explanations)

\`\`\`bash
cd /Users/aadvikchaturvedi/Desktop/MapLY/ml_services
source .venv/bin/activate
python -m chatbot.rag_chatbot
\`\`\`

Then:
\`\`\`
Enter command (or state name): Maharashtra
Enter district name: Mumbai
Context (optional): [press Enter]
Include technical ML details? (y/n): n

[Receives user-friendly explanation]
\`\`\`

### Technical Mode (ML Explanations)

\`\`\`
Enter command (or state name): Maharashtra
Enter district name: Mumbai
Context (optional): traveling at night
Include technical ML details? (y/n): y

[Receives detailed ML explanation including:]
- How the score was calculated
- Which features the model considered
- Why certain crimes have higher weights
- Technical details about XGBoost
\`\`\`

### Explain ML Models

\`\`\`
Enter command (or state name): explain risk_score

[Chatbot explains how the risk score model works]

Enter command (or state name): explain sentiment

[Chatbot explains sentiment analysis]

Enter command (or state name): explain explainability

[Chatbot explains why the system is trustworthy]
\`\`\`

## 🎓 Example Outputs

### Standard Explanation

\`\`\`
📍 Location: Mumbai, Maharashtra
Safety Score: 85/100
Risk Category: Low Risk

This area is classified as "Low Risk" based on comprehensive analysis 
of government crime data. The 85/100 safety score indicates this is 
a relatively safe area compared to other regions.

Safety Recommendations:
• Maintain general awareness of surroundings
• Share location with trusted contacts when traveling
• Stick to well-lit, populated areas at night
• Keep emergency contacts accessible

This assessment is based on official government crime statistics 
from the National Crime Records Bureau (NCRB).
\`\`\`

### Technical ML Explanation

\`\`\`
📍 Location: Mumbai, Maharashtra
Safety Score: 85/100
Risk Category: Low Risk

**How This Score Was Calculated:**
Our machine learning model (XGBoost) analyzes government crime data 
across 7 categories:
- Crimes are weighted by severity (rape=9/10, kidnapping=7/10, etc.)
- Multiple factors considered: total crimes, domestic violence ratio, 
  public safety incidents
- Score normalized to 0-100 scale using MinMaxScaler
- Based on National Crime Records Bureau (NCRB) data

**Model Reasoning:**
The 85/100 score reflects:
1. Below-average crime rates in this district
2. Low Public_Safety_Total (street-level incidents)
3. Favorable DV_to_Total_Ratio (domestic vs public safety)
4. Historical trend analysis showing consistent safety

**Features Analyzed:**
- Total_Women_Crimes: Lower than regional average
- Severity_Score: Weighted sum favoring less severe incidents
- Public_to_Total_Ratio: Indicates good street safety
- Domestic_Violence_Total: Within acceptable range

Safety Recommendations:
[... continues with safety tips ...]
\`\`\`

### Model Explanation

\`\`\`
User: explain risk_score

Chatbot:
The Risk Score Engine uses XGBoost, a gradient boosting algorithm, 
to predict safety scores based on government crime data.

**How It Works:**
Think of it like a smart calculator that learned from thousands of 
examples. It looks at 7 types of crimes against women, gives each 
type a "severity weight" (like rape being more serious than verbal 
harassment), and combines them mathematically.

**Why It's Trustworthy:**
1. Uses official government data (NCRB)
2. All weights are documented and justified
3. Calculations are reproducible
4. Can trace any score back to source data

**Key Technical Details:**
- Algorithm: XGBoost (100 trees, depth=3)
- Features: 4 engineered features from 7 crime categories
- Scaling: RobustScaler for outlier handling
- Output: 0-100 score (higher = safer)

The model achieves R² > 0.85 on validation data, meaning it's 
highly accurate at predicting safety levels.
\`\`\`

## 🔧 How RAG Works

### 1. Knowledge Base
- Comprehensive markdown document with technical details
- Organized into sections (Risk Score, Sentiment, Explainability)
- ~15,000 words of documentation

### 2. Context Retrieval
- Based on query type, extracts relevant sections
- Simple keyword-based retrieval (can be enhanced with embeddings)
- Limits context to avoid token limits

### 3. Enhanced Prompting
- Combines user query + retrieved context
- Gemini AI generates natural language explanation
- Maintains accuracy while being accessible

### 4. Fallback System
- If AI fails, uses template-based explanations
- Ensures users always get information
- Includes technical details when requested

## 📊 Use Cases

### 1. General Users
- Simple, clear safety explanations
- No technical jargon
- Actionable advice

### 2. Technical Users
- Detailed ML explanations
- Understanding model reasoning
- Transparency and trust

### 3. Researchers/Auditors
- Full model documentation
- Explainability features
- Reproducible results

### 4. Developers
- Integration examples
- API documentation
- Technical specifications

## 🔌 Integration

### Python Library

\`\`\`python
from chatbot.rag_chatbot import RAGEnhancedChatbot

# Initialize
chatbot = RAGEnhancedChatbot()

# Basic explanation
explanation = chatbot.chat("Maharashtra", "Mumbai")

# Technical explanation
technical_explanation = chatbot.chat(
    "Maharashtra", 
    "Mumbai",
    explain_technical=True
)

# Explain the model
model_explanation = chatbot.explain_model("risk_score")
\`\`\`

### API Endpoint (Future)

\`\`\`bash
curl -X POST "http://localhost:8000/api/v1/chatbot/explain" \\
  -H "Content-Type: application/json" \\
  -d '{
    "state": "Maharashtra",
    "district": "Mumbai",
    "include_technical": true
  }'
\`\`\`

## 🧪 Testing

\`\`\`bash
# Activate virtual environment
source .venv/bin/activate

# Run RAG tests
python chatbot/test_rag.py
\`\`\`

Expected output:
- ✓ Basic safety explanations
- ✓ Technical ML explanations
- ✓ Model reasoning explanations
- ✓ Sentiment analysis explanations
- ✓ Explainability features

## 📚 Knowledge Base Contents

### Risk Score Engine
- Data sources and crime categories
- Feature engineering details
- XGBoost model configuration
- Risk categorization logic
- Explainability features

### Sentiment Analysis
- DistilBERT architecture
- How it processes text
- Output interpretation
- Integration with risk scores

### Explainability
- Why the approach is transparent
- Auditability features
- Trust mechanisms
- Future enhancements

### Technical Specifications
- Performance metrics
- Model parameters
- Inference times
- Accuracy scores

## 🎯 Key Features

✅ **Dual Mode Operation**
- Simple mode for general users
- Technical mode for experts

✅ **Comprehensive Knowledge Base**
- 15,000+ words of documentation
- Covers all ML aspects
- Regularly updated

✅ **Intelligent Retrieval**
- Context-aware extraction
- Relevant information only
- Optimized for token limits

✅ **Natural Language Generation**
- Gemini AI powered
- Accessible explanations
- Technical accuracy maintained

✅ **Fallback System**
- Always provides information
- Graceful degradation
- Maintains core functionality

## 🔄 Comparison: Basic vs RAG

| Feature | Basic Chatbot | RAG-Enhanced |
|---------|--------------|--------------|
| Safety explanations | ✅ | ✅ |
| Context-aware advice | ✅ | ✅ |
| Technical ML details | ❌ | ✅ |
| Model explanations | ❌ | ✅ |
| Knowledge base | ❌ | ✅ |
| Explain features | ❌ | ✅ |
| Research/audit support | ❌ | ✅ |

## 🚀 Next Steps

### For Users
1. Try basic mode: `python -m chatbot.rag_chatbot`
2. Request technical details when needed
3. Use `explain` commands to learn about ML

### For Developers
1. Review `knowledge_base.md` for technical details
2. Integrate RAG chatbot into your application
3. Customize knowledge base for your needs

### For Enhancement
1. Add vector embeddings for better retrieval
2. Expand knowledge base with more details
3. Add real-time data integration
4. Implement caching for faster responses

## 📖 Documentation

- **Knowledge Base**: `knowledge_base.md` - Full technical documentation
- **RAG Implementation**: `rag_chatbot.py` - Source code
- **Testing**: `test_rag.py` - Test suite
- **Original Chatbot**: `explainable_chatbot.py` - Basic version

## ✨ Summary

The RAG-enhanced chatbot provides:
- ✅ User-friendly safety explanations
- ✅ Technical ML transparency
- ✅ Comprehensive knowledge base
- ✅ Explainable AI features
- ✅ Multiple explanation modes
- ✅ Production-ready implementation

**Ready to use with full ML explainability!** 🎉
