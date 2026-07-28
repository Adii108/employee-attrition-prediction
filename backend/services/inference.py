import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from backend.config import (
    BEST_MODEL_PATH, SCALER_PATH, SELECTED_FEATURES_PATH, 
    MODEL_COLUMNS_PATH, METRICS_JSON_PATH
)
from backend.schemas.employee import EmployeeInput, PredictionResponse

class InferenceService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.selected_features = None
        self.model_columns = None
        self.load_artifacts()

    def load_artifacts(self):
        """Loads all serialized model and preprocessing objects."""
        if not os.path.exists(BEST_MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at {BEST_MODEL_PATH}")
        if not os.path.exists(SCALER_PATH):
            raise FileNotFoundError(f"Scaler file not found at {SCALER_PATH}")
        if not os.path.exists(SELECTED_FEATURES_PATH):
            raise FileNotFoundError(f"Selected features file not found at {SELECTED_FEATURES_PATH}")
        if not os.path.exists(MODEL_COLUMNS_PATH):
            raise FileNotFoundError(f"Model columns file not found at {MODEL_COLUMNS_PATH}")

        self.model = joblib.load(BEST_MODEL_PATH)
        self.scaler = joblib.load(SCALER_PATH)
        self.selected_features = joblib.load(SELECTED_FEATURES_PATH)
        self.model_columns = joblib.load(MODEL_COLUMNS_PATH)

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies exact feature engineering, column selection, encoding and scaling."""
        df_feat = df.copy()

        # Remove targets or dropped columns if present in batch uploads
        cols_to_drop = ["EmployeeCount", "EmployeeNumber", "Over18", "StandardHours", "Attrition", "Attrition_Num"]
        existing_cols = [c for c in cols_to_drop if c in df_feat.columns]
        if existing_cols:
            df_feat.drop(columns=existing_cols, inplace=True)

        # 1. Feature Engineering (using training-set quantile definitions for MonthlyIncome qcut)
        # Bins: [1009.0, 2911.0, 4919.0, 8379.0, 19999.0] -> extend boundaries to handle extreme values
        income_bins = [-float('inf'), 2911.0, 4919.0, 8379.0, float('inf')]
        df_feat["Income_Group"] = pd.cut(
            df_feat["MonthlyIncome"], 
            bins=income_bins, 
            labels=["Low", "Medium", "High", "Very High"]
        )

        df_feat["Experience_Group"] = pd.cut(
            df_feat["TotalWorkingYears"], 
            bins=[-1, 2, 5, 10, 20, np.inf], 
            labels=["Entry", "Junior", "Mid", "Senior", "Executive"]
        )

        df_feat["Promotion_Delay_Flag"] = (
            (df_feat["YearsSinceLastPromotion"] >= 3) & 
            (df_feat["YearsAtCompany"] >= 3)
        ).astype(int)

        df_feat["Frequent_Traveller_Flag"] = (df_feat["BusinessTravel"] == "Travel_Frequently").astype(int)

        df_feat["Early_Career_Flag"] = (
            (df_feat["Age"] < 30) & 
            (df_feat["YearsAtCompany"] < 3)
        ).astype(int)

        # 2. Select the modeling features
        X = df_feat[self.selected_features]

        # 3. Categorical vs Numerical identification
        X_cat = X.select_dtypes(include=[object, "category"]).columns.tolist()
        X_num = X.select_dtypes(include=[np.number]).columns.tolist()

        # 4. One-hot encoding
        X_encoded = pd.get_dummies(X, columns=X_cat, drop_first=True)

        # 5. Align with training column layout (Zero fill missing columns)
        X_encoded = X_encoded.reindex(columns=self.model_columns, fill_value=0)

        # 6. Apply Standard Scaling on numerical variables only
        X_encoded[X_num] = self.scaler.transform(X_encoded[X_num])

        return X_encoded

    def predict_single(self, employee: EmployeeInput) -> PredictionResponse:
        """Runs predictions for a single employee record."""
        # Convert Pydantic object to dataframe
        data_dict = employee.model_dump()
        df = pd.DataFrame([data_dict])
        
        # Preprocess
        preprocessed_df = self.preprocess(df)
        
        # Run inference
        probability = float(self.model.predict_proba(preprocessed_df)[0][1])
        threshold = getattr(self.model, "threshold", 0.5)
        prediction = 1 if probability >= threshold else 0
        
        # Confidence score (Probability of the predicted class)
        confidence = probability if prediction == 1 else (1.0 - probability)
        
        # Determine Risk Level and Recommendation
        if probability < 0.3:
            risk_level = "Low"
            recommendation = (
                "Employee shows low risk of attrition. Maintain current engagement "
                "levels, recognize contributions, and continue periodic performance feedback."
            )
        elif probability < 0.6:
            risk_level = "Medium"
            recommendation = (
                "Employee shows medium risk of attrition. Recommend checking work-life "
                "balance, evaluating career growth opportunities, and checking department tenure."
            )
        else:
            risk_level = "High"
            recommendation = (
                "Employee is at high risk of attrition! Action recommended: Schedule a 1-on-1 "
                "retention review, check for excessive overtime, evaluate compensation competitive index, "
                "and discuss clear path for professional development."
            )
            
        return PredictionResponse(
            attrition_prediction=prediction,
            attrition_probability=round(probability, 4),
            confidence=round(confidence, 4),
            risk_level=risk_level,
            recommendation=recommendation,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

    def predict_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """Runs predictions on a dataframe batch and appends prediction columns."""
        # Make a copy to avoid side-effects
        output_df = df.copy()
        
        # Preprocess
        preprocessed_df = self.preprocess(df)
        
        # Run inference
        probabilities = self.model.predict_proba(preprocessed_df)[:, 1]
        threshold = getattr(self.model, "threshold", 0.5)
        predictions = (probabilities >= threshold).astype(int)
        
        # Add prediction columns
        output_df["Attrition_Prediction"] = predictions
        output_df["Attrition_Probability"] = np.round(probabilities, 4)
        output_df["Confidence_Score"] = np.round(
            np.where(predictions == 1, probabilities, 1.0 - probabilities), 4
        )
        
        # Set Risk levels
        output_df["Risk_Level"] = np.where(
            probabilities < 0.3, "Low", 
            np.where(probabilities < 0.6, "Medium", "High")
        )
        
        return output_df
