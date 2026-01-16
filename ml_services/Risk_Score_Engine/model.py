"""
Women Safety Risk Score Engine API
Enhanced version to return District/State mapped Risk Scores
"""

import pandas as pd
import numpy as np
import os
import json
import warnings
from pathlib import Path
from typing import Dict, List
from sklearn.preprocessing import RobustScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
import xgboost as xgb

warnings.filterwarnings('ignore')

class DataPreprocessor:
    def __init__(self):
        self.crimes_against_women = [
            'Rape', 'Insult to modesty of Women', 'Kidnapping and Abduction',
            'Dowry Deaths', 'Importation of Girls', 'Cruelty by Husband or his Relatives',
            'Assault on women with intent to outrage her modesty'
        ]
        
    def load_and_combine_datasets(self, file_paths: List[str]) -> pd.DataFrame:
        dataframes = [pd.read_csv(fp) for fp in file_paths if os.path.exists(fp)]
        if not dataframes:
            raise FileNotFoundError("No valid CSV files found.")

        rename_map = {
            'State/ UT': 'STATE/UT', 'District/ Area': 'DISTRICT',
            'Kidnapping & Abduction_Total': 'Kidnapping and Abduction',
            'Assault on Women with intent to outrage her Modesty_Total': 'Assault on women with intent to outrage her modesty',
            'Insult to the Modesty of Women_Total': 'Insult to modesty of Women',
            'Importation of Girls from Foreign Country': 'Importation of Girls'
        }
        
        for df in dataframes:
            df.rename(columns=rename_map, inplace=True)
        
        common_cols = list(set.intersection(*(set(df.columns) for df in dataframes)))
        combined = pd.concat([df[common_cols] for df in dataframes], ignore_index=True)
        return combined.drop_duplicates().reset_index(drop=True)

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['Total_Women_Crimes'] = df[self.crimes_against_women].sum(axis=1)
        df['Domestic_Violence_Total'] = df['Dowry Deaths'] + df['Cruelty by Husband or his Relatives']
        df['Public_Safety_Total'] = df['Rape'] + df['Assault on women with intent to outrage her modesty'] + df['Insult to modesty of Women']
        
        weights = {'Dowry Deaths': 10, 'Rape': 9, 'Importation of Girls': 8, 'Kidnapping and Abduction': 7, 
                   'Cruelty by Husband or his Relatives': 5, 'Assault on women with intent to outrage her modesty': 3, 'Insult to modesty of Women': 2}
        
        df['Severity_Score'] = sum(df[c] * w for c, w in weights.items() if c in df.columns)
        df['Safety_Score'] = 100 * (1 - MinMaxScaler().fit_transform(df[['Severity_Score']]))
        
        df['DV_to_Total_Ratio'] = df['Domestic_Violence_Total'] / (df['Total_Women_Crimes'] + 1)
        df['Public_to_Total_Ratio'] = df['Public_Safety_Total'] / (df['Total_Women_Crimes'] + 1)
        
        return df.fillna(0)

class RiskScoreModel:
    def __init__(self):
        self.features = ['Total_Women_Crimes', 'DV_to_Total_Ratio', 'Public_to_Total_Ratio']
        self.scaler = RobustScaler()
        self.model = None

    def train(self, df: pd.DataFrame):
        X, y = df[self.features], df['Safety_Score']
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        
        self.model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=3)
        self.model.fit(X_scaled, y)

    def get_risk_levels(self, df: pd.DataFrame) -> List[Dict]:
        """Generates the specific JSON structure for the navigation app"""
        X_scaled = self.scaler.transform(df[self.features])
        predictions = self.model.predict(X_scaled)
        
        results = []
        for i, score in enumerate(predictions):
            # Clip score between 0-100 and round
            final_score = round(float(np.clip(score, 0, 100)), 2)
            
            # Categorize Risk
            if final_score >= 80: level = "Low Risk"
            elif final_score >= 60: level = "Moderate Risk"
            else: level = "High Risk"

            results.append({
                "state": df.iloc[i]['STATE/UT'],
                "district": df.iloc[i]['DISTRICT'],
                "safety_score": final_score,
                "risk_category": level
            })
        return results

class RiskScoreAPI:
    def __init__(self):
        self.preprocessor = DataPreprocessor()
        self.model = RiskScoreModel()

    def get_navigation_data(self, file_paths: List[str]):
        try:
            # 1. Process Data
            raw_data = self.preprocessor.load_and_combine_datasets(file_paths)
            processed_data = self.preprocessor.engineer_features(raw_data)
            
            # 2. Train and Predict
            self.model.train(processed_data)
            risk_data = self.model.get_risk_levels(processed_data)
            
            return {
                "status": "success",
                "total_regions": len(risk_data),
                "data": risk_data
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Path configuration
    current_dir = Path(__file__).resolve().parent
    data_dir = current_dir.parent.parent / "data"
    csv_files = [str(p) for p in data_dir.glob("*.csv")]
    
    if csv_files:
        api = RiskScoreAPI()
        response = api.get_navigation_data(csv_files)
        
        # Print only the first 3 results as an example JSON response
        example_output = {
            "status": response["status"],
            "sample_data": response["data"][:3] 
        }
        print(json.dumps(example_output, indent=4))