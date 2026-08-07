import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

def render_dashboard(df: pd.DataFrame, model_info: dict):
    # 1. High Risk Alert Banner (Stitch Design)
    st.markdown("""
    <div style="background-color: #fff1f2; border: 1px solid #fecdd3; padding: 1.25rem 1.5rem; border-radius: 14px; margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: space-between;">
        <div>
            <h4 style="color: #9f1239; margin: 0; font-size: 1.1rem; font-weight: 700;">⚠️ Retention Alert: High Risk Cluster Detected</h4>
            <p style="color: #be123c; margin: 0.25rem 0 0 0; font-size: 0.9rem;">Sales Representatives and Overtime employees exhibit the highest attrition risk rate (20.6%). Proactive intervention recommended.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. KPIs Row
    total_employees = len(df)
    high_risk_df = df[df["Risk_Level"] == "High"]
    high_risk_count = len(high_risk_df)
    high_risk_pct = (high_risk_count / total_employees) * 100
    
    predicted_attrition_count = (df["Attrition_Prediction"] == 1).sum()
    predicted_attrition_rate = (predicted_attrition_count / total_employees) * 100

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Active Employees", f"{total_employees:,}")
    with col2:
        st.metric("Predicted Attrition Rate", f"{predicted_attrition_rate:.2f}%")
    with col3:
        st.metric("High-Risk Employees", f"{high_risk_count}")
    with col4:
        st.metric("High-Risk Percentage", f"{high_risk_pct:.2f}%")

    st.markdown("---")

    # 3. First Chart Row: Probability Distribution & Department Risk
    col_left, col_right = st.columns(2)

    with col_left:
        st.write("### Attrition Risk Probability Distribution")
        fig_dist = px.histogram(
            df, 
            x="Attrition_Probability", 
            nbins=20,
            color="Risk_Level",
            color_discrete_map={"Low": "#006c49", "Medium": "#f49d09", "High": "#ba1a1a"},
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
            color_discrete_sequence=["#1f108e"]
        )
        fig_dept.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(ticksuffix="%"),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_dept, use_container_width=True)

    # 4. Second Chart Row: Job Role Analysis & Salary Distribution
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
            color_discrete_sequence=["#3730a3"]
        )
        fig_role.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(ticksuffix="%"),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_role, use_container_width=True)

    with col_right_2:
        st.write("### Salary Distribution by Attrition Risk")
        df_salary = df.copy()
        df_salary["Predicted Attrition"] = df_salary["Attrition_Prediction"].map({0: "Low/Medium Risk", 1: "High Risk"})
        
        fig_salary = px.box(
            df_salary,
            x="Predicted Attrition",
            y="MonthlyIncome",
            color="Predicted Attrition",
            color_discrete_map={"Low/Medium Risk": "#006c49", "High Risk": "#ba1a1a"},
            labels={"MonthlyIncome": "Monthly Income ($)", "Predicted Attrition": "Prediction Outcome"}
        )
        fig_salary.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_salary, use_container_width=True)
