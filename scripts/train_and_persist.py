import os
import json
import numpy as np
import pandas as pd
from scipy import stats
import joblib

from sklearn.model_selection import train_test_split
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

    # Baseline Model - Logistic Regression
    lr_model = LogisticRegression(random_state=42, max_iter=1000, class_weight="balanced")
    lr_model.fit(X_train, y_train)
    lr_preds = lr_model.predict(X_test)
    lr_probs = lr_model.predict_proba(X_test)[:, 1]

    # Models definition
    ratio = (y_train == 0).sum() / (y_train == 1).sum()
    models = {
        "Logistic Regression": lr_model,
        "Decision Tree": DecisionTreeClassifier(random_state=42, max_depth=5, class_weight="balanced"),
        "Random Forest": RandomForestClassifier(random_state=42, n_estimators=150, max_depth=10, class_weight="balanced"),
        "SVM": SVC(random_state=42, probability=True, class_weight="balanced"),
        "XGBoost": XGBClassifier(random_state=42, eval_metric="logloss", n_estimators=100, max_depth=4, scale_pos_weight=ratio),
    }

    model_metrics = {}
    trained_models = {}

    for name, model in models.items():
        if name != "Logistic Regression":
            model.fit(X_train, y_train)
        
        preds = model.predict(X_test)
        probs = model.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, preds)
        prec = precision_score(y_test, preds)
        rec = recall_score(y_test, preds)
        f1 = f1_score(y_test, preds)

        fpr, tpr, _ = roc_curve(y_test, probs)
        roc_auc = auc(fpr, tpr)

        model_metrics[name] = {
            "Accuracy": float(acc),
            "Precision": float(prec),
            "Recall": float(rec),
            "F1 Score": float(f1),
            "ROC AUC": float(roc_auc)
        }
        trained_models[name] = model

    # Determine best model by F1 Score
    best_model_name = max(model_metrics, key=lambda k: model_metrics[k]["F1 Score"])
    best_model = trained_models[best_model_name]

    print(f"\nBest Model: {best_model_name}")
    print(f"Metrics: {model_metrics[best_model_name]}")

    # Create directories
    os.makedirs("models", exist_ok=True)
    os.makedirs("artifacts", exist_ok=True)

    # Save artifacts
    joblib.dump(best_model, "models/best_model.joblib")
    joblib.dump(scaler, "models/scaler.joblib")
    joblib.dump(selected_features, "models/selected_features.joblib")
    joblib.dump(one_hot_columns, "models/model_columns.joblib")

    # Save all metrics
    with open("artifacts/all_models_metrics.json", "w") as f:
        json.dump({
            "best_model_name": best_model_name,
            "metrics": model_metrics
        }, f, indent=4)

    print("\nAll artifacts saved successfully.")

if __name__ == "__main__":
    run_pipeline()
