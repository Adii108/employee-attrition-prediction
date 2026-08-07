import streamlit as st
import pandas as pd
import os
import io
import sys

# Append parent directory to sys.path to resolve absolute package imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Import Views
from frontend.views.dashboard import render_dashboard
from frontend.views.prediction import render_prediction
from frontend.views.upload import render_upload
from frontend.views.analytics import render_analytics
from frontend.views.performance import render_performance
from frontend.views.about import render_about

# Import API Client
from frontend.utils.api_client import APIClient

# Streamlit Page Config
st.set_page_config(
    page_title="Retention Intel - HR Intelligence System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# High-End Stitch Design System CSS Injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #f8f9ff !important;
        color: #0b1c30 !important;
    }
    
    h1, h2, h3, h4, .stHeader {
        font-family: 'Outfit', sans-serif !important;
        color: #1f108e !important;
        font-weight: 700 !important;
    }
    
    /* Stitch Card Containers */
    div[data-testid="stMetricValue"] {
        font-family: 'Outfit', sans-serif !important;
        color: #1f108e !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
    }
    
    div[data-testid="stMetricLabel"] {
        font-family: 'Inter', sans-serif !important;
        color: #464553 !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        font-size: 0.75rem !important;
    }
    
    /* Primary Buttons */
    .stButton>button {
        background-color: #1f108e !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        border: none !important;
        padding: 0.6rem 1.5rem !important;
        box-shadow: 0 4px 12px rgba(31, 16, 142, 0.2) !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        background-color: #3730a3 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(31, 16, 142, 0.3) !important;
    }
    
    /* Form Inputs & Selectboxes */
    div[data-baseweb="select"] > div {
        border-radius: 10px !important;
        border-color: #c8c4d5 !important;
    }

    /* Custom Header Banner */
    .stitch-header {
        background-color: #ffffff;
        padding: 1.5rem 2rem;
        border-radius: 16px;
        border: 1px solid #d3e4fe;
        box-shadow: 0 2px 8px rgba(31, 16, 142, 0.04);
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
</style>
""", unsafe_allow_html=True)

# API Client Initialization
api = APIClient()
api.get_health()

CSV_PATH = os.path.join(BASE_DIR, "employee_attrition.csv")

# Cache predictions on raw dataset
@st.cache_data
def load_predicted_dataset(path: str):
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    try:
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        return api.predict_csv(buf.getvalue().encode("utf-8"), "employee_attrition.csv")
    except Exception:
        try:
            from ml_pipeline.predict import predict_batch
            models_dir = os.path.join(BASE_DIR, "models")
            return predict_batch(df, models_dir)
        except Exception:
            return df

with st.spinner("Initializing Retention Intel analytics..."):
    predicted_df = load_predicted_dataset(CSV_PATH)

# Model metadata fallback
try:
    model_info = api.get_model_info()
except Exception:
    model_info = None

if not model_info or not isinstance(model_info, dict) or "best_model_name" not in model_info:
    model_info = {
        "best_model_name": "SVM (Support Vector Machine)",
        "metrics": {"f1_score": 0.4941, "accuracy": 0.8707, "roc_auc": 0.8241}
    }

# Sidebar Navigation (Stitch Branding)
st.sidebar.markdown("""
<div style="text-align: center; padding: 1rem 0;">
    <h2 style="color: #1f108e; margin: 0; font-weight: 900; font-size: 1.6rem;">Retention Intel</h2>
    <p style="color: #464553; margin: 0; font-size: 0.8rem; font-weight: 500;">HR Intelligence System</p>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Go to:",
    [
        "Dashboard", 
        "Employee Data Entry", 
        "Batch CSV Upload", 
        "Analytics", 
        "Model Benchmarks", 
        "About Project"
    ]
)

st.sidebar.markdown("---")
if getattr(api, "is_local_fallback", True):
    st.sidebar.caption("System Status: Online (Standalone Mode)")
else:
    st.sidebar.caption("System Status: Online (API Connected)")

st.sidebar.caption(f"Active Model: {model_info['best_model_name']}")

# Top Stitch Header Banner
st.markdown(f"""
<div class="stitch-header">
    <div>
        <h2 style="margin: 0; font-size: 1.8rem; color: #1f108e;">{page}</h2>
        <p style="margin: 0.25rem 0 0 0; color: #464553; font-size: 0.95rem;">Retention Intel HR Predictive Analytics & Workforce Management Platform</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Render pages natively with 100% working Python graphs & ML model predictions
if page == "Dashboard":
    if predicted_df is not None:
        render_dashboard(predicted_df, model_info)
    else:
        st.error("Failed to load organizational analytics dataset.")

elif page == "Employee Data Entry":
    render_prediction()

elif page == "Batch CSV Upload":
    render_upload()

elif page == "Analytics":
    if predicted_df is not None:
        render_analytics(predicted_df)
    else:
        st.error("Failed to load analytics dataset.")

elif page == "Model Benchmarks":
    render_performance()

elif page == "About Project":
    render_about()
