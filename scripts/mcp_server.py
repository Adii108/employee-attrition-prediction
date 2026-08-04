import os
import sys

# Add root folder to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("[ERROR] Model Context Protocol (MCP) SDK not installed. Run: pip install mcp")
    sys.exit(1)

from backend.schemas.employee import EmployeeInput
from backend.services.inference import InferenceService

# 1. Initialize FastMCP Server
mcp = FastMCP("IBM Attrition Analytics Server")
service = InferenceService()

# 2. Expose the prediction model as a Tool for AI assistants
@mcp.tool()
def analyze_employee_attrition_risk(
    age: int,
    business_travel: str,
    department: str,
    distance_from_home: int,
    environment_satisfaction: int,
    gender: str,
    job_involvement: int,
    job_level: int,
    job_role: str,
    job_satisfaction: int,
    marital_status: str,
    monthly_income: int,
    overtime: str,
    percent_salary_hike: int,
    performance_rating: int,
    relationship_satisfaction: int,
    stock_option_level: int,
    total_working_years: int,
    training_times_last_year: int,
    work_life_balance: int,
    years_at_company: int,
    years_in_current_role: int,
    years_since_last_promotion: int,
    years_with_manager: int
) -> str:
    """
    Submits a single employee's profile to predict their attrition risk.
    Returns the prediction category, probability, SHAP-derived positive/negative risk drivers, and suggested HR actions.
    """
    payload = {
        "Age": age,
        "BusinessTravel": business_travel,
        "DailyRate": 800, # Ignored redundant rate
        "Department": department,
        "DistanceFromHome": distance_from_home,
        "Education": 3,
        "EducationField": "Life Sciences",
        "EnvironmentSatisfaction": environment_satisfaction,
        "Gender": gender,
        "HourlyRate": 70, # Ignored redundant rate
        "JobInvolvement": job_involvement,
        "JobLevel": job_level,
        "JobRole": job_role,
        "JobSatisfaction": job_satisfaction,
        "MaritalStatus": marital_status,
        "MonthlyIncome": monthly_income,
        "MonthlyRate": 15000, # Ignored redundant rate
        "NumCompaniesWorked": 1,
        "OverTime": overtime,
        "PercentSalaryHike": percent_salary_hike,
        "PerformanceRating": performance_rating,
        "RelationshipSatisfaction": relationship_satisfaction,
        "StockOptionLevel": stock_option_level,
        "TotalWorkingYears": total_working_years,
        "TrainingTimesLastYear": training_times_last_year,
        "WorkLifeBalance": work_life_balance,
        "YearsAtCompany": years_at_company,
        "YearsInCurrentRole": years_in_current_role,
        "YearsSinceLastPromotion": years_since_last_promotion,
        "YearsWithCurrManager": years_with_manager
    }
    
    try:
        emp = EmployeeInput(**payload)
        res = service.predict_single(emp)
        import json
        return json.dumps(res.model_dump(), indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed running prediction tool: {str(e)}"}, indent=2)

if __name__ == "__main__":
    # Runs the stdio-based MCP server by default
    mcp.run()
