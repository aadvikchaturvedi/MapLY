"""
Women Safety Risk Score Engine API
Enhanced version to return District/State mapped Risk Scores
"""

import logging
import pandas as pd
import numpy as np
import os
import json
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from sklearn.preprocessing import RobustScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
from scipy.spatial import cKDTree
import xgboost as xgb

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

# Default fallback centroid used when a district is missing from the centroid
# lookup table. Picked at New Delhi, which is roughly central for India.
DEFAULT_INDIAN_CENTROID: Tuple[float, float] = (28.6139, 77.2090)

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
        df['Safety_Score'] = np.clip(100 * (1 - MinMaxScaler().fit_transform(df[['Severity_Score']])), 0, 100)
        
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
    def __init__(
        self,
        centroids_path: Optional[str] = None,
        default_centroid: Tuple[float, float] = DEFAULT_INDIAN_CENTROID,
    ):
        self.preprocessor = DataPreprocessor()
        self.model = RiskScoreModel()
        self.default_centroid = tuple(default_centroid)

        # Centroid lookup: state_lower -> district_lower -> [lat, lng]
        self._centroid_lookup: Dict[str, Dict[str, List[float]]] = {}
        # Risk lookup: (state_lower, district_lower) -> risk record dict
        self._risk_lookup: Dict[Tuple[str, str], Dict] = {}
        # cKDTree state
        self._tree: Optional[cKDTree] = None
        self._tree_keys: List[Tuple[str, str]] = []
        self._tree_coords: List[List[float]] = []

        self._load_centroids(centroids_path)
        self._build_tree()

    # ------------------------------------------------------------------
    # Centroid table management
    # ------------------------------------------------------------------
    def _load_centroids(self, centroids_path: Optional[str] = None) -> None:
        """Load the built-in district centroid lookup table from JSON."""
        if centroids_path is None:
            centroids_path = str(
                Path(__file__).resolve().parent / "district_centroids.json"
            )

        if not os.path.exists(centroids_path):
            logger.warning(
                "Centroid lookup table not found at %s; spatial queries will use "
                "the default Indian centroid for every input.",
                centroids_path,
            )
            return

        try:
            with open(centroids_path, "r", encoding="utf-8") as fp:
                raw = json.load(fp)
        except Exception as exc:
            logger.warning(
                "Failed to load centroid lookup table %s: %s", centroids_path, exc
            )
            return

        normalized: Dict[str, Dict[str, List[float]]] = {}
        for state, districts in raw.items():
            if not isinstance(districts, dict):
                continue
            state_key = str(state).strip().lower()
            normalized[state_key] = {}
            for district, coords in districts.items():
                if not isinstance(coords, (list, tuple)) or len(coords) != 2:
                    continue
                try:
                    lat = float(coords[0])
                    lng = float(coords[1])
                except (TypeError, ValueError):
                    continue
                normalized[state_key][str(district).strip().lower()] = [lat, lng]

        self._centroid_lookup = normalized
        logger.info(
            "Loaded %d states / %d district centroid entries.",
            len(normalized),
            sum(len(v) for v in normalized.values()),
        )

    def _build_tree(self) -> None:
        """Build a cKDTree over all known district centroids."""
        coords: List[List[float]] = []
        keys: List[Tuple[str, str]] = []
        for state, districts in self._centroid_lookup.items():
            for district, latlng in districts.items():
                coords.append([latlng[0], latlng[1]])
                keys.append((state, district))

        if coords:
            self._tree = cKDTree(np.array(coords, dtype=float))
            self._tree_coords = coords
            self._tree_keys = keys
        else:
            self._tree = None
            self._tree_coords = []
            self._tree_keys = []

    def register_risk_data(self, risk_data: List[Dict]) -> None:
        """Index risk records so spatial queries can resolve them.

        Also backfills any CSV-derived (state, district) pair missing from the
        centroid lookup with the default Indian centroid so the spatial index
        remains usable for the full dataset.
        """
        indexed: Dict[Tuple[str, str], Dict] = {}
        for record in risk_data:
            if not isinstance(record, dict):
                continue
            state = str(record.get("state", "")).strip().lower()
            district = str(record.get("district", "")).strip().lower()
            if not state or not district:
                continue
            indexed[(state, district)] = record

        self._risk_lookup = indexed

        # Backfill missing centroids so the tree can resolve any record.
        added = 0
        for state, district in indexed.keys():
            state_bucket = self._centroid_lookup.setdefault(state, {})
            if district not in state_bucket:
                logger.warning(
                    "District %r in %r missing from centroid lookup table; "
                    "falling back to default Indian centroid %s.",
                    district,
                    state,
                    self.default_centroid,
                )
                state_bucket[district] = [
                    float(self.default_centroid[0]),
                    float(self.default_centroid[1]),
                ]
                added += 1

        if added:
            self._build_tree()

    # ------------------------------------------------------------------
    # Coordinate-based queries
    # ------------------------------------------------------------------
    def _categorize(self, safety_score: float) -> str:
        score = float(np.clip(safety_score, 0, 100))
        if score >= 80:
            return "Low Risk"
        if score >= 60:
            return "Moderate Risk"
        return "High Risk"

    def get_risk_for_coordinate(
        self, lat: float, lng: float
    ) -> Dict[str, object]:
        """Look up risk for an arbitrary (lat, lng) coordinate.

        Returns a dict with keys: ``state``, ``district``, ``safety_score``,
        ``risk_category``, and ``risk_score`` where ``risk_score = 1 -
        safety_score / 100``. If the nearest centroid cannot be matched to a
        loaded risk record, the default Indian centroid's record (or a neutral
        fallback) is used and a warning is logged.
        """
        lat_f = float(lat)
        lng_f = float(lng)

        # 1. Resolve to a nearest centroid key.
        state_key: Optional[str] = None
        dist_key: Optional[str] = None

        if self._tree is not None and self._tree_keys:
            try:
                _, idx = self._tree.query([lat_f, lng_f], k=1)
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("cKDTree query failed: %s", exc)
                idx = None
            if idx is not None:
                idx_i = int(idx)
                if 0 <= idx_i < len(self._tree_keys):
                    state_key, dist_key = self._tree_keys[idx_i]

        if state_key is None or dist_key is None:
            logger.warning(
                "No centroid available for (%.6f, %.6f); using default Indian "
                "centroid fallback.",
                lat_f,
                lng_f,
            )
            state_key, dist_key = "delhi", "new delhi"

        record = self._risk_lookup.get((state_key, dist_key))

        if record is None:
            logger.warning(
                "Nearest district (%r, %r) for (%.6f, %.6f) has no risk data; "
                "returning neutral fallback.",
                dist_key,
                state_key,
                lat_f,
                lng_f,
            )
            safety_score = 0.0
            risk_category = "Unknown"
            state_name = state_key.title() if state_key else "Unknown"
            district_name = dist_key.title() if dist_key else "Unknown"
        else:
            safety_score = float(record.get("safety_score", 0.0))
            risk_category = str(record.get("risk_category") or self._categorize(safety_score))
            state_name = str(record.get("state", state_key.title()))
            district_name = str(record.get("district", dist_key.title()))

        risk_score = round(1.0 - (float(safety_score) / 100.0), 4)

        return {
            "state": state_name,
            "district": district_name,
            "safety_score": round(float(safety_score), 2),
            "risk_category": risk_category,
            "risk_score": max(0.0, min(1.0, risk_score)),
        }

    # ------------------------------------------------------------------
    # Existing entry point
    # ------------------------------------------------------------------
    def get_navigation_data(self, file_paths: List[str]):
        try:
            # 1. Process Data
            raw_data = self.preprocessor.load_and_combine_datasets(file_paths)
            processed_data = self.preprocessor.engineer_features(raw_data)

            # 2. Train and Predict
            self.model.train(processed_data)
            risk_data = self.model.get_risk_levels(processed_data)

            # 3. Index risk data for coordinate-based lookups.
            self.register_risk_data(risk_data)

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