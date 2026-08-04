import sys
import os
import numpy as np
import pandas as pd
import joblib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.inference import InferenceService
from backend.schemas.employee import EmployeeInput

def validate_pipeline():
    print("--- STARTING SYSTEMATIC INFERENCE & PROFILE VALIDATION ---")
    
    # 1. Load raw dataset and split
    df = pd.read_csv('employee_attrition.csv')
    df_raw_train, df_raw_test = train_test_split_compat(df)
    
    # Initialize Inference Service
    service = InferenceService()
    
    # Test batch prediction alignment
    batch_predictions_df = service.predict_batch(df_raw_test)
    service_preds = batch_predictions_df["Attrition_Prediction"].values
    service_probs = batch_predictions_df["Attrition_Probability"].values
    
    # Verify predictions directly with saved pipeline
    pipeline = joblib.load(os.path.join("models", "pipeline.pkl"))
    threshold = joblib.load(os.path.join("models", "pipeline.pkl")).threshold
    
    df_test_features = df_raw_test.drop(columns=["Attrition", "Attrition_Num"], errors="ignore")
    ref_probs = pipeline.predict_proba(df_test_features)[:, 1]
    ref_preds = (ref_probs >= threshold).astype(int)
    
    print("Verifying alignment of outputs...")
    pred_matches = np.array_equal(ref_preds, service_preds)
    print(f"  Prediction classes match exactly: {pred_matches}")
    if not pred_matches:
        print("    ERROR: Prediction classes do not match!")
        sys.exit(1)
        
    prob_diff = np.abs(ref_probs - service_probs)
    max_prob_diff = np.max(prob_diff)
    print(f"  Maximum probability deviation: {max_prob_diff:.6f}")
    if max_prob_diff > 1e-4:
        print("    ERROR: Probability deviation is too high!")
        sys.exit(1)
        
    print("\n--- BATCH INFERENCE VERIFIED SUCCESSFULLY ---")
    
    # 2. Run 30 Manually Designed Personas to Validate prediction realism
    print("\n--- STARTING PERSONA REALISM VALIDATION (30 PROFILES) ---")
    profiles = generate_30_personas()
    
    failures = 0
    for idx, p in enumerate(profiles):
        emp_input = EmployeeInput(**p["data"])
        pred_res = service.predict_single(emp_input)
        
        predicted_outcome = "Leave" if pred_res.attrition_prediction == 1 else "Stay"
        expected_outcome = p["expected"]
        
        prob_percent = pred_res.attrition_probability * 100
        
        print(f"Profile #{idx+1:02d} [{p['name']}]:")
        print(f"  Expected: {expected_outcome} | Predicted: {predicted_outcome} (Prob: {prob_percent:.1f}%, Risk: {pred_res.risk_level})")
        print(f"  Top Drivers: {', '.join(pred_res.top_reasons)}")
        
        # Realism check assertions
        if expected_outcome == "Leave" and pred_res.attrition_prediction != 1:
            print("  [WARNING] Fails realism check. Expected 'Leave' but predicted 'Stay'.")
            failures += 1
        elif expected_outcome == "Stay" and pred_res.attrition_prediction != 0:
            print("  [WARNING] Fails realism check. Expected 'Stay' but predicted 'Leave'.")
            failures += 1
            
    print(f"\nPersona Validation Summary: {len(profiles) - failures}/{len(profiles)} passed realism guidelines.")
    if failures > 5:
        print("    ERROR: Too many realism failures! Prediction model is not sensitive enough.")
        sys.exit(1)
    else:
        print("\n--- VALIDATION SUCCESSFUL: Prediction quality is highly realistic and responsive! ---")

def train_test_split_compat(df):
    """Splits original raw DataFrame identically to training stratified split."""
    if "Attrition" in df.columns:
        y = (df["Attrition"] == "Yes").astype(int)
    else:
        y = df["Attrition_Num"]
    
    # Split indexes
    np.random.seed(42)
    shuffled_indices = np.random.permutation(len(df))
    test_set_size = int(len(df) * 0.2)
    
    # Simple stratified selection
    test_indices = []
    class_0_indices = [i for i in shuffled_indices if y.iloc[i] == 0]
    class_1_indices = [i for i in shuffled_indices if y.iloc[i] == 1]
    
    test_0_size = int(test_set_size * (len(class_0_indices) / len(df)))
    test_1_size = test_set_size - test_0_size
    
    test_indices.extend(class_0_indices[:test_0_size])
    test_indices.extend(class_1_indices[:test_1_size])
    
    train_indices = [i for i in shuffled_indices if i not in test_indices]
    
    return df.iloc[train_indices], df.iloc[test_indices]

def generate_30_personas():
    """Constructs 30 distinct employee profiles covering extreme risk and healthy scenarios."""
    base_stay = {
        "Age": 38, "BusinessTravel": "Travel_Rarely", "DailyRate": 800, "Department": "Research & Development",
        "DistanceFromHome": 5, "Education": 3, "EducationField": "Life Sciences", "EnvironmentSatisfaction": 3,
        "Gender": "Male", "HourlyRate": 70, "JobInvolvement": 3, "JobLevel": 2, "JobRole": "Research Scientist",
        "JobSatisfaction": 3, "MaritalStatus": "Married", "MonthlyIncome": 6000, "MonthlyRate": 15000,
        "NumCompaniesWorked": 1, "OverTime": "No", "PercentSalaryHike": 14, "PerformanceRating": 3,
        "RelationshipSatisfaction": 3, "StockOptionLevel": 1, "TotalWorkingYears": 10, "TrainingTimesLastYear": 3,
        "WorkLifeBalance": 3, "YearsAtCompany": 8, "YearsInCurrentRole": 5, "YearsSinceLastPromotion": 1, "YearsWithCurrManager": 5
    }
    
    base_leave = {
        "Age": 24, "BusinessTravel": "Travel_Frequently", "DailyRate": 400, "Department": "Sales",
        "DistanceFromHome": 25, "Education": 2, "EducationField": "Technical Degree", "EnvironmentSatisfaction": 1,
        "Gender": "Male", "HourlyRate": 35, "JobInvolvement": 1, "JobLevel": 1, "JobRole": "Sales Representative",
        "JobSatisfaction": 1, "MaritalStatus": "Single", "MonthlyIncome": 2200, "MonthlyRate": 8000,
        "NumCompaniesWorked": 3, "OverTime": "Yes", "PercentSalaryHike": 11, "PerformanceRating": 3,
        "RelationshipSatisfaction": 1, "StockOptionLevel": 0, "TotalWorkingYears": 2, "TrainingTimesLastYear": 1,
        "WorkLifeBalance": 1, "YearsAtCompany": 1, "YearsInCurrentRole": 1, "YearsSinceLastPromotion": 0, "YearsWithCurrManager": 1
    }
    
    personas = []
    
    # 1-5: Extreme Risk / Leave profiles
    p1 = base_leave.copy()
    personas.append({"name": "Overworked Junior Representative", "data": p1, "expected": "Leave"})
    
    p2 = base_stay.copy()
    p2.update({"JobSatisfaction": 1, "EnvironmentSatisfaction": 1, "OverTime": "Yes", "WorkLifeBalance": 1, "MonthlyIncome": 2500, "DistanceFromHome": 28})
    personas.append({"name": "Highly Dissatisfied Long Commute", "data": p2, "expected": "Leave"})
    
    p3 = base_stay.copy()
    p3.update({"Age": 21, "TotalWorkingYears": 1, "YearsAtCompany": 1, "OverTime": "Yes", "MonthlyIncome": 1900, "JobSatisfaction": 1})
    personas.append({"name": "Low Salary Overtime Intern", "data": p3, "expected": "Leave"})
    
    p4 = base_stay.copy()
    p4.update({"YearsSinceLastPromotion": 8, "YearsAtCompany": 8, "JobSatisfaction": 1, "PercentSalaryHike": 11})
    personas.append({"name": "Stagnant Role Promotion Delay", "data": p4, "expected": "Leave"})
    
    p5 = base_leave.copy()
    p5.update({"BusinessTravel": "Travel_Frequently", "DistanceFromHome": 29, "NumCompaniesWorked": 6})
    personas.append({"name": "Frequent Traveler Job Hopper", "data": p5, "expected": "Leave"})

    # 6-15: Dissatisfied and Overworked variations (Leave)
    for i in range(10):
        p = base_leave.copy()
        p["Age"] = 22 + i
        p["MonthlyIncome"] = 2000 + (i * 100)
        p["DistanceFromHome"] = 20 + i
        personas.append({"name": f"Dissatisfied Variation #{i+1}", "data": p, "expected": "Leave"})

    # 16-20: High Performer / High Salary (Stay)
    p16 = base_stay.copy()
    p16.update({"MonthlyIncome": 18000, "JobLevel": 5, "JobRole": "Manager", "TotalWorkingYears": 25, "YearsAtCompany": 15})
    personas.append({"name": "Senior Executive Director", "data": p16, "expected": "Stay"})
    
    p17 = base_stay.copy()
    p17.update({"PerformanceRating": 4, "PercentSalaryHike": 24, "JobSatisfaction": 4, "EnvironmentSatisfaction": 4})
    personas.append({"name": "Happy Star Performer", "data": p17, "expected": "Stay"})
    
    p18 = base_stay.copy()
    p18.update({"WorkLifeBalance": 4, "RelationshipSatisfaction": 4, "JobSatisfaction": 4})
    personas.append({"name": "Perfect Work-Life Balance", "data": p18, "expected": "Stay"})
    
    p19 = base_stay.copy()
    p19.update({"Age": 60, "TotalWorkingYears": 38, "YearsAtCompany": 30, "YearsInCurrentRole": 12, "JobSatisfaction": 4})
    personas.append({"name": "Loyal Senior Vet Near Retirement", "data": p19, "expected": "Stay"})
    
    p20 = base_stay.copy()
    p20.update({"StockOptionLevel": 3, "MonthlyIncome": 12000, "EnvironmentSatisfaction": 4})
    personas.append({"name": "Highly Equity Vested Manager", "data": p20, "expected": "Stay"})

    # 21-30: Healthy variations (Stay)
    for i in range(10):
        p = base_stay.copy()
        p["Age"] = 35 + i
        p["MonthlyIncome"] = 5500 + (i * 200)
        p["DistanceFromHome"] = 2 + i
        p["YearsAtCompany"] = 5 + i
        personas.append({"name": f"Healthy Variation #{i+1}", "data": p, "expected": "Stay"})
        
    return personas

if __name__ == "__main__":
    validate_pipeline()
