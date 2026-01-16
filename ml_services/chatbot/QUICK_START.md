# Explainable Safety Chatbot - Quick Start Guide

## What It Does

The Explainable Safety Chatbot uses **Gemini AI** to provide detailed, human-friendly explanations when users enter high-risk zones. It:

- 🎯 **Detects risk levels** using the ML-powered risk score engine
- 🤖 **Generates explanations** using Gemini AI for natural language responses
- ⚠️ **Alerts users** when entering high-risk zones
- 📊 **Explains the "why"** - provides reasoning behind risk classifications
- 💡 **Gives actionable advice** - specific safety recommendations
- 🔄 **Context-aware** - adapts advice based on user's situation

## Quick Start

### 1. Set Up API Key

Already done! Your `.env` file has:
\`\`\`
GEMINI_API_KEY=AIzaSyAOblObZ7vnylujnhrnSDwCNQWfLFrSTdE
\`\`\`

### 2. Run Interactive Chatbot

\`\`\`bash
cd /Users/aadvikchaturvedi/Desktop/MapLY/ml_services
python -m chatbot.explainable_chatbot
\`\`\`

### 3. Try It Out

\`\`\`
Enter state name: Maharashtra
Enter district name: Mumbai
Any additional context? traveling alone at night

[AI generates detailed explanation with safety tips]
\`\`\`

## Example Output

When entering a **high-risk zone**:

\`\`\`
⚠️  HIGH RISK ZONE DETECTED: District X, State Y
Safety Score: 45/100

Risk Level Summary:
This area is classified as "High Risk" based on government crime data 
analysis. This means there's a higher incidence of safety concerns 
compared to other regions.

Key Factors:
• Elevated reports of crimes against women
• Lower public safety infrastructure  
• Historical trends showing consistent concerns

Safety Recommendations:
1. Avoid traveling alone, especially after dark
2. Stay in well-populated, well-lit areas
3. Share your real-time location with trusted contacts
4. Keep emergency contacts readily accessible
5. Consider using verified transportation services

Positive Notes:
Main commercial areas during daytime hours tend to be safer.
\`\`\`

## Use Cases

### 1. Navigation App Integration
When user enters a high-risk zone:
\`\`\`python
from chatbot.explainable_chatbot import ExplainableSafetyChatbot

chatbot = ExplainableSafetyChatbot()
explanation = chatbot.chat("Maharashtra", "Mumbai", "traveling at night")
# Display explanation to user
\`\`\`

### 2. API Endpoint
\`\`\`bash
curl -X POST "http://localhost:8000/api/v1/chatbot/explain" \\
  -H "Content-Type: application/json" \\
  -d '{
    "state": "Maharashtra",
    "district": "Mumbai",
    "context": "traveling alone at night"
  }'
\`\`\`

### 3. Batch Processing
Check multiple locations:
\`\`\`python
locations = [
    ("Maharashtra", "Mumbai"),
    ("Delhi", "New Delhi"),
    ("Karnataka", "Bangalore")
]

for state, district in locations:
    explanation = chatbot.chat(state, district)
    print(f"{district}: {explanation}\\n")
\`\`\`

## Features

### Explainable AI
- Uses Gemini AI to generate natural, empathetic explanations
- Avoids technical jargon
- Focuses on actionable advice

### Risk Detection
- Automatically detects high-risk zones
- Shows safety scores (0-100)
- Categorizes as High/Moderate/Low Risk

### Context-Aware
- Adapts advice based on user context
- Different recommendations for day vs. night
- Considers traveling alone vs. in groups

### Fallback System
- If AI fails, uses template-based explanations
- Ensures users always get safety information

## Commands

\`\`\`bash
# Interactive mode
python -m chatbot.explainable_chatbot

# Run demo
python chatbot/demo.py

# Run tests
python chatbot/test.py
\`\`\`

## Integration

### Add to Main API

Edit `api/main.py`:

\`\`\`python
from chatbot.api import router as chatbot_router, initialize_chatbot

# In startup event
@app.on_event("startup")
async def startup_event():
    # ... existing code ...
    initialize_chatbot()

# Include router
app.include_router(chatbot_router)
\`\`\`

### Frontend Integration

\`\`\`javascript
// When user enters a location
async function checkLocationSafety(state, district, context) {
  const response = await fetch('/api/v1/chatbot/explain', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({state, district, context})
  });
  
  const data = await response.json();
  
  if (data.risk_category === 'High Risk') {
    // Show prominent alert
    showHighRiskAlert(data.explanation);
  } else {
    // Show info notification
    showSafetyInfo(data.explanation);
  }
}
\`\`\`

## Customization

### Change AI Model

Edit `explainable_chatbot.py`:
\`\`\`python
self.model_name = "gemini-2.0-flash-exp"  # or other Gemini model
\`\`\`

### Customize Prompt

Modify the prompt in `generate_explanation()` method to change:
- Tone (formal/casual)
- Length (brief/detailed)
- Focus areas (safety tips, statistics, etc.)

### Add More Context

Extend `_get_crime_statistics()` to fetch real crime data from your database.

## Troubleshooting

**API Key Error:**
\`\`\`
ValueError: GEMINI_API_KEY not found
\`\`\`
→ Check `.env` file has `GEMINI_API_KEY=your_key`

**Location Not Found:**
\`\`\`
❌ Sorry, I don't have safety data for...
\`\`\`
→ Check spelling, ensure location exists in risk database

**AI Response Slow:**
→ Normal for first request (model loading)
→ Subsequent requests are faster

## Next Steps

1. ✅ Test the chatbot: `python chatbot/test.py`
2. ✅ Run the demo: `python chatbot/demo.py`
3. ✅ Try interactive mode: `python -m chatbot.explainable_chatbot`
4. 🔄 Integrate with your frontend
5. 🔄 Add to main API endpoints
6. 🔄 Customize prompts for your use case

## Documentation

- Full README: `chatbot/README.md`
- API Integration: `chatbot/api.py`
- Main Code: `chatbot/explainable_chatbot.py`

---

**Ready to use!** The chatbot is fully functional and integrated with your risk score engine. 🎉
