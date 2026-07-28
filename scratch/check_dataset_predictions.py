import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.inference import InferenceService

service = InferenceService()
df = pd.read_csv('employee_attrition.csv')

# Run prediction batch
pred_df = service.predict_batch(df)

# Print summary of predictions and risk levels
print("Value counts of Attrition_Prediction:")
print(pred_df["Attrition_Prediction"].value_counts())

print("\nValue counts of Risk_Level:")
print(pred_df["Risk_Level"].value_counts())

print("\nCrosstab of Attrition_Prediction vs Risk_Level:")
print(pd.crosstab(pred_df["Attrition_Prediction"], pred_df["Risk_Level"]))

# Find some examples where Attrition_Prediction = 1
print("\nSample records predicted as Attrition_Prediction = 1:")
sample_ones = pred_df[pred_df["Attrition_Prediction"] == 1][["Attrition_Prediction", "Attrition_Probability", "Risk_Level"]].head(10)
print(sample_ones)
