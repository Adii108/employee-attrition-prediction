import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.inference import InferenceService
from backend.schemas.employee import EmployeeInput

service = InferenceService()
print("Loaded model:", service.model)
print("Model threshold:", getattr(service.model, "threshold", None))

# Test with a dummy input that should trigger high attrition (overtime, low income, frequent travel, etc.)
payload = {
    "Age": 25,
    "BusinessTravel": "Travel_Frequently",
    "DailyRate": 500,
    "Department": "Sales",
    "DistanceFromHome": 25,
    "Education": 3,
    "EducationField": "Life Sciences",
    "EnvironmentSatisfaction": 1,
    "Gender": "Male",
    "HourlyRate": 50,
    "JobInvolvement": 1,
    "JobLevel": 1,
    "JobRole": "Sales Representative",
    "JobSatisfaction": 1,
    "MaritalStatus": "Single",
    "MonthlyIncome": 1500,
    "MonthlyRate": 10000,
    "NumCompaniesWorked": 5,
    "OverTime": "Yes",
    "PercentSalaryHike": 12,
    "PerformanceRating": 3,
    "RelationshipSatisfaction": 1,
    "StockOptionLevel": 0,
    "TotalWorkingYears": 1,
    "TrainingTimesLastYear": 1,
    "WorkLifeBalance": 1,
    "YearsAtCompany": 1,
    "YearsInCurrentRole": 1,
    "YearsSinceLastPromotion": 1,
    "YearsWithCurrManager": 1
}

emp = EmployeeInput(**payload)
res = service.predict_single(emp)
print("\nPrediction Response:")
print(res.model_dump())
