from pydantic import BaseModel, Field, field_validator
from typing import Literal, Dict, List
from datetime import datetime

class EmployeeInput(BaseModel):
    Age: int = Field(..., ge=18, le=100, description="Age of the employee")
    BusinessTravel: Literal["Travel_Rarely", "Travel_Frequently", "Non-Travel"] = Field(..., description="Frequency of business travel")
    DailyRate: int = Field(..., ge=0, description="Daily billing rate")
    Department: Literal["Research & Development", "Sales", "Human Resources"] = Field(..., description="Employee's department")
    DistanceFromHome: int = Field(..., ge=0, description="Distance from home in miles")
    Education: int = Field(..., ge=1, le=5, description="Education level (1: Below College, 5: Doctor)")
    EducationField: Literal["Life Sciences", "Medical", "Marketing", "Technical Degree", "Other", "Human Resources"] = Field(..., description="Field of education")
    EnvironmentSatisfaction: int = Field(..., ge=1, le=4, description="Environment satisfaction rating (1: Low, 4: Very High)")
    Gender: Literal["Female", "Male"] = Field(..., description="Gender of the employee")
    HourlyRate: int = Field(..., ge=0, description="Hourly billing rate")
    JobInvolvement: int = Field(..., ge=1, le=4, description="Job involvement rating (1: Low, 4: Very High)")
    JobLevel: int = Field(..., ge=1, le=5, description="Job level inside organization")
    JobRole: Literal[
        "Sales Executive", "Research Scientist", "Laboratory Technician", 
        "Manufacturing Director", "Healthcare Representative", "Manager", 
        "Sales Representative", "Research Director", "Human Resources"
    ] = Field(..., description="Job role of the employee")
    JobSatisfaction: int = Field(..., ge=1, le=4, description="Job satisfaction rating (1: Low, 4: Very High)")
    MaritalStatus: Literal["Single", "Married", "Divorced"] = Field(..., description="Marital status")
    MonthlyIncome: int = Field(..., ge=0, description="Monthly salary in USD")
    MonthlyRate: int = Field(..., ge=0, description="Monthly rate in USD")
    NumCompaniesWorked: int = Field(..., ge=0, description="Number of companies worked at previously")
    OverTime: Literal["Yes", "No"] = Field(..., description="Whether the employee works overtime")
    PercentSalaryHike: int = Field(..., ge=0, description="Percentage of last salary increase")
    PerformanceRating: int = Field(..., ge=1, le=4, description="Performance rating (1: Low, 4: Outstanding)")
    RelationshipSatisfaction: int = Field(..., ge=1, le=4, description="Relationship satisfaction rating (1: Low, 4: Very High)")
    StockOptionLevel: int = Field(..., ge=0, le=3, description="Stock option level")
    TotalWorkingYears: int = Field(..., ge=0, description="Total years of work experience")
    TrainingTimesLastYear: int = Field(..., ge=0, description="Training times last year")
    WorkLifeBalance: int = Field(..., ge=1, le=4, description="Work-life balance rating (1: Bad, 4: Best)")
    YearsAtCompany: int = Field(..., ge=0, description="Total years at current company")
    YearsInCurrentRole: int = Field(..., ge=0, description="Years in current role")
    YearsSinceLastPromotion: int = Field(..., ge=0, description="Years since last promotion")
    YearsWithCurrManager: int = Field(..., ge=0, description="Years under current manager")

    # Custom validator to handle uppercase or lowercase checks if needed
    @field_validator("BusinessTravel", "Department", "EducationField", "Gender", "JobRole", "MaritalStatus", "OverTime", mode="before")
    @classmethod
    def strip_and_capitalize(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

class PredictionResponse(BaseModel):
    attrition_prediction: int = Field(..., description="Predicted attrition status (0: No, 1: Yes)")
    attrition_probability: float = Field(..., description="Probability of attrition (0.0 to 1.0)")
    confidence: float = Field(..., description="Confidence score of the prediction (0.0 to 1.0)")
    risk_level: str = Field(..., description="Risk level categorisation (Low, Medium, High)")
    recommendation: str = Field(..., description="HR retention recommendation message")
    timestamp: str = Field(..., description="ISO 8601 timestamp of request execution")
    top_reasons: List[str] = Field(default=[], description="Top drivers increasing attrition probability")
    negative_reasons: List[str] = Field(default=[], description="Top drivers reducing attrition probability")
    suggested_actions: List[str] = Field(default=[], description="Suggested retention actions for HR managers")
    retention_priority: str = Field(default="LOW", description="Retention action priority rating (LOW, MEDIUM, HIGH)")

class ModelInfoResponse(BaseModel):
    best_model_name: str = Field(..., description="Name of the best performing model loaded")
    selected_features: List[str] = Field(..., description="List of top features used by the model")
    metrics: Dict[str, float] = Field(..., description="Evaluation metrics of the loaded model")

class ModelCompareResponse(BaseModel):
    best_model_name: str = Field(..., description="The primary model used for inference")
    models: Dict[str, Dict[str, float]] = Field(..., description="Comparison metrics for all models")
