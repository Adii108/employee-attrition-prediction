import streamlit as st
import streamlit.components.v1 as components
import os
import sys

# Append parent directory to sys.path to resolve absolute package imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Streamlit Page Config
st.set_page_config(
    page_title="Retention Intel - HR Intelligence System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Remove default Streamlit padding, header & footer for full-width Stitch UI rendering
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }
    iframe {
        border: none !important;
        width: 100% !important;
        min-height: 100vh !important;
    }
</style>
""", unsafe_allow_html=True)

# Resolve path to bundled standalone Stitch HTML
HTML_PATH = os.path.join(BASE_DIR, "frontend", "static", "standalone_app.html")

if not os.path.exists(HTML_PATH):
    try:
        from scripts.build_standalone_html import build_standalone
        build_standalone()
    except Exception as e:
        st.error(f"Failed to build Stitch UI: {e}")

if os.path.exists(HTML_PATH):
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()
    components.html(html_content, height=1000, scrolling=True)
else:
    st.error("Stitch UI template file not found.")
