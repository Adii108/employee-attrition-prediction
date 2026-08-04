# Machine Learning Pipeline Performance Report

This report summarizes the performance evaluation and systematic search across various ML models and class-imbalance resamplers for predicting employee attrition.

## Selected Best Model
- **Model Family:** Logistic Regression
- **Resampling Method:** Original
- **Optimized Classification Threshold:** 0.31
- **Cross-Validation OOF F1 Score:** 0.6104

### Why this model performed best:
The combination of advanced feature engineering with tree-based models and optimal thresholding provides superior predictive power compared to linear models. Resamplers (like SMOTE/SMOTEENN/ADASYN) effectively balance the minority attrition class during training folds, and searching for the classification threshold on OOF probability outputs prevents predictions from collapsing into default "Stay" classifications under class imbalance.

---

## Model Comparison Matrix

| Model Configuration | Optimized Threshold | Validation OOF F1 | Accuracy | Precision | Recall | F1 Score | ROC AUC | PR AUC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Logistic Regression (BalancedWeights) | 0.57 | 0.5905 | 0.8605 | 0.5556 | 0.6383 | 0.5941 | 0.8203 | 0.6133 |
| Logistic Regression (SMOTEENN) | 0.71 | 0.5473 | 0.8503 | 0.5273 | 0.617 | 0.5686 | 0.8137 | 0.5849 |
| CatBoost (Original) | 0.24 | 0.5759 | 0.8435 | 0.5088 | 0.617 | 0.5577 | 0.8236 | 0.5589 |
| Logistic Regression (SMOTETomek) | 0.63 | 0.5722 | 0.8503 | 0.5294 | 0.5745 | 0.551 | 0.8153 | 0.5918 |
| Logistic Regression (ADASYN) | 0.63 | 0.605 | 0.8469 | 0.5192 | 0.5745 | 0.5455 | 0.815 | 0.6 |
| Logistic Regression (SMOTE) | 0.61 | 0.5751 | 0.8435 | 0.5094 | 0.5745 | 0.54 | 0.8153 | 0.5918 |
| Random Forest (Original) | 0.26 | 0.523 | 0.8197 | 0.4559 | 0.6596 | 0.5391 | 0.8175 | 0.4721 |
| Balanced Random Forest (Original) | 0.52 | 0.5296 | 0.8299 | 0.4754 | 0.617 | 0.537 | 0.8047 | 0.4738 |
| Logistic Regression (Original) | 0.31 | 0.6104 | 0.8367 | 0.4909 | 0.5745 | 0.5294 | 0.8128 | 0.543 |
| CatBoost (SMOTEENN) | 0.55 | 0.5495 | 0.8299 | 0.4746 | 0.5957 | 0.5283 | 0.8151 | 0.5562 |
| Balanced Random Forest (ADASYN) | 0.43 | 0.5087 | 0.8163 | 0.4462 | 0.617 | 0.5179 | 0.781 | 0.4133 |
| Random Forest (ADASYN) | 0.44 | 0.5361 | 0.8197 | 0.4516 | 0.5957 | 0.5138 | 0.7852 | 0.4243 |
| Random Forest (BalancedWeights) | 0.39 | 0.5256 | 0.8027 | 0.4225 | 0.6383 | 0.5085 | 0.8014 | 0.4776 |
| CatBoost (BalancedWeights) | 0.57 | 0.5667 | 0.8333 | 0.4808 | 0.5319 | 0.5051 | 0.8039 | 0.5487 |
| Balanced Random Forest (SMOTEENN) | 0.55 | 0.5327 | 0.8027 | 0.4203 | 0.617 | 0.5 | 0.786 | 0.4182 |
| XGBoost (SMOTEENN) | 0.9 | 0.5049 | 0.8299 | 0.4717 | 0.5319 | 0.5 | 0.7772 | 0.4686 |
| Extra Trees (SMOTE) | 0.49 | 0.5337 | 0.8129 | 0.4355 | 0.5745 | 0.4954 | 0.7869 | 0.4425 |
| Extra Trees (Original) | 0.29 | 0.5623 | 0.8333 | 0.48 | 0.5106 | 0.4948 | 0.7878 | 0.4872 |
| Extra Trees (BalancedWeights) | 0.48 | 0.5166 | 0.7959 | 0.4085 | 0.617 | 0.4915 | 0.7865 | 0.4689 |
| Extra Trees (SMOTETomek) | 0.48 | 0.5398 | 0.8095 | 0.4286 | 0.5745 | 0.4909 | 0.7845 | 0.4391 |
| CatBoost (SMOTE) | 0.4 | 0.5534 | 0.8469 | 0.525 | 0.4468 | 0.4828 | 0.7839 | 0.4825 |
| Extra Trees (ADASYN) | 0.49 | 0.5428 | 0.8095 | 0.4262 | 0.5532 | 0.4815 | 0.7728 | 0.458 |
| Balanced Random Forest (BalancedWeights) | 0.44 | 0.5369 | 0.7891 | 0.3944 | 0.5957 | 0.4746 | 0.7804 | 0.4568 |
| LightGBM (ADASYN) | 0.37 | 0.5171 | 0.8537 | 0.5588 | 0.4043 | 0.4691 | 0.7725 | 0.486 |
| Random Forest (SMOTETomek) | 0.45 | 0.5308 | 0.8129 | 0.4286 | 0.5106 | 0.466 | 0.792 | 0.4117 |
| Random Forest (SMOTE) | 0.42 | 0.5237 | 0.7959 | 0.4 | 0.5532 | 0.4643 | 0.793 | 0.4071 |
| Extra Trees (SMOTEENN) | 0.64 | 0.5282 | 0.8095 | 0.4211 | 0.5106 | 0.4615 | 0.7718 | 0.4161 |
| Decision Tree (BalancedWeights) | 0.57 | 0.4457 | 0.7993 | 0.4032 | 0.5319 | 0.4587 | 0.7077 | 0.3858 |
| LightGBM (BalancedWeights) | 0.54 | 0.5486 | 0.8061 | 0.4138 | 0.5106 | 0.4571 | 0.7576 | 0.5041 |
| CatBoost (SMOTETomek) | 0.33 | 0.5511 | 0.8095 | 0.4182 | 0.4894 | 0.451 | 0.7839 | 0.4825 |
| CatBoost (ADASYN) | 0.32 | 0.5722 | 0.8333 | 0.4762 | 0.4255 | 0.4494 | 0.7909 | 0.5082 |
| Random Forest (SMOTEENN) | 0.61 | 0.5181 | 0.8129 | 0.4231 | 0.4681 | 0.4444 | 0.7766 | 0.3935 |
| Balanced Random Forest (SMOTE) | 0.46 | 0.5208 | 0.8061 | 0.4074 | 0.4681 | 0.4356 | 0.7918 | 0.411 |
| Balanced Random Forest (SMOTETomek) | 0.46 | 0.5193 | 0.8061 | 0.4074 | 0.4681 | 0.4356 | 0.7918 | 0.411 |
| XGBoost (BalancedWeights) | 0.54 | 0.5156 | 0.8061 | 0.4074 | 0.4681 | 0.4356 | 0.7514 | 0.4385 |
| LightGBM (SMOTEENN) | 0.51 | 0.5022 | 0.7721 | 0.3571 | 0.5319 | 0.4274 | 0.7563 | 0.4022 |
| XGBoost (Original) | 0.14 | 0.5215 | 0.7823 | 0.3651 | 0.4894 | 0.4182 | 0.7476 | 0.4519 |
| LightGBM (Original) | 0.22 | 0.5191 | 0.8163 | 0.4222 | 0.4043 | 0.413 | 0.7613 | 0.4657 |
| LightGBM (SMOTETomek) | 0.41 | 0.55 | 0.8469 | 0.5357 | 0.3191 | 0.4 | 0.7585 | 0.451 |
| LightGBM (SMOTE) | 0.41 | 0.5409 | 0.8469 | 0.5357 | 0.3191 | 0.4 | 0.7585 | 0.451 |
| XGBoost (ADASYN) | 0.41 | 0.5013 | 0.7993 | 0.38 | 0.4043 | 0.3918 | 0.7516 | 0.4254 |
| Decision Tree (SMOTEENN) | 0.6 | 0.4528 | 0.6837 | 0.27 | 0.5745 | 0.3673 | 0.6533 | 0.23 |
| Decision Tree (SMOTETomek) | 0.1 | 0.3816 | 0.7687 | 0.322 | 0.4043 | 0.3585 | 0.6212 | 0.2254 |
| Decision Tree (SMOTE) | 0.1 | 0.375 | 0.7687 | 0.322 | 0.4043 | 0.3585 | 0.6212 | 0.2254 |
| XGBoost (SMOTETomek) | 0.44 | 0.517 | 0.7891 | 0.3404 | 0.3404 | 0.3404 | 0.7501 | 0.423 |
| XGBoost (SMOTE) | 0.44 | 0.5131 | 0.7891 | 0.3404 | 0.3404 | 0.3404 | 0.7501 | 0.423 |
| Decision Tree (ADASYN) | 0.1 | 0.3927 | 0.7313 | 0.2714 | 0.4043 | 0.3248 | 0.6023 | 0.2111 |
| Decision Tree (Original) | 0.1 | 0.3753 | 0.7687 | 0.2439 | 0.2128 | 0.2273 | 0.5436 | 0.1777 |

---
*Report generated automatically by Antigravity ML Pipeline training suite.*
