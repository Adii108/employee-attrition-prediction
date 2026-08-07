# Deployment Guide: Streamlit Community Cloud & Hosting

This document details how to deploy the **Retention Intel - Employee Attrition Prediction System** to **Streamlit Community Cloud** or any cloud hosting platform (Hugging Face Spaces, Render, AWS, GCP, Azure).

---

## Option 1: Deploy to Streamlit Community Cloud (Recommended & Free)

Streamlit Community Cloud hosts Streamlit apps directly from your GitHub repository for free.

### Step 1: Push Code to GitHub
Ensure your repository is initialized and pushed to GitHub:
```bash
git add .
git commit -m "Prepare Streamlit Cloud deployment entrypoint"
git push origin main
```

### Step 2: Connect to Streamlit Community Cloud
1. Go to **[share.streamlit.io](https://share.streamlit.io/)** and sign in with your GitHub account.
2. Click **"New App"** on your Streamlit Cloud workspace.
3. Select your repository: `Adii108/employee-attrition-prediction` (or your repository fork).
4. Set the **Branch** to `main`.
5. Set the **Main file path** to `app.py`.
6. Click **"Deploy!"**.

### How Standalone Mode Works on Streamlit Cloud:
- The app automatically detects if the FastAPI backend is offline and switches to **Standalone Inference Mode**.
- It uses local joblib models (`models/best_model.joblib`, `scaler.joblib`) for zero-latency single predictions and CSV batch processing.

---

## Option 2: Run Streamlit Locally

To run the Streamlit application locally on your machine:

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch Streamlit**:
   ```bash
   streamlit run app.py
   ```
   Or:
   ```bash
   streamlit run frontend/app.py
   ```

3. **Access App**:
   Open **`http://localhost:8501`** in your browser.

---

## Option 3: Deploy Dual Services (FastAPI Backend + Streamlit Cloud)

If you wish to run the FastAPI API backend separately on a cloud provider (e.g. Render, Railway, AWS App Runner):

1. **Deploy FastAPI Backend**:
   - Start Command: `python -m uvicorn backend.app:app --host 0.0.0.0 --port $PORT`
2. **Configure Streamlit Environment Variable**:
   - In Streamlit Cloud **Advanced Settings** -> **Secrets**:
     ```toml
     BACKEND_URL = "https://your-fastapi-backend-url.onrender.com"
     ```
   - Streamlit will route predictions and batch requests directly to your live FastAPI backend API.
