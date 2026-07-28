import os
import io
import json
from datetime import datetime
import pandas as pd
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Dict

from backend.config import METRICS_JSON_PATH
from backend.schemas.employee import (
    EmployeeInput, PredictionResponse, ModelInfoResponse, ModelCompareResponse
)
from backend.services.inference import InferenceService

# Define APIRouter
router = APIRouter()

# Dependency to get InferenceService
_inference_service = None

def get_inference_service() -> InferenceService:
    global _inference_service
    if _inference_service is None:
        _inference_service = InferenceService()
    return _inference_service

@router.get("/")
def get_project_info():
    """Returns basic information about the employee attrition prediction project."""
    service = get_inference_service()
    return {
        "project": "IBM HR Analytics - Employee Attrition Prediction System",
        "description": "A production-ready API for predicting employee attrition probabilities.",
        "api_version": "1.0.0",
        "loaded_model": service.model.__class__.__name__,
        "available_endpoints": {
            "GET /": "Project details",
            "GET /health": "Server status",
            "GET /model": "Metadata and metrics of the loaded best model",
            "GET /metrics": "Comparison metrics for all trained models",
            "POST /predict": "Predict attrition for a single employee (JSON input)",
            "POST /predict-csv": "Upload a CSV file and download attrition predictions"
        }
    }

@router.get("/health")
def get_health():
    """Returns server health status."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@router.get("/model", response_model=ModelInfoResponse)
def get_model_info():
    """Returns the metadata and performance metrics of the best loaded model."""
    if not os.path.exists(METRICS_JSON_PATH):
        raise HTTPException(status_code=500, detail="Model metrics file not found.")

    with open(METRICS_JSON_PATH, "r") as f:
        data = json.load(f)

    best_model_name = data["best_model_name"]
    best_metrics = data["metrics"][best_model_name]
    
    service = get_inference_service()
    
    return ModelInfoResponse(
        best_model_name=best_model_name,
        selected_features=service.selected_features,
        metrics=best_metrics
    )

@router.get("/metrics", response_model=ModelCompareResponse)
def get_metrics_comparison():
    """Returns the metrics comparison across all trained models."""
    if not os.path.exists(METRICS_JSON_PATH):
        raise HTTPException(status_code=500, detail="Model comparison metrics not found.")

    with open(METRICS_JSON_PATH, "r") as f:
        data = json.load(f)

    return ModelCompareResponse(
        best_model_name=data["best_model_name"],
        models=data["metrics"]
    )

@router.post("/predict", response_model=PredictionResponse)
def predict_attrition(
    employee: EmployeeInput, 
    service: InferenceService = Depends(get_inference_service)
):
    """Predicts attrition status and probability for a single employee."""
    try:
        return service.predict_single(employee)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.post("/predict-csv")
async def predict_attrition_csv(
    file: UploadFile = File(...),
    service: InferenceService = Depends(get_inference_service)
):
    """
    Accepts an uploaded CSV file containing employee details.
    Runs predictions for each employee and returns a downloadable CSV file.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV file.")
        
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV file: {str(e)}")

    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded CSV file is empty.")

    # Validate that required features are present
    required_cols = list(EmployeeInput.__fields__.keys())
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        raise HTTPException(
            status_code=400, 
            detail=f"CSV file is missing required columns: {', '.join(missing_cols)}"
        )

    try:
        # Run batch predictions
        predicted_df = service.predict_batch(df)
        
        # Convert predicted dataframe to CSV bytes
        output = io.StringIO()
        predicted_df.to_csv(output, index=False)
        
        response = StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv"
        )
        response.headers["Content-Disposition"] = f"attachment; filename=predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error during batch execution: {str(e)}")
