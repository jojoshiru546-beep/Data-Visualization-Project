# Run app using streamlit run dashboard/app.py
"""
Global Health Analytics Dashboard
Milestone 5 + Milestone 6 Integration
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
import os

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Global Health Analytics",
    layout="wide",
    page_icon="🩺",
    initial_sidebar_state="expanded"
)

st.title("🩺 Global Health Analytics Dashboard")
st.markdown("**Milestone 5**: Interactive Visual Analytics + **Milestone 6**: Predictive Research Contribution")

# ====================== LOAD DATA ======================
@st.cache_data(ttl=3600)
def load_data():
    """Load the enriched dataset"""
    data_path = "data/processed/global_health_enriched.csv.gz"
    if not os.path.exists(data_path):
        st.error(f"File not found: {data_path}. Please run load_dataset.ipynb first.")
        st.stop()
    return pd.read_csv(data_path, compression='gzip')

df = load_data()

# ====================== SIDEBAR FILTERS ======================
st.sidebar.header("🔎 Filters")

# Section 2: Interactive Controls
countries = st.sidebar.multiselect(
    "Select Country(s)", 
    options=sorted(df['Country'].unique()), 
    default=[]
)

disease_categories = st.sidebar.multiselect(
    "Disease Category", 
    options=sorted(df['Disease Category'].unique()), 
    default=[]
)

year_range = st.sidebar.slider(
    "Year Range", 
    int(df['Year'].min()), 
    int(df['Year'].max()), 
    (2015, 2023)
)

age_groups = st.sidebar.multiselect(
    "Age Group", 
    options=sorted(df['Age Group'].unique()), 
    default=[]
)

# Apply filters
filtered_df = df.copy()

if countries:
    filtered_df = filtered_df[filtered_df['Country'].isin(countries)]
if disease_categories:
    filtered_df = filtered_df[filtered_df['Disease Category'].isin(disease_categories)]
if age_groups:
    filtered_df = filtered_df[filtered_df['Age Group'].isin(age_groups)]

filtered_df = filtered_df[
    (filtered_df['Year'] >= year_range[0]) & 
    (filtered_df['Year'] <= year_range[1])
]

# ====================== TABS ======================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview & KPIs", 
    "📈 Disease Trends", 
    "🌍 Geographical Analysis", 
    "👥 Demographics", 
    "⚠️ Risk Assessment",
    "🔮 Prediction & Insights (M6)"
])

# ====================== TAB 1: OVERVIEW & KPIs ======================
with tab1:
    st.subheader("Key Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Avg Mortality Rate", f"{filtered_df['Mortality Rate (%)'].mean():.2f}%")
    with col2:
        st.metric("Avg Recovery Rate", f"{filtered_df['Recovery Rate (%)'].mean():.2f}%")
    with col3:
        st.metric("Total Affected", f"{filtered_df['Population Affected'].sum():,}")
    with col4:
        st.metric("Avg Healthcare Access", f"{filtered_df['Healthcare Access (%)'].mean():.1f}%")
    with col5:
        st.metric("Avg DALYs", f"{filtered_df['DALYs'].mean():,.0f}")
    
    st.plotly_chart(
        px.line(filtered_df.groupby('Year')['Mortality Rate (%)'].mean().reset_index(),
                x='Year', y='Mortality Rate (%)', title="Mortality Rate Trend"),
        use_container_width=True
    )

# ====================== TAB 2–5: PLACEHOLDERS ======================
with tab2:
    st.subheader("Disease Trends")
    st.info("Add line/bar charts comparing diseases over time here (Milestone 5)")
    # Add disease-wise trend charts

with tab3:
    st.subheader("Geographical Analysis")
    st.info("Add choropleth map or country comparison here")
    # Add geographical visualizations

with tab4:
    st.subheader("Demographic Insights")
    st.info("Add age group and gender analysis here")
    # Add demographic breakdowns

with tab5:
    st.subheader("Risk Assessment")
    st.info("Add High_Risk_Demographic and Severity_Index analysis here")
    # Add risk heatmaps / top risk tables

# ====================== TAB 6: PREDICTION (MILESTONE 6) ======================
with tab6:
    st.subheader("Mortality Rate Prediction & Explainable AI")
    st.markdown("**Research Contribution**: XGBoost + SHAP Explainability")

    # Load trained model
    model_path = "models/mortality_predictor.pkl"
    
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        st.success("Model loaded successfully")
        
        # Feature inputs for prediction
        st.subheader("Make a Prediction")
        
        col1, col2 = st.columns(2)
        
        with col1:
            prevalence = st.slider("Prevalence Rate (%)", 0.0, 50.0, 5.0)
            healthcare = st.slider("Healthcare Access (%)", 0.0, 100.0, 70.0)
            doctors = st.slider("Doctors per 1000", 0.0, 10.0, 2.5)
        
        with col2:
            urbanization = st.slider("Urbanization Rate (%)", 0.0, 100.0, 60.0)
            age_group = st.selectbox("Age Group", options=df['Age Group'].unique())
            disease_cat = st.selectbox("Disease Category", options=df['Disease Category'].unique())
        
        if st.button("Predict Mortality Rate"):
            # TODO: Create input DataFrame with proper feature engineering
            input_data = pd.DataFrame({
                'Prevalence Rate (%)': [prevalence],
                'Healthcare Access (%)': [healthcare],
                'Doctors per 1000': [doctors],
                'Urbanization Rate (%)': [urbanization],
                # Add more features as used during training
            })
            
            # One-hot encode categorical variables (update according to your training)
            # input_data = pd.get_dummies(input_data, drop_first=True)
            
            prediction = model.predict(input_data)[0]
            st.success(f"**Predicted Mortality Rate: {prediction:.2f}%**")
            
            # Add SHAP explanation here
            st.info("SHAP Force Plot / Summary Plot will be shown here (Explainability)")
            
    else:
        st.warning("Model not found. Train the model in `milestone6_research.ipynb` and save it to `models/mortality_predictor.pkl`")

# ====================== FOOTER ======================
st.caption("Data-Visualization-Project | Milestone 5 + Milestone 6 | Streamlit Dashboard")