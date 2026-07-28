import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

def render_dashboard(df: pd.DataFrame, model_info: dict):
    st.title("HR Analytics Attrition Dashboard")
    st.subheader("High-level analytics and predictive insights for organizational stability")

    # 1. KPIs Row
    total_employees = len(df)
    high_risk_df = df[df["Risk_Level"] == "High"]
    high_risk_count = len(high_risk_df)
    high_risk_pct = (high_risk_count / total_employees) * 100
    
    # Calculate Attrition Rate (predicted attrition = 1)
    predicted_attrition_count = (df["Attrition_Prediction"] == 1).sum()
    predicted_attrition_rate = (predicted_attrition_count / total_employees) * 100

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Employees", f"{total_employees}")
    with col2:
        st.metric("Predicted Attrition Rate", f"{predicted_attrition_rate:.2f}%")
    with col3:
        st.metric("High-Risk Employees", f"{high_risk_count}")
    with col4:
        st.metric("High-Risk Percentage", f"{high_risk_pct:.2f}%")

    st.markdown("---")

    # 2. First Chart Row: Probability Distribution & Department Risk
    col_left, col_right = st.columns(2)

    with col_left:
        st.write("### Attrition Probability Distribution")
        fig_dist = px.histogram(
            df, 
            x="Attrition_Probability", 
            nbins=20,
            color="Risk_Level",
            color_discrete_map={"Low": "#2E7D32", "Medium": "#F57C00", "High": "#C62828"},
            labels={"Attrition_Probability": "Predicted Probability", "count": "Employee Count"},
            category_orders={"Risk_Level": ["Low", "Medium", "High"]}
        )
        fig_dist.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            legend_title_text="Risk Level",
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_dist, use_container_width=True)

    with col_right:
        st.write("### Department-Wise Attrition Risk")
        dept_risk = df.groupby("Department")["Attrition_Probability"].mean().reset_index()
        dept_risk["Attrition_Probability"] = dept_risk["Attrition_Probability"] * 100
        dept_risk = dept_risk.sort_values(by="Attrition_Probability", ascending=False)
        
        fig_dept = px.bar(
            dept_risk,
            x="Department",
            y="Attrition_Probability",
            labels={"Attrition_Probability": "Average Risk Rate (%)"},
            color_discrete_sequence=["#1976D2"]
        )
        fig_dept.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(ticksuffix="%"),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_dept, use_container_width=True)

    # 3. Second Chart Row: Job Role Analysis & Salary Distribution
    col_left_2, col_right_2 = st.columns(2)

    with col_left_2:
        st.write("### Job-Role Attrition Risk Analysis")
        role_risk = df.groupby("JobRole")["Attrition_Probability"].mean().reset_index()
        role_risk["Attrition_Probability"] = role_risk["Attrition_Probability"] * 100
        role_risk = role_risk.sort_values(by="Attrition_Probability", ascending=True)

        fig_role = px.bar(
            role_risk,
            y="JobRole",
            x="Attrition_Probability",
            orientation="h",
            labels={"Attrition_Probability": "Average Risk Rate (%)", "JobRole": "Job Role"},
            color_discrete_sequence=["#37474F"]
        )
        fig_role.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(ticksuffix="%"),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_role, use_container_width=True)

    with col_right_2:
        st.write("### Salary Distribution by Predicted Attrition")
        df_salary = df.copy()
        df_salary["Predicted Attrition"] = df_salary["Attrition_Prediction"].map({0: "Stay (No Attrition)", 1: "Leave (Attrition)"})
        
        fig_salary = px.box(
            df_salary,
            x="Predicted Attrition",
            y="MonthlyIncome",
            color="Predicted Attrition",
            color_discrete_map={"Stay (No Attrition)": "#1E88E5", "Leave (Attrition)": "#E53935"},
            labels={"MonthlyIncome": "Monthly Income ($)", "Predicted Attrition": "Prediction Outcome"}
        )
        fig_salary.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_salary, use_container_width=True)

    # 4. Third Chart Row: Satisfaction Analysis & Feature Importance
    col_left_3, col_right_3 = st.columns(2)

    with col_left_3:
        st.write("### Attrition Risk by Satisfaction Levels")
        # Compute mean risk by JobSatisfaction
        satisfaction_risk = df.groupby("JobSatisfaction")["Attrition_Probability"].mean().reset_index()
        satisfaction_risk["Attrition_Probability"] = satisfaction_risk["Attrition_Probability"] * 100
        satisfaction_risk["JobSatisfaction"] = satisfaction_risk["JobSatisfaction"].astype(str)

        fig_sat = px.bar(
            satisfaction_risk,
            x="JobSatisfaction",
            y="Attrition_Probability",
            labels={"JobSatisfaction": "Job Satisfaction Level (1: Low, 4: Very High)", "Attrition_Probability": "Average Risk Rate (%)"},
            color_discrete_sequence=["#00ACC1"]
        )
        fig_sat.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(ticksuffix="%"),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_sat, use_container_width=True)

    with col_right_3:
        st.write("### Top Selected Feature Importance")
        # Display static feature importance plot
        feat_importance_path = "plots/06_feature_importance.png"
        if os.path.exists(feat_importance_path):
            st.image(feat_importance_path, caption="Consolidated feature importance scores from training.", use_container_width=True)
        else:
            st.info("Feature importance plot not found. Run training script to generate.")
