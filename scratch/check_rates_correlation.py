import pandas as pd

# Load data
df = pd.read_csv("employee_attrition.csv")

rate_cols = ["MonthlyIncome", "MonthlyRate", "DailyRate", "HourlyRate"]
sub_df = df[rate_cols]

# Calculate correlation matrix
corr_matrix = sub_df.corr()
print("Correlation Matrix between Pay Columns:")
print(corr_matrix)

# Print some basic stats
print("\nDescriptive statistics:")
print(sub_df.describe().T)

# Check correlation with Attrition
df["Attrition_Num"] = (df["Attrition"] == "Yes").astype(int)
attrition_corr = df[rate_cols + ["Attrition_Num"]].corr()["Attrition_Num"]
print("\nCorrelation with Attrition:")
print(attrition_corr)
