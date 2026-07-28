import streamlit as st
import datetime
from frontend.utils.api_client import APIClient

def render_prediction():
    st.title("Employee Attrition Prediction")
    st.subheader("Evaluate individual attrition risk and receive tailored retention recommendations")

    api = APIClient()

    # Form to group input fields
    with st.form("employee_form"):
        st.write("### Employee Profile Data Entry")
        
        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("#### Demographics & Satisfaction")
            age = st.slider("Age", 18, 100, 35)
            gender = st.selectbox("Gender", ["Female", "Male"])
            marital_status = st.selectbox("Marital Status", ["Single", "Married", "Divorced"])
            distance_from_home = st.slider("Distance From Home (miles)", 1, 30, 5)
            
            st.write("#### Satisfaction Ratings")
            job_satisfaction = st.selectbox("Job Satisfaction (1: Low, 4: Very High)", [1, 2, 3, 4], index=2)
            env_satisfaction = st.selectbox("Environment Satisfaction (1: Low, 4: Very High)", [1, 2, 3, 4], index=2)
            rel_satisfaction = st.selectbox("Relationship Satisfaction (1: Low, 4: Very High)", [1, 2, 3, 4], index=2)
            job_involvement = st.selectbox("Job Involvement (1: Low, 4: Very High)", [1, 2, 3, 4], index=2)
            work_life_balance = st.selectbox("Work-Life Balance (1: Bad, 4: Best)", [1, 2, 3, 4], index=2)

        with col2:
            st.write("#### Job Details & Compensation")
            dept = st.selectbox("Department", ["Research & Development", "Sales", "Human Resources"])
            
            # Restrict job roles depending on department selected
            job_roles = {
                "Research & Development": [
                    "Research Scientist", "Laboratory Technician", "Manufacturing Director", 
                    "Healthcare Representative", "Manager", "Research Director"
                ],
                "Sales": ["Sales Executive", "Sales Representative", "Manager"],
                "Human Resources": ["Human Resources", "Manager"]
            }
            # Fallback list of roles to be safe
            all_roles = [
                "Sales Executive", "Research Scientist", "Laboratory Technician", 
                "Manufacturing Director", "Healthcare Representative", "Manager", 
                "Sales Representative", "Research Director", "Human Resources"
            ]
            
            # Since department is selected, we filter roles dynamically or let them select all.
            # In Streamlit form, dynamically changing a selectbox depending on another in the same form
            # can be tricky without double runs. Letting them select from all_roles is simpler and robust.
            job_role = st.selectbox("Job Role", all_roles)
            job_level = st.slider("Job Level", 1, 5, 2)
            business_travel = st.selectbox("Business Travel Frequency", ["Travel_Rarely", "Travel_Frequently", "Non-Travel"])
            overtime = st.selectbox("Overtime Status", ["No", "Yes"])
            
            st.write("#### Salary & Rates")
            monthly_income = st.number_input("Monthly Income ($)", 1000, 30000, 5000)
            monthly_rate = st.number_input("Monthly Rate ($)", 2000, 30000, 15000)
            daily_rate = st.number_input("Daily Rate ($)", 100, 2000, 800)
            hourly_rate = st.number_input("Hourly Rate ($)", 30, 150, 70)
            percent_salary_hike = st.slider("Percent Salary Hike (%)", 11, 25, 14)
            performance_rating = st.selectbox("Performance Rating", [3, 4], index=0)

        with col3:
            st.write("#### Experience & Tenure")
            total_working_years = st.slider("Total Working Years", 0, 40, 10)
            num_companies = st.slider("Number of Companies Worked At", 0, 9, 2)
            stock_option = st.slider("Stock Option Level", 0, 3, 1)
            training_times = st.slider("Training Times Last Year", 0, 6, 3)
            
            st.write("#### Tenure at Current Employer")
            years_at_company = st.slider("Years At Company", 0, 40, 5)
            years_in_role = st.slider("Years In Current Role", 0, 20, 3)
            years_since_promo = st.slider("Years Since Last Promotion", 0, 15, 1)
            years_with_manager = st.slider("Years With Current Manager", 0, 20, 3)

        submitted = st.form_submit_button("Predict Attrition Risk")

    if submitted:
        # Prepare payload
        payload = {
            "Age": age,
            "BusinessTravel": business_travel,
            "DailyRate": daily_rate,
            "Department": dept,
            "DistanceFromHome": distance_from_home,
            "Education": 3,  # Set default values for features not in inputs but in CSV
            "EducationField": "Life Sciences", # default
            "EnvironmentSatisfaction": env_satisfaction,
            "Gender": gender,
            "HourlyRate": hourly_rate,
            "JobInvolvement": job_involvement,
            "JobLevel": job_level,
            "JobRole": job_role,
            "JobSatisfaction": job_satisfaction,
            "MaritalStatus": marital_status,
            "MonthlyIncome": monthly_income,
            "MonthlyRate": monthly_rate,
            "NumCompaniesWorked": num_companies,
            "OverTime": overtime,
            "PercentSalaryHike": percent_salary_hike,
            "PerformanceRating": performance_rating,
            "RelationshipSatisfaction": rel_satisfaction,
            "StockOptionLevel": stock_option,
            "TotalWorkingYears": total_working_years,
            "TrainingTimesLastYear": training_times,
            "WorkLifeBalance": work_life_balance,
            "YearsAtCompany": years_at_company,
            "YearsInCurrentRole": years_in_role,
            "YearsSinceLastPromotion": years_since_promo,
            "YearsWithCurrManager": years_with_manager
        }

        with st.spinner("Analyzing profile..."):
            result = api.predict(payload)

        # Check for error
        if "error" in result:
            st.error(result["error"])
        elif "validation_error" in result:
            st.error("Validation Error. Please check your inputs.")
            st.json(result["validation_error"])
        else:
            # Display prediction results
            st.markdown("---")
            st.write("### Prediction Results")

            # Risk level color formatting
            risk = result["risk_level"]
            prob = result["attrition_probability"]
            confidence = result["confidence"]
            prediction = result["attrition_prediction"]

            if risk == "Low":
                color = "green"
                status_text = "Low Risk of Attrition"
            elif risk == "Medium":
                color = "orange"
                status_text = "Medium Risk of Attrition"
            else:
                color = "red"
                status_text = "High Risk of Attrition"

            # Create visual cards using html/css
            st.markdown(
                f"""
                <div style="background-color: #f8f9fa; padding: 20px; border-left: 6px solid {color}; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0; color: {color};">{status_text}</h4>
                    <p style="margin: 5px 0 0 0; font-size: 16px; color: #495057;">
                        Probability: <b>{prob * 100:.2f}%</b> &nbsp;|&nbsp; 
                        Confidence: <b>{confidence * 100:.2f}%</b> &nbsp;|&nbsp; 
                        Model Outcome: <b>{"Leave (1)" if prediction == 1 else "Stay (0)"}</b>
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Recommendation section
            st.write("#### Retention Recommendation")
            st.info(result["recommendation"])
