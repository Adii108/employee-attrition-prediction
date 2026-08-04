import os
import numpy as np
import pandas as pd
import shap
import joblib

from ml_pipeline.model_loader import ModelLoader
from ml_pipeline.utils import get_human_readable_feature_name, get_risk_metadata, get_suggested_hr_actions

_explainer = None
_background_data = None

def get_shap_explainer(pipeline):
    """Initializes and caches model-agnostic probability explainer for SHAP explanations."""
    global _explainer, _background_data
    if _explainer is None:
        model = pipeline.named_steps['model']
        preprocessor = pipeline.named_steps['preprocessor']
        
        # Load reference background dataset from original csv
        if os.path.exists("employee_attrition.csv"):
            try:
                df_bg = pd.read_csv("employee_attrition.csv")
                if "Attrition" in df_bg.columns:
                    df_bg = df_bg.drop(columns=["Attrition", "Attrition_Num"], errors="ignore")
                
                # Transform background data
                df_bg_eng = pipeline.named_steps['engineer'].transform(df_bg)
                bg_processed = preprocessor.transform(df_bg_eng)
                if hasattr(bg_processed, "toarray"):
                    bg_processed = bg_processed.toarray()
                
                # Select a small representative sample to optimize explanation speed (under 100ms)
                _background_data = bg_processed[:30]
            except Exception:
                feature_names = preprocessor.get_feature_names_out()
                _background_data = np.zeros((1, len(feature_names)))
        else:
            feature_names = preprocessor.get_feature_names_out()
            _background_data = np.zeros((1, len(feature_names)))
            
        def predict_class1(X):
            # Ensure dense array type for model predictability
            if hasattr(X, "toarray"):
                X = X.toarray()
            return model.predict_proba(X)[:, 1]
            
        # Standard model-agnostic explainer mapping direct probability shifts
        _explainer = shap.Explainer(predict_class1, _background_data)
        
    return _explainer

def explain_prediction(X_raw, pipeline):
    """Generates feature importance reasons using SHAP for a single raw prediction row."""
    try:
        engineer = pipeline.named_steps['engineer']
        preprocessor = pipeline.named_steps['preprocessor']
        
        # Preprocess single record
        df_eng = engineer.transform(X_raw)
        X_processed = preprocessor.transform(df_eng)
        if hasattr(X_processed, "toarray"):
            X_processed = X_processed.toarray()
            
        explainer = get_shap_explainer(pipeline)
        shap_values = explainer(X_processed)
        
        feature_names = preprocessor.get_feature_names_out()
        row_values = shap_values.values[0]
        
        reasons = []
        for name, val in zip(feature_names, row_values):
            # Threshold cutoff to ignore trivial contributors
            if abs(val) > 0.005:
                reasons.append({
                    "name": get_human_readable_feature_name(name),
                    "val": val
                })
                
        # Split positive and negative drivers
        pos_drivers = sorted([r for r in reasons if r["val"] > 0], key=lambda x: x["val"], reverse=True)
        neg_drivers = sorted([r for r in reasons if r["val"] < 0], key=lambda x: x["val"])
        
        pos_reasons = [f"{r['name']} (+{r['val']*100:.0f}%)" for r in pos_drivers[:5]]
        neg_reasons = [f"{r['name']} ({r['val']*100:.0f}%)" for r in neg_drivers[:5]]
        
        return pos_reasons, neg_reasons
    except Exception as e:
        return [f"Unable to generate reasons due to error: {str(e)}"], []

def predict_single(employee_dict: dict, models_dir="models") -> dict:
    """Runs prediction, SHAP explanation, and priority mapping for a single employee dict."""
    pipeline, threshold = ModelLoader.load_artifacts(models_dir)
    
    # Create DataFrame row
    df = pd.DataFrame([employee_dict])
    
    # Run prediction
    probability = float(pipeline.predict_proba(df)[0][1])
    prediction = 1 if probability >= threshold else 0
    confidence = probability if prediction == 1 else (1.0 - probability)
    
    # Get Dynamic risk metadata
    risk_level, retention_priority, recommendation = get_risk_metadata(probability, threshold)
    
    # Calculate SHAP reasons
    pos_reasons, neg_reasons = explain_prediction(df, pipeline)
    
    # Suggested HR actions based on key drivers
    suggested_actions = get_suggested_hr_actions(pos_reasons)
    
    return {
        "attrition_prediction": prediction,
        "attrition_probability": round(probability, 4),
        "confidence": round(confidence, 4),
        "risk_level": risk_level,
        "retention_priority": retention_priority,
        "recommendation": recommendation,
        "top_reasons": pos_reasons,
        "negative_reasons": neg_reasons,
        "suggested_actions": suggested_actions
    }

def predict_batch(df: pd.DataFrame, models_dir="models") -> pd.DataFrame:
    """Runs batch predictions and attaches analytics columns."""
    pipeline, threshold = ModelLoader.load_artifacts(models_dir)
    
    # Make local copy
    output_df = df.copy()
    
    # Run prediction
    probabilities = pipeline.predict_proba(df)[:, 1]
    predictions = (probabilities >= threshold).astype(int)
    
    # Append predictions
    output_df["Attrition_Prediction"] = predictions
    output_df["Attrition_Probability"] = np.round(probabilities, 4)
    output_df["Confidence_Score"] = np.round(
        np.where(predictions == 1, probabilities, 1.0 - probabilities), 4
    )
    
    # Risk Level mapping
    output_df["Risk_Level"] = np.where(
        probabilities < 0.35, "Low", 
        np.where(probabilities < 0.65, "Medium", "High")
    )
    
    return output_df
