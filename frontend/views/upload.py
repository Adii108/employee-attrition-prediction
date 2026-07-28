import streamlit as st
import pandas as pd
import io
from frontend.utils.api_client import APIClient

def render_upload():
    st.title("Bulk Employee Predictions (CSV)")
    st.subheader("Upload employee datasets to run attrition predictions in batches")

    api = APIClient()

    # Step 1: Upload box
    uploaded_file = st.file_uploader("Choose a CSV file containing employee details", type=["csv"])

    if uploaded_file is not None:
        try:
            # Read bytes
            file_bytes = uploaded_file.read()
            
            # Show a brief loading indicator
            with st.spinner("Processing batch predictions..."):
                predicted_df = api.predict_csv(file_bytes, uploaded_file.name)
            
            st.success("Batch predictions processed successfully!")

            # 2. Display brief summary stats
            total_records = len(predicted_df)
            attrite_count = (predicted_df["Attrition_Prediction"] == 1).sum()
            stay_count = total_records - attrite_count
            attrite_rate = (attrite_count / total_records) * 100

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Records Uploaded", f"{total_records}")
            with col2:
                st.metric("Predicted to Stay", f"{stay_count}")
            with col3:
                st.metric("Predicted to Leave", f"{attrite_count} ({attrite_rate:.1f}%)")

            # 3. Allow CSV download
            # Convert final predicted df to csv bytes
            output = io.StringIO()
            predicted_df.to_csv(output, index=False)
            csv_bytes = output.getvalue().encode("utf-8")

            st.download_button(
                label="Download Predictions (CSV)",
                data=csv_bytes,
                file_name=f"attrition_predictions_{uploaded_file.name}",
                mime="text/csv"
            )

            st.write("### Predictions Preview")
            # Select key columns to show in preview to avoid wide scrollbar clutter
            display_cols = [
                "Age", "Department", "JobRole", "MonthlyIncome", 
                "YearsAtCompany", "OverTime", "Attrition_Prediction", 
                "Attrition_Probability", "Risk_Level"
            ]
            # Fallback if some display columns aren't in dataframe
            actual_display_cols = [c for c in display_cols if c in predicted_df.columns]
            st.dataframe(predicted_df[actual_display_cols].head(100), use_container_width=True)

        except Exception as e:
            st.error(f"Error executing batch prediction: {str(e)}")
            st.info("Ensure the uploaded CSV matches the required columns template (including identical naming and datatypes).")
            
    st.markdown("---")
    st.write("### CSV Schema Template")
    st.write(
        "To perform predictions, the uploaded CSV must contain all the original columns from the IBM HR dataset. "
        "The target column 'Attrition' and columns like 'EmployeeNumber' are ignored if present."
    )
    # Renders a small markdown list of example columns
    st.markdown(
        """
        **Required Columns:**  
        `Age`, `BusinessTravel`, `DailyRate`, `Department`, `DistanceFromHome`, `Education`, `EducationField`, 
        `EnvironmentSatisfaction`, `Gender`, `HourlyRate`, `JobInvolvement`, `JobLevel`, `JobRole`, 
        `JobSatisfaction`, `MaritalStatus`, `MonthlyIncome`, `MonthlyRate`, `NumCompaniesWorked`, 
        `OverTime`, `PercentSalaryHike`, `PerformanceRating`, `RelationshipSatisfaction`, `StockOptionLevel`, 
        `TotalWorkingYears`, `TrainingTimesLastYear`, `WorkLifeBalance`, `YearsAtCompany`, `YearsInCurrentRole`, 
        `YearsSinceLastPromotion`, `YearsWithCurrManager`
        """
    )
