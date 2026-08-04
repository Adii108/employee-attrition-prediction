import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline

class FeatureEngineer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        
        # 1. Income per Total Working Years (avoid division by zero)
        X["Income_WorkingYears_Ratio"] = X["MonthlyIncome"] / (X["TotalWorkingYears"] + 1)
        
        # 2. Promotion Delay
        X["Promotion_Delay"] = X["YearsSinceLastPromotion"]
        
        # 3. Overtime + WorkLifeBalance interaction
        ot_numeric = (X["OverTime"] == "Yes").astype(int)
        X["Overtime_WorkLife_Interaction"] = ot_numeric * (5 - X["WorkLifeBalance"])
        
        # 4. Job Satisfaction * Environment Satisfaction
        X["Satisfaction_Product"] = X["JobSatisfaction"] * X["EnvironmentSatisfaction"]
        
        # 5. Income Band
        X["Income_Band"] = pd.cut(
            X["MonthlyIncome"],
            bins=[-float('inf'), 3000, 7000, 15000, float('inf')],
            labels=["Low", "Medium", "High", "Very High"]
        ).astype(str)
        
        # 6. Experience Band
        X["Experience_Band"] = pd.cut(
            X["TotalWorkingYears"],
            bins=[-float('inf'), 2, 5, 10, 20, float('inf')],
            labels=["Entry", "Junior", "Mid", "Senior", "Executive"]
        ).astype(str)
        
        # 7. Tenure Band
        X["Tenure_Band"] = pd.cut(
            X["YearsAtCompany"],
            bins=[-float('inf'), 2, 5, 10, 20, float('inf')],
            labels=["New", "Junior", "Mid", "Senior", "Loyal"]
        ).astype(str)
        
        # 8. Age Group
        X["Age_Group"] = pd.cut(
            X["Age"],
            bins=[-float('inf'), 25, 35, 45, 55, float('inf')],
            labels=["Young", "Early Career", "Mid Career", "Senior", "Near Retirement"]
        ).astype(str)
        
        # 9. Distance Category
        X["Distance_Category"] = pd.cut(
            X["DistanceFromHome"],
            bins=[-float('inf'), 5, 15, 25, float('inf')],
            labels=["Near", "Moderate", "Far", "Very Far"]
        ).astype(str)
        
        # 10. Combined Satisfaction Score
        X["Combined_Satisfaction"] = X["JobSatisfaction"] + X["EnvironmentSatisfaction"] + X["RelationshipSatisfaction"] + X["WorkLifeBalance"]
        
        # 11. Overall Engagement Score
        X["Overall_Engagement"] = X["JobInvolvement"] + X["PerformanceRating"] + (X["Combined_Satisfaction"] / 4)
        
        # High-risk flags for prediction realism
        X["High_Risk_Flag"] = (((X["JobSatisfaction"] <= 2) | (X["EnvironmentSatisfaction"] <= 2) | (X["WorkLifeBalance"] <= 2)) & (X["OverTime"] == "Yes")).astype(int)
        X["Low_Income_Overtime_Flag"] = ((X["MonthlyIncome"] < 4000) & (X["OverTime"] == "Yes")).astype(int)
        
        return X

def get_preprocessing_pipeline():
    categorical_cols = [
        "BusinessTravel", "Department", "EducationField", "Gender", "JobRole", 
        "MaritalStatus", "OverTime", "Income_Band", "Experience_Band", 
        "Tenure_Band", "Age_Group", "Distance_Category"
    ]
    
    numerical_cols = [
        "Age", "DistanceFromHome", "Education", "EnvironmentSatisfaction", 
        "JobInvolvement", "JobLevel", "JobSatisfaction", "MonthlyIncome", 
        "NumCompaniesWorked", "PercentSalaryHike", "PerformanceRating", 
        "RelationshipSatisfaction", "StockOptionLevel", "TotalWorkingYears", 
        "TrainingTimesLastYear", "WorkLifeBalance", "YearsAtCompany", "YearsInCurrentRole", 
        "YearsSinceLastPromotion", "YearsWithCurrManager", "Income_WorkingYears_Ratio", 
        "Promotion_Delay", "Overtime_WorkLife_Interaction", "Satisfaction_Product", 
        "Combined_Satisfaction", "Overall_Engagement", "High_Risk_Flag", "Low_Income_Overtime_Flag"
    ]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_cols),
            ('cat', OneHotEncoder(handle_unknown='ignore', drop=None), categorical_cols)
        ]
    )
    
    pipeline = Pipeline([
        ('engineer', FeatureEngineer()),
        ('preprocessor', preprocessor)
    ])
    
    return pipeline
