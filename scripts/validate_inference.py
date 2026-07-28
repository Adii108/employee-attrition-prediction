import sys
import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

# Add current workspace directory to python path to import backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.inference import InferenceService

def validate_pipeline():
    print("--- STARTING INFERENCE VALIDATION ---")
    
    # 1. Re-run original pipeline split for comparison
    df = pd.read_csv('employee_attrition.csv')
    
    # Pre-split drops
    cols_to_drop = ["EmployeeCount", "EmployeeNumber", "Over18", "StandardHours"]
    df.drop(columns=cols_to_drop, inplace=True)
    
    # Feature engineering
    df_feat = df.copy()
    df_feat["Income_Group"] = pd.qcut(df_feat["MonthlyIncome"], q=4, labels=["Low", "Medium", "High", "Very High"])
    df_feat["Experience_Group"] = pd.cut(df_feat["TotalWorkingYears"], 
                                         bins=[-1, 2, 5, 10, 20, np.inf], 
                                         labels=["Entry", "Junior", "Mid", "Senior", "Executive"])
    df_feat["Promotion_Delay_Flag"] = ((df_feat["YearsSinceLastPromotion"] >= 3) & (df_feat["YearsAtCompany"] >= 3)).astype(int)
    df_feat["Frequent_Traveller_Flag"] = (df_feat["BusinessTravel"] == "Travel_Frequently").astype(int)
    df_feat["Early_Career_Flag"] = ((df_feat["Age"] < 30) & (df_feat["YearsAtCompany"] < 3)).astype(int)
    df_feat["Attrition_Num"] = df_feat["Attrition"].map({"Yes": 1, "No": 0})

    # Load artifacts
    service = InferenceService()
    
    # Modeling prep
    X = df_feat[service.selected_features]
    y = df_feat["Attrition_Num"]
    
    X_cat = X.select_dtypes(include=[object, "category"]).columns.tolist()
    X_num = X.select_dtypes(include=[np.number]).columns.tolist()
    
    X_encoded = pd.get_dummies(X, columns=X_cat, drop_first=True)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42, stratify=y)
    
    # Scale comparison reference
    scaler_ref = StandardScaler()
    X_train[X_num] = scaler_ref.fit_transform(X_train[X_num])
    X_test[X_num] = scaler_ref.transform(X_test[X_num])
    
    # Load model and verify reference predictions
    ref_preds = service.model.predict(X_test)
    ref_probs = service.model.predict_proba(X_test)[:, 1]
    
    # 2. Run Inference using InferenceService (Simulating batch prediction uploads)
    # Split the original raw df (df) into train and test splits to test inference on unseen raw records
    df_raw_train, df_raw_test = train_test_split(df, test_size=0.2, random_state=42, stratify=df["Attrition"].map({"Yes": 1, "No": 0}))
    
    # Predict using inference service
    batch_predictions_df = service.predict_batch(df_raw_test)
    
    service_preds = batch_predictions_df["Attrition_Prediction"].values
    service_probs = batch_predictions_df["Attrition_Probability"].values
    
    # 3. Perform Assertions
    print("\nVerifying alignment of outputs...")
    
    # Check predictions
    pred_matches = np.array_equal(ref_preds, service_preds)
    print(f"  Prediction classes match exactly: {pred_matches}")
    if not pred_matches:
        mismatches = np.where(ref_preds != service_preds)[0]
        print(f"    WARNING: {len(mismatches)} prediction class mismatches found!")
        sys.exit(1)
        
    # Check probabilities (allowing tiny rounding difference due to round(x, 4) in prediction)
    prob_diff = np.abs(ref_probs - service_probs)
    max_prob_diff = np.max(prob_diff)
    print(f"  Maximum probability deviation: {max_prob_diff:.6f}")
    
    # Max difference should be <= 0.0001 due to rounding to 4 decimals in API, otherwise <= 1e-7
    if max_prob_diff > 1e-4:
        print("    WARNING: Probability deviation is too high!")
        sys.exit(1)
        
    print("\n--- VALIDATION SUCCESSFUL: Predictions and probability scores match exactly! ---")

if __name__ == "__main__":
    validate_pipeline()
