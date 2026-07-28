import streamlit as st
import pandas as pd
import os
import io
import sys

# Append parent directory to sys.path to resolve absolute package imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Views
from frontend.views.dashboard import render_dashboard
from frontend.views.prediction import render_prediction
from frontend.views.upload import render_upload
from frontend.views.analytics import render_analytics
from frontend.views.performance import render_performance
from frontend.views.about import render_about

# Import API Client
from frontend.utils.api_client import APIClient

# Page Config
st.set_page_config(
    page_title="HR Attrition Prediction System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Client Initialization
api = APIClient()

# Check backend health
backend_running = api.get_health()

if not backend_running:
    st.error("Cannot connect to the FastAPI backend server.")
    st.warning("Please ensure the backend is running by executing: python -m backend.app")
    st.info("The application requires the backend API to run predictions and fetch model metadata.")
else:
    # Resolve CSV Path
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CSV_PATH = os.path.join(BASE_DIR, "employee_attrition.csv")

    # Cache predictions on raw dataset for Dashboard and Analytics
    @st.cache_data
    def load_predicted_dataset(path: str):
        if not os.path.exists(path):
            return None
        
        # Load raw dataset
        df = pd.read_csv(path)
        
        # Call backend to get predictions
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        csv_bytes = buf.getvalue().encode("utf-8")
        
        try:
            predicted_df = api.predict_csv(csv_bytes, "employee_attrition.csv")
            return predicted_df
        except Exception:
            # Fallback if connection fails during cache build
            return None

    # Load predicted data
    with st.spinner("Initializing organizational analytics..."):
        predicted_df = load_predicted_dataset(CSV_PATH)

    # Fetch active model info
    model_info = api.get_model_info()

    # Sidebar Navigation (No Emojis)
    st.sidebar.title("HR Portal")
    st.sidebar.subheader("Navigation")
    
    page = st.sidebar.radio(
        "Go to:",
        [
            "Dashboard", 
            "Employee Prediction", 
            "CSV Upload", 
            "Analytics", 
            "Model Performance", 
            "About Project"
        ]
    )

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.caption("System Status: Online")
    st.sidebar.caption(f"Backend URL: {api.base_url}")
    if "best_model_name" in model_info:
        st.sidebar.caption(f"Active Model: {model_info['best_model_name']}")

    # Render pages
    if page == "Dashboard":
        if predicted_df is not None:
            render_dashboard(predicted_df, model_info)
        else:
            st.error("Failed to load organizational analytics dataset.")
            
    elif page == "Employee Prediction":
        render_prediction()
        
    elif page == "CSV Upload":
        render_upload()
        
    elif page == "Analytics":
        if predicted_df is not None:
            render_analytics(predicted_df)
        else:
            st.error("Failed to load analytics dataset.")
            
    elif page == "Model Performance":
        render_performance()
        
    elif page == "About Project":
        render_about()
