# MapLY ML Services - Technical Knowledge Base

## Risk Score Engine - Explainable AI Layer

### Overview
The Risk Score Engine uses a multi-layered machine learning approach to calculate safety scores for different regions across India. The system is designed to be transparent and explainable.

### Data Sources
- **Government Crime Statistics**: Official data on crimes against women from National Crime Records Bureau (NCRB)
- **District-Level Data**: Granular information for each district in every state
- **Historical Trends**: Multi-year data to identify patterns and trends

### Crime Categories Analyzed
The engine analyzes seven major categories of crimes against women:

1. **Rape** (Weight: 9/10)
   - Most severe category
   - Directly impacts public safety perception
   - Strong indicator of overall safety concerns

2. **Kidnapping and Abduction** (Weight: 7/10)
   - Indicates organized crime presence
   - Affects mobility and freedom
   - Often linked to trafficking

3. **Assault on Women with Intent to Outrage Modesty** (Weight: 3/10)
   - Public safety incidents
   - Street harassment and assault
   - Affects daily commute safety

4. **Insult to Modesty of Women** (Weight: 2/10)
   - Verbal harassment and intimidation
   - Creates hostile environment
   - Often underreported

5. **Dowry Deaths** (Weight: 10/10)
   - Highest severity weight
   - Indicates domestic violence issues
   - Reflects societal safety concerns

6. **Cruelty by Husband or Relatives** (Weight: 5/10)
   - Domestic violence indicator
   - Affects household safety
   - Often correlates with broader safety issues

7. **Importation of Girls** (Weight: 8/10)
   - Trafficking indicator
   - Organized crime presence
   - Severe human rights violation

### Feature Engineering

#### Primary Features
1. **Total_Women_Crimes**: Sum of all crime categories
   - Provides overall crime volume
   - Normalized per capita when possible

2. **Domestic_Violence_Total**: Dowry Deaths + Cruelty by Husband/Relatives
   - Indicates household safety
   - Reflects cultural safety factors

3. **Public_Safety_Total**: Rape + Assault + Insult to Modesty
   - Measures street-level safety
   - Most relevant for navigation safety

#### Derived Features
1. **Severity_Score**: Weighted sum of all crimes
   - Uses crime-specific weights
   - Emphasizes more severe crimes
   - Formula: Σ(crime_count × weight)

2. **Safety_Score**: Inverse normalized severity (0-100 scale)
   - Higher score = Safer area
   - Formula: 100 × (1 - MinMaxScaled(Severity_Score))
   - Intuitive interpretation

3. **DV_to_Total_Ratio**: Domestic Violence / Total Crimes
   - Identifies domestic vs. public safety issues
   - Helps contextualize risk type

4. **Public_to_Total_Ratio**: Public Safety Crimes / Total Crimes
   - Measures street safety specifically
   - Most relevant for navigation decisions

### Machine Learning Model

#### Algorithm: XGBoost Regressor
**Why XGBoost?**
- Handles non-linear relationships
- Robust to outliers
- Provides feature importance
- Fast inference for real-time use

**Model Configuration:**
- n_estimators: 100 (number of trees)
- learning_rate: 0.1 (conservative to prevent overfitting)
- max_depth: 3 (prevents overfitting, maintains interpretability)

**Training Process:**
1. Data preprocessing with RobustScaler
   - Handles outliers better than StandardScaler
   - Maintains feature relationships
2. Feature scaling for numerical stability
3. Model training on historical data
4. Validation using R² score and MSE

### Risk Categorization

Safety scores are categorized into three risk levels:

1. **Low Risk** (Score ≥ 80)
   - Below-average crime rates
   - Strong public safety infrastructure
   - Generally safe for navigation

2. **Moderate Risk** (Score 60-79)
   - Average crime rates
   - Standard safety precautions recommended
   - Time-of-day considerations important

3. **High Risk** (Score < 60)
   - Above-average crime rates
   - Enhanced safety measures recommended
   - Avoid if possible, especially at night

### Explainability Features

#### Transparency
- All weights are documented and justified
- Feature importance can be extracted from XGBoost
- Scores are traceable to source data

#### Interpretability
- Simple 0-100 scale
- Clear risk categories
- Human-readable explanations

#### Auditability
- Source data from government records
- Reproducible calculations
- Version-controlled model

---

## Sentiment Analysis - Explainable AI Layer

### Overview
The Sentiment Analysis system uses transformer-based deep learning to analyze user feedback about safety, providing real-time sentiment scores that can adjust risk assessments.

### Model Architecture

#### Base Model: DistilBERT
**Model**: `distilbert-base-uncased-finetuned-sst-2-english`

**Why DistilBERT?**
- **Efficiency**: 40% smaller than BERT, 60% faster
- **Performance**: Retains 97% of BERT's language understanding
- **Pre-trained**: Fine-tuned on Stanford Sentiment Treebank (SST-2)
- **Production-Ready**: Optimized for real-time inference

**Architecture Details:**
- 6 transformer layers (vs. 12 in BERT)
- 768 hidden dimensions
- 12 attention heads
- ~66M parameters

### How It Works

#### Input Processing
1. **Tokenization**: Text → Token IDs
   - Handles up to 128 tokens (configurable)
   - Special tokens: [CLS], [SEP]
   - WordPiece tokenization

2. **Encoding**: Token IDs → Embeddings
   - Position embeddings
   - Token type embeddings
   - Layer normalization

3. **Transformer Layers**: Embeddings → Contextualized Representations
   - Multi-head self-attention
   - Feed-forward networks
   - Residual connections

4. **Classification**: Representations → Sentiment Probabilities
   - Linear layer
   - Softmax activation
   - Binary classification (Positive/Negative)

#### Output Interpretation

**Label**: POSITIVE or NEGATIVE
- POSITIVE: User feels safe
- NEGATIVE: User feels unsafe

**Confidence**: 0.0 to 1.0
- Probability of predicted class
- Higher = more confident prediction

**Normalized Score**: -1.0 to +1.0
- Formula: P(positive) - P(negative)
- +1.0: Very positive (very safe)
- 0.0: Neutral
- -1.0: Very negative (very unsafe)

**Probabilities**: Dict with both class probabilities
- positive: P(POSITIVE)
- negative: P(NEGATIVE)
- Sum = 1.0

### Example Analysis

**Input**: "I felt very safe walking here at night, good lighting and people around"

**Processing**:
1. Tokenize: ["i", "felt", "very", "safe", "walking", ...]
2. Encode: [101, 1045, 2371, 2200, 3647, ...]
3. Transform: Contextualized embeddings
4. Classify: Logits → Probabilities

**Output**:
- Label: POSITIVE
- Confidence: 0.95
- Normalized Score: 0.90
- Probabilities: {positive: 0.95, negative: 0.05}

**Interpretation**: Strong positive sentiment indicating the user feels very safe in this area.

### Integration with Risk Scores

#### Dynamic Risk Adjustment
The sentiment scores can be used to adjust static risk scores:

**Formula**: 
```
Updated_Risk = Base_Risk + λ × Sentiment_Adjustment
```

Where:
- Base_Risk: ML-calculated risk score
- λ (lambda): Learning rate (default: 0.05)
- Sentiment_Adjustment: Aggregated user sentiment

**Example**:
- Base Risk Score: 70 (Moderate Risk)
- User Sentiment: -0.8 (Very negative)
- Adjustment: 70 + (0.05 × -0.8 × 10) = 69.6
- Result: Slightly increased risk based on user feedback

### Explainability Features

#### Attention Visualization
- Can extract attention weights
- Shows which words influenced the decision
- Helps understand model reasoning

#### Confidence Scores
- Provides uncertainty estimates
- Low confidence → ambiguous text
- High confidence → clear sentiment

#### Probability Distribution
- Full probability breakdown
- Not just binary decision
- Shows model's uncertainty

---

## Why This Approach is Explainable

### 1. Transparent Data Sources
- Government crime statistics (publicly available)
- Documented data collection methods
- Traceable to original sources

### 2. Clear Feature Engineering
- Every feature has a clear purpose
- Weights are justified and documented
- Simple mathematical operations

### 3. Interpretable Models
- XGBoost provides feature importance
- DistilBERT has attention mechanisms
- Both can be analyzed and understood

### 4. Human-Readable Outputs
- 0-100 safety scores (intuitive)
- Clear risk categories (Low/Moderate/High)
- Natural language sentiment labels

### 5. Auditability
- Version-controlled code
- Reproducible results
- Documented decision logic

### 6. User Feedback Loop
- Sentiment analysis captures user experience
- Can validate or challenge static scores
- Continuous improvement mechanism

---

## Technical Specifications

### Risk Score Engine
- **Language**: Python 3.11+
- **ML Framework**: XGBoost 2.0+, Scikit-learn 1.4+
- **Data Processing**: Pandas 2.0+, NumPy 1.24+
- **Scaling**: RobustScaler, MinMaxScaler
- **Output**: JSON with state, district, safety_score, risk_category

### Sentiment Analysis
- **Language**: Python 3.11+
- **ML Framework**: PyTorch 2.0+, Transformers 4.40+
- **Model**: DistilBERT (66M parameters)
- **Input**: Text (1-1000 characters)
- **Output**: JSON with label, confidence, normalized_score, probabilities
- **Inference Time**: ~50-200ms per prediction

### Performance Metrics

#### Risk Score Engine
- **Coverage**: 11,530+ regions across India
- **Update Frequency**: Based on government data releases
- **Accuracy**: R² > 0.85 on validation set
- **Inference**: <10ms per location

#### Sentiment Analysis
- **Accuracy**: ~95% on SST-2 benchmark
- **Precision**: ~94% for both classes
- **Recall**: ~95% for both classes
- **F1-Score**: ~94.5% overall
- **Inference**: ~50-200ms per text

---

## Use Cases for Explainability

### 1. User Trust
Users can understand WHY an area is marked as high-risk:
- "Based on 45 reported incidents of crimes against women"
- "Historical data shows consistent safety concerns"
- "Public safety score is below regional average"

### 2. Transparency
Authorities and stakeholders can audit the system:
- Trace scores to source data
- Understand feature weights
- Validate model decisions

### 3. Continuous Improvement
User feedback helps refine the system:
- Sentiment analysis captures real experiences
- Identifies discrepancies between data and reality
- Enables model updates and recalibration

### 4. Contextual Advice
Explainable AI enables better recommendations:
- "High domestic violence but lower street crime"
- "Safe during day, higher risk at night"
- "Commercial areas safer than residential"

---

## Future Enhancements

### Planned Improvements
1. **Real-time Data Integration**: Live incident reports
2. **Temporal Analysis**: Time-of-day risk variations
3. **Spatial Clustering**: Neighborhood-level granularity
4. **Multi-modal Analysis**: Combine crime data with infrastructure, lighting, population density
5. **Causal Inference**: Identify root causes of safety issues
6. **Counterfactual Explanations**: "What would make this area safer?"

### Research Directions
1. **Explainable Deep Learning**: LIME, SHAP for model interpretation
2. **Fairness Analysis**: Ensure unbiased risk assessment
3. **Uncertainty Quantification**: Confidence intervals for predictions
4. **Transfer Learning**: Adapt to new regions with limited data

---

## References

### Data Sources
- National Crime Records Bureau (NCRB)
- State Police Departments
- Ministry of Home Affairs

### Academic References
- XGBoost: Chen & Guestrin (2016)
- DistilBERT: Sanh et al. (2019)
- Transformer Architecture: Vaswani et al. (2017)
- SST-2 Dataset: Socher et al. (2013)

### Model Documentation
- Hugging Face Transformers: https://huggingface.co/docs
- XGBoost Documentation: https://xgboost.readthedocs.io
- Scikit-learn: https://scikit-learn.org

---

**Last Updated**: January 2026
**Version**: 1.0.0
**Maintained by**: MapLY ML Team
