import os
import sys
import runpy

# Ensure project root directory is at the top of sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Execute frontend/app.py as main on every Streamlit script execution rerun
frontend_app_path = os.path.join(BASE_DIR, "frontend", "app.py")
runpy.run_path(frontend_app_path, run_name="__main__")
