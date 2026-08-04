import os
import json
import numpy as np

def get_human_readable_feature_name(col_name: str) -> str:
    """Cleans machine learning feature names for business UI display."""
    name = col_name
    if name.startswith("num__"):
        name = name[5:]
    elif name.startswith("cat__"):
        name = name[5:]
    
    # Strip common encoding suffixes
    if name.endswith("_Yes"):
        name = name[:-4]
    
    mapping = {
        "Age": "Age",
        "OverTime": "Overtime",
        "MonthlyIncome": "Monthly Income",
        "DistanceFromHome": "Distance From Home",
        "JobSatisfaction": "Job Satisfaction",
        "EnvironmentSatisfaction": "Environment Satisfaction",
        "WorkLifeBalance": "Work-Life Balance",
        "JobInvolvement": "Job Involvement",
        "TotalWorkingYears": "Total Working Years",
        "YearsAtCompany": "Years At Company",
        "YearsSinceLastPromotion": "Years Since Last Promotion",
        "YearsWithCurrManager": "Years Under Current Manager",
        "PercentSalaryHike": "Percent Salary Hike",
        "RelationshipSatisfaction": "Relationship Satisfaction",
        "NumCompaniesWorked": "Num Companies Worked",
        "Income_WorkingYears_Ratio": "Income-to-Experience Ratio",
        "Promotion_Delay": "Promotion Delay",
        "Overtime_WorkLife_Interaction": "Overtime & Work-Life Conflict",
        "Satisfaction_Product": "Job & Environment Dissatisfaction",
        "Combined_Satisfaction": "Combined Satisfaction Score",
        "Overall_Engagement": "Overall Engagement Score",
        "High_Risk_Flag": "High Attrition Risk Profile",
        "Low_Income_Overtime_Flag": "Low Pay & High Overtime Work"
    }
    
    for key, val in mapping.items():
        if key in name:
            return val
            
    return name.replace("_", " ").title()

def get_suggested_hr_actions(top_reasons: list) -> list:
    """Generates targeted retention action plans based on prediction drivers."""
    actions = []
    reason_actions = {
        "Overtime": "Reduce overtime hours and evaluate workload distribution",
        "Monthly Income": "Conduct a salary review and consider market competitive adjustment",
        "Job Satisfaction": "Schedule a 1-on-1 career development review with the manager",
        "Environment Satisfaction": "Evaluate physical workspace conditions and team chemistry",
        "Work-Life Balance": "Introduce flexible working options or work-from-home days",
        "Distance From Home": "Discuss commute options, travel allowance, or remote work",
        "Promotion Delay": "Assess career progression timeline and define a clear advancement path",
        "Years Under Current Manager": "Facilitate communication check-in or management styling review",
        "Job Involvement": "Involve employee in key projects or decision-making opportunities"
    }
    
    for reason in top_reasons:
        for keyword, action in reason_actions.items():
            if keyword.lower() in reason.lower() and action not in actions:
                actions.append(action)
                
    # Fallback actions
    if not actions:
        actions.append("Schedule a proactive 1-on-1 retention review")
        actions.append("Conduct an engagement survey to identify hidden concerns")
        
    return actions[:5]

def get_risk_metadata(probability: float, threshold: float) -> tuple:
    """Categorizes risk levels and recommendations dynamically using optimized threshold."""
    # User requested specific boundaries:
    # 0-35% Low Risk
    # 35-65% Medium Risk
    # 65-100% High Risk
    if probability < 0.35:
        risk_level = "Low"
        retention_priority = "LOW"
        recommendation = (
            "Employee shows low risk of attrition. Maintain current engagement "
            "levels, recognize contributions, and continue periodic performance feedback."
        )
    elif probability < 0.65:
        risk_level = "Medium"
        retention_priority = "MEDIUM"
        recommendation = (
            "Employee shows medium risk of attrition. Recommend checking work-life "
            "balance, evaluating career growth opportunities, and checking department tenure."
        )
    else:
        risk_level = "High"
        retention_priority = "HIGH"
        recommendation = (
            "Employee is at high risk of attrition! Action recommended: Schedule a 1-on-1 "
            "retention review, check for excessive overtime, evaluate compensation competitive index, "
            "and discuss clear path for professional development."
        )
        
    return risk_level, retention_priority, recommendation
