import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    confusion_matrix, roc_curve, precision_recall_curve, 
    classification_report, auc, average_precision_score
)
from sklearn.model_selection import learning_curve
from sklearn.calibration import calibration_curve
import shap

def evaluate_and_plot_all(model, X_train, y_train, X_test, y_test, threshold=0.5, save_dir="plots"):
    """Generates and saves all requested performance evaluation graphs and reports."""
    os.makedirs(save_dir, exist_ok=True)
    
    # 1. Classification Predictions using Threshold
    y_test_probs = model.predict_proba(X_test)[:, 1]
    y_test_pred = (y_test_probs >= threshold).astype(int)
    
    y_train_probs = model.predict_proba(X_train)[:, 1]
    
    # Classification Report
    cls_report = classification_report(y_test, y_test_pred, output_dict=False)
    with open(os.path.join(save_dir, "classification_report.txt"), "w") as f:
        f.write(cls_report)
        
    # 2. Confusion Matrix Plot
    plt.figure(figsize=(6, 5))
    cm = confusion_matrix(y_test, y_test_pred)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", 
                xticklabels=["Stay", "Leave"], yticklabels=["Stay", "Leave"])
    plt.title(f"Confusion Matrix (Threshold: {threshold:.2f})")
    plt.ylabel("Actual")
    plt.xlabel("Predicted")
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "confusion_matrix.png"), dpi=150)
    plt.close()
    
    # 3. ROC Curve Plot
    plt.figure(figsize=(6, 5))
    fpr, tpr, _ = roc_curve(y_test, y_test_probs)
    roc_auc = auc(fpr, tpr)
    plt.plot(fpr, tpr, label=f"AUC = {roc_auc:.4f}")
    plt.plot([0, 1], [0, 1], 'k--')
    plt.title("Receiver Operating Characteristic (ROC) Curve")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "roc_curve.png"), dpi=150)
    plt.close()
    
    # 4. Precision-Recall Curve Plot
    plt.figure(figsize=(6, 5))
    precision, recall, _ = precision_recall_curve(y_test, y_test_probs)
    pr_auc = average_precision_score(y_test, y_test_probs)
    plt.plot(recall, precision, label=f"PR-AUC = {pr_auc:.4f}")
    plt.title("Precision-Recall (PR) Curve")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.legend(loc="lower left")
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "precision_recall_curve.png"), dpi=150)
    plt.close()
    
    # 5. Calibration Curve Plot
    plt.figure(figsize=(6, 5))
    prob_true, prob_pred = calibration_curve(y_test, y_test_probs, n_bins=10)
    plt.plot(prob_pred, prob_true, marker='o', label="Calibrated Model")
    plt.plot([0, 1], [0, 1], 'k--', label="Perfectly Calibrated")
    plt.title("Probability Calibration Curve")
    plt.xlabel("Mean Predicted Probability")
    plt.ylabel("Fraction of Positives")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "calibration_curve.png"), dpi=150)
    plt.close()
    
    # 6. Feature Importance Graph (Top 20)
    try:
        # Extract features and classifier
        clf = model.named_steps['model']
        preprocessor = model.named_steps['preprocessor']
        feature_names = preprocessor.get_feature_names_out()
        
        # Strip prefixes
        cleaned_feature_names = [f.split("__")[1] if "__" in f else f for f in feature_names]
        
        if hasattr(clf, "feature_importances_"):
            importances = clf.feature_importances_
        elif hasattr(clf, "coef_"):
            importances = np.abs(clf.coef_[0])
        else:
            importances = None
            
        if importances is not None:
            feat_imp_df = pd.DataFrame({
                "Feature": cleaned_feature_names,
                "Importance": importances
            }).sort_values(by="Importance", ascending=False).head(20)
            
            plt.figure(figsize=(10, 6))
            sns.barplot(x="Importance", y="Feature", data=feat_imp_df, palette="viridis")
            plt.title("Top 20 Most Important Features")
            plt.xlabel("Importance")
            plt.ylabel("Feature")
            plt.tight_layout()
            plt.savefig(os.path.join(save_dir, "feature_importance.png"), dpi=150)
            plt.close()
    except Exception as e:
        print(f"Skipped Feature Importance Plotting due to error: {str(e)}")
        
    # 7. Learning Curve Plot
    try:
        train_sizes, train_scores, test_scores = learning_curve(
            model, X_train, y_train, cv=5, scoring='f1', n_jobs=1,
            train_sizes=np.linspace(0.2, 1.0, 5), random_state=42
        )
        train_mean = np.mean(train_scores, axis=1)
        test_mean = np.mean(test_scores, axis=1)
        
        plt.figure(figsize=(6, 5))
        plt.plot(train_sizes, train_mean, 'o-', label="Training Score")
        plt.plot(train_sizes, test_mean, 's-', label="Cross-Validation Score")
        plt.title("Model Learning Curve")
        plt.xlabel("Training Set Size")
        plt.ylabel("F1 Score")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, "learning_curve.png"), dpi=150)
        plt.close()
    except Exception as e:
        print(f"Skipped Learning Curve Plotting due to error: {str(e)}")
        
    # 8. SHAP Summary Plot
    try:
        clf = model.named_steps['model']
        preprocessor = model.named_steps['preprocessor']
        feature_names = preprocessor.get_feature_names_out()
        cleaned_feature_names = [f.split("__")[1] if "__" in f else f for f in feature_names]
        
        engineer = model.named_steps['engineer']
        X_train_eng = engineer.transform(X_train)
        X_train_proc = preprocessor.transform(X_train_eng)
        if hasattr(X_train_proc, "toarray"):
            X_train_proc = X_train_proc.toarray()
            
        df_train_proc = pd.DataFrame(X_train_proc, columns=cleaned_feature_names)
        
        # Use a subset of training data for faster SHAP calculation
        shap_sample = df_train_proc.sample(min(100, len(df_train_proc)), random_state=42)
        
        def predict_class1(X):
            return clf.predict_proba(X)[:, 1]
            
        explainer = shap.Explainer(predict_class1, shap_sample)
        shap_values = explainer(shap_sample)
        
        plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_values, shap_sample, show=False)
        plt.title("SHAP Summary Plot", fontsize=14)
        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, "shap_summary_plot.png"), dpi=150)
        plt.close()
    except Exception as e:
        print(f"Skipped SHAP Summary Plotting due to error: {str(e)}")
        
    print(f"All performance plots successfully generated and saved to '{save_dir}/'.")
