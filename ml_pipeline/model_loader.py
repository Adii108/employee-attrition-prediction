import os
import json
import joblib

class ModelLoader:
    _pipeline = None
    _threshold = 0.5
    
    @classmethod
    def load_artifacts(cls, models_dir="models"):
        """Loads and caches model pipeline and optimized threshold."""
        pipeline_path = os.path.join(models_dir, "pipeline.pkl")
        threshold_path = os.path.join(models_dir, "optimized_threshold.json")
        
        if cls._pipeline is None:
            if os.path.exists(pipeline_path):
                cls._pipeline = joblib.load(pipeline_path)
            else:
                # Try joblib fallback file from previous checkpoint
                fallback_path = os.path.join(models_dir, "best_model.joblib")
                if os.path.exists(fallback_path):
                    cls._pipeline = joblib.load(fallback_path)
                else:
                    raise FileNotFoundError(f"Neither pipeline.pkl nor best_model.joblib found in {models_dir}")
            
            if os.path.exists(threshold_path):
                try:
                    with open(threshold_path, "r") as f:
                        cls._threshold = json.load(f).get("threshold", 0.5)
                except Exception:
                    cls._threshold = 0.5
            else:
                # Retrieve from model attribute if set during training
                cls._threshold = getattr(cls._pipeline, "threshold", 0.5)
                
        return cls._pipeline, cls._threshold
        
    @classmethod
    def clear_cache(cls):
        cls._pipeline = None
        cls._threshold = 0.5
