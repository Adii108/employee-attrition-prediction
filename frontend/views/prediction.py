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
            "DailyRate": 800,  # Default (feature removed from model)
            "Department": dept,
            "DistanceFromHome": distance_from_home,
            "Education": 3,  # Set default values for features not in inputs but in CSV
            "EducationField": "Life Sciences", # default
            "EnvironmentSatisfaction": env_satisfaction,
            "Gender": gender,
            "HourlyRate": 70,  # Default (feature removed from model)
            "JobInvolvement": job_involvement,
            "JobLevel": job_level,
            "JobRole": job_role,
            "JobSatisfaction": job_satisfaction,
            "MaritalStatus": marital_status,
            "MonthlyIncome": monthly_income,
            "MonthlyRate": 15000,  # Default (feature removed from model)
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
            st.write("### 📊 Retention Analytics Dashboard")

            risk = result.get("risk_level", "Low")
            prob = result.get("attrition_probability", 0.0)
            confidence = result.get("confidence", 0.5)
            prediction = result.get("attrition_prediction", 0)
            retention_priority = result.get("retention_priority", "LOW")
            top_reasons = result.get("top_reasons", [])
            negative_reasons = result.get("negative_reasons", [])
            suggested_actions = result.get("suggested_actions", [])

            if risk == "Low":
                color = "#2ec4b6"
                status_text = "Low Risk of Attrition"
            elif risk == "Medium":
                color = "#ff9f1c"
                status_text = "Medium Risk of Attrition"
            else:
                color = "#e71d36"
                status_text = "High Risk of Attrition"

            # 3-column key metrics display
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric(
                    label="Prediction Outcome", 
                    value="Likely to Leave" if prediction == 1 else "Likely to Stay",
                    delta="Requires Attention!" if prediction == 1 else "Healthy Status",
                    delta_color="inverse" if prediction == 1 else "normal"
                )
            with m2:
                st.metric(
                    label="Attrition Probability", 
                    value=f"{prob * 100:.1f}%",
                    delta=f"Confidence: {confidence * 100:.1f}%"
                )
            with m3:
                st.metric(
                    label="Retention Priority", 
                    value=retention_priority,
                    delta=f"Risk Category: {risk}",
                    delta_color="inverse" if risk == "High" else "normal"
                )

            # Styled alert box
            st.markdown(
                f"""
                <div style="background-color: #f8f9fa; padding: 18px; border-left: 6px solid {color}; border-radius: 4px; margin-bottom: 25px;">
                    <h4 style="margin: 0 0 8px 0; color: {color}; font-weight: 600;">{status_text}</h4>
                    <p style="margin: 0; font-size: 14.5px; line-height: 1.5; color: #495057;">
                        {result.get("recommendation", "")}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Two columns: Reasons vs Actions
            c1, c2 = st.columns(2)
            with c1:
                st.write("#### 🔍 Top Attrition Drivers (SHAP)")
                if prediction == 1:
                    st.write("Below are the primary factors contributing to this employee's risk of leaving:")
                    for reason in top_reasons:
                        st.markdown(f"🔴 **{reason}**")
                else:
                    st.write("Below are the positive factors helping retain this employee, followed by risk factors:")
                    if negative_reasons:
                        for reason in negative_reasons:
                            st.markdown(f"🟢 **{reason}**")
                    if top_reasons:
                        st.caption("Minor active risk factors:")
                        for reason in top_reasons:
                            st.markdown(f"⚠️ {reason}")
                    if not negative_reasons and not top_reasons:
                        st.info("No dominant attrition or retention factors detected.")

            with c2:
                st.write("#### 📋 Suggested HR Action Plan")
                st.write("Recommended proactive measures to optimize employee retention:")
                for action in suggested_actions:
                    st.markdown(f"⚡ **{action}**")
