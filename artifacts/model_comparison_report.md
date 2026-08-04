# Machine Learning Pipeline Performance Report

This report summarizes the performance evaluation and systematic search across various ML models and class-imbalance resamplers for predicting employee attrition.

## Selected Best Model
- **Model Family:** Logistic Regression
- **Resampling Method:** Original
- **Optimized Classification Threshold:** 0.34
- **Cross-Validation OOF F1 Score:** 0.6298

### Why this model performed best:
The combination of advanced feature engineering with tree-based models and optimal thresholding provides superior predictive power compared to linear models. Resamplers (like SMOTE/SMOTEENN/ADASYN) effectively balance the minority attrition class during training folds, and searching for the classification threshold on OOF probability outputs prevents predictions from collapsing into default "Stay" classifications under class imbalance.

---

## Model Comparison Matrix

| Model Configuration | Optimized Threshold | Validation OOF F1 | Accuracy | Precision | Recall | F1 Score | ROC AUC | PR AUC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Logistic Regression (Original) | 0.34 | 0.6298 | 0.881 | 0.65 | 0.5532 | 0.5977 | 0.8274 | 0.606 |
| Logistic Regression (SMOTETomek) | 0.64 | 0.5904 | 0.8707 | 0.6 | 0.5745 | 0.587 | 0.822 | 0.5938 |
| Logistic Regression (SMOTE) | 0.64 | 0.5882 | 0.8707 | 0.6 | 0.5745 | 0.587 | 0.822 | 0.5938 |
| Logistic Regression (BalancedWeights) | 0.64 | 0.5955 | 0.8673 | 0.5909 | 0.5532 | 0.5714 | 0.8228 | 0.616 |
| Logistic Regression (ADASYN) | 0.61 | 0.5922 | 0.8401 | 0.5 | 0.5957 | 0.5437 | 0.8169 | 0.6044 |
| Logistic Regression (SMOTEENN) | 0.69 | 0.5616 | 0.8333 | 0.4833 | 0.617 | 0.5421 | 0.8135 | 0.5803 |
| Random Forest (Original) | 0.29 | 0.545 | 0.8469 | 0.52 | 0.5532 | 0.5361 | 0.8287 | 0.4895 |
| Random Forest (BalancedWeights) | 0.49 | 0.5352 | 0.8027 | 0.4247 | 0.6596 | 0.5167 | 0.794 | 0.4415 |
| CatBoost (ADASYN) | 0.28 | 0.5602 | 0.8333 | 0.4808 | 0.5319 | 0.5051 | 0.8063 | 0.5186 |
| CatBoost (Original) | 0.16 | 0.5564 | 0.8197 | 0.45 | 0.5745 | 0.5047 | 0.8018 | 0.525 |
| Random Forest (SMOTEENN) | 0.51 | 0.5196 | 0.8129 | 0.4375 | 0.5957 | 0.5045 | 0.7714 | 0.3432 |
| Extra Trees (BalancedWeights) | 0.5 | 0.5318 | 0.8095 | 0.4308 | 0.5957 | 0.5 | 0.7935 | 0.4702 |
| CatBoost (SMOTEENN) | 0.5 | 0.5409 | 0.8095 | 0.4308 | 0.5957 | 0.5 | 0.7941 | 0.5045 |
| CatBoost (BalancedWeights) | 0.39 | 0.5553 | 0.8367 | 0.4898 | 0.5106 | 0.5 | 0.7973 | 0.4982 |
| Extra Trees (SMOTEENN) | 0.54 | 0.5217 | 0.8163 | 0.4426 | 0.5745 | 0.5 | 0.7757 | 0.3997 |
| Extra Trees (SMOTE) | 0.46 | 0.5376 | 0.7993 | 0.4143 | 0.617 | 0.4957 | 0.7842 | 0.4445 |
| Balanced Random Forest (ADASYN) | 0.45 | 0.5236 | 0.8197 | 0.4483 | 0.5532 | 0.4952 | 0.7924 | 0.4359 |
| Extra Trees (SMOTETomek) | 0.49 | 0.5495 | 0.8095 | 0.4286 | 0.5745 | 0.4909 | 0.7836 | 0.4407 |
| XGBoost (SMOTEENN) | 0.83 | 0.5103 | 0.8163 | 0.4407 | 0.5532 | 0.4906 | 0.7814 | 0.4596 |
| CatBoost (SMOTE) | 0.43 | 0.5533 | 0.8469 | 0.525 | 0.4468 | 0.4828 | 0.8018 | 0.5238 |
| Balanced Random Forest (Original) | 0.54 | 0.5484 | 0.8129 | 0.431 | 0.5319 | 0.4762 | 0.8031 | 0.4932 |
| Extra Trees (ADASYN) | 0.5 | 0.5547 | 0.8027 | 0.4127 | 0.5532 | 0.4727 | 0.7752 | 0.4578 |
| Balanced Random Forest (BalancedWeights) | 0.46 | 0.5308 | 0.7959 | 0.4 | 0.5532 | 0.4643 | 0.7792 | 0.4358 |
| Decision Tree (BalancedWeights) | 0.57 | 0.4469 | 0.7993 | 0.4032 | 0.5319 | 0.4587 | 0.7077 | 0.3858 |
| LightGBM (BalancedWeights) | 0.52 | 0.5395 | 0.7925 | 0.3906 | 0.5319 | 0.4505 | 0.7667 | 0.4906 |
| XGBoost (Original) | 0.24 | 0.537 | 0.8197 | 0.4375 | 0.4468 | 0.4421 | 0.7571 | 0.4594 |
| Extra Trees (Original) | 0.31 | 0.5589 | 0.8197 | 0.4375 | 0.4468 | 0.4421 | 0.7783 | 0.4631 |
| LightGBM (SMOTEENN) | 0.51 | 0.514 | 0.7925 | 0.3871 | 0.5106 | 0.4404 | 0.7529 | 0.3497 |
| CatBoost (SMOTETomek) | 0.44 | 0.5562 | 0.8435 | 0.5143 | 0.383 | 0.439 | 0.8018 | 0.5238 |
| LightGBM (SMOTE) | 0.33 | 0.5294 | 0.8333 | 0.475 | 0.4043 | 0.4368 | 0.7967 | 0.4564 |
| LightGBM (SMOTETomek) | 0.31 | 0.5296 | 0.8299 | 0.4634 | 0.4043 | 0.4318 | 0.7967 | 0.4564 |
| Balanced Random Forest (SMOTETomek) | 0.45 | 0.5211 | 0.7993 | 0.3929 | 0.4681 | 0.4272 | 0.7859 | 0.406 |
| LightGBM (ADASYN) | 0.31 | 0.5399 | 0.8231 | 0.4419 | 0.4043 | 0.4222 | 0.7914 | 0.4635 |
| XGBoost (BalancedWeights) | 0.62 | 0.5333 | 0.8435 | 0.5161 | 0.3404 | 0.4103 | 0.7424 | 0.463 |
| XGBoost (SMOTETomek) | 0.53 | 0.5281 | 0.8197 | 0.4286 | 0.383 | 0.4045 | 0.7456 | 0.4407 |
| Balanced Random Forest (SMOTEENN) | 0.64 | 0.5369 | 0.8129 | 0.4091 | 0.383 | 0.3956 | 0.7787 | 0.3817 |
| Balanced Random Forest (SMOTE) | 0.47 | 0.5257 | 0.8129 | 0.4091 | 0.383 | 0.3956 | 0.7859 | 0.406 |
| LightGBM (Original) | 0.35 | 0.5629 | 0.8333 | 0.4706 | 0.3404 | 0.3951 | 0.7666 | 0.4457 |
| XGBoost (SMOTE) | 0.55 | 0.5284 | 0.8197 | 0.425 | 0.3617 | 0.3908 | 0.7456 | 0.4407 |
| Random Forest (SMOTE) | 0.51 | 0.5266 | 0.8265 | 0.4444 | 0.3404 | 0.3855 | 0.7927 | 0.4209 |
| Random Forest (SMOTETomek) | 0.51 | 0.5296 | 0.8265 | 0.4444 | 0.3404 | 0.3855 | 0.7927 | 0.4209 |
| XGBoost (ADASYN) | 0.62 | 0.486 | 0.8367 | 0.4839 | 0.3191 | 0.3846 | 0.7518 | 0.4446 |
| Decision Tree (SMOTEENN) | 0.1 | 0.4195 | 0.7109 | 0.2889 | 0.5532 | 0.3796 | 0.647 | 0.2312 |
| Random Forest (ADASYN) | 0.5 | 0.5296 | 0.8231 | 0.4286 | 0.3191 | 0.3659 | 0.7872 | 0.4217 |
| Decision Tree (Original) | 0.34 | 0.4119 | 0.7857 | 0.3333 | 0.3404 | 0.3368 | 0.6105 | 0.2223 |
| Decision Tree (ADASYN) | 0.1 | 0.392 | 0.7721 | 0.3148 | 0.3617 | 0.3366 | 0.606 | 0.2159 |
| Decision Tree (SMOTETomek) | 0.76 | 0.399 | 0.7721 | 0.2619 | 0.234 | 0.2472 | 0.5701 | 0.1922 |
| Decision Tree (SMOTE) | 0.76 | 0.402 | 0.7721 | 0.2619 | 0.234 | 0.2472 | 0.5701 | 0.1922 |

---
*Report generated automatically by Antigravity ML Pipeline training suite.*
