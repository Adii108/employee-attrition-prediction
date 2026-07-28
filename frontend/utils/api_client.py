import os
import requests
import pandas as pd
import io

class APIClient:
    def __init__(self):
        # Reads backend URL from environment or defaults to localhost
        self.base_url = os.environ.get("BACKEND_URL", "http://localhost:8000")

    def get_health(self) -> bool:
        """Checks if the FastAPI backend is running and healthy."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=3)
            return response.status_code == 200 and response.json().get("status") == "healthy"
        except requests.RequestException:
            return False

    def get_model_info(self) -> dict:
        """Retrieves details of the primary model currently used for inference."""
        try:
            response = requests.get(f"{self.base_url}/model", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Failed to retrieve model info: {str(e)}"}

    def get_metrics(self) -> dict:
        """Retrieves comparisons of all trained models."""
        try:
            response = requests.get(f"{self.base_url}/metrics", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Failed to retrieve metrics comparison: {str(e)}"}

    def predict(self, employee_data: dict) -> dict:
        """Submits single employee data for prediction."""
        try:
            response = requests.post(
                f"{self.base_url}/predict", 
                json=employee_data, 
                timeout=5
            )
            if response.status_code == 422:
                # Custom validation error format returned by our app.py handler
                return {"validation_error": response.json()}
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Prediction request failed: {str(e)}"}

    def predict_csv(self, file_content: bytes, filename: str) -> pd.DataFrame:
        """Submits a CSV file for batch predictions and returns a Pandas DataFrame."""
        files = {"file": (filename, file_content, "text/csv")}
        try:
            response = requests.post(
                f"{self.base_url}/predict-csv", 
                files=files, 
                timeout=15
            )
            response.raise_for_status()
            
            # Read CSV content from the StreamingResponse bytes
            csv_data = io.BytesIO(response.content)
            return pd.read_csv(csv_data)
        except requests.RequestException as e:
            # Propagate detailed error message from FastAPI if present
            try:
                error_detail = response.json().get("detail", str(e))
            except Exception:
                error_detail = str(e)
            raise RuntimeError(f"CSV batch prediction failed: {error_detail}")
