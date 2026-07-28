import streamlit as st

def render_about():
    st.title("About the Attrition Prediction Project")
    st.subheader("Overview, technical architecture, and key analytics insights")

    st.write(
        "This project provides an end-to-end predictive system for analyzing employee attrition risk "
        "and suggesting preventive HR recommendations. It allows organizations to transition from "
        "reactive turnover mitigation to proactive talent retention."
    )

    st.markdown("---")

    st.write("### Technical Architecture")
    st.write(
        "The system has been built following a decoupled, microservice-like clean architecture, "
        "comprising the following layers:"
    )
    st.markdown(
        """
        * **Machine Learning Pipeline**: Custom preprocessor, consolidated feature importance ranking, and classification models trained on the IBM HR Watson dataset. The best trained model is serialized and deployed.
        * **FastAPI Backend**: Handles incoming REST requests, enforces input constraints via Pydantic, executes modular inference pipelines, and returns standardized predictions and metrics.
        * **Streamlit Frontend**: A professional, dashboard-style interface utilizing Plotly for dynamic charts, supporting single-employee profiling, bulk file processing, and interactive filters.
        """
    )

    st.markdown("---")

    st.write("### Key Data Insights (Exploratory Data Analysis)")
    st.write(
        "Statistical tests (ANOVA and Chi-Square) and consolidated feature selection identify several key drivers of attrition:"
    )
    
    st.markdown(
        """
        1. **Overtime Impact**: Employees working Overtime exhibit an attrition rate of approximately 30%, compared to just 10% for non-overtime peers. Overtime is the single most statistically significant categorical factor.
        2. **Compensation Contrast**: Monthly Income is a heavy driver. Resigned employees earn an average of $4,787 per month compared to $7,308 for those who stay.
        3. **Vulnerable Roles**: Sales Representatives and Laboratory Technicians experience exceptionally high voluntary exit rates (exceeding 20% on average).
        4. **Tenure & Manager Trust**: Employees with shorter tenures (especially under 3 years) are significantly more likely to leave, particularly if their relationship with their direct manager is new.
        5. **Job & Environment Satisfaction**: Low ratings in Job Satisfaction, Environment Satisfaction, or Work-Life Balance strongly correlate with voluntary resignations.
        """
    )
    
    st.markdown("---")
    st.write("### Tech Stack Specifications")
    st.markdown(
        """
        * **Programming Language**: Python 3.9+
        * **Web API Layer**: FastAPI, Uvicorn, Pydantic
        * **UI/Visualizations**: Streamlit, Plotly, Plotly Express
        * **Scientific Computing**: Scikit-Learn, XGBoost, SciPy, Pandas, NumPy
        * **Serialization**: Joblib, JSON
        """
    )
