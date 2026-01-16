# Explainable Safety Chatbot

Interactive chatbot that provides detailed, AI-generated explanations for safety risk zones using Gemini AI.

## Features

- 🤖 **AI-Powered Explanations**: Uses Gemini AI to generate human-friendly safety explanations
- 🎯 **Risk Analysis**: Integrates with the risk score engine for accurate data
- 📊 **Detailed Insights**: Explains risk factors, provides safety tips, and contextual advice
- 💬 **Interactive Mode**: Command-line chat interface
- 🔌 **API Integration**: REST API endpoints for frontend integration
- ⚠️ **High-Risk Alerts**: Special handling for high-risk zones

## Quick Start

### Interactive Mode

```bash
cd /Users/aadvikchaturvedi/Desktop/MapLY/ml_services
python -m chatbot.explainable_chatbot
```

### Example Interaction

```
🛡️  MapLY Explainable Safety Chatbot
====================================

Enter state name: Maharashtra
Enter district name: Mumbai
Any additional context? (optional): traveling alone at night

============================================================
⚠️  HIGH RISK ZONE DETECTED: Mumbai, Maharashtra
Safety Score: 65.5/100

[AI-generated explanation with safety recommendations]
============================================================
```

## API Usage

### Start API Server

The chatbot endpoints are integrated into the main API. Start the server:

```bash
python -m uvicorn api.main:app --reload
```

### API Endpoint

```bash
curl -X POST "http://localhost:8000/api/v1/chatbot/explain" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "Maharashtra",
    "district": "Mumbai",
    "context": "traveling alone at night"
  }'
```

### Response

```json
{
  "state": "Maharashtra",
  "district": "Mumbai",
  "safety_score": 65.5,
  "risk_category": "Moderate Risk",
  "explanation": "AI-generated detailed explanation with safety tips..."
}
```

## How It Works

1. **User Input**: User provides location (state, district) and optional context
2. **Risk Lookup**: System retrieves safety score and risk category from the risk engine
3. **AI Generation**: Gemini AI generates a detailed, empathetic explanation including:
   - Risk level summary in practical terms
   - Key factors contributing to the risk
   - 3-4 specific safety recommendations
   - Positive notes and safer alternatives
4. **Response**: User receives human-friendly explanation

## Configuration

### Environment Variables

Add to `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### Customization

Edit `explainable_chatbot.py` to customize:
- AI model (`model_name`)
- Prompt template
- Response format
- Fallback messages

## Features in Detail

### Explainable AI

The chatbot uses Gemini AI to provide:
- **Clear explanations** of risk scores in non-technical language
- **Context-aware advice** based on user's situation
- **Actionable recommendations** for staying safe
- **Empathetic tone** that's informative, not alarmist

### High-Risk Zone Alerts

When a high-risk zone is detected:
- Special warning message displayed
- More detailed safety recommendations
- Emphasis on immediate precautions
- Alternative suggestions when possible

### Fallback Mechanism

If AI service fails:
- Automatic fallback to template-based explanations
- Ensures users always receive safety information
- Maintains core functionality

## Integration with Main API

To integrate with the main API, add to `api/main.py`:

```python
from chatbot.api import router as chatbot_router, initialize_chatbot

# In startup event
@app.on_event("startup")
async def startup_event():
    # ... existing code ...
    initialize_chatbot()

# Include router
app.include_router(chatbot_router)
```

## Testing

```bash
# Test the chatbot
python chatbot/explainable_chatbot.py

# Test API endpoint
curl http://localhost:8000/api/v1/chatbot/health
```

## Example Explanations

### High-Risk Zone

```
⚠️  HIGH RISK ZONE DETECTED: District X, State Y
Safety Score: 45/100

Risk Level Summary:
This area is classified as "High Risk" based on government crime data analysis. 
This means there's a higher incidence of safety concerns compared to other regions.

Key Factors:
- Elevated reports of crimes against women
- Lower public safety infrastructure
- Historical trends showing consistent concerns

Safety Recommendations:
1. Avoid traveling alone, especially after dark
2. Stay in well-populated, well-lit areas
3. Share your real-time location with trusted contacts
4. Keep emergency contacts readily accessible
5. Consider using verified transportation services

Positive Notes:
Main commercial areas during daytime hours tend to be safer. 
Consider planning activities during peak hours when more people are around.
```

### Moderate Risk Zone

```
Risk Level: Moderate Risk
Safety Score: 68/100

This area shows moderate safety concerns. While not high-risk, 
it's important to remain vigilant and follow basic safety precautions...
```

## Dependencies

- `google-genai`: Gemini AI SDK
- `python-dotenv`: Environment variable management
- Risk Score Engine (from parent module)

## Troubleshooting

**API Key Error:**
```
ValueError: GEMINI_API_KEY not found
```
Solution: Add `GEMINI_API_KEY` to `.env` file

**Location Not Found:**
```
❌ Sorry, I don't have safety data for...
```
Solution: Check spelling, ensure location exists in risk database

**AI Service Error:**
Falls back to template-based explanation automatically.

## Future Enhancements

- [ ] Multi-language support
- [ ] Voice interface
- [ ] Historical trend analysis
- [ ] Personalized recommendations based on user profile
- [ ] Integration with real-time incident reports
- [ ] Mobile app integration
