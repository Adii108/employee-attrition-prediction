import os
import json
import numpy as np
import pandas as pd
from scipy import stats
import joblib

from sklearn.model_selection import train_test_split, StratifiedKFold, RandomizedSearchCV, cross_val_predict
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_selection import mutual_info_classif
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_curve, auc
)

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier

from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE, BorderlineSMOTE
from imblearn.combine import SMOTEENN
from datetime import datetime

import warnings
warnings.filterwarnings("ignore")

def run_pipeline():
    dataset_path = 'employee_attrition.csv'
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset '{dataset_path}' not found.")

    df = pd.read_csv(dataset_path)

    # Data cleaning
    cols_to_drop = ["EmployeeCount", "EmployeeNumber", "Over18", "StandardHours"]
    existing_cols_to_drop = [col for col in cols_to_drop if col in df.columns]
    df.drop(columns=existing_cols_to_drop, inplace=True)

    num_features = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_features = df.select_dtypes(include=[object]).columns.tolist()
    if "Attrition" in cat_features:
        cat_features.remove("Attrition")

    # Feature engineering
    df_feat = df.copy()
    df_feat["Income_Group"] = pd.qcut(df_feat["MonthlyIncome"], q=4, labels=["Low", "Medium", "High", "Very High"])
    df_feat["Experience_Group"] = pd.cut(df_feat["TotalWorkingYears"], 
                                         bins=[-1, 2, 5, 10, 20, np.inf], 
                                         labels=["Entry", "Junior", "Mid", "Senior", "Executive"])
    df_feat["Promotion_Delay_Flag"] = ((df_feat["YearsSinceLastPromotion"] >= 3) & (df_feat["YearsAtCompany"] >= 3)).astype(int)
    df_feat["Frequent_Traveller_Flag"] = (df_feat["BusinessTravel"] == "Travel_Frequently").astype(int)
    df_feat["Early_Career_Flag"] = ((df_feat["Age"] < 30) & (df_feat["YearsAtCompany"] < 3)).astype(int)

    # Feature selection
    df_feat["Attrition_Num"] = df_feat["Attrition"].map({"Yes": 1, "No": 0})
    df_sel = df_feat.copy()
    le_target = LabelEncoder()
    df_sel["Attrition"] = le_target.fit_transform(df_sel["Attrition"])
    df_sel.drop(columns=["Attrition_Num"], inplace=True)

    cat_cols_all = df_sel.select_dtypes(include=[object, "category"]).columns.tolist()
    for col in cat_cols_all:
        df_sel[col] = LabelEncoder().fit_transform(df_sel[col].astype(str))

    X_sel = df_sel.drop(columns=["Attrition"])
    y_sel = df_sel["Attrition"]

    corr_with_attrition = df_feat[num_features + ["Attrition_Num"]].corr()["Attrition_Num"].drop("Attrition_Num").abs().sort_values(ascending=False)
    corr_df = pd.DataFrame({"Correlation_Score": corr_with_attrition})

    mi_scores = mutual_info_classif(X_sel, y_sel, random_state=42)
    mi_df = pd.DataFrame({"Mutual_Info_Score": mi_scores}, index=X_sel.columns).sort_values(by="Mutual_Info_Score", ascending=False)

    rf_temp = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_temp.fit(X_sel, y_sel)
    rf_df = pd.DataFrame({"RF_Importance": rf_temp.feature_importances_}, index=X_sel.columns).sort_values(by="RF_Importance", ascending=False)

    ranking_df = pd.concat([corr_df, mi_df, rf_df], axis=1).fillna(0)
    for col in ranking_df.columns:
        ranking_df[col] = (ranking_df[col] - ranking_df[col].min()) / (ranking_df[col].max() - ranking_df[col].min())

    ranking_df["Average_Score"] = ranking_df.mean(axis=1)
    ranking_df = ranking_df.sort_values(by="Average_Score", ascending=False)

    selected_features = ranking_df.head(20).index.tolist()
    print("Selected Top 20 Features:")
    for i, feat in enumerate(selected_features, 1):
        print(f"  {i}. {feat}")

    # Data preprocessing
    X = df_feat[selected_features]
    y = df_feat["Attrition_Num"]

    X_cat = X.select_dtypes(include=[object, "category"]).columns.tolist()
    X_num = X.select_dtypes(include=[np.number]).columns.tolist()

    X_encoded = pd.get_dummies(X, columns=X_cat, drop_first=True)
    one_hot_columns = X_encoded.columns.tolist()

    X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42, stratify=y)

    scaler = StandardScaler()
    X_train[X_num] = scaler.fit_transform(X_train[X_num])
    X_test[X_num] = scaler.transform(X_test[X_num])

    # Ratio for XGBoost scaling
    ratio = (y_train == 0).sum() / (y_train == 1).sum()

    # Define hyperparameter distribution grids
    param_dist_svc = {
        'model__C': [0.01, 0.1, 1, 10, 100],
        'model__gamma': ['scale', 'auto', 0.001, 0.01, 0.1, 1],
        'model__kernel': ['rbf', 'linear', 'sigmoid']
    }

    param_dist_rf = {
        'model__n_estimators': [50, 100, 150, 200, 300],
        'model__max_depth': [3, 5, 10, 15, 20, None],
        'model__min_samples_split': [2, 5, 10],
        'model__min_samples_leaf': [1, 2, 4],
        'model__max_features': ['sqrt', 'log2', None]
    }

    param_dist_xgb = {
        'model__n_estimators': [50, 100, 150, 200, 300],
        'model__max_depth': [3, 4, 5, 6, 7],
        'model__learning_rate': [0.01, 0.05, 0.1, 0.2],
        'model__subsample': [0.6, 0.8, 1.0],
        'model__colsample_bytree': [0.6, 0.8, 1.0]
    }

    # Define imbalance methods
    samplers = {
        'Original': 'passthrough',
        'Balanced': 'passthrough',
        'SMOTE': SMOTE(random_state=42),
        'SMOTEENN': SMOTEENN(random_state=42),
        'BorderlineSMOTE': BorderlineSMOTE(random_state=42)
    }

    # Stratified K-Fold for CV tuning
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # Models configurations
    model_configs = [
        ("SVM", lambda is_balanced: SVC(probability=True, random_state=42, class_weight='balanced' if is_balanced else None), param_dist_svc),
        ("Random Forest", lambda is_balanced: RandomForestClassifier(random_state=42, class_weight='balanced' if is_balanced else None), param_dist_rf),
        ("XGBoost", lambda is_balanced: XGBClassifier(random_state=42, eval_metric='logloss', scale_pos_weight=ratio if is_balanced else 1.0), param_dist_xgb)
    ]

    all_runs = []

    print("\n--- STARTING SYSTEMATIC ML PIPELINE IMPROVEMENTS ---")
    for model_name, model_fn, param_dist in model_configs:
        for imbalance_name, sampler in samplers.items():
            print(f"Optimizing {model_name} with {imbalance_name} handling...")
            is_balanced = (imbalance_name == 'Balanced')
            base_model = model_fn(is_balanced)

            pipeline = ImbPipeline([
                ('sampler', sampler),
                ('model', base_model)
            ])

            # Hyperparameter tuning using RandomizedSearchCV
            search = RandomizedSearchCV(
                pipeline,
                param_distributions=param_dist,
                n_iter=10,
                scoring='f1',
                cv=cv,
                random_state=42,
                n_jobs=1
            )
            search.fit(X_train, y_train)
            best_est = search.best_estimator_

            # Cross-validated out-of-fold probability predictions on training set
            oof_probs = cross_val_predict(
                best_est,
                X_train,
                y_train,
                cv=cv,
                method='predict_proba'
            )[:, 1]

            # Optimize classification threshold to maximize training OOF F1 Score
            best_thresh = 0.5
            best_oof_f1 = 0.0
            for thresh in np.linspace(0.1, 0.9, 81):
                preds = (oof_probs >= thresh).astype(int)
                score = f1_score(y_train, preds)
                if score > best_oof_f1:
                    best_oof_f1 = score
                    best_thresh = thresh

            # Evaluate the optimized final model on the test set
            test_probs = best_est.predict_proba(X_test)[:, 1]
            test_preds = (test_probs >= best_thresh).astype(int)

            acc = accuracy_score(y_test, test_preds)
            prec = precision_score(y_test, test_preds, zero_division=0)
            rec = recall_score(y_test, test_preds)
            f1 = f1_score(y_test, test_preds)

            fpr, tpr, _ = roc_curve(y_test, test_probs)
            roc_auc = auc(fpr, tpr)

            all_runs.append({
                'model_name': model_name,
                'imbalance_method': imbalance_name,
                'best_params': search.best_params_,
                'best_threshold': float(best_thresh),
                'train_oof_f1': float(best_oof_f1),
                'test_accuracy': float(acc),
                'test_precision': float(prec),
                'test_recall': float(rec),
                'test_f1': float(f1),
                'test_auc': float(roc_auc),
                'estimator': best_est
            })

            print(f"  OOF F1: {best_oof_f1:.4f} | Test F1: {f1:.4f} (Threshold: {best_thresh:.2f})")

    # Select the best model within each model family based on train OOF F1 Score (validation F1)
    best_svm_run = max([r for r in all_runs if r['model_name'] == 'SVM'], key=lambda x: x['train_oof_f1'])
    best_rf_run = max([r for r in all_runs if r['model_name'] == 'Random Forest'], key=lambda x: x['train_oof_f1'])
    best_xgb_run = max([r for r in all_runs if r['model_name'] == 'XGBoost'], key=lambda x: x['train_oof_f1'])

    # Determine absolute best run
    best_overall_run = max([best_svm_run, best_rf_run, best_xgb_run], key=lambda x: x['train_oof_f1'])
    best_model_name = best_overall_run['model_name']

    # Extract standard classifier from the pipeline
    best_model = best_overall_run['estimator'].named_steps['model']
    best_model.threshold = best_overall_run['best_threshold']

    print(f"\nAbsolute Selected Best Model: {best_model_name} (Tuned with {best_overall_run['imbalance_method']})")
    print(f"Selected Threshold: {best_overall_run['best_threshold']:.2f}")
    print(f"Selected Validation OOF F1: {best_overall_run['train_oof_f1']:.4f}")
    print(f"Selected Test F1 Score: {best_overall_run['test_f1']:.4f}")

    # Create directories
    os.makedirs("models", exist_ok=True)
    os.makedirs("artifacts", exist_ok=True)

    # Save artifacts
    joblib.dump(best_model, "models/best_model.joblib")
    joblib.dump(scaler, "models/scaler.joblib")
    joblib.dump(selected_features, "models/selected_features.joblib")
    joblib.dump(one_hot_columns, "models/model_columns.joblib")

    # Load baseline metrics or use hardcoded if not exists
    original_metrics_path = "artifacts/all_models_metrics.json"
    if os.path.exists(original_metrics_path):
        try:
            with open(original_metrics_path, "r") as f:
                old_metrics = json.load(f)["metrics"]
        except Exception:
            old_metrics = {}
    else:
        old_metrics = {}

    baseline_lr = old_metrics.get("Logistic Regression", {
        "Accuracy": 0.7585, "Precision": 0.3571, "Recall": 0.6383, "F1 Score": 0.4580, "ROC AUC": 0.7728
    })
    baseline_dt = old_metrics.get("Decision Tree", {
        "Accuracy": 0.7449, "Precision": 0.2941, "Recall": 0.4255, "F1 Score": 0.3478, "ROC AUC": 0.6227
    })

    # Prepare standard keys for frontend metrics
    model_metrics = {
        "Logistic Regression": {
            "Accuracy": float(baseline_lr.get("Accuracy", 0.7585)),
            "Precision": float(baseline_lr.get("Precision", 0.3571)),
            "Recall": float(baseline_lr.get("Recall", 0.6383)),
            "F1 Score": float(baseline_lr.get("F1 Score", 0.4580)),
            "ROC AUC": float(baseline_lr.get("ROC AUC", 0.7728))
        },
        "Decision Tree": {
            "Accuracy": float(baseline_dt.get("Accuracy", 0.7449)),
            "Precision": float(baseline_dt.get("Precision", 0.2941)),
            "Recall": float(baseline_dt.get("Recall", 0.4255)),
            "F1 Score": float(baseline_dt.get("F1 Score", 0.3478)),
            "ROC AUC": float(baseline_dt.get("ROC AUC", 0.6227))
        },
        "Random Forest": {
            "Accuracy": best_rf_run['test_accuracy'],
            "Precision": best_rf_run['test_precision'],
            "Recall": best_rf_run['test_recall'],
            "F1 Score": best_rf_run['test_f1'],
            "ROC AUC": best_rf_run['test_auc']
        },
        "SVM": {
            "Accuracy": best_svm_run['test_accuracy'],
            "Precision": best_svm_run['test_precision'],
            "Recall": best_svm_run['test_recall'],
            "F1 Score": best_svm_run['test_f1'],
            "ROC AUC": best_svm_run['test_auc']
        },
        "XGBoost": {
            "Accuracy": best_xgb_run['test_accuracy'],
            "Precision": best_xgb_run['test_precision'],
            "Recall": best_xgb_run['test_recall'],
            "F1 Score": best_xgb_run['test_f1'],
            "ROC AUC": best_xgb_run['test_auc']
        }
    }

    # Save all metrics
    with open("artifacts/all_models_metrics.json", "w") as f:
        json.dump({
            "best_model_name": best_model_name,
            "metrics": model_metrics
        }, f, indent=4)

    # Generate Markdown Comparison Report
    report_md = f"""# Machine Learning Pipeline Performance Optimization Report

This report summarizes the improvements made to the IBM HR Analytics Employee Attrition Prediction models.

## Executive Summary
- **Selected Best Model:** {best_model_name}
- **Imbalance Handling Technique:** {best_overall_run['imbalance_method']}
- **Optimized Classification Threshold:** {best_overall_run['best_threshold']:.2f}
- **F1 Score Improvement (Test Set):**
  - **Original Best Model (SVM):** {old_metrics.get("SVM", {}).get("F1 Score", 0.4909):.4f}
  - **Improved Best Model ({best_model_name}):** {best_overall_run['test_f1']:.4f}

---

## Comparison of Best Tuned Models (Hold-out Test Set)

| Model Name | Imbalance Handling | Optimized Threshold | Accuracy | Precision | Recall | F1 Score | ROC AUC |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SVM (Tuned)** | {best_svm_run['imbalance_method']} | {best_svm_run['best_threshold']:.2f} | {best_svm_run['test_accuracy']:.4f} | {best_svm_run['test_precision']:.4f} | {best_svm_run['test_recall']:.4f} | {best_svm_run['test_f1']:.4f} | {best_svm_run['test_auc']:.4f} |
| **Random Forest (Tuned)** | {best_rf_run['imbalance_method']} | {best_rf_run['best_threshold']:.2f} | {best_rf_run['test_accuracy']:.4f} | {best_rf_run['test_precision']:.4f} | {best_rf_run['test_recall']:.4f} | {best_rf_run['test_f1']:.4f} | {best_rf_run['test_auc']:.4f} |
| **XGBoost (Tuned)** | {best_xgb_run['imbalance_method']} | {best_xgb_run['best_threshold']:.2f} | {best_xgb_run['test_accuracy']:.4f} | {best_xgb_run['test_precision']:.4f} | {best_xgb_run['test_recall']:.4f} | {best_xgb_run['test_f1']:.4f} | {best_xgb_run['test_auc']:.4f} |

---

## Original Baselines vs. Improved Models

| Model Family | Original F1 Score | Improved F1 Score | F1 Score Delta |
| :--- | :--- | :--- | :--- |
| **SVM** | {old_metrics.get("SVM", {}).get("F1 Score", 0.4909):.4f} | {best_svm_run['test_f1']:.4f} | {best_svm_run['test_f1'] - old_metrics.get("SVM", {}).get("F1 Score", 0.4909):+.4f} |
| **Random Forest** | {old_metrics.get("Random Forest", {}).get("F1 Score", 0.1667):.4f} | {best_rf_run['test_f1']:.4f} | {best_rf_run['test_f1'] - old_metrics.get("Random Forest", {}).get("F1 Score", 0.1667):+.4f} |
| **XGBoost** | {old_metrics.get("XGBoost", {}).get("F1 Score", 0.3488):.4f} | {best_xgb_run['test_f1']:.4f} | {best_xgb_run['test_f1'] - old_metrics.get("XGBoost", {}).get("F1 Score", 0.3488):+.4f} |

---

## Selected Best Model Hyperparameters
- **Model:** {best_model_name}
- **Parameters:**
```json
{json.dumps(best_overall_run['best_params'], indent=4)}
```

Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.
"""

    with open("artifacts/model_comparison_report.md", "w") as f:
        f.write(report_md)

    print("\nAll artifacts and comparison report saved successfully.")

if __name__ == "__main__":
    run_pipeline()
