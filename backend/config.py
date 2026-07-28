import os

# Base Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")

# Serialized Model Artifact Paths
BEST_MODEL_PATH = os.path.join(MODELS_DIR, "best_model.joblib")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler.joblib")
SELECTED_FEATURES_PATH = os.path.join(MODELS_DIR, "selected_features.joblib")
MODEL_COLUMNS_PATH = os.path.join(MODELS_DIR, "model_columns.joblib")
METRICS_JSON_PATH = os.path.join(ARTIFACTS_DIR, "all_models_metrics.json")

# FastAPI Settings
API_TITLE = "IBM HR Analytics - Employee Attrition Prediction API"
API_DESCRIPTION = "Production-ready API for predicting employee attrition using machine learning."
API_VERSION = "1.0.0"
DEBUG = False
ALLOWED_HOSTS = ["*"]
