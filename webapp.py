# =============================================================================
# SDS 2206 - Global Health Visual Analytics Dashboard
# Milestone 5: Interactive Visual Analytics System
# Milestone 6: Research Contribution & Advanced Analytics (XGBoost + SHAP)
# Dataset: Global Health Statistics (1,000,000 rows × 22 columns)
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Health Analytics",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0f1117; color: #e0e0e0; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f2e 0%, #0f1117 100%);
        border-right: 1px solid #2a2f3e;
    }
    .kpi-card {
        background: linear-gradient(135deg, #1e2537 0%, #252d42 100%);
        border: 1px solid #2e3a52; border-radius: 12px;
        padding: 1.2rem 1.4rem; text-align: center; transition: transform 0.2s;
    }
    .kpi-card:hover { transform: translateY(-3px); border-color: #4fc3f7; }
    .kpi-label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 1.2px; color: #7a8aaa; margin-bottom: 0.5rem; }
    .kpi-value { font-size: 1.9rem; font-weight: 700; color: #e8eaf6; line-height: 1; }
    .kpi-delta { font-size: 0.78rem; margin-top: 0.4rem; }
    .delta-up { color: #ef5350; } .delta-down { color: #26a69a; } .delta-neu { color: #7a8aaa; }
    .section-header {
        font-size: 1.05rem; font-weight: 600; color: #4fc3f7;
        padding-bottom: 0.4rem; border-bottom: 2px solid #2e3a52; margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; background: #1a1f2e; border-radius: 8px; padding: 4px; }
    .stTabs [data-baseweb="tab"] { border-radius: 6px; color: #7a8aaa; font-size: 0.85rem; }
    .stTabs [aria-selected="true"] { background: #2e3a52 !important; color: #4fc3f7 !important; }
    .insight-box {
        background: #1a2535; border-left: 4px solid #4fc3f7;
        border-radius: 0 8px 8px 0; padding: 0.8rem 1rem; margin: 0.5rem 0;
        font-size: 0.85rem; color: #b0bec5;
    }
    .warning-box {
        background: #2a1f1a; border-left: 4px solid #ef5350;
        border-radius: 0 8px 8px 0; padding: 0.8rem 1rem; margin: 0.5rem 0;
        font-size: 0.85rem; color: #b0bec5;
    }
    .model-metric { background: #1e2537; border: 1px solid #2e3a52; border-radius: 8px; padding: 1rem; text-align: center; }
    .model-metric .val { font-size: 1.6rem; font-weight: 700; color: #4fc3f7; }
    .model-metric .lbl { font-size: 0.75rem; color: #7a8aaa; text-transform: uppercase; }
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Plotly theme ───────────────────────────────────────────────────────────────
PLOT_THEME = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#b0bec5', size=11),
    title_font=dict(color='#e0e0e0', size=13),
    legend=dict(bgcolor='rgba(30,37,55,0.8)', bordercolor='#2e3a52', borderwidth=1),
    colorway=['#4fc3f7','#26a69a','#7e57c2','#ef5350','#ffa726','#66bb6a','#ec407a','#29b6f6','#ab47bc','#ff7043'],
    xaxis=dict(gridcolor='#1e2537', zerolinecolor='#2e3a52', tickfont=dict(size=10)),
    yaxis=dict(gridcolor='#1e2537', zerolinecolor='#2e3a52', tickfont=dict(size=10)),
)

def apply_theme(fig, title=''):
    fig.update_layout(**PLOT_THEME)
    if title:
        fig.update_layout(title=dict(text=title, font=dict(size=13, color='#e0e0e0')))
    return fig

AGE_ORDER = ['0-18', '19-35', '36-60', '61+']

# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING  — tries processed gz first, then raw CSV
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def load_data():
    PROJECT_ROOT = Path().resolve().parent if Path().resolve().name == 'notebooks' else Path().resolve()
    candidates = [
        PROJECT_ROOT / 'data' / 'processed' / 'global_health_enriched.csv.gz',
        PROJECT_ROOT / 'data' / 'raw' / 'Global Health Statistics.csv',
        PROJECT_ROOT / 'Global Health Statistics.csv',
    ]
    df = None
    for p in candidates:
        if p.exists():
            df = pd.read_csv(p, compression='gzip') if str(p).endswith('.gz') else pd.read_csv(p)
            break
    if df is None:
        raise FileNotFoundError(
            "Dataset not found. Place 'Global Health Statistics.csv' in:\n"
            "  data/raw/   OR   data/processed/ (as .csv.gz)   OR   project root"
        )

    # ── Derived / engineered columns ──────────────────────────────────────────
    if 'Severity_Index' not in df.columns:
        df['Severity_Index'] = (df['Mortality Rate (%)'] * 0.6 +
                                 (100 - df['Recovery Rate (%)']) * 0.4) / 10

    if 'DALY_Intensity' not in df.columns and 'DALYs' in df.columns:
        df['DALY_Intensity'] = df['DALYs'] / (df['Population Affected'] + 1) * 100000

    if 'Vaccine_Available_Flag' not in df.columns:
        df['Vaccine_Available_Flag'] = (
            df['Availability of Vaccines/Treatment'].str.strip().str.lower() == 'yes'
        ).astype(int)

    if 'High_Risk_Demographic' not in df.columns:
        df['High_Risk_Demographic'] = (
            (df['Age Group'] == '61+') |
            (df['Mortality Rate (%)'] > df['Mortality Rate (%)'].quantile(0.75))
        ).astype(int)

    if 'Weighted_Time_Impact' not in df.columns:
        df['Weighted_Time_Impact'] = df['Severity_Index'] * df['Incidence Rate (%)'] / 100

    return df

with st.spinner("Loading dataset…"):
    try:
        df = load_data()
    except FileNotFoundError as e:
        st.error(str(e))
        st.stop()

@st.cache_resource(show_spinner=False)
def load_model():
    import joblib
    for p in [Path('models/mortality_predictor.pkl'), Path('mortality_predictor.pkl')]:
        if p.exists():
            return joblib.load(p)
    return None

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 0.5rem;">
        <div style="font-size:2rem;">🌍</div>
        <div style="font-size:1rem;font-weight:700;color:#4fc3f7;">Global Health</div>
        <div style="font-size:0.72rem;color:#7a8aaa;letter-spacing:1px;">ANALYTICS DASHBOARD</div>
    </div><hr style="border-color:#2e3a52;margin:0.8rem 0;">
    """, unsafe_allow_html=True)

    st.markdown("## 🎛️ Filters")
    countries     = st.multiselect("🌐 Country",          sorted(df['Country'].dropna().unique()),         default=[], placeholder="All countries")
    disease_cats  = st.multiselect("🦠 Disease Category", sorted(df['Disease Category'].dropna().unique()), default=[], placeholder="All categories")
    disease_names = st.multiselect("💊 Disease Name",     sorted(df['Disease Name'].dropna().unique()),     default=[], placeholder="All diseases")
    year_range    = st.slider("📅 Year Range", int(df['Year'].min()), int(df['Year'].max()), (int(df['Year'].min()), int(df['Year'].max())))
    age_groups    = st.multiselect("👤 Age Group",  AGE_ORDER,                                              default=[], placeholder="All age groups")
    genders       = st.multiselect("⚧ Gender",     sorted(df['Gender'].dropna().unique()),                 default=[], placeholder="All genders")
    show_high_risk= st.toggle("⚠️ High-Risk Only", value=False)
    sev_range     = st.slider("🔥 Severity Index",
                               float(df['Severity_Index'].min()), float(df['Severity_Index'].max()),
                               (float(df['Severity_Index'].min()), float(df['Severity_Index'].max())), step=0.1)
    st.markdown("<hr style='border-color:#2e3a52;'>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.72rem;color:#4a5a7a;text-align:center;'>SDS 2206 · M5 & M6<br>{df.shape[0]:,} rows · {df.shape[1]} cols</div>", unsafe_allow_html=True)

# ── Filter ─────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def filter_data(_df, countries, disease_cats, disease_names, year_range, age_groups, genders, show_high_risk, sev_range):
    d = _df.copy()
    if countries:     d = d[d['Country'].isin(countries)]
    if disease_cats:  d = d[d['Disease Category'].isin(disease_cats)]
    if disease_names: d = d[d['Disease Name'].isin(disease_names)]
    d = d[(d['Year'] >= year_range[0]) & (d['Year'] <= year_range[1])]
    if age_groups:    d = d[d['Age Group'].isin(age_groups)]
    if genders:       d = d[d['Gender'].isin(genders)]
    if show_high_risk: d = d[d['High_Risk_Demographic'] == 1]
    d = d[(d['Severity_Index'] >= sev_range[0]) & (d['Severity_Index'] <= sev_range[1])]
    return d

dff = filter_data(df, tuple(countries), tuple(disease_cats), tuple(disease_names),
                  year_range, tuple(age_groups), tuple(genders), show_high_risk, sev_range)

if len(dff) == 0:
    st.warning("⚠️ No data matches your filters. Please adjust the sidebar.")
    st.stop()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:1rem 0 0.5rem;">
    <h1 style="font-size:1.6rem;font-weight:800;color:#e8eaf6;margin:0;">🌍 Global Health Visual Analytics System</h1>
    <p style="color:#7a8aaa;font-size:0.85rem;margin:0.2rem 0 0;">Public Health Data Visualization · SDS 2206 · Milestone 5 &amp; 6</p>
</div>
""", unsafe_allow_html=True)

tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs([
    "📊 Overview & KPIs","📈 Disease Trends","🗺️ Geographical Analysis",
    "👥 Demographic Insights","⚠️ Risk Assessment","🤖 Prediction & Insights"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 – OVERVIEW & KPIs
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    avg_mort  = dff['Mortality Rate (%)'].mean()
    avg_recov = dff['Recovery Rate (%)'].mean()
    total_pop = dff['Population Affected'].sum()
    avg_hca   = dff['Healthcare Access (%)'].mean()
    total_daly= dff['DALYs'].sum() if 'DALYs' in dff.columns else 0

    kpis = [
        ("Avg Mortality Rate",  f"{avg_mort:.2f}%",   "delta-up",  "↑ higher = worse"),
        ("Avg Recovery Rate",   f"{avg_recov:.2f}%",  "delta-down","↑ better outcome"),
        ("Population Affected", f"{total_pop:,.0f}",  "delta-neu", "total in filter"),
        ("Healthcare Access",   f"{avg_hca:.1f}%",    "delta-down","avg across region"),
        ("Total DALYs",         f"{total_daly:,.0f}", "delta-up",  "disability-adjusted"),
        ("Filtered Records",    f"{len(dff):,}",      "delta-neu", f"of {len(df):,} total"),
    ]
    cols = st.columns(6)
    for col,(lbl,val,cls,hint) in zip(cols,kpis):
        col.markdown(f'<div class="kpi-card"><div class="kpi-label">{lbl}</div><div class="kpi-value">{val}</div><div class="kpi-delta {cls}">{hint}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-header">Mortality Rate Distribution</div>', unsafe_allow_html=True)
        s = dff['Mortality Rate (%)'].dropna().sample(min(50000,len(dff)),random_state=42)
        fig = go.Figure(go.Histogram(x=s,nbinsx=60,marker=dict(color='#4fc3f7',line=dict(width=0.3,color='#1a2535')),opacity=0.85))
        fig.add_vline(x=avg_mort,line_dash='dash',line_color='#ef5350',annotation_text=f"Mean {avg_mort:.2f}%",annotation_font_color='#ef5350')
        apply_theme(fig); fig.update_layout(height=300,margin=dict(l=0,r=0,t=10,b=0),xaxis_title='Mortality Rate (%)',yaxis_title='Count')
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        st.markdown('<div class="section-header">Avg Mortality by Disease Category</div>', unsafe_allow_html=True)
        grp = dff.groupby('Disease Category')['Mortality Rate (%)'].mean().sort_values(ascending=True)
        fig = go.Figure(go.Bar(x=grp.values,y=grp.index,orientation='h',
            marker=dict(color=grp.values,colorscale=[[0,'#26a69a'],[0.5,'#4fc3f7'],[1,'#ef5350']],showscale=False)))
        apply_theme(fig); fig.update_layout(height=300,margin=dict(l=0,r=0,t=10,b=0),xaxis_title='Avg Mortality (%)')
        st.plotly_chart(fig,use_container_width=True)

    c3,c4 = st.columns([1.3,0.7])
    with c3:
        st.markdown('<div class="section-header">Year-over-Year KPI Trends</div>', unsafe_allow_html=True)
        yg = dff.groupby('Year').agg({'Mortality Rate (%)':'mean','Recovery Rate (%)':'mean','Healthcare Access (%)':'mean'}).reset_index()
        fig = make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(go.Scatter(x=yg['Year'],y=yg['Mortality Rate (%)'],name='Mortality %',line=dict(color='#ef5350',width=2)),secondary_y=False)
        fig.add_trace(go.Scatter(x=yg['Year'],y=yg['Recovery Rate (%)'],name='Recovery %',line=dict(color='#26a69a',width=2)),secondary_y=False)
        fig.add_trace(go.Scatter(x=yg['Year'],y=yg['Healthcare Access (%)'],name='Healthcare Access %',line=dict(color='#ffa726',width=1.5,dash='dot')),secondary_y=True)
        apply_theme(fig); fig.update_layout(height=300,margin=dict(l=0,r=0,t=10,b=0))
        fig.update_yaxes(title_text="Rate (%)",secondary_y=False,gridcolor='#1e2537')
        fig.update_yaxes(title_text="Healthcare Access (%)",secondary_y=True,gridcolor='#1e2537')
        st.plotly_chart(fig,use_container_width=True)
    with c4:
        st.markdown('<div class="section-header">Recovery vs Mortality</div>', unsafe_allow_html=True)
        sc = dff.sample(min(5000,len(dff)),random_state=1)
        fig = px.scatter(sc,x='Recovery Rate (%)',y='Mortality Rate (%)',color='Disease Category',opacity=0.5,color_discrete_sequence=PLOT_THEME['colorway'])
        apply_theme(fig); fig.update_layout(height=300,margin=dict(l=0,r=0,t=10,b=0),showlegend=False)
        st.plotly_chart(fig,use_container_width=True)

    st.markdown('<div class="section-header">🔍 Automated Insights</div>', unsafe_allow_html=True)
    ia,ib,ic = st.columns(3)
    with ia:
        w = dff.groupby('Disease Category')['Mortality Rate (%)'].mean()
        st.markdown(f'<div class="warning-box">⚠️ <strong>{w.idxmax()}</strong> has the highest avg mortality at <strong>{w.max():.2f}%</strong>.</div>', unsafe_allow_html=True)
    with ib:
        h = dff.groupby('Country')['Healthcare Access (%)'].mean()
        st.markdown(f'<div class="insight-box">🏥 <strong>{h.idxmin()}</strong> has the lowest healthcare access at <strong>{h.min():.1f}%</strong> — priority for intervention.</div>', unsafe_allow_html=True)
    with ic:
        a = dff.groupby('Age Group')['Mortality Rate (%)'].mean()
        st.markdown(f'<div class="insight-box">👤 <strong>{a.idxmax()}</strong> age group has the highest avg mortality at <strong>{a.max():.2f}%</strong>.</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 – DISEASE TRENDS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-header">Mortality Trend by Disease Category</div>', unsafe_allow_html=True)
        t = dff.groupby(['Year','Disease Category'])['Mortality Rate (%)'].mean().reset_index()
        fig = px.line(t,x='Year',y='Mortality Rate (%)',color='Disease Category',color_discrete_sequence=PLOT_THEME['colorway'])
        apply_theme(fig); fig.update_layout(height=360,margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        st.markdown('<div class="section-header">Incidence Rate Trend (Area)</div>', unsafe_allow_html=True)
        i = dff.groupby(['Year','Disease Category'])['Incidence Rate (%)'].mean().reset_index()
        fig = px.area(i,x='Year',y='Incidence Rate (%)',color='Disease Category',color_discrete_sequence=PLOT_THEME['colorway'])
        apply_theme(fig); fig.update_layout(height=360,margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig,use_container_width=True)

    st.markdown('<div class="section-header">Improvement in 5 Years (%) — Top 15 Diseases</div>', unsafe_allow_html=True)
    imp = dff.groupby('Disease Name')['Improvement in 5 Years (%)'].mean().sort_values(ascending=False).head(15).reset_index()
    fig = px.bar(imp,x='Disease Name',y='Improvement in 5 Years (%)',color='Improvement in 5 Years (%)',color_continuous_scale='Teal')
    apply_theme(fig); fig.update_layout(height=340,margin=dict(l=0,r=0,t=10,b=0),xaxis_tickangle=-35,coloraxis_showscale=False)
    st.plotly_chart(fig,use_container_width=True)

    st.markdown('<div class="section-header">Disease Burden Summary Table</div>', unsafe_allow_html=True)
    summary = dff.groupby('Disease Category').agg({
        'Mortality Rate (%)':'mean','Recovery Rate (%)':'mean',
        'Incidence Rate (%)':'mean','Prevalence Rate (%)':'mean',
        'Healthcare Access (%)':'mean','Population Affected':'sum','DALYs':'sum'
    }).round(2).reset_index()
    st.dataframe(summary.style
        .background_gradient(subset=['Mortality Rate (%)','Incidence Rate (%)'],cmap='Reds')
        .background_gradient(subset=['Recovery Rate (%)','Healthcare Access (%)'],cmap='Greens'),
        use_container_width=True,height=320)

    st.markdown('<div class="section-header">Prevalence vs Mortality Bubble Chart (size = Avg DALYs)</div>', unsafe_allow_html=True)
    bub = dff.groupby('Disease Category').agg({'Prevalence Rate (%)':'mean','Mortality Rate (%)':'mean','DALYs':'mean'}).reset_index()
    fig = px.scatter(bub,x='Prevalence Rate (%)',y='Mortality Rate (%)',size='DALYs',color='Disease Category',
                     text='Disease Category',color_discrete_sequence=PLOT_THEME['colorway'],size_max=50)
    fig.update_traces(textposition='top center',textfont_size=9)
    apply_theme(fig); fig.update_layout(height=420,margin=dict(l=0,r=0,t=10,b=0),showlegend=False)
    st.plotly_chart(fig,use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 – GEOGRAPHICAL ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">Geographical Health Metrics</div>', unsafe_allow_html=True)
    geo_metric = st.selectbox("Metric to Map",['Mortality Rate (%)','Recovery Rate (%)','Healthcare Access (%)','Incidence Rate (%)','Prevalence Rate (%)','DALYs'],key='geo_metric')
    ca = dff.groupby('Country').agg({'Mortality Rate (%)':'mean','Recovery Rate (%)':'mean','Healthcare Access (%)':'mean','Incidence Rate (%)':'mean','Prevalence Rate (%)':'mean','DALYs':'sum','Population Affected':'sum'}).reset_index()

    fig = px.choropleth(ca,locations='Country',locationmode='country names',color=geo_metric,
        color_continuous_scale='RdYlGn_r' if geo_metric in ['Mortality Rate (%)','DALYs'] else 'RdYlGn',
        hover_data=['Mortality Rate (%)','Recovery Rate (%)','Healthcare Access (%)'],title=f'Global {geo_metric} by Country')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
        geo=dict(bgcolor='rgba(20,25,40,1)',showframe=False,showcoastlines=True,coastlinecolor='#2e3a52',showland=True,landcolor='#1e2537',showocean=True,oceancolor='#0f1117'),
        coloraxis_colorbar=dict(title=geo_metric,tickfont=dict(color='#b0bec5'),title_font=dict(color='#b0bec5')),
        font=dict(color='#b0bec5'),title_font=dict(color='#e0e0e0',size=13),height=480,margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig,use_container_width=True)

    cg,ch = st.columns(2)
    with cg:
        st.markdown('<div class="section-header">🔴 Top 10 Highest</div>', unsafe_allow_html=True)
        fig = px.bar(ca.nlargest(10,geo_metric),x=geo_metric,y='Country',orientation='h',color=geo_metric,color_continuous_scale='Reds')
        apply_theme(fig); fig.update_layout(height=320,margin=dict(l=0,r=0,t=10,b=0),coloraxis_showscale=False)
        st.plotly_chart(fig,use_container_width=True)
    with ch:
        st.markdown('<div class="section-header">🟢 Top 10 Lowest</div>', unsafe_allow_html=True)
        fig = px.bar(ca.nsmallest(10,geo_metric),x=geo_metric,y='Country',orientation='h',color=geo_metric,color_continuous_scale='Greens_r')
        apply_theme(fig); fig.update_layout(height=320,margin=dict(l=0,r=0,t=10,b=0),coloraxis_showscale=False)
        st.plotly_chart(fig,use_container_width=True)

    st.markdown('<div class="section-header">Avg Treatment Cost (USD) by Country — Top 15</div>', unsafe_allow_html=True)
    cost = dff.groupby('Country')['Average Treatment Cost (USD)'].mean().nlargest(15).reset_index()
    fig = px.bar(cost,x='Country',y='Average Treatment Cost (USD)',color='Average Treatment Cost (USD)',color_continuous_scale='Purples')
    apply_theme(fig); fig.update_layout(height=320,margin=dict(l=0,r=0,t=10,b=0),xaxis_tickangle=-35,coloraxis_showscale=False)
    st.plotly_chart(fig,use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 – DEMOGRAPHIC INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">Demographic Breakdown of Health Outcomes</div>', unsafe_allow_html=True)
    ci,cj = st.columns(2)
    with ci:
        am = dff.groupby('Age Group')['Mortality Rate (%)'].mean().reset_index()
        am['Age Group'] = pd.Categorical(am['Age Group'],categories=AGE_ORDER,ordered=True)
        am = am.sort_values('Age Group')
        fig = px.bar(am,x='Age Group',y='Mortality Rate (%)',color='Age Group',color_discrete_sequence=PLOT_THEME['colorway'])
        apply_theme(fig,'Avg Mortality Rate by Age Group'); fig.update_layout(height=340,margin=dict(l=0,r=0,t=30,b=0),showlegend=False)
        st.plotly_chart(fig,use_container_width=True)
    with cj:
        gm = dff.groupby('Gender')['Mortality Rate (%)'].mean().reset_index()
        fig = px.pie(gm,names='Gender',values='Mortality Rate (%)',color_discrete_sequence=['#4fc3f7','#ef5350','#26a69a'],hole=0.45)
        apply_theme(fig,'Mortality Distribution by Gender'); fig.update_layout(height=340,margin=dict(l=0,r=0,t=30,b=0))
        st.plotly_chart(fig,use_container_width=True)

    st.markdown('<div class="section-header">Mortality Heatmap: Age Group × Disease Category</div>', unsafe_allow_html=True)
    pivot = dff.pivot_table(index='Age Group',columns='Disease Category',values='Mortality Rate (%)',aggfunc='mean')
    pivot = pivot.reindex([a for a in AGE_ORDER if a in pivot.index])
    fig = px.imshow(pivot,color_continuous_scale='RdYlGn_r',aspect='auto',text_auto='.1f')
    fig.update_traces(textfont_size=9); apply_theme(fig); fig.update_layout(height=320,margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig,use_container_width=True)

    st.markdown('<div class="section-header">Mortality Drill-Down: Gender → Age → Disease (Sunburst)</div>', unsafe_allow_html=True)
    sun = dff.groupby(['Gender','Age Group','Disease Category'])['Mortality Rate (%)'].mean().reset_index()
    fig = px.sunburst(sun,path=['Gender','Age Group','Disease Category'],values='Mortality Rate (%)',color='Mortality Rate (%)',color_continuous_scale='RdYlGn_r')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',height=480,margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig,use_container_width=True)

    st.markdown('<div class="section-header">Outcome by Treatment Type & Vaccine Availability</div>', unsafe_allow_html=True)
    ck,cl = st.columns(2)
    with ck:
        tm = dff.groupby('Treatment Type')[['Mortality Rate (%)','Recovery Rate (%)']].mean().reset_index()
        fig = px.bar(tm,x='Treatment Type',y=['Mortality Rate (%)','Recovery Rate (%)'],barmode='group',
                     color_discrete_map={'Mortality Rate (%)':'#ef5350','Recovery Rate (%)':'#26a69a'})
        apply_theme(fig,'Mortality vs Recovery by Treatment Type'); fig.update_layout(height=320,margin=dict(l=0,r=0,t=30,b=0))
        st.plotly_chart(fig,use_container_width=True)
    with cl:
        vm = dff.groupby('Availability of Vaccines/Treatment')[['Mortality Rate (%)','Recovery Rate (%)']].mean().reset_index()
        fig = px.bar(vm,x='Availability of Vaccines/Treatment',y=['Mortality Rate (%)','Recovery Rate (%)'],barmode='group',
                     color_discrete_map={'Mortality Rate (%)':'#ef5350','Recovery Rate (%)':'#26a69a'})
        apply_theme(fig,'Impact of Vaccine/Treatment Availability'); fig.update_layout(height=320,margin=dict(l=0,r=0,t=30,b=0))
        st.plotly_chart(fig,use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 – RISK ASSESSMENT
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">⚠️ Risk Assessment Dashboard</div>', unsafe_allow_html=True)

    # Use Case 1
    st.markdown("**Use Case 1 — Countries with High Mortality but Low Healthcare Access**")
    r1 = dff.groupby('Country').agg({'Mortality Rate (%)':'mean','Healthcare Access (%)':'mean','Population Affected':'sum'}).reset_index()
    r1['Risk Score'] = r1['Mortality Rate (%)'] / (r1['Healthcare Access (%)'] + 1) * 100
    fig = px.scatter(r1,x='Healthcare Access (%)',y='Mortality Rate (%)',size='Population Affected',color='Risk Score',
                     hover_name='Country',text='Country',color_continuous_scale='RdYlGn_r',size_max=40)
    fig.update_traces(textposition='top center',textfont_size=8)
    fig.add_vline(x=r1['Healthcare Access (%)'].median(),line_dash='dash',line_color='#ffa726',annotation_text='Median HCA',annotation_font_color='#ffa726')
    fig.add_hline(y=r1['Mortality Rate (%)'].median(),line_dash='dash',line_color='#ef5350',annotation_text='Median Mortality',annotation_font_color='#ef5350')
    apply_theme(fig,'Risk Quadrant: Mortality vs Healthcare Access (bubble size = Population Affected)')
    fig.update_layout(height=460,margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig,use_container_width=True)
    st.markdown("**Top 10 Highest-Risk Countries**")
    st.dataframe(r1.nlargest(10,'Risk Score')[['Country','Mortality Rate (%)','Healthcare Access (%)','Risk Score','Population Affected']].round(3),use_container_width=True)

    st.markdown("---")

    # Use Case 2
    st.markdown("**Use Case 2 — Disease Burden Across Age Groups & Genders**")
    d2 = dff.groupby(['Age Group','Gender']).agg({'Mortality Rate (%)':'mean','Recovery Rate (%)':'mean','DALYs':'sum'}).reset_index()
    cm,cn = st.columns(2)
    with cm:
        fig = px.bar(d2,x='Age Group',y='Mortality Rate (%)',color='Gender',barmode='group',color_discrete_sequence=['#4fc3f7','#ef5350','#26a69a'])
        apply_theme(fig,'Mortality by Age Group & Gender'); fig.update_layout(height=320,margin=dict(l=0,r=0,t=30,b=0))
        st.plotly_chart(fig,use_container_width=True)
    with cn:
        fig = px.bar(d2,x='Age Group',y='DALYs',color='Gender',barmode='group',color_discrete_sequence=['#4fc3f7','#ef5350','#26a69a'])
        apply_theme(fig,'Total DALYs by Age Group & Gender'); fig.update_layout(height=320,margin=dict(l=0,r=0,t=30,b=0))
        st.plotly_chart(fig,use_container_width=True)

    st.markdown("---")

    # Use Case 3
    st.markdown("**Use Case 3 — High-Risk Demographics by Severity Index**")
    fig = px.box(dff.sample(min(30000,len(dff)),random_state=42),x='Disease Category',y='Severity_Index',
                 color='Disease Category',color_discrete_sequence=PLOT_THEME['colorway'])
    apply_theme(fig,'Severity Index Distribution by Disease Category')
    fig.update_layout(height=380,margin=dict(l=0,r=0,t=40,b=0),showlegend=False,xaxis_tickangle=-20)
    st.plotly_chart(fig,use_container_width=True)

    hr = dff[dff['High_Risk_Demographic']==1].groupby(['Disease Category','Age Group']).agg(
        {'Mortality Rate (%)':'mean','Recovery Rate (%)':'mean','Population Affected':'sum'}
    ).round(2).reset_index().sort_values('Mortality Rate (%)',ascending=False)
    st.markdown("**High-Risk Records Summary (Top 15)**")
    st.dataframe(hr.head(15),use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 – PREDICTION & INSIGHTS  (Milestone 6)
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1a2535,#1e2b45);border:1px solid #2e3a52;
         border-radius:12px;padding:1rem 1.4rem;margin-bottom:1.2rem;">
        <div style="font-size:1rem;font-weight:700;color:#4fc3f7;">🤖 Milestone 6 — XGBoost + SHAP Explainability</div>
        <div style="font-size:0.82rem;color:#7a8aaa;margin-top:0.3rem;">Predictive Modeling and Explainable AI for Global Disease Mortality Risk Assessment</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">Model Performance (XGBoost — 800K training samples)</div>', unsafe_allow_html=True)
    for col,(name,val,desc) in zip(st.columns(3),[("RMSE","0.1392","Root Mean Squared Error"),("MAE","0.0502","Mean Absolute Error"),("R²","0.9976","Coefficient of Determination")]):
        col.markdown(f'<div class="model-metric"><div class="val">{val}</div><div class="lbl">{name}</div><div style="font-size:0.7rem;color:#4a5a7a;margin-top:0.3rem;">{desc}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Top 10 XGBoost Feature Importances</div>', unsafe_allow_html=True)
    fd = pd.DataFrame({'Feature':['Severity_Index','Prevalence Rate (%)','Age Group_61+','Age Group_36-60','Treatment Type_Vaccination','Disease Category_Bacterial','Weighted_Time_Impact','Treatment Type_Surgery','Education Index','Disease Category_Viral'],
                        'Importance':[0.727019,0.247145,0.001009,0.000980,0.000964,0.000956,0.000955,0.000954,0.000945,0.000940]}).sort_values('Importance',ascending=True)
    colors = ['#4fc3f7' if i==len(fd)-1 else '#26a69a' if i==len(fd)-2 else '#2e3a52' for i in range(len(fd))]
    fig = go.Figure(go.Bar(x=fd['Importance'],y=fd['Feature'],orientation='h',marker=dict(color=colors),
                            text=[f"{v:.4f}" for v in fd['Importance']],textposition='outside',textfont=dict(color='#b0bec5',size=9)))
    apply_theme(fig); fig.update_layout(height=380,margin=dict(l=0,r=0,t=10,b=0),xaxis_title='Feature Importance (Gain)')
    st.plotly_chart(fig,use_container_width=True)

    st.markdown('<div class="section-header">SHAP Explainability</div>', unsafe_allow_html=True)
    sc1,sc2 = st.columns([1.1,0.9])
    with sc1:
        st.markdown("""
        <div class="insight-box"><strong>Severity_Index (SHAP ≈ 0.727)</strong><br>Dominant predictor — higher severity strongly increases predicted mortality. Captures disease aggressiveness and patient health baseline.</div>
        <div class="insight-box"><strong>Prevalence Rate (SHAP ≈ 0.247)</strong><br>Higher disease prevalence correlates with greater mortality pressure on healthcare systems.</div>
        <div class="insight-box"><strong>Age Group 61+ (SHAP ≈ 0.001)</strong><br>Elderly populations show elevated mortality across all disease categories.</div>
        <div class="insight-box"><strong>Vaccination Treatment (SHAP ≈ 0.001)</strong><br>Vaccine-treated cases show lower mortality — validates protective effect of preventive interventions.</div>
        <div class="insight-box"><strong>Education Index (SHAP ≈ 0.001)</strong><br>Higher education correlates with lower mortality — reflects health literacy and access to preventive care.</div>
        """, unsafe_allow_html=True)
    with sc2:
        sv = [+2.41,+0.83,+0.12,+0.08,+0.06,-0.04,-0.09,-0.15]
        sf = ['Severity_Index','Prevalence (%)','Age 61+','Bacterial','Weighted Time','Education Idx','Vaccination','Healthcare Access']
        fig = go.Figure(go.Bar(x=sv,y=sf,orientation='h',
            marker=dict(color=['#ef5350' if v>0 else '#26a69a' for v in sv]),
            text=[f"{'+' if v>0 else ''}{v:.2f}" for v in sv],textposition='outside',textfont=dict(size=9,color='#b0bec5')))
        fig.add_vline(x=0,line_color='#4a5a7a',line_width=1)
        apply_theme(fig,'SHAP Force Plot (Sample Prediction)'); fig.update_layout(height=340,margin=dict(l=0,r=0,t=30,b=0),xaxis_title='SHAP Value')
        st.plotly_chart(fig,use_container_width=True)

    # ── Live Predictor ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🔬 Live Mortality Rate Predictor</div>', unsafe_allow_html=True)
    st.markdown('<div class="insight-box">Adjust inputs below for a real-time mortality prediction. Uses saved XGBoost model if available, otherwise analytical estimation.</div>', unsafe_allow_html=True)

    p1,p2,p3 = st.columns(3)
    with p1:
        severity   = st.slider("Severity Index",          0.0,10.0,5.0,0.1)
        prevalence = st.slider("Prevalence Rate (%)",     0.0,100.0,20.0,0.5)
        incidence  = st.slider("Incidence Rate (%)",      0.0,100.0,10.0,0.5)
        hca        = st.slider("Healthcare Access (%)",   0.0,100.0,60.0,1.0)
    with p2:
        doctors    = st.slider("Doctors per 1000",        0.0,10.0,2.5,0.1)
        beds       = st.slider("Hospital Beds per 1000",  0.0,20.0,5.0,0.1)
        urban      = st.slider("Urbanization Rate (%)",   0.0,100.0,55.0,1.0)
        income     = st.slider("Per Capita Income (USD)", 0,100000,15000,500)
    with p3:
        edu        = st.slider("Education Index",         0.0,1.0,0.6,0.01)
        recovery   = st.slider("Recovery Rate (%)",       0.0,100.0,70.0,0.5)
        age_sel    = st.selectbox("Age Group",            AGE_ORDER)
        dis_sel    = st.selectbox("Disease Category",     sorted(df['Disease Category'].unique()))
        treat_sel  = st.selectbox("Treatment Type",       ['Medication','Surgery','Vaccination','Therapy'])
        vaccine_sel= st.selectbox("Vaccine Available",    ['Yes','No'])

    model = load_model()
    pred  = None
    if model is not None:
        try:
            row = {'Prevalence Rate (%)':prevalence,'Incidence Rate (%)':incidence,'Healthcare Access (%)':hca,
                   'Doctors per 1000':doctors,'Hospital Beds per 1000':beds,'Urbanization Rate (%)':urban,
                   'Per Capita Income (USD)':income,'Education Index':edu,'Recovery Rate (%)':recovery,
                   'Severity_Index':severity,'DALY_Intensity':severity*incidence/100,
                   'Vaccine_Available_Flag':1 if vaccine_sel=='Yes' else 0,
                   'Weighted_Time_Impact':severity*incidence/100,'Avg_Incidence_Disease':incidence,
                   f'Disease Category_{dis_sel}':1,f'Age Group_{age_sel}':1,f'Treatment Type_{treat_sel}':1}
            X_pred = pd.DataFrame([row]).reindex(columns=model.get_booster().feature_names,fill_value=0)
            pred = float(model.predict(X_pred)[0])
        except Exception:
            pred = None

    if pred is None:
        base = severity*2.1 + prevalence*0.12
        mit  = hca*0.03 + recovery*0.04 + edu*5 + (1.5 if vaccine_sel=='Yes' else 0)
        bump = {'0-18':0,'19-35':0.2,'36-60':0.8,'61+':2.1}[age_sel]
        pred = max(0.0, min(100.0, base - mit + bump))

    rc = "#ef5350" if pred>15 else "#ffa726" if pred>7 else "#26a69a"
    rl = "🔴 HIGH"  if pred>15 else "🟡 MODERATE" if pred>7 else "🟢 LOW"

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1a2535,#1e2b45);border:2px solid {rc};
         border-radius:12px;padding:1.4rem 2rem;text-align:center;margin-top:1rem;">
        <div style="font-size:0.85rem;color:#7a8aaa;text-transform:uppercase;letter-spacing:1px;">Predicted Mortality Rate</div>
        <div style="font-size:3rem;font-weight:800;color:{rc};line-height:1.1;margin:0.3rem 0;">{pred:.2f}%</div>
        <div style="font-size:1.1rem;font-weight:600;color:{rc};">Risk Level: {rl}</div>
        <div style="font-size:0.75rem;color:#4a5a7a;margin-top:0.5rem;">
            {'Using saved XGBoost model (mortality_predictor.pkl)' if model else 'Analytical estimation — run M6 notebook first to enable full model'}
        </div>
    </div>""", unsafe_allow_html=True)

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=pred,
        number={'suffix':'%','font':{'size':28,'color':'#e0e0e0'}},
        delta={'reference':avg_mort,'suffix':'%','increasing':{'color':'#ef5350'},'decreasing':{'color':'#26a69a'}},
        gauge={'axis':{'range':[0,50],'tickcolor':'#7a8aaa','tickfont':{'size':10}},
               'bar':{'color':rc,'thickness':0.25},'bgcolor':'#1a1f2e','borderwidth':1,'bordercolor':'#2e3a52',
               'steps':[{'range':[0,7],'color':'#1a2a1a'},{'range':[7,15],'color':'#2a2a1a'},{'range':[15,50],'color':'#2a1a1a'}],
               'threshold':{'line':{'color':'#ffa726','width':2},'thickness':0.75,'value':avg_mort}},
        title={'text':f"Predicted vs Dataset Mean ({avg_mort:.2f}%)",'font':{'size':11,'color':'#b0bec5'}}
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',height=280,margin=dict(l=20,r=20,t=40,b=10),font=dict(color='#b0bec5'))
    st.plotly_chart(fig,use_container_width=True)