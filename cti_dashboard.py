import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(
    page_title="IFRC Community Trust Index",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLING ---
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #C8102E 0%, #8B0000 100%);
        padding: 20px 30px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        border-left: 5px solid #C8102E;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 10px;
    }
    .alert-card {
        background: #FFF3CD;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #FF6B35;
        margin-bottom: 10px;
    }
    .good-score { color: #2E8B57; font-weight: bold; font-size: 24px; }
    .medium-score { color: #FF8C00; font-weight: bold; font-size: 24px; }
    .low-score { color: #C8102E; font-weight: bold; font-size: 24px; }
    .stMetric { background: white; border-radius: 8px; padding: 10px; }
</style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    base = "/home/claude/cti_data"
    mart = pd.read_csv(f"{base}/mart_trust_index_gold.csv")
    qual = pd.read_csv(f"{base}/qualitative_responses_bronze.csv")
    surveys = pd.read_csv(f"{base}/dim_survey.csv")
    geo = pd.read_csv(f"{base}/dim_geography.csv")
    responses = pd.read_csv(f"{base}/survey_responses_bronze.csv")
    mart["survey_date"] = pd.to_datetime(mart["survey_date"])
    return mart, qual, surveys, geo, responses

mart, qual, surveys, geo, responses = load_data()

# --- HEADER ---
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size:28px;">🔴 IFRC Community Trust Index Dashboard</h1>
    <p style="margin:5px 0 0 0; opacity:0.9; font-size:14px;">
        Real-time community trust monitoring across IFRC operations | 
        Bronze → Silver → Gold Lakehouse Architecture
    </p>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR FILTERS ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Flag_of_the_Red_Cross.svg/200px-Flag_of_the_Red_Cross.svg.png", width=80)
st.sidebar.title("🔍 Filters")

zones = ["All Zones"] + sorted(mart["ifrc_zone"].unique().tolist())
selected_zone = st.sidebar.selectbox("IFRC Zone", zones)

if selected_zone != "All Zones":
    filtered_countries = mart[mart["ifrc_zone"] == selected_zone]["country_name"].unique()
else:
    filtered_countries = mart["country_name"].unique()

countries = ["All Countries"] + sorted(filtered_countries.tolist())
selected_country = st.sidebar.selectbox("Country", countries)

quarters = ["All Quarters"] + [f"Q{q}" for q in sorted(mart["quarter"].unique())]
selected_quarter = st.sidebar.selectbox("Quarter", quarters)

show_alerts_only = st.sidebar.checkbox("🚨 Show Alert Countries Only", False)

st.sidebar.markdown("---")
st.sidebar.markdown("**Pipeline Architecture**")
st.sidebar.markdown("""
- 🟫 **Bronze**: Raw KoboToolbox ingestion
- 🥈 **Silver**: Cleaned & standardised
- 🥇 **Gold**: Analytics-ready mart
""")
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Data Summary**")
st.sidebar.markdown(f"- {len(responses):,} survey responses")
st.sidebar.markdown(f"- {len(qual):,} qualitative responses")
st.sidebar.markdown(f"- {len(mart['country_name'].unique())} countries")
st.sidebar.markdown(f"- {len(surveys)} surveys")

# --- FILTER DATA ---
filtered = mart.copy()
if selected_zone != "All Zones":
    filtered = filtered[filtered["ifrc_zone"] == selected_zone]
if selected_country != "All Countries":
    filtered = filtered[filtered["country_name"] == selected_country]
if selected_quarter != "All Quarters":
    q_num = int(selected_quarter[1])
    filtered = filtered[filtered["quarter"] == q_num]
if show_alerts_only:
    filtered = filtered[filtered["alert_flag"] == True]

# --- KPI METRICS ---
st.markdown("### 📊 Key Trust Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

avg_trust = filtered["overall_trust_score"].mean()
avg_competence = filtered["competence_score"].mean()
avg_integrity = filtered["integrity_score"].mean()
avg_benevolence = filtered["benevolence_score"].mean()
avg_transparency = filtered["transparency_score"].mean()
alert_count = filtered["alert_flag"].sum()

def score_color(score):
    if score >= 60: return "good-score"
    elif score >= 45: return "medium-score"
    else: return "low-score"

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <p style="margin:0; color:#666; font-size:12px;">OVERALL TRUST INDEX</p>
        <p class="{score_color(avg_trust)}">{avg_trust:.1f}</p>
        <p style="margin:0; color:#999; font-size:11px;">out of 100</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <p style="margin:0; color:#666; font-size:12px;">COMPETENCE</p>
        <p class="{score_color(avg_competence)}">{avg_competence:.1f}</p>
        <p style="margin:0; color:#999; font-size:11px;">out of 100</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <p style="margin:0; color:#666; font-size:12px;">INTEGRITY</p>
        <p class="{score_color(avg_integrity)}">{avg_integrity:.1f}</p>
        <p style="margin:0; color:#999; font-size:11px;">out of 100</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <p style="margin:0; color:#666; font-size:12px;">BENEVOLENCE</p>
        <p class="{score_color(avg_benevolence)}">{avg_benevolence:.1f}</p>
        <p style="margin:0; color:#999; font-size:11px;">out of 100</p>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="{'alert-card' if alert_count > 0 else 'metric-card'}">
        <p style="margin:0; color:#666; font-size:12px;">🚨 ACTIVE ALERTS</p>
        <p style="color:{'#C8102E' if alert_count > 0 else '#2E8B57'}; font-weight:bold; font-size:24px;">{int(alert_count)}</p>
        <p style="margin:0; color:#999; font-size:11px;">regions flagged</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- ROW 1: MAP + TRUST BY COUNTRY ---
col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown("#### 🗺️ Trust Index by Country")
    country_avg = filtered.groupby(["country_name", "country_code"])["overall_trust_score"].mean().reset_index()
    
    fig_map = px.choropleth(
        country_avg,
        locations="country_code",
        color="overall_trust_score",
        hover_name="country_name",
        color_continuous_scale=["#C8102E", "#FF8C00", "#2E8B57"],
        range_color=[30, 80],
        labels={"overall_trust_score": "Trust Score"},
        title=""
    )
    fig_map.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(title="Score", ticksuffix="/100")
    )
    st.plotly_chart(fig_map, use_container_width=True)

with col2:
    st.markdown("#### 📈 Trust Dimensions by Country")
    country_dims = filtered.groupby("country_name").agg({
        "competence_score": "mean",
        "integrity_score": "mean",
        "benevolence_score": "mean",
        "transparency_score": "mean"
    }).reset_index().round(1)
    
    fig_bar = go.Figure()
    dimensions = ["competence_score", "integrity_score", "benevolence_score", "transparency_score"]
    colors = ["#2E75B6", "#C8102E", "#2E8B57", "#FF8C00"]
    labels = ["Competence", "Integrity", "Benevolence", "Transparency"]
    
    for dim, color, label in zip(dimensions, colors, labels):
        fig_bar.add_trace(go.Bar(
            name=label,
            x=country_dims["country_name"],
            y=country_dims[dim],
            marker_color=color,
            opacity=0.85
        ))
    
    fig_bar.update_layout(
        barmode="group",
        height=350,
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        yaxis=dict(title="Score (0-100)", range=[0, 100]),
        xaxis=dict(tickangle=-30)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# --- ROW 2: TREND + SENTIMENT ---
col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown("#### 📉 Trust Score Trend Over Time")
    trend = filtered.groupby(["country_name", "quarter"])["overall_trust_score"].mean().reset_index()
    trend["quarter_label"] = "Q" + trend["quarter"].astype(str) + " 2024"
    
    fig_trend = px.line(
        trend,
        x="quarter_label",
        y="overall_trust_score",
        color="country_name",
        markers=True,
        labels={"overall_trust_score": "Trust Score", "quarter_label": "Quarter", "country_name": "Country"},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_trend.add_hline(y=45, line_dash="dash", line_color="#C8102E",
                        annotation_text="Alert threshold (45)", annotation_position="bottom right")
    fig_trend.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=20, b=0),
        yaxis=dict(range=[0, 100]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=10))
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with col2:
    st.markdown("#### 💬 Community Sentiment Analysis")
    
    # Filter qualitative data
    if selected_country != "All Countries":
        qual_filtered = qual[qual["survey_id"].isin(
            surveys[surveys["country_code"] == filtered["country_code"].iloc[0]]["survey_id"]
        )] if not filtered.empty else qual
    else:
        qual_filtered = qual
    
    sentiment_counts = qual_filtered["sentiment_label"].value_counts().reset_index()
    sentiment_counts.columns = ["sentiment", "count"]
    
    colors_sent = {"positive": "#2E8B57", "neutral": "#FF8C00", "negative": "#C8102E"}
    fig_sentiment = px.pie(
        sentiment_counts,
        values="count",
        names="sentiment",
        color="sentiment",
        color_discrete_map=colors_sent,
        hole=0.4
    )
    fig_sentiment.update_layout(
        height=250,
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2)
    )
    st.plotly_chart(fig_sentiment, use_container_width=True)
    
    # Theme breakdown
    theme_counts = qual_filtered["theme_label"].value_counts().head(5).reset_index()
    theme_counts.columns = ["theme", "count"]
    
    fig_themes = px.bar(
        theme_counts,
        x="count",
        y="theme",
        orientation="h",
        color="count",
        color_continuous_scale=["#C8102E", "#FF8C00", "#2E8B57"],
        labels={"count": "Mentions", "theme": ""}
    )
    fig_themes.update_layout(
        height=200,
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=False,
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_themes, use_container_width=True)

st.markdown("---")

# --- ROW 3: ALERTS + RAW DATA ---
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("#### 🚨 Active Alerts")
    alerts = filtered[filtered["alert_flag"] == True][
        ["country_name", "region", "overall_trust_score", "integrity_score", "alert_reason", "quarter"]
    ].sort_values("overall_trust_score")
    
    if len(alerts) > 0:
        for _, alert in alerts.head(8).iterrows():
            st.markdown(f"""
            <div class="alert-card">
                <strong>🚨 {alert['country_name']} — {alert['region']} (Q{alert['quarter']})</strong><br>
                <span style="color:#C8102E;">Trust Score: {alert['overall_trust_score']:.1f}/100</span> | 
                Integrity: {alert['integrity_score']:.1f}/100<br>
                <small>{alert['alert_reason']}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No active alerts for selected filters")

with col2:
    st.markdown("#### 🔴 Rumour & Misinformation Flags")
    rumours = qual[qual["rumour_flag"] == True][["theme_label", "sentiment_label", "free_text_response", "nlp_confidence_score"]]
    
    if len(rumours) > 0:
        for _, r in rumours.head(5).iterrows():
            st.markdown(f"""
            <div class="alert-card">
                <strong>⚠️ {r['theme_label']}</strong> 
                <span style="color:#C8102E; font-size:11px;">[Confidence: {r['nlp_confidence_score']:.0%}]</span><br>
                <small style="color:#666;">"{r['free_text_response'][:120]}..."</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No rumour flags detected")

st.markdown("---")

# --- EMERGENCY vs NON-EMERGENCY COMPARISON ---
st.markdown("#### 🆚 Emergency Context vs Stable Context — Trust Comparison")
emergency_comp = filtered.groupby("emergency_context").agg({
    "overall_trust_score": "mean",
    "competence_score": "mean",
    "integrity_score": "mean",
    "benevolence_score": "mean",
    "transparency_score": "mean"
}).reset_index().round(1)
emergency_comp["context"] = emergency_comp["emergency_context"].map({True: "Emergency Context", False: "Stable Context"})

fig_comp = go.Figure()
dims = ["overall_trust_score", "competence_score", "integrity_score", "benevolence_score", "transparency_score"]
dim_labels = ["Overall Trust", "Competence", "Integrity", "Benevolence", "Transparency"]

for _, row in emergency_comp.iterrows():
    fig_comp.add_trace(go.Bar(
        name=row["context"],
        x=dim_labels,
        y=[row[d] for d in dims],
        marker_color="#C8102E" if row["emergency_context"] else "#2E75B6"
    ))

fig_comp.update_layout(
    barmode="group",
    height=300,
    margin=dict(l=0, r=0, t=20, b=0),
    yaxis=dict(title="Score (0-100)", range=[0, 100]),
    legend=dict(orientation="h", yanchor="bottom", y=1.02)
)
st.plotly_chart(fig_comp, use_container_width=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#999; font-size:12px;">
    🔴 IFRC Community Trust Index Dashboard | Built by Henrietta Atsenokhai<br>
    Bronze → Silver → Gold Lakehouse Architecture | Python · PostgreSQL · dbt · Streamlit · Plotly<br>
    <em>Data engineering solution for IFRC CEA Community Trust Index consultancy</em>
</div>
""", unsafe_allow_html=True)
