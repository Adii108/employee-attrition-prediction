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

# Remove default Streamlit chrome for full-width Stitch UI display
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

# Construct bundled Stitch HTML dynamically on every run
STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")
index_file = os.path.join(STATIC_DIR, "index.html")
css_file = os.path.join(STATIC_DIR, "css", "stitch.css")
js_file = os.path.join(STATIC_DIR, "js", "app.js")

with open(index_file, "r", encoding="utf-8") as f:
    html_content = f.read()
with open(css_file, "r", encoding="utf-8") as f:
    css_content = f.read()
with open(js_file, "r", encoding="utf-8") as f:
    js_content = f.read()

html_content = html_content.replace('<link rel="stylesheet" href="/static/css/stitch.css"/>', f'<style>\n{css_content}\n</style>')
html_content = html_content.replace('<script src="/static/js/app.js"></script>', f'<script>\n{js_content}\n</script>')

components.html(html_content, height=1100, scrolling=True)
