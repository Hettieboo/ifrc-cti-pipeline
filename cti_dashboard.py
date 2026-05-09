import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import os

st.set_page_config(
    page_title="IFRC Community Trust Index",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #C8102E 0%, #8B0000 100%);
        padding: 20px 30px; border-radius: 10px; margin-bottom: 20px; color: white;
    }
    .metric-card {
        background: white; border-radius: 10px; padding: 20px;
        border-left: 5px solid #C8102E; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 10px;
    }
    .alert-card {
        background: #FFF3CD; border-radius: 10px; padding: 15px;
        border-left: 5px solid #FF6B35; margin-bottom: 10px;
    }
    .rumour-card {
        background: #FFE8E8; border-radius: 10px; padding: 15px;
        border-left: 5px solid #C8102E; margin-bottom: 10px;
    }
    .good-score { color: #2E8B57; font-weight: bold; font-size: 24px; }
    .medium-score { color: #FF8C00; font-weight: bold; font-size: 24px; }
    .low-score { color: #C8102E; font-weight: bold; font-size: 24px; }
</style>
""", unsafe_allow_html=True)

COUNTRY_COORDS = {
    "Kenya": (-0.0236, 37.9062),
    "Nigeria": (9.0820, 8.6753),
    "Philippines": (12.8797, 121.7740),
    "Colombia": (4.5709, -74.2973),
    "Ukraine": (48.3794, 31.1656),
    "Bangladesh": (23.6850, 90.3563),
    "Ethiopia": (9.1450, 40.4897),
    "Mexico": (23.6345, -102.5528),
}

def get_marker_color(score):
    if score >= 60: return "green"
    elif score >= 45: return "orange"
    else: return "red"

@st.cache_data
def load_data():
    base = "cti_data"
    mart = pd.read_csv(f"{base}/mart_trust_index_gold.csv")
    qual = pd.read_csv(f"{base}/qualitative_responses_bronze.csv")
    surveys = pd.read_csv(f"{base}/dim_survey.csv")
    geo = pd.read_csv(f"{base}/dim_geography.csv")
    responses = pd.read_csv(f"{base}/survey_responses_bronze.csv")
    mart["survey_date"] = pd.to_datetime(mart["survey_date"])
    return mart, qual, surveys, geo, responses

mart, qual, surveys, geo, responses = load_data()

st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size:28px;">🔴 IFRC Community Trust Index Dashboard</h1>
    <p style="margin:5px 0 0 0; opacity:0.9; font-size:14px;">
        Real-time community trust monitoring | Bronze → Silver → Gold Lakehouse Architecture
    </p>
</div>
""", unsafe_allow_html=True)

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
st.sidebar.markdown("- 🟫 **Bronze**: Raw KoboToolbox ingestion\n- 🥈 **Silver**: Cleaned & standardised\n- 🥇 **Gold**: Analytics-ready mart")
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Data Summary**\n- {len(responses):,} survey responses\n- {len(qual):,} qualitative responses\n- {len(mart['country_name'].unique())} countries\n- {len(surveys)} surveys")

filtered = mart.copy()
if selected_zone != "All Zones": filtered = filtered[filtered["ifrc_zone"] == selected_zone]
if selected_country != "All Countries": filtered = filtered[filtered["country_name"] == selected_country]
if selected_quarter != "All Quarters": filtered = filtered[filtered["quarter"] == int(selected_quarter[1])]
if show_alerts_only: filtered = filtered[filtered["alert_flag"] == True]

st.markdown("### 📊 Key Trust Metrics")
col1, col2, col3, col4, col5 = st.columns(5)
avg_trust = filtered["overall_trust_score"].mean()
avg_competence = filtered["competence_score"].mean()
avg_integrity = filtered["integrity_score"].mean()
avg_benevolence = filtered["benevolence_score"].mean()
alert_count = filtered["alert_flag"].sum()

def sc(s): return "good-score" if s>=60 else "medium-score" if s>=45 else "low-score"

for col, label, val in zip([col1,col2,col3,col4],[
    "OVERALL TRUST INDEX","COMPETENCE","INTEGRITY","BENEVOLENCE"
],[avg_trust,avg_competence,avg_integrity,avg_benevolence]):
    with col:
        st.markdown(f'<div class="metric-card"><p style="margin:0;color:#666;font-size:12px;">{label}</p><p class="{sc(val)}">{val:.1f}</p><p style="margin:0;color:#999;font-size:11px;">out of 100</p></div>', unsafe_allow_html=True)

with col5:
    st.markdown(f'<div class="{"alert-card" if alert_count>0 else "metric-card"}"><p style="margin:0;color:#666;font-size:12px;">🚨 ACTIVE ALERTS</p><p style="color:{"#C8102E" if alert_count>0 else "#2E8B57"};font-weight:bold;font-size:24px;">{int(alert_count)}</p><p style="margin:0;color:#999;font-size:11px;">regions flagged</p></div>', unsafe_allow_html=True)

st.markdown("---")
col1, col2 = st.columns([1.3, 1])

with col1:
    st.markdown("#### 🛰️ Trust Index — Satellite Map")
    country_avg = filtered.groupby("country_name").agg({
        "overall_trust_score":"mean","competence_score":"mean","integrity_score":"mean",
        "benevolence_score":"mean","transparency_score":"mean","alert_flag":"sum","sample_size":"sum"
    }).reset_index().round(1)

    m = folium.Map(
        location=[15,20], zoom_start=2,
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery", control_scale=True
    )
    folium.TileLayer(
        tiles="https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
        attr="Esri", name="Labels", overlay=True, control=False
    ).add_to(m)

    for _, row in country_avg.iterrows():
        coords = COUNTRY_COORDS.get(row["country_name"])
        if not coords: continue
        score = row["overall_trust_score"]
        color = get_marker_color(score)
        popup_html = f"""
        <div style="font-family:Arial;min-width:220px;">
            <h4 style="margin:0 0 8px;color:#C8102E;border-bottom:1px solid #eee;padding-bottom:6px;">{row['country_name']}</h4>
            <table style="width:100%;font-size:13px;border-collapse:collapse;">
                <tr style="background:#f9f9f9;"><td style="padding:4px;"><b>Overall Trust</b></td><td style="text-align:right;padding:4px;color:{'#2E8B57' if score>=60 else '#FF8C00' if score>=45 else '#C8102E'};"><b>{score}/100</b></td></tr>
                <tr><td style="padding:4px;">Competence</td><td style="text-align:right;padding:4px;">{row['competence_score']}/100</td></tr>
                <tr style="background:#f9f9f9;"><td style="padding:4px;">Integrity</td><td style="text-align:right;padding:4px;">{row['integrity_score']}/100</td></tr>
                <tr><td style="padding:4px;">Benevolence</td><td style="text-align:right;padding:4px;">{row['benevolence_score']}/100</td></tr>
                <tr style="background:#f9f9f9;"><td style="padding:4px;">Transparency</td><td style="text-align:right;padding:4px;">{row['transparency_score']}/100</td></tr>
                <tr><td style="padding:4px;">Sample size</td><td style="text-align:right;padding:4px;">{int(row['sample_size'])} respondents</td></tr>
            </table>
            {'<p style="color:#C8102E;margin:8px 0 0;font-size:12px;font-weight:bold;">⚠️ Low trust alert</p>' if score<45 else '<p style="color:#2E8B57;margin:8px 0 0;font-size:12px;">✅ Within acceptable range</p>'}
        </div>"""
        folium.CircleMarker(
            location=coords, radius=max(15,min(45,score/1.8)),
            color="white", weight=2, fill=True, fill_color=color, fill_opacity=0.85,
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=folium.Tooltip(f"<b>{row['country_name']}</b><br>Trust Score: {score}/100", sticky=True)
        ).add_to(m)
        folium.Marker(
            location=[coords[0]+3.5, coords[1]],
            icon=folium.DivIcon(
                html=f'<div style="font-size:11px;font-weight:bold;color:white;text-shadow:1px 1px 3px black,-1px -1px 3px black;white-space:nowrap;text-align:center;">{row["country_name"]}<br><span style="font-size:12px;">{score}/100</span></div>',
                icon_size=(120,35), icon_anchor=(60,0)
            )
        ).add_to(m)

    st_folium(m, height=400, use_container_width=True)

with col2:
    st.markdown("#### 📊 Trust Dimensions by Country")
    country_dims = filtered.groupby("country_name").agg({
        "competence_score":"mean","integrity_score":"mean","benevolence_score":"mean","transparency_score":"mean"
    }).reset_index().round(1)
    fig_bar = go.Figure()
    for dim, color, label in zip(
        ["competence_score","integrity_score","benevolence_score","transparency_score"],
        ["#2E75B6","#C8102E","#2E8B57","#FF8C00"],
        ["Competence","Integrity","Benevolence","Transparency"]
    ):
        fig_bar.add_trace(go.Bar(name=label, x=country_dims["country_name"], y=country_dims[dim], marker_color=color, opacity=0.85))
    fig_bar.update_layout(barmode="group", height=400, margin=dict(l=0,r=0,t=20,b=0),
        legend=dict(orientation="h",yanchor="bottom",y=1.02),
        yaxis=dict(title="Score (0-100)",range=[0,100]), xaxis=dict(tickangle=-30))
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")
col1, col2 = st.columns([1.2,1])

with col1:
    st.markdown("#### 📉 Trust Score Trend Over Time")
    trend = filtered.groupby(["country_name","quarter"])["overall_trust_score"].mean().reset_index()
    trend["quarter_label"] = "Q" + trend["quarter"].astype(str) + " 2024"
    fig_trend = px.line(trend, x="quarter_label", y="overall_trust_score", color="country_name",
        markers=True, color_discrete_sequence=px.colors.qualitative.Set2,
        labels={"overall_trust_score":"Trust Score","quarter_label":"Quarter","country_name":"Country"})
    fig_trend.add_hline(y=45, line_dash="dash", line_color="#C8102E",
        annotation_text="Alert threshold (45)", annotation_position="bottom right")
    fig_trend.update_layout(height=320, margin=dict(l=0,r=0,t=20,b=0), yaxis=dict(range=[0,100]),
        legend=dict(orientation="h",yanchor="bottom",y=1.02,font=dict(size=10)))
    st.plotly_chart(fig_trend, use_container_width=True)

with col2:
    st.markdown("#### 💬 Community Sentiment by Country")
    
    # Join qualitative responses with survey to get country
    qual_with_country = qual.merge(
        surveys[["survey_id","country_code"]], on="survey_id", how="left"
    ).merge(
        mart[["country_code","country_name"]].drop_duplicates(), on="country_code", how="left"
    )
    
    # Filter to match selected filters
    if selected_country != "All Countries":
        qual_with_country = qual_with_country[qual_with_country["country_name"] == selected_country]
    if selected_zone != "All Zones":
        zone_countries = filtered["country_name"].unique()
        qual_with_country = qual_with_country[qual_with_country["country_name"].isin(zone_countries)]

    # Build sentiment by country
    sentiment_by_country = qual_with_country.groupby(["country_name","sentiment_label"]).size().reset_index(name="count")
    sentiment_totals = sentiment_by_country.groupby("country_name")["count"].sum().reset_index(name="total")
    sentiment_by_country = sentiment_by_country.merge(sentiment_totals, on="country_name")
    sentiment_by_country["pct"] = (sentiment_by_country["count"] / sentiment_by_country["total"] * 100).round(1)
    
    # Sort countries by positive sentiment descending
    positive_order = sentiment_by_country[sentiment_by_country["sentiment_label"]=="positive"].sort_values("pct", ascending=True)["country_name"].tolist()

    fig_sent_country = px.bar(
        sentiment_by_country,
        x="pct",
        y="country_name",
        color="sentiment_label",
        orientation="h",
        color_discrete_map={"positive":"#2E8B57","neutral":"#FF8C00","negative":"#C8102E"},
        labels={"pct":"% of responses","country_name":"","sentiment_label":"Sentiment"},
        category_orders={"country_name": positive_order, "sentiment_label":["positive","neutral","negative"]},
        barmode="stack",
        text="pct"
    )
    fig_sent_country.update_traces(texttemplate="%{text:.0f}%", textposition="inside", textfont_size=11)
    fig_sent_country.update_layout(
        height=380,
        margin=dict(l=0,r=0,t=10,b=0),
        xaxis=dict(title="% of responses", range=[0,100], ticksuffix="%"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        bargap=0.25
    )
    st.plotly_chart(fig_sent_country, use_container_width=True)

st.markdown("---")
col1, col2 = st.columns([1,1])

with col1:
    st.markdown("#### 🚨 Active Alerts")
    alerts = filtered[filtered["alert_flag"]==True][
        ["country_name","region","overall_trust_score","integrity_score","alert_reason","quarter"]
    ].sort_values("overall_trust_score")
    if len(alerts) > 0:
        for _, alert in alerts.head(8).iterrows():
            st.markdown(f'<div class="alert-card"><strong>🚨 {alert["country_name"]} — {alert["region"]} (Q{alert["quarter"]})</strong><br><span style="color:#C8102E;">Trust Score: {alert["overall_trust_score"]:.1f}/100</span> | Integrity: {alert["integrity_score"]:.1f}/100<br><small>{alert["alert_reason"]}</small></div>', unsafe_allow_html=True)
    else:
        st.success("✅ No active alerts for selected filters")

with col2:
    st.markdown("#### 🔴 Rumour & Misinformation Flags")
    rumours = qual[qual["rumour_flag"]==True][["theme_label","sentiment_label","free_text_response","nlp_confidence_score"]]
    if len(rumours) > 0:
        for _, r in rumours.head(5).iterrows():
            st.markdown(f'<div class="rumour-card"><strong>⚠️ {r["theme_label"]}</strong> <span style="color:#C8102E;font-size:11px;">[Confidence: {r["nlp_confidence_score"]:.0%}]</span><br><small style="color:#666;">"{r["free_text_response"][:120]}..."</small></div>', unsafe_allow_html=True)
    else:
        st.success("✅ No rumour flags detected")

st.markdown("---")
st.markdown("#### 🆚 Emergency vs Stable Context Comparison")
emergency_comp = filtered.groupby("emergency_context").agg({
    "overall_trust_score":"mean","competence_score":"mean","integrity_score":"mean",
    "benevolence_score":"mean","transparency_score":"mean"
}).reset_index().round(1)
emergency_comp["context"] = emergency_comp["emergency_context"].map({True:"Emergency Context",False:"Stable Context"})
fig_comp = go.Figure()
for _, row in emergency_comp.iterrows():
    fig_comp.add_trace(go.Bar(
        name=row["context"],
        x=["Overall Trust","Competence","Integrity","Benevolence","Transparency"],
        y=[row[d] for d in ["overall_trust_score","competence_score","integrity_score","benevolence_score","transparency_score"]],
        marker_color="#C8102E" if row["emergency_context"] else "#2E75B6"
    ))
fig_comp.update_layout(barmode="group", height=300, margin=dict(l=0,r=0,t=20,b=0),
    yaxis=dict(title="Score (0-100)",range=[0,100]),
    legend=dict(orientation="h",yanchor="bottom",y=1.02))
st.plotly_chart(fig_comp, use_container_width=True)

st.markdown("---")
st.markdown("""
<div style="background:#f8f8f8; border-top: 1px solid #ddd; border-radius:8px; padding:16px 20px; margin-top:10px;">
    <div style="text-align:center; margin-bottom:10px;">
        <span style="color:#C8102E; font-weight:bold; font-size:14px;">🔴 IFRC Community Trust Index Dashboard</span><br>
        <span style="color:#666; font-size:12px;">Built by Henrietta Atsenokhai | Data Engineer</span><br>
        <span style="color:#999; font-size:11px;">Bronze → Silver → Gold Lakehouse Architecture | Python · dbt · Streamlit · Folium · Plotly · Esri Satellite Imagery</span>
    </div>
    <hr style="border:none; border-top:1px solid #ddd; margin:10px 0;">
    <div style="text-align:center;">
        <p style="color:#888; font-size:11px; margin:0 0 6px;">
            <strong>⚠️ Disclaimer:</strong> This dashboard is a prototype built for demonstration purposes using synthetically generated sample data. 
            All data presented is fictional and does not represent real communities, survey responses, or IFRC operations. 
            Any resemblance to actual persons, locations, or events is coincidental.
        </p>
        <p style="color:#888; font-size:11px; margin:0;">
            <strong>© Intellectual Property Notice:</strong> All pipeline architecture, data models, dashboard design, 
            and code presented in this prototype are original works and constitute the exclusive intellectual property of 
            Henrietta Atsenokhai. Unauthorised reproduction, distribution, or use of these materials without express 
            written permission is strictly prohibited. All rights reserved © 2026.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
