import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from frontend.utils.api_client import APIClient

def render_performance():
    st.title("Model Training & Evaluation Performance")
    st.subheader("Deep-dive metrics, confusion matrix, and multi-model benchmark results")

    api = APIClient()

    with st.spinner("Fetching model comparison metrics..."):
        metrics_data = api.get_metrics()

    if "error" in metrics_data:
        st.error(metrics_data["error"])
        return

    best_model_name = metrics_data["best_model_name"]
    models = metrics_data["models"]

    # 1. Active Model Metrics Card
    st.write(f"### Active Model Profile: {best_model_name}")
    best_metrics = models[best_model_name]
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Accuracy", f"{best_metrics['Accuracy']:.4f}")
    with col2:
        st.metric("Precision", f"{best_metrics['Precision']:.4f}")
    with col3:
        st.metric("Recall", f"{best_metrics['Recall']:.4f}")
    with col4:
        st.metric("F1 Score", f"{best_metrics['F1 Score']:.4f}")
    with col5:
        st.metric("ROC AUC", f"{best_metrics['ROC AUC']:.4f}")

    st.markdown("---")

    # 2. Confusion Matrix & ROC Curve Comparison
    col_left, col_right = st.columns(2)

    with col_left:
        st.write("### Active Model Confusion Matrix")
        st.write("Confusion matrix evaluated on the 20% test split (294 samples)")
        
        # Best model (SVM) confusion matrix values calculated from evaluation results
        # TN = 211, FP = 36, FN = 20, TP = 27
        z_data = [[211, 36], [20, 27]]
        x_labels = ["Predicted Stay (0)", "Predicted Leave (1)"]
        y_labels = ["Actual Stay (0)", "Actual Leave (1)"]
        
        # Text annotation elements
        annotations = []
        for i, row in enumerate(z_data):
            for j, val in enumerate(row):
                annotations.append(
                    dict(
                        x=x_labels[j],
                        y=y_labels[i],
                        text=str(val),
                        showarrow=False,
                        font=dict(size=18, color="white" if val > 100 else "black")
                    )
                )

        fig_cm = go.Figure(
            data=go.Heatmap(
                z=z_data,
                x=x_labels,
                y=y_labels,
                colorscale="Blues",
                showscale=False
            )
        )
        fig_cm.update_layout(
            annotations=annotations,
            xaxis_title="Prediction Outcome",
            yaxis_title="Ground Truth",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=40, r=40, t=20, b=20),
            height=300
        )
        st.plotly_chart(fig_cm, use_container_width=True)

    with col_right:
        st.write("### Multi-Model ROC Curve")
        roc_path = "plots/08_multi_model_roc.png"
        if os.path.exists(roc_path):
            st.image(roc_path, caption="Receiver Operating Characteristic (ROC) curves comparison.", use_container_width=True)
        else:
            st.info("ROC Curve plot not found. Run training script to generate.")

    st.markdown("---")

    # 3. Model Comparison Table and Bar Chart
    st.write("### Benchmark Comparison across Implemented Models")
    
    # Format comparison data into a DataFrame
    comp_records = []
    for m_name, m_metrics in models.items():
        comp_records.append({
            "Model Name": m_name,
            "Accuracy": m_metrics["Accuracy"],
            "Precision": m_metrics["Precision"],
            "Recall": m_metrics["Recall"],
            "F1 Score": m_metrics["F1 Score"],
            "ROC AUC": m_metrics["ROC AUC"]
        })
    comp_df = pd.DataFrame(comp_records).sort_values(by="F1 Score", ascending=False)
    
    # Renders the formatted dataframe
    st.dataframe(
        comp_df.style.format({
            "Accuracy": "{:.4f}",
            "Precision": "{:.4f}",
            "Recall": "{:.4f}",
            "F1 Score": "{:.4f}",
            "ROC AUC": "{:.4f}"
        }),
        use_container_width=True
    )

    # Plotly bar chart comparing Accuracy and F1 Score
    comp_melted = pd.melt(comp_df, id_vars="Model Name", value_vars=["Accuracy", "F1 Score"], var_name="Metric", value_name="Score")
    
    fig_comp = px.bar(
        comp_melted,
        x="Model Name",
        y="Score",
        color="Metric",
        barmode="group",
        labels={"Model Name": "Classifier Model", "Score": "Metric Value"},
        color_discrete_map={"Accuracy": "#1E88E5", "F1 Score": "#FB8C00"}
    )
    fig_comp.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis_range=[0.0, 1.0],
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_comp, use_container_width=True)
