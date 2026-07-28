# Machine Learning Pipeline Performance Optimization Report

This report summarizes the improvements made to the IBM HR Analytics Employee Attrition Prediction models.

## Executive Summary
- **Selected Best Model:** SVM
- **Imbalance Handling Technique:** SMOTE
- **Optimized Classification Threshold:** 0.60
- **F1 Score Improvement (Test Set):**
  - **Original Best Model (SVM):** 0.4909
  - **Improved Best Model (SVM):** 0.4615

---

## Comparison of Best Tuned Models (Hold-out Test Set)

| Model Name | Imbalance Handling | Optimized Threshold | Accuracy | Precision | Recall | F1 Score | ROC AUC |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SVM (Tuned)** | SMOTE | 0.60 | 0.8571 | 0.5806 | 0.3830 | 0.4615 | 0.7663 |
| **Random Forest (Tuned)** | SMOTE | 0.47 | 0.8095 | 0.4237 | 0.5319 | 0.4717 | 0.7983 |
| **XGBoost (Tuned)** | BorderlineSMOTE | 0.34 | 0.8095 | 0.4211 | 0.5106 | 0.4615 | 0.8058 |

---

## Original Baselines vs. Improved Models

| Model Family | Original F1 Score | Improved F1 Score | F1 Score Delta |
| :--- | :--- | :--- | :--- |
| **SVM** | 0.4909 | 0.4615 | -0.0294 |
| **Random Forest** | 0.1667 | 0.4717 | +0.3050 |
| **XGBoost** | 0.3488 | 0.4615 | +0.1127 |

---

## Selected Best Model Hyperparameters
- **Model:** SVM
- **Parameters:**
```json
{
    "model__kernel": "linear",
    "model__gamma": "auto",
    "model__C": 0.1
}
```

Report generated on 2026-07-28 18:48:48.
