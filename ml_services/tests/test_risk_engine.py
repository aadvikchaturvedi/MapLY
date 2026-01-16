"""
Risk Score Engine Tests
========================

Unit tests for the risk score engine.
"""

import pytest
import pandas as pd
import numpy as np
from Risk_Score_Engine.model import (
    DataPreprocessor,
    RiskScoreModel,
    RiskScoreAPI
)


class TestDataPreprocessor:
    """Test suite for DataPreprocessor."""
    
    @pytest.fixture
    def preprocessor(self):
        """Create a preprocessor instance."""
        return DataPreprocessor()
    
    def test_initialization(self, preprocessor):
        """Test preprocessor initialization."""
        assert preprocessor is not None
        assert len(preprocessor.crimes_against_women) > 0
    
    def test_feature_engineering(self, preprocessor):
        """Test feature engineering."""
        # Create sample data
        data = {
            'STATE/UT': ['State1', 'State2'],
            'DISTRICT': ['District1', 'District2'],
            'Rape': [10, 20],
            'Insult to modesty of Women': [5, 10],
            'Kidnapping and Abduction': [8, 15],
            'Dowry Deaths': [3, 7],
            'Importation of Girls': [1, 2],
            'Cruelty by Husband or his Relatives': [12, 18],
            'Assault on women with intent to outrage her modesty': [6, 11]
        }
        df = pd.DataFrame(data)
        
        result = preprocessor.engineer_features(df)
        
        # Check new features exist
        assert 'Total_Women_Crimes' in result.columns
        assert 'Domestic_Violence_Total' in result.columns
        assert 'Public_Safety_Total' in result.columns
        assert 'Severity_Score' in result.columns
        assert 'Safety_Score' in result.columns
        
        # Check values are valid
        assert all(result['Total_Women_Crimes'] > 0)
        assert all(result['Safety_Score'] >= 0)
        assert all(result['Safety_Score'] <= 100)


class TestRiskScoreModel:
    """Test suite for RiskScoreModel."""
    
    @pytest.fixture
    def model(self):
        """Create a risk score model instance."""
        return RiskScoreModel()
    
    @pytest.fixture
    def sample_data(self):
        """Create sample training data."""
        preprocessor = DataPreprocessor()
        data = {
            'STATE/UT': ['State1'] * 10,
            'DISTRICT': [f'District{i}' for i in range(10)],
            'Rape': np.random.randint(5, 50, 10),
            'Insult to modesty of Women': np.random.randint(3, 30, 10),
            'Kidnapping and Abduction': np.random.randint(4, 40, 10),
            'Dowry Deaths': np.random.randint(2, 20, 10),
            'Importation of Girls': np.random.randint(0, 5, 10),
            'Cruelty by Husband or his Relatives': np.random.randint(5, 50, 10),
            'Assault on women with intent to outrage her modesty': np.random.randint(3, 30, 10)
        }
        df = pd.DataFrame(data)
        return preprocessor.engineer_features(df)
    
    def test_model_training(self, model, sample_data):
        """Test model training."""
        model.train(sample_data)
        
        assert model.model is not None
        assert model.scaler is not None
    
    def test_risk_level_generation(self, model, sample_data):
        """Test risk level generation."""
        model.train(sample_data)
        results = model.get_risk_levels(sample_data)
        
        assert len(results) == len(sample_data)
        
        for result in results:
            assert 'state' in result
            assert 'district' in result
            assert 'safety_score' in result
            assert 'risk_category' in result
            
            # Validate score range
            assert 0 <= result['safety_score'] <= 100
            
            # Validate risk category
            assert result['risk_category'] in ['Low Risk', 'Moderate Risk', 'High Risk']


class TestRiskScoreAPI:
    """Test suite for RiskScoreAPI."""
    
    @pytest.fixture
    def api(self):
        """Create a risk score API instance."""
        return RiskScoreAPI()
    
    def test_api_initialization(self, api):
        """Test API initialization."""
        assert api is not None
        assert api.preprocessor is not None
        assert api.model is not None
