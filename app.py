import os
import sys

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Execute Streamlit app from frontend package
from frontend.app import *
