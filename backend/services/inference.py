import os
import json
import pandas as pd
from datetime import datetime
from backend.config import MODELS_DIR
from backend.schemas.employee import EmployeeInput, PredictionResponse
from ml_pipeline.model_loader import ModelLoader
from ml_pipeline.predict import predict_single as ml_predict_single, predict_batch as ml_predict_batch

class InferenceService:
    def __init__(self):
        self.model = None
        self.threshold = 0.5
        self.selected_features = []
        self.model_columns = []
        self.load_artifacts()

    def load_artifacts(self):
        """Loads and updates model state from serialized artifacts folder."""
        self.model, self.threshold = ModelLoader.load_artifacts(MODELS_DIR)
        
        feature_names_path = os.path.join(MODELS_DIR, "feature_names.json")
        if os.path.exists(feature_names_path):
            with open(feature_names_path, "r") as f:
                self.model_columns = json.load(f)
        else:
            self.model_columns = list(getattr(self.model, "feature_names_in_", []))
            
        # Backward compatibility aliases
        self.selected_features = self.model_columns

    def predict_single(self, employee: EmployeeInput) -> PredictionResponse:
        """Runs predictions and calculates SHAP explanation factors for a single employee."""
        res_dict = ml_predict_single(employee.model_dump(), MODELS_DIR)
        
        return PredictionResponse(
            attrition_prediction=res_dict["attrition_prediction"],
            attrition_probability=res_dict["attrition_probability"],
            confidence=res_dict["confidence"],
            risk_level=res_dict["risk_level"],
            recommendation=res_dict["recommendation"],
            timestamp=datetime.utcnow().isoformat() + "Z",
            top_reasons=res_dict["top_reasons"],
            negative_reasons=res_dict.get("negative_reasons", []),
            suggested_actions=res_dict["suggested_actions"],
            retention_priority=res_dict["retention_priority"]
        )

    def predict_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies pipeline and predictions in batches."""
        return ml_predict_batch(df, MODELS_DIR)
