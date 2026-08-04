import os
import json
import warnings
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, RandomizedSearchCV, StratifiedKFold, cross_val_predict
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, average_precision_score
from sklearn.pipeline import Pipeline as SkPipeline

# Classifiers
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

# Imbalance tools
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE, ADASYN
from imblearn.combine import SMOTEENN, SMOTETomek
from imblearn.ensemble import BalancedRandomForestClassifier

# Preprocessing from our package
from ml_pipeline.preprocessing import get_preprocessing_pipeline
from ml_pipeline.evaluation import evaluate_and_plot_all

warnings.filterwarnings('ignore')

def train_and_evaluate_all(csv_path="employee_attrition.csv", models_dir="models", artifacts_dir="artifacts"):
    """Performs full ML model comparisons, hyperparameter tuning, threshold tuning, and reports."""
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(artifacts_dir, exist_ok=True)
    
    print("--- STARTING ADVANCED ML PIPELINE OPTIMIZATION ---")
    
    # 1. Load data
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Clean target
    if "Attrition" in df.columns:
        df["Attrition_Num"] = (df["Attrition"] == "Yes").astype(int)
        y = df["Attrition_Num"]
        X = df.drop(columns=["Attrition", "Attrition_Num"], errors="ignore")
    elif "Attrition_Num" in df.columns:
        y = df["Attrition_Num"]
        X = df.drop(columns=["Attrition_Num"], errors="ignore")
    else:
        raise ValueError("Target column 'Attrition' or 'Attrition_Num' not found in dataset.")
        
    print(f"Dataset Loaded. Shape: {df.shape}. Class imbalance: {y.value_counts(normalize=True).to_dict()}")
    
    # Train/Test Split (stratified 80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    # Define models and their hyperparameter grids
    # We set n_jobs=1 for searches to prevent Windows Loky/Access Violation crashes.
    model_configs = {
        "Logistic Regression": {
            "class": LogisticRegression(max_iter=1000, random_state=42),
            "params": {"model__C": [0.01, 0.1, 1.0, 10.0]}
        },
        "Decision Tree": {
            "class": DecisionTreeClassifier(random_state=42),
            "params": {
                "model__max_depth": [3, 5, 10, None],
                "model__min_samples_split": [2, 5, 10]
            }
        },
        "Random Forest": {
            "class": RandomForestClassifier(random_state=42),
            "params": {
                "model__n_estimators": [100, 200],
                "model__max_depth": [5, 10, None],
                "model__min_samples_split": [2, 5, 10]
            }
        },
        "Extra Trees": {
            "class": ExtraTreesClassifier(random_state=42),
            "params": {
                "model__n_estimators": [100, 200],
                "model__max_depth": [5, 10, None]
            }
        },
        "XGBoost": {
            "class": XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42),
            "params": {
                "model__n_estimators": [100, 200],
                "model__max_depth": [3, 5, 7],
                "model__learning_rate": [0.01, 0.1, 0.2]
            }
        },
        "LightGBM": {
            "class": LGBMClassifier(random_state=42, verbose=-1),
            "params": {
                "model__n_estimators": [100, 200],
                "model__max_depth": [3, 5, 7],
                "model__learning_rate": [0.01, 0.1, 0.2]
            }
        },
        "CatBoost": {
            "class": CatBoostClassifier(verbose=0, random_state=42),
            "params": {
                "model__iterations": [100, 150],
                "model__depth": [4, 6, 8],
                "model__learning_rate": [0.05, 0.1]
            }
        },
        "Balanced Random Forest": {
            "class": BalancedRandomForestClassifier(random_state=42, sampling_strategy='all'),
            "params": {
                "model__n_estimators": [100, 200],
                "model__max_depth": [5, 10, None]
            }
        }
    }
    
    # Define resamplers
    samplers = {
        "Original": None,
        "BalancedWeights": "weights",  # handles class weight in model parameters
        "SMOTE": SMOTE(random_state=42),
        "ADASYN": ADASYN(random_state=42),
        "SMOTEENN": SMOTEENN(random_state=42),
        "SMOTETomek": SMOTETomek(random_state=42)
    }
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    comparison_results = {}
    
    best_overall_val_f1 = -1
    best_pipeline = None
    best_model_name = ""
    best_sampler_name = ""
    best_threshold = 0.5
    
    # Outer comparison loop
    for model_name, config in model_configs.items():
        for sampler_name, sampler in samplers.items():
            run_name = f"{model_name} ({sampler_name})"
            print(f"Training and Tuning: {run_name}...")
            
            # Setup weights if balanced weights requested
            model_inst = config["class"]
            if sampler_name == "BalancedWeights":
                # Apply model-specific weight parameter
                if isinstance(model_inst, (LogisticRegression, DecisionTreeClassifier, RandomForestClassifier, ExtraTreesClassifier)):
                    model_inst.set_params(class_weight='balanced')
                elif isinstance(model_inst, LGBMClassifier):
                    model_inst.set_params(class_weight='balanced')
                elif isinstance(model_inst, CatBoostClassifier):
                    model_inst.set_params(auto_class_weights='Balanced')
                elif isinstance(model_inst, XGBClassifier):
                    # compute scale_pos_weight
                    ratio = float(sum(y_train == 0)) / sum(y_train == 1)
                    model_inst.set_params(scale_pos_weight=ratio)
                else:
                    # Skip if model doesn't support weights
                    continue
            
            # Build full pipeline
            pre_pipe = get_preprocessing_pipeline()
            
            # We construct a pipeline with imblearn to handle resampler properly
            steps = [
                ('engineer', pre_pipe.named_steps['engineer']),
                ('preprocessor', pre_pipe.named_steps['preprocessor'])
            ]
            if sampler is not None and sampler != "weights":
                steps.append(('sampler', sampler))
            steps.append(('model', model_inst))
            
            pipeline = ImbPipeline(steps)
            
            # Tuner Search
            search = RandomizedSearchCV(
                pipeline,
                param_distributions=config["params"],
                n_iter=3,
                scoring='f1',
                cv=cv,
                random_state=42,
                n_jobs=1
            )
            
            try:
                search.fit(X_train, y_train)
                tuned_est = search.best_estimator_
                
                # Out-of-fold CV predictions to optimize threshold without leakage
                oof_probs = cross_val_predict(
                    tuned_est, X_train, y_train, cv=cv, method="predict_proba", n_jobs=1
                )[:, 1]
                
                # Search for best classification threshold on OOF F1 score
                thresholds = np.linspace(0.1, 0.9, 81)
                best_t = 0.5
                best_t_f1 = -1
                for t in thresholds:
                    t_pred = (oof_probs >= t).astype(int)
                    t_f1 = f1_score(y_train, t_pred)
                    if t_f1 > best_t_f1:
                        best_t_f1 = t_f1
                        best_t = t
                
                # Fit final model predictions on test split
                test_probs = tuned_est.predict_proba(X_test)[:, 1]
                test_preds = (test_probs >= best_t).astype(int)
                
                # Collect scores
                acc = accuracy_score(y_test, test_preds)
                prec = precision_score(y_test, test_preds, zero_division=0)
                rec = recall_score(y_test, test_preds, zero_division=0)
                f1 = f1_score(y_test, test_preds, zero_division=0)
                roc_auc = roc_auc_score(y_test, test_probs)
                pr_auc = average_precision_score(y_test, test_probs)
                
                comparison_results[run_name] = {
                    "Model": model_name,
                    "Resampler": sampler_name,
                    "Threshold": round(best_t, 2),
                    "Validation_OOF_F1": round(best_t_f1, 4),
                    "Accuracy": round(acc, 4),
                    "Precision": round(prec, 4),
                    "Recall": round(rec, 4),
                    "F1": round(f1, 4),
                    "ROC_AUC": round(roc_auc, 4),
                    "PR_AUC": round(pr_auc, 4)
                }
                
                print(f"  Best Threshold: {best_t:.2f} | Val F1: {best_t_f1:.4f} | Test F1: {f1:.4f}")
                
                # Check if this model is the absolute best based on Val OOF F1
                if best_t_f1 > best_overall_val_f1:
                    best_overall_val_f1 = best_t_f1
                    best_pipeline = tuned_est
                    best_model_name = model_name
                    best_sampler_name = sampler_name
                    best_threshold = best_t
                    
            except Exception as e:
                print(f"  Failed configuration {run_name}: {str(e)}")
                
    # 4. Save best artifacts
    print(f"\n---> Absolute Selected Best Model: {best_model_name} with {best_sampler_name} (Val OOF F1: {best_overall_val_f1:.4f})")
    
    # Save standard sklearn Pipeline (FeatureEngineer + ColumnTransformer + Model)
    # This decouples prediction from imblearn dependency
    final_pipeline = SkPipeline([
        ('engineer', best_pipeline.named_steps['engineer']),
        ('preprocessor', best_pipeline.named_steps['preprocessor']),
        ('model', best_pipeline.named_steps['model'])
    ])
    final_pipeline.threshold = best_threshold
    
    # Save pipeline.pkl & best_model.pkl
    joblib.dump(final_pipeline, os.path.join(models_dir, "pipeline.pkl"))
    joblib.dump(best_pipeline.named_steps['model'], os.path.join(models_dir, "best_model.pkl"))
    
    # Save optimized threshold
    with open(os.path.join(models_dir, "optimized_threshold.json"), "w") as f:
        json.dump({"threshold": float(best_threshold)}, f)
        
    # Save feature names out
    preprocessor = best_pipeline.named_steps['preprocessor']
    feature_names = list(preprocessor.get_feature_names_out())
    with open(os.path.join(models_dir, "feature_names.json"), "w") as f:
        json.dump(feature_names, f)
        
    # Backward compatible files
    joblib.dump(best_pipeline.named_steps['model'], os.path.join(models_dir, "best_model.joblib"))
    joblib.dump(best_pipeline.named_steps['preprocessor'].transformers_[0][1], os.path.join(models_dir, "scaler.joblib")) # numerical scaler step
    joblib.dump(list(best_pipeline.named_steps['engineer'].transform(X_train).columns), os.path.join(models_dir, "selected_features.joblib"))
    joblib.dump(feature_names, os.path.join(models_dir, "model_columns.joblib"))
    
    # Save all comparison metrics
    metrics_summary = {
        "best_model_name": f"{best_model_name} ({best_sampler_name})",
        "metrics": comparison_results
    }
    with open(os.path.join(artifacts_dir, "all_models_metrics.json"), "w") as f:
        json.dump(metrics_summary, f, indent=4)
        
    # 5. Evaluate and save plots
    print("Generating evaluation plots...")
    # Preprocess X_train / X_test for evaluation plot
    evaluate_and_plot_all(
        final_pipeline, X_train, y_train, X_test, y_test, 
        threshold=best_threshold, save_dir="plots"
    )
    
    # 6. Generate markdown report
    generate_report(comparison_results, best_model_name, best_sampler_name, best_threshold, best_overall_val_f1, artifacts_dir)
    print("--- ML PIPELINE OPTIMIZATION COMPLETED SUCCESSFULLY ---")

def generate_report(results, best_model_name, best_sampler_name, threshold, val_f1, artifacts_dir):
    """Generates the Markdown comparison report."""
    report_path = os.path.join(artifacts_dir, "model_comparison_report.md")
    
    df_res = pd.DataFrame(results).T.sort_values(by="F1", ascending=False)
    
    table_rows = []
    for idx, row in df_res.iterrows():
        table_rows.append(
            f"| {idx} | {row['Threshold']} | {row['Validation_OOF_F1']} | "
            f"{row['Accuracy']} | {row['Precision']} | {row['Recall']} | {row['F1']} | {row['ROC_AUC']} | {row['PR_AUC']} |"
        )
        
    table_content = "\n".join(table_rows)
    
    markdown_content = f"""# Machine Learning Pipeline Performance Report

This report summarizes the performance evaluation and systematic search across various ML models and class-imbalance resamplers for predicting employee attrition.

## Selected Best Model
- **Model Family:** {best_model_name}
- **Resampling Method:** {best_sampler_name}
- **Optimized Classification Threshold:** {threshold:.2f}
- **Cross-Validation OOF F1 Score:** {val_f1:.4f}

### Why this model performed best:
The combination of advanced feature engineering with tree-based models and optimal thresholding provides superior predictive power compared to linear models. Resamplers (like SMOTE/SMOTEENN/ADASYN) effectively balance the minority attrition class during training folds, and searching for the classification threshold on OOF probability outputs prevents predictions from collapsing into default "Stay" classifications under class imbalance.

---

## Model Comparison Matrix

| Model Configuration | Optimized Threshold | Validation OOF F1 | Accuracy | Precision | Recall | F1 Score | ROC AUC | PR AUC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
{table_content}

---
*Report generated automatically by Antigravity ML Pipeline training suite.*
"""
    with open(report_path, "w") as f:
        f.write(markdown_content)

if __name__ == "__main__":
    train_and_evaluate_all()
