# IBM HR Analytics - Employee Attrition Prediction System

This project converts the existing machine learning pipeline into a production-ready web application with a FastAPI backend and a Streamlit frontend. It exposes validated endpoints and a professional dashboard for predicting and exploring employee attrition risk without altering the original model training or preprocessing pipeline.

---

## What Has Been Done

### 1. Model and Preprocessing Serialization
* Created a deterministic training script (`scripts/train_and_persist.py`) that executes the original ML pipeline.
* Evaluated baseline and advanced models (Logistic Regression, Decision Tree, Random Forest, SVM, XGBoost) and identified SVM as the best-performing model with an F1 Score of 0.4909.
* Saved the trained model binary (`models/best_model.joblib`), the standard scaler (`models/scaler.joblib`), the list of selected features (`models/selected_features.joblib`), and the one-hot encoded column index template (`models/model_columns.joblib`).
* Saved model comparison metrics across all models to `artifacts/all_models_metrics.json`.

### 2. FastAPI Backend
* Implemented Pydantic models in `backend/schemas/employee.py` to strictly validate 30 incoming employee features with value constraints.
* Structured modular prediction logic in `backend/services/inference.py` to replicate the training-set feature engineering, column layout reindexing, and Standard Scaling.
* Programmed REST routes in `backend/routes/prediction.py` and the main application setup in `backend/app.py`:
  * GET /: Project metadata
  * GET /health: API health check status
  * GET /model: Retrives active model metrics and features
  * GET /metrics: Retrieves comparisons for all models
  * POST /predict: Predicts attrition probability for a single employee record
  * POST /predict-csv: Executes batch predictions on uploaded CSV sheets and streams back predicted data

### 3. Streamlit Frontend
* Created a professional, minimalist multi-page application in `frontend/app.py` utilizing Plotly visualizations for interactive insights.
* Designed modular views under `frontend/views/`:
  * **Dashboard**: Displays organizational metrics (Total Employees, Attrition Rate, High-Risk counts) and dynamic Plotly charts (Probability distribution, Department Risk, Job-Role analysis, Salary/Satisfaction levels).
  * **Employee Prediction**: Provides a 3-column structured form mapping to Pydantic constraints, rendering colored risk levels and retention recommendations.
  * **CSV Upload**: Accepts raw employee sheets, executes batch predictions via the API, displays sortable previews, and enables predicted file downloads.
  * **Analytics**: Implements a collapsible filter panel (Age, Income, Department, Gender, Job Role) linking to dynamic charts (Travel, Overtime, Marital status rate comparisons).
  * **Model Performance**: Visualizes multi-model performance benchmarks and a confusion matrix heatmap.
  * **About Project**: Summarizes Exploratory Data Analysis insights and system specifications.
* Configured a custom white/light theme with blue accents in `.streamlit/config.toml`.

### 4. Integration Verification
* Created a verification script (`scripts/validate_inference.py`) to confirm zero prediction regression.
* Validated that predictions on raw CSV test records match the original script output exactly, yielding a classification mismatch rate of 0.0% and a negligible maximum probability difference (0.00005) due to response rounding.
* Tested the API connection health and dashboard data loading.

---

## File Structure

The project directory layout is organized as follows:

```
Employee_attrition/
├── .streamlit/
│   └── config.toml         # Streamlit styling settings
├── backend/
│   ├── api/
│   │   └── prediction.py   # Endpoint handlers
│   ├── schemas/
│   │   └── employee.py     # Pydantic schemas
│   ├── services/
│   │   └── inference.py    # Inference & preprocessing logic
│   ├── utils/
│   │   └── helpers.py      # Helper utilities
│   ├── app.py              # Main application entrypoint
│   └── config.py           # Configuration parameters
├── frontend/
│   ├── utils/
│   │   └── api_client.py   # API client helper
│   ├── views/
│   │   ├── dashboard.py    # Dashboard visualizations
│   │   ├── prediction.py   # Individual employee form
│   │   ├── upload.py       # CSV upload & batch prediction
│   │   ├── analytics.py    # Interactive analytics
│   │   ├── performance.py  # Model performance & confusion matrix
│   │   └── about.py        # About page view
│   └── app.py              # Main Streamlit router entrypoint
├── models/                 # Serialized objects (scaler, columns, model)
│   ├── best_model.joblib
│   ├── scaler.joblib
│   ├── selected_features.joblib
│   └── model_columns.joblib
├── artifacts/              # Metadata & metrics
│   └── all_models_metrics.json
├── scripts/
│   ├── train_and_persist.py # Replicates training & saves artifacts
│   └── validate_inference.py # Checks inference alignment
├── requirements.txt        # Python dependency list
├── .env.example            # Environment variables example
└── README.md               # Project documentation
```

---

## Installation & Running Instructions

### 1. Install Dependencies
Run:
```bash
pip install -r requirements.txt
```

### 2. Verify Output Alignment
Verify the mathematical alignment of predictions by running:
```bash
python scripts/validate_inference.py
```

### 3. Run the FastAPI Backend
Start the backend server on port 8000:
```bash
python -m backend.app
```

### 4. Run the Streamlit Frontend
In a separate terminal, launch the Streamlit frontend:
```bash
streamlit run frontend/app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.
