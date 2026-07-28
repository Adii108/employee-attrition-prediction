import streamlit as st
import pandas as pd
import plotly.express as px

def render_analytics(df: pd.DataFrame):
    st.title("Interactive HR Analytics")
    st.subheader("Explore correlations and drill down into attrition factors using dynamic filters")

    # 1. Filters inside an expander
    with st.expander("Filter Controls", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            departments = df["Department"].unique().tolist()
            selected_depts = st.multiselect("Departments", departments, default=departments)
            
            genders = df["Gender"].unique().tolist()
            selected_genders = st.multiselect("Gender", genders, default=genders)

        with col2:
            roles = df["JobRole"].unique().tolist()
            selected_roles = st.multiselect("Job Roles", roles, default=roles)
            
            marital_statuses = df["MaritalStatus"].unique().tolist()
            selected_marital = st.multiselect("Marital Status", marital_statuses, default=marital_statuses)

        with col3:
            min_age = int(df["Age"].min())
            max_age = int(df["Age"].max())
            selected_age_range = st.slider("Age Range", min_age, max_age, (min_age, max_age))
            
            min_income = int(df["MonthlyIncome"].min())
            max_income = int(df["MonthlyIncome"].max())
            selected_income_range = st.slider("Monthly Income Range ($)", min_income, max_income, (min_income, max_income))

    # Apply Filters
    filtered_df = df[
        (df["Department"].isin(selected_depts)) &
        (df["Gender"].isin(selected_genders)) &
        (df["JobRole"].isin(selected_roles)) &
        (df["MaritalStatus"].isin(selected_marital)) &
        (df["Age"].between(selected_age_range[0], selected_age_range[1])) &
        (df["MonthlyIncome"].between(selected_income_range[0], selected_income_range[1]))
    ]

    # Show count of filtered records
    st.write(f"Showing **{len(filtered_df)}** of **{len(df)}** employees based on current filters.")

    if filtered_df.empty:
        st.warning("No records match the current filters. Please adjust the controls.")
        return

    st.markdown("---")

    # 2. Charts Section
    col_a, col_b = st.columns(2)

    with col_a:
        st.write("#### Attrition Rate by Business Travel Frequency")
        travel_data = filtered_df.groupby("BusinessTravel")["Attrition_Prediction"].mean().reset_index()
        travel_data["Attrition_Prediction"] = travel_data["Attrition_Prediction"] * 100
        
        fig_travel = px.bar(
            travel_data,
            x="BusinessTravel",
            y="Attrition_Prediction",
            labels={"Attrition_Prediction": "Attrition Rate (%)", "BusinessTravel": "Travel Frequency"},
            color_discrete_sequence=["#5E35B1"]
        )
        fig_travel.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(ticksuffix="%"),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_travel, use_container_width=True)

    with col_b:
        st.write("#### Overtime vs. Attrition Rate")
        ot_data = filtered_df.groupby("OverTime")["Attrition_Prediction"].mean().reset_index()
        ot_data["Attrition_Prediction"] = ot_data["Attrition_Prediction"] * 100
        
        fig_ot = px.bar(
            ot_data,
            x="OverTime",
            y="Attrition_Prediction",
            labels={"Attrition_Prediction": "Attrition Rate (%)", "OverTime": "Worked Overtime"},
            color_discrete_sequence=["#D81B60"]
        )
        fig_ot.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(ticksuffix="%"),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_ot, use_container_width=True)

    col_c, col_d = st.columns(2)

    with col_c:
        st.write("#### Years at Company vs Attrition Probability")
        fig_years = px.scatter(
            filtered_df,
            x="YearsAtCompany",
            y="Attrition_Probability",
            color="Attrition_Prediction",
            color_continuous_scale=["#2E7D32", "#C62828"],
            labels={"YearsAtCompany": "Years at Company", "Attrition_Probability": "Attrition Probability", "Attrition_Prediction": "Prediction"},
        )
        fig_years.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_years, use_container_width=True)

    with col_d:
        st.write("#### Attrition Rate by Marital Status")
        marital_data = filtered_df.groupby("MaritalStatus")["Attrition_Prediction"].mean().reset_index()
        marital_data["Attrition_Prediction"] = marital_data["Attrition_Prediction"] * 100
        
        fig_marital = px.bar(
            marital_data,
            x="MaritalStatus",
            y="Attrition_Prediction",
            labels={"Attrition_Prediction": "Attrition Rate (%)", "MaritalStatus": "Marital Status"},
            color_discrete_sequence=["#3949AB"]
        )
        fig_marital.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(ticksuffix="%"),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_marital, use_container_width=True)
