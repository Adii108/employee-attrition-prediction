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
    page_title="Retention Intel - HR Intelligence System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Stitch CSS Injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    h1, h2, h3, h4 {
        font-family: 'Outfit', sans-serif !important;
        color: #1f108e !important;
    }
    .stButton>button {
        background-color: #1f108e !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.5rem 1.25rem !important;
    }
    .stButton>button:hover {
        background-color: #3730a3 !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)


# API Client Initialization
api = APIClient()

# Check backend health (sets local fallback if offline)
api.get_health()

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
    
    # Call API or local fallback to get predictions
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    csv_bytes = buf.getvalue().encode("utf-8")
    
    try:
        predicted_df = api.predict_csv(csv_bytes, "employee_attrition.csv")
        return predicted_df
    except Exception:
        # If API prediction fails, run local batch prediction directly
        try:
            from ml_pipeline.predict import predict_batch
            models_dir = os.path.join(BASE_DIR, "models")
            return predict_batch(df, models_dir)
        except Exception:
            return df

# Load predicted data
with st.spinner("Initializing organizational analytics..."):
    predicted_df = load_predicted_dataset(CSV_PATH)

# Fetch active model info with safe fallback
try:
    model_info = api.get_model_info()
except Exception:
    model_info = None

if not model_info or not isinstance(model_info, dict) or "best_model_name" not in model_info:
    model_info = {
        "best_model_name": "SVM (Support Vector Machine)",
        "metrics": {"f1_score": 0.4941, "accuracy": 0.8707, "roc_auc": 0.8241}
    }


# Sidebar Navigation
st.sidebar.title("Retention Intel")
st.sidebar.caption("HR Intelligence & Attrition Analytics")

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
if getattr(api, "is_local_fallback", True):
    st.sidebar.caption("System Status: Online (Standalone Mode)")
else:
    st.sidebar.caption("System Status: Online (API Connected)")
    st.sidebar.caption(f"Backend URL: {api.base_url}")
    
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

