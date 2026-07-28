import os
import requests
import pandas as pd
import io

try:
    from backend.services.inference import InferenceService
    from backend.schemas.employee import EmployeeInput
    from backend.config import METRICS_JSON_PATH
    import json
    LOCAL_INFERENCE_AVAILABLE = True
except ImportError:
    LOCAL_INFERENCE_AVAILABLE = False

class APIClient:
    def __init__(self):
        # Reads backend URL from environment or defaults to localhost
        self.base_url = os.environ.get("BACKEND_URL", "http://localhost:8000")
        self.is_local_fallback = False
        self._local_service = None

    @property
    def local_service(self):
        if self._local_service is None and LOCAL_INFERENCE_AVAILABLE:
            self._local_service = InferenceService()
        return self._local_service

    def get_health(self) -> bool:
        """Checks if the FastAPI backend is running and healthy, falling back to local mode if offline."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            if response.status_code == 200 and response.json().get("status") == "healthy":
                self.is_local_fallback = False
                return True
        except requests.RequestException:
            pass

        if LOCAL_INFERENCE_AVAILABLE:
            self.is_local_fallback = True
            return True
        return False

    def get_model_info(self) -> dict:
        """Retrieves details of the primary model currently used for inference."""
        if self.is_local_fallback:
            return self._get_local_model_info()

        try:
            response = requests.get(f"{self.base_url}/model", timeout=3)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            if LOCAL_INFERENCE_AVAILABLE:
                self.is_local_fallback = True
                return self._get_local_model_info()
            return {"error": "Failed to retrieve model info from API"}

    def _get_local_model_info(self) -> dict:
        try:
            with open(METRICS_JSON_PATH, "r") as f:
                data = json.load(f)
            best_model_name = data["best_model_name"]
            return {
                "best_model_name": best_model_name,
                "selected_features": self.local_service.selected_features,
                "metrics": data["metrics"][best_model_name]
            }
        except Exception as e:
            return {"error": f"Failed to retrieve local model info: {str(e)}"}

    def get_metrics(self) -> dict:
        """Retrieves comparisons of all trained models."""
        if self.is_local_fallback:
            return self._get_local_metrics()

        try:
            response = requests.get(f"{self.base_url}/metrics", timeout=3)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            if LOCAL_INFERENCE_AVAILABLE:
                self.is_local_fallback = True
                return self._get_local_metrics()
            return {"error": "Failed to retrieve metrics comparison from API"}

    def _get_local_metrics(self) -> dict:
        try:
            with open(METRICS_JSON_PATH, "r") as f:
                data = json.load(f)
            return {
                "best_model_name": data["best_model_name"],
                "models": data["metrics"]
            }
        except Exception as e:
            return {"error": f"Failed to retrieve local metrics comparison: {str(e)}"}

    def predict(self, employee_data: dict) -> dict:
        """Submits single employee data for prediction."""
        if self.is_local_fallback:
            return self._predict_local(employee_data)

        try:
            response = requests.post(
                f"{self.base_url}/predict", 
                json=employee_data, 
                timeout=5
            )
            if response.status_code == 422:
                return {"validation_error": response.json()}
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            if LOCAL_INFERENCE_AVAILABLE:
                self.is_local_fallback = True
                return self._predict_local(employee_data)
            return {"error": "Prediction request failed"}

    def _predict_local(self, employee_data: dict) -> dict:
        try:
            emp = EmployeeInput(**employee_data)
            res = self.local_service.predict_single(emp)
            return res.model_dump()
        except Exception as e:
            return {"error": f"Local prediction failed: {str(e)}"}

    def predict_csv(self, file_content: bytes, filename: str) -> pd.DataFrame:
        """Submits a CSV file for batch predictions and returns a Pandas DataFrame."""
        if self.is_local_fallback:
            return self._predict_csv_local(file_content)

        files = {"file": (filename, file_content, "text/csv")}
        try:
            response = requests.post(
                f"{self.base_url}/predict-csv", 
                files=files, 
                timeout=15
            )
            response.raise_for_status()
            csv_data = io.BytesIO(response.content)
            return pd.read_csv(csv_data)
        except requests.RequestException as e:
            if LOCAL_INFERENCE_AVAILABLE:
                self.is_local_fallback = True
                return self._predict_csv_local(file_content)
            try:
                error_detail = response.json().get("detail", str(e))
            except Exception:
                error_detail = str(e)
            raise RuntimeError(f"CSV batch prediction failed: {error_detail}")

    def _predict_csv_local(self, file_content: bytes) -> pd.DataFrame:
        try:
            df = pd.read_csv(io.BytesIO(file_content))
            return self.local_service.predict_batch(df)
        except Exception as e:
            raise RuntimeError(f"Local CSV batch prediction failed: {str(e)}")

